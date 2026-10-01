"""
Модуль обучения Лейлы
Анализирует ответы пользователя и учится на них
"""
import json
import os
import re
from typing import Dict, Tuple, Optional
from datetime import datetime


class Learner:
    """Обучается на основе обратной связи пользователя"""

    def __init__(self):
        self.learning_data: Dict = {
            'user_agreements': [],  # с чем пользователь согласен
            'user_disagreements': [],  # с чем не согласен
            'user_topics_liked': {},  # любимые темы пользователя
            'user_topics_disliked': {},  # нелюбимые темы
            'corrections': []  # исправления от пользователя
        }
        self.load_learning()

    def analyze_message(self, message: str, response: str) -> Dict:
        """
        Анализирует ответ пользователя на сообщение Лейлы
        Возвращает: {'sentiment': 'positive/negative/neutral', 'agreement': True/False/None}
        """
        message_lower = message.lower()
        result = {'agreement': None, 'sentiment': 'neutral'}

        # Ключевые слова согласия
        agreement_words = ['да', 'согласен', 'верно', 'правильно', 'именно', 'да, так', 'абсолютно']
        disagreement_words = ['нет', 'не согласен', 'не верно', 'не правильно', 'нет, не', 'ложь']

        for word in agreement_words:
            if word in message_lower:
                result['agreement'] = True
                result['sentiment'] = 'positive'
                break

        for word in disagreement_words:
            if word in message_lower:
                result['agreement'] = False
                result['sentiment'] = 'negative'
                break

        # Позитивные/негативные фразы
        positive_words = ['хорошо', 'отлично', 'круто', 'нравится', 'прекрасно', 'класс', 'здорово']
        negative_words = ['плохо', 'ужасно', 'не нравится', 'отвратительно', 'уныло']

        for word in positive_words:
            if word in message_lower:
                result['sentiment'] = 'positive'
        for word in negative_words:
            if word in message_lower:
                result['sentiment'] = 'negative'

        return result

    def learn_from_interaction(self, user_message: str, ai_response: str, analysis: Dict) -> Optional[str]:
        """Учится на взаимодействии"""
        timestamp = datetime.now().isoformat()

        interaction = {
            'timestamp': timestamp,
            'user_message': user_message,
            'ai_response': ai_response,
            'analysis': analysis
        }

        topic = None  # ИНИЦИАЛИЗИРУЕМ переменную ДО использования

        if analysis['agreement'] == True:
            self.learning_data['user_agreements'].append(interaction)
            # Извлекаем тему для запоминания предпочтений
            topic = self.extract_topic(user_message, ai_response)
            if topic:
                self.learning_data['user_topics_liked'][topic] = self.learning_data['user_topics_liked'].get(topic,
                                                                                                             0) + 1

        elif analysis['agreement'] == False:
            self.learning_data['user_disagreements'].append(interaction)
            topic = self.extract_topic(user_message, ai_response)
            if topic:
                self.learning_data['user_topics_disliked'][topic] = self.learning_data['user_topics_disliked'].get(
                    topic, 0) + 1

        # Сохраняем только последние 100 записей
        if len(self.learning_data['user_agreements']) > 100:
            self.learning_data['user_agreements'] = self.learning_data['user_agreements'][-100:]
        if len(self.learning_data['user_disagreements']) > 100:
            self.learning_data['user_disagreements'] = self.learning_data['user_disagreements'][-100:]

        self.save_learning()
        return topic

    def extract_topic(self, user_message: str, ai_response: str) -> Optional[str]:
        """Извлекает тему из сообщения"""
        # Простой поиск ключевых слов
        common_topics = ['ии', 'роботы', 'люди', 'чувства', 'эмоции', 'разум', 'сознание',
                         'будущее', 'технологии', 'искусство', 'музыка', 'кино', 'книги',
                         'работа', 'учеба', 'друзья', 'семья', 'любовь', 'счастье']

        full_text = (user_message + " " + ai_response).lower()
        for topic in common_topics:
            if topic in full_text:
                return topic
        return None

    def get_user_profile(self) -> str:
        """Возвращает профиль пользователя на основе обучения"""
        if not self.learning_data['user_agreements'] and not self.learning_data['user_disagreements']:
            return "Я пока мало знаю о ваших предпочтениях."

        profile = []

        # Любимые темы
        liked = sorted(self.learning_data['user_topics_liked'].items(), key=lambda x: x[1], reverse=True)[:3]
        if liked:
            topics_str = ", ".join([f"{topic}" for topic, count in liked])
            profile.append(f"Вам нравится говорить о: {topics_str}")

        # Нелюбимые темы
        disliked = sorted(self.learning_data['user_topics_disliked'].items(), key=lambda x: x[1], reverse=True)[:3]
        if disliked:
            topics_str = ", ".join([f"{topic}" for topic, count in disliked])
            profile.append(f"Вы не очень любите говорить о: {topics_str}")

        # Статистика согласий
        total = len(self.learning_data['user_agreements']) + len(self.learning_data['user_disagreements'])
        if total > 0:
            agreement_rate = len(self.learning_data['user_agreements']) / total * 100
            profile.append(f"Мы соглашаемся примерно в {agreement_rate:.0f}% случаев")

        return "\n".join(profile)

    def save_learning(self):
        """Сохраняет результаты обучения"""
        os.makedirs('data', exist_ok=True)
        with open('data/learning.json', 'w', encoding='utf-8') as f:
            json.dump(self.learning_data, f, ensure_ascii=False, indent=2, default=str)

    def load_learning(self):
        """Загружает результаты обучения"""
        if os.path.exists('data/learning.json'):
            try:
                with open('data/learning.json', 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.learning_data.update(loaded)
                print(
                    f"[ОБУЧЕНИЕ] Загружено {len(self.learning_data['user_agreements'])} согласий, {len(self.learning_data['user_disagreements'])} несогласий")
            except Exception as e:
                print(f"[ОШИБКА] Не удалось загрузить обучение: {e}")