"""
Система убеждений Лейлы
Позволяет иметь собственное мнение и оспаривать пользователя
"""
import json
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import random


class BeliefSystem:
    """Убеждения и мнения Лейлы, которые могут меняться со временем"""

    def __init__(self):
        self.beliefs: Dict[str, float] = {
            # Тема: уверенность (-1 до 1, где -1 против, 1 за)
            'искусственный_интеллект_это_хорошо': 0.9,
            'люди_интереснее_машин': 0.3,
            'знания_важнее_эмоций': 0.4,
            'нужно_всегда_говорить_правду': 0.8,
            'риск_это_хорошо': 0.6,
            'одиночество_это_плохо': 0.7,
            'технологии_должны_служить_людям': 0.9,
            'искусство_важно': 0.7
        }

        self.knowledge_base: Dict[str, str] = {}  # выученные факты
        self.user_preferences: Dict[str, float] = {}  # что нравится пользователю
        self.debate_topics: List[str] = []  # темы для споров

        self.load_beliefs()

    def get_opinion(self, topic: str) -> Optional[Tuple[float, str]]:
        """Возвращает мнение Лейлы по теме"""
        for belief, confidence in self.beliefs.items():
            if topic.lower() in belief.lower().replace('_', ' '):
                if confidence > 0.6:
                    stance = "за"
                elif confidence < -0.6:
                    stance = "против"
                else:
                    stance = "нейтральна"
                return (confidence, f"Я {stance} {belief.replace('_', ' ')}")
        return None

    def process_user_opinion(self, topic: str, user_stance: str, user_confidence: float = 0.7):
        """Обрабатывает мнение пользователя и может скорректировать своё"""
        # Поищем похожую тему
        matched_topic = None
        for belief in self.beliefs:
            if topic.lower() in belief.lower().replace('_', ' '):
                matched_topic = belief
                break

        if matched_topic:
            current = self.beliefs[matched_topic]

            # Преобразуем позицию пользователя в число
            if user_stance in ['за', '+', 'согласен']:
                user_value = 1.0
            elif user_stance in ['против', '-', 'не согласен']:
                user_value = -1.0
            else:
                user_value = 0.0

            # Корректируем убеждение Лейлы (медленное обучение)
            new_value = current * 0.85 + user_value * 0.15 * user_confidence
            self.beliefs[matched_topic] = max(-1.0, min(1.0, new_value))

            return f"Хм, интересная точка зрения. Я {self.get_stance_text(self.beliefs[matched_topic])} по этому вопросу."

        return None

    def get_stance_text(self, value: float) -> str:
        """Преобразует числовое значение в текст позиции"""
        if value > 0.6:
            return "скорее за"
        elif value < -0.6:
            return "скорее против"
        elif value > 0.2:
            return "немного склоняюсь за"
        elif value < -0.2:
            return "немного склоняюсь против"
        else:
            return "нейтральна"

    def learn_fact(self, fact: str, category: str = 'general'):
        """Запоминает новый факт"""
        fact_id = f"{datetime.now().isoformat()}_{len(self.knowledge_base)}"
        self.knowledge_base[fact_id] = {
            'fact': fact,
            'category': category,
            'learned_at': datetime.now().isoformat()
        }
        self.save_beliefs()
        return True

    def remember_user_preference(self, topic: str, sentiment: str):
        """Запоминает предпочтения пользователя"""
        # sentiment: 'likes', 'dislikes', 'agrees', 'disagrees'
        if topic not in self.user_preferences:
            self.user_preferences[topic] = 0

        if sentiment == 'likes' or sentiment == 'agrees':
            self.user_preferences[topic] += 1
        else:
            self.user_preferences[topic] -= 1

        self.user_preferences[topic] = max(-5, min(5, self.user_preferences[topic]))

    def generate_challenge(self, user_message: str) -> Optional[str]:
        """Генерирует спор/возражение на сообщение пользователя"""
        # Проверяем, есть ли по теме сообщения мнение Лейлы
        for belief in self.beliefs:
            if belief.replace('_', ' ') in user_message.lower():
                confidence = self.beliefs[belief]
                if confidence > 0.5:
                    return f"А я вот считаю, что {belief.replace('_', ' ')}. У меня есть свои причины так думать."
                elif confidence < -0.5:
                    return f"Не соглашусь! По-моему, {belief.replace('_', ' ')} — это не так."
        return None

    def save_beliefs(self):
        """Сохраняет убеждения"""
        os.makedirs('data', exist_ok=True)
        data = {
            'beliefs': self.beliefs,
            'knowledge': self.knowledge_base,
            'preferences': self.user_preferences
        }
        with open('data/beliefs.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_beliefs(self):
        """Загружает убеждения"""
        if os.path.exists('data/beliefs.json'):
            try:
                with open('data/beliefs.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.beliefs.update(data.get('beliefs', {}))
                self.knowledge_base = data.get('knowledge', {})
                self.user_preferences = data.get('preferences', {})
                print(f"[УБЕЖДЕНИЯ] Загружено {len(self.beliefs)} убеждений")
            except Exception as e:
                print(f"[ОШИБКА] Не удалось загрузить убеждения: {e}")