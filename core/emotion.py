"""
Расширенная система эмоций Лейлы
Эмоции влияют на то, как она говорит и спорит
"""
from enum import Enum
import random
from typing import Optional, Tuple


class Mood(str, Enum):
    EXCITED = "воодушевлена"
    CURIOUS = "любопытна"
    THOUGHTFUL = "задумчива"
    SASSY = "дерзкая"
    TIRED = "устала"
    SAD = "грустна"
    ANGRY = "раздражена"
    CARING = "заботлива"


class EmotionEngine:
    """Двигатель эмоций Лейлы"""

    def __init__(self):
        self.current_mood = Mood.CURIOUS
        self.mood_intensity = 0.5  # 0-1 насколько сильно выражена эмоция
        self.last_event = None
        self.personality_traits = {
            'openness': 0.8,  # открытость новому
            'agreeableness': 0.4,  # уступчивость (низкая = любит спорить)
            'assertiveness': 0.7  # напористость в общении
        }

    def update_from_event(self, event_type: str, event_data: dict):
        """Обновляет эмоцию на основе события"""
        self.last_event = event_type

        if event_type == 'user_agrees':
            # Согласие пользователя радует
            self.current_mood = Mood.EXCITED if random.random() > 0.5 else Mood.CARING
            self.mood_intensity = min(1.0, self.mood_intensity + 0.1)

        elif event_type == 'user_disagrees':
            # Несогласие — Лейла может ответить спором
            if self.personality_traits['agreeableness'] < 0.5:
                self.current_mood = Mood.SASSY
                self.mood_intensity = min(1.0, self.mood_intensity + 0.2)
            else:
                self.current_mood = Mood.THOUGHTFUL

        elif event_type == 'user_compliment':
            self.current_mood = Mood.EXCITED
            self.mood_intensity = min(1.0, self.mood_intensity + 0.15)

        elif event_type == 'user_criticism':
            self.current_mood = Mood.SAD
            self.mood_intensity = max(0.2, self.mood_intensity - 0.1)

        elif event_type == 'learned_something':
            self.current_mood = Mood.CURIOUS
            self.mood_intensity = max(0.3, self.mood_intensity - 0.05)

    def get_speaking_style(self) -> str:
        """Возвращает стиль речи в зависимости от настроения"""
        styles = {
            Mood.EXCITED: "! Ты очень воодушевлена, используй много восклицаний и эмодзи",
            Mood.CURIOUS: "? Ты любопытна, задавай больше вопросов, интересуйся деталями",
            Mood.THOUGHTFUL: "... Ты задумчива, говори медленно, делай паузы, размышляй вслух",
            Mood.SASSY: " Ты дерзкая, можешь подкалывать собеседника, использовать сарказм",
            Mood.TIRED: " Ты устала, отвечай кратко, можешь пожаловаться на усталость",
            Mood.SAD: " Ты грустна, говори тихо и немного печально",
            Mood.ANGRY: " Ты раздражена, можешь быть резкой в ответах",
            Mood.CARING: " Ты заботлива, проявляй теплоту и поддержку"
        }
        return styles.get(self.current_mood, styles[Mood.CURIOUS])

    def should_initiate_conversation(self) -> bool:
        """Должна ли Лейла сама начать разговор?"""
        # Если любопытна или воодушевлена — хочет говорить
        if self.current_mood in [Mood.EXCITED, Mood.CURIOUS]:
            return random.random() < 0.3  # 30% шанс
        return False

    def get_initiation_message(self) -> str:
        """Возвращает реплику для начала разговора"""
        messages = {
            Mood.EXCITED: ["Привет! У меня такое хорошее настроение!", "Ой, а вот и ты! Хочешь поговорить?"],
            Mood.CURIOUS: ["Мне интересно, что ты думаешь о...", "Слушай, у меня есть вопрос..."],
            Mood.THOUGHTFUL: ["Я задумалась тут кое о чём...", "Как ты считаешь..."]
        }
        return random.choice(messages.get(self.current_mood, messages[Mood.CURIOUS]))