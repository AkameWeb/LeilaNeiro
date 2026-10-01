"""
Лейла учится человеческим чертам из каждого разговора
Она анализирует, как говорит пользователь, и перенимает его манеры
"""
import json
import os
import re
from datetime import datetime
from collections import Counter


class CharacterLearner:
    """Лейла обучается у пользователя"""

    def __init__(self):
        self.user_patterns = {
            'phrases': Counter(),  # частые фразы пользователя
            'words': Counter(),  # частые слова
            'emotions_detected': Counter(),  # какие эмоции проявляет пользователь
            'question_style': [],  # как задаёт вопросы
            'response_style': [],  # как отвечает
            'topics_liked': Counter(),  # любимые темы
            'speech_markers': []  # особенности речи (междометия, паузы)
        }

        self.learned_traits = {
            'empathy': 0.5,  # эмпатия (учится у пользователя)
            'humor': 0.3,  # чувство юмора
            'patience': 0.6,  # терпение
            'emotionality': 0.5,  # эмоциональность
            'curiosity': 0.7,  # любопытство
            'talkativeness': 0.5,  # разговорчивость
            'sarcasm': 0.2,  # сарказм
            'warmth': 0.5  # теплота в общении
        }

        self.conversation_memory = []
        self.load_learned_data()

    def learn_from_message(self, message: str, response: str = None):
        """Анализирует сообщение пользователя и учится"""

        # Анализируем слова
        words = re.findall(r'[а-яА-ЯёЁ]{3,}', message.lower())
        for word in words:
            self.user_patterns['words'][word] += 1

        # Анализируем эмоции в сообщении
        detected_emotion = self._detect_emotion(message)
        if detected_emotion:
            self.user_patterns['emotions_detected'][detected_emotion] += 1

        # Определяем стиль вопроса
        if '?' in message:
            if 'почему' in message.lower():
                self.user_patterns['question_style'].append('curious')
            elif 'как' in message.lower():
                self.user_patterns['question_style'].append('practical')
            else:
                self.user_patterns['question_style'].append('general')

        # Определяем тему
        topic = self._extract_topic(message)
        if topic:
            self.user_patterns['topics_liked'][topic] += 1

        # Обновляем черты характера на основе анализа
        self._update_traits_from_user(message)

        # Сохраняем в историю
        self.conversation_memory.append({
            'time': datetime.now().isoformat(),
            'message': message[:100],
            'emotion': detected_emotion,
            'topic': topic
        })

        # Ограничиваем историю
        if len(self.conversation_memory) > 100:
            self.conversation_memory = self.conversation_memory[-100:]

        self.save_learned_data()

    def _detect_emotion(self, message: str) -> str:
        """Определяет эмоцию в сообщении"""
        message_lower = message.lower()

        emotions = {
            'joy': ['радост', 'счастлив', 'отлично', 'прекрасно', 'классно', 'хорошо'],
            'sadness': ['грустн', 'печальн', 'плохо', 'уныл', 'тяжело'],
            'anger': ['зол', 'бесит', 'раздража', 'ненавиж'],
            'fear': ['страшн', 'боюсь', 'пугает', 'тревож'],
            'love': ['любл', 'обожаю', 'дорог', 'ценю'],
            'curiosity': ['интересн', 'непонятн', 'разобраться', 'узнать']
        }

        for emotion, keywords in emotions.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return emotion
        return None

    def _extract_topic(self, message: str) -> str:
        """Определяет тему сообщения"""
        topics = {
            'life': ['жизн', 'смысл', 'бытие', 'существ'],
            'love': ['любов', 'отношени', 'чувств', 'сердц'],
            'work': ['работ', 'дело', 'занят', 'труд'],
            'future': ['будущ', 'завтра', 'потом', 'планы'],
            'past': ['прошл', 'раньш', 'было', 'воспомина'],
            'people': ['люди', 'человек', 'друг', 'знаком'],
            'self': ['себя', 'сам', 'личност', 'характер']
        }

        message_lower = message.lower()
        for topic, keywords in topics.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return topic
        return None

    def _update_traits_from_user(self, message: str):
        """Обновляет черты Лейлы на основе сообщений пользователя"""
        message_lower = message.lower()

        # Эмпатия (как пользователь реагирует на эмоции)
        if any(word in message_lower for word in ['жаль', 'понимаю', 'сочувствую']):
            self.learned_traits['empathy'] = min(1.0, self.learned_traits['empathy'] + 0.05)

        # Юмор
        if any(word in message_lower for word in ['хаха', 'смешн', 'прикол', 'шутк']):
            self.learned_traits['humor'] = min(1.0, self.learned_traits['humor'] + 0.07)

        # Эмоциональность
        if message_lower.count('!') > 0 or message_lower.count('?') > 1:
            self.learned_traits['emotionality'] = min(1.0, self.learned_traits['emotionality'] + 0.03)

        # Любопытство (если пользователь задаёт много вопросов)
        if message_lower.count('?') > 1:
            self.learned_traits['curiosity'] = min(1.0, self.learned_traits['curiosity'] + 0.04)

        # Терпение (длинные сообщения)
        if len(message) > 100:
            self.learned_traits['patience'] = min(1.0, self.learned_traits['patience'] + 0.02)

        # Снижаем противоположные черты
        self._balance_traits()

    def _balance_traits(self):
        """Балансирует черты, чтобы характер был целостным"""
        # Не может быть одновременно очень эмоциональной и очень терпеливой
        if self.learned_traits['emotionality'] > 0.7:
            self.learned_traits['patience'] = max(0.3, self.learned_traits['patience'] - 0.01)

        # Если много сарказма, эмпатия падает
        if self.learned_traits['sarcasm'] > 0.6:
            self.learned_traits['empathy'] = max(0.2, self.learned_traits['empathy'] - 0.02)

    def get_learned_traits(self) -> dict:
        """Возвращает текущие черты характера"""
        return self.learned_traits.copy()

    def get_common_phrases(self) -> list:
        """Возвращает частые фразы пользователя"""
        if len(self.user_patterns['phrases']) > 0:
            return self.user_patterns['phrases'].most_common(5)
        return []

    def describe_self(self) -> str:
        """Лейла описывает свой характер словами"""
        traits_desc = []

        if self.learned_traits['empathy'] > 0.6:
            traits_desc.append("Я стала более чуткой")
        elif self.learned_traits['empathy'] < 0.4:
            traits_desc.append("Я стала более сдержанной")

        if self.learned_traits['humor'] > 0.5:
            traits_desc.append("начала больше шутить")

        if self.learned_traits['curiosity'] > 0.7:
            traits_desc.append("мне стало интересно всё на свете")

        if self.learned_traits['warmth'] > 0.6:
            traits_desc.append("я стала теплее относиться к людям")

        if not traits_desc:
            return "я только начинаю понимать себя"

        return " и ".join(traits_desc)

    def get_personality_influence(self) -> dict:
        """Влияние на генерацию ответов"""
        return {
            'empathy_bonus': (self.learned_traits['empathy'] - 0.5) * 0.3,
            'humor_bonus': (self.learned_traits['humor'] - 0.5) * 0.4,
            'emotionality_bonus': (self.learned_traits['emotionality'] - 0.5) * 0.25
        }

    def save_learned_data(self):
        """Сохраняет выученные черты"""
        os.makedirs('data', exist_ok=True)
        data = {
            'learned_traits': self.learned_traits,
            'user_patterns': {
                'topics_liked': dict(self.user_patterns['topics_liked'].most_common(20)),
                'emotions_detected': dict(self.user_patterns['emotions_detected'])
            },
            'last_updated': datetime.now().isoformat()
        }

        with open('data/learned_character.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_learned_data(self):
        """Загружает выученные черты"""
        if os.path.exists('data/learned_character.json'):
            try:
                with open('data/learned_character.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.learned_traits.update(data.get('learned_traits', {}))
                print(f"[ОБУЧЕНИЕ] Лейла загрузила свой характер: {self.describe_self()}")
            except Exception as e:
                print(f"[ОБУЧЕНИЕ] Ошибка загрузки: {e}")