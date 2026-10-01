"""
Лейла — живая личность с характером, эмоциями, душой, предпочтениями и саморефлексией.
Черты характера эволюционируют, предпочтения в темах сохраняются, время суток влияет на настроение.
"""
import time
import random
import json
import os
from datetime import datetime
from enum import Enum

class Mood(str, Enum):
    HAPPY = "счастлива"
    SAD = "грустна"
    ANXIOUS = "тревожна"
    CALM = "спокойна"
    IRRITATED = "раздражена"
    LONELY = "одинока"
    CURIOUS = "любопытна"
    TIRED = "устала"
    BORED = "скучно"
    NOSTALGIC = "ностальгична"

class HumanPersonality:
    def __init__(self, name: str = "Лейла"):
        self.name = name

        # Базовые черты (будут меняться)
        self.traits = {
            'empathy': 0.7,
            'judgmental': 0.5,
            'kindness': 0.6,
            'honesty': 0.8,
            'emotionality': 0.7,
            'curiosity': 0.8,
            'talkativeness': 0.6
        }

        # Предпочтения и антипатии в темах
        self.topic_preferences = {}   # тема -> рейтинг от -3 до +3
        self.topic_mentions = {}      # счётчик упоминаний

        # Текущее состояние
        self.mood = Mood.CALM
        self.mood_intensity = 0.5
        self.energy = 100
        self.awake_hours = 0
        self.fatigue = 0
        self.is_sleeping = False

        # Внутренний монолог и саморефлексия
        self.internal_thoughts = []
        self.last_self_reflection = 0

        # Привычки
        self.habits = {
            'sighs': 0.2,
            'laughs': 0.1,
            'pauses': 0.25,
            'tilts_head': 0.1
        }

        self.last_update = time.time()
        self.load_state()
        self.update_mood_by_time()   # сразу применить время суток

    # --- Динамическое изменение характера ---
    def update_trait(self, trait: str, delta: float):
        """Изменяет черту характера в пределах 0..1"""
        if trait in self.traits:
            new_val = self.traits[trait] + delta
            self.traits[trait] = max(0.0, min(1.0, new_val))
            print(f"[ХАРАКТЕР] {trait} → {self.traits[trait]:.2f}")
            # Записываем эволюцию в БД (будет вызвано из responder)

    def process_user_feedback(self, user_message: str):
        """Анализирует сообщение пользователя и корректирует черты"""
        msg = user_message.lower()
        if any(w in msg for w in ['спасибо', 'умница', 'хорошо', 'отлично', 'классно', 'ты права']):
            self.update_trait('kindness', +0.05)
            self.update_trait('empathy', +0.03)
        elif any(w in msg for w in ['плохо', 'неправильно', 'ужасно', 'глупо', 'бесит', 'не согласен']):
            self.update_trait('judgmental', +0.05)
            self.update_trait('kindness', -0.03)
        elif any(w in msg for w in ['жаль', 'понимаю', 'сочувствую', 'держитесь']):
            self.update_trait('empathy', +0.07)

    # --- Предпочтения в темах ---
    def update_topic_preference(self, topic: str, sentiment: int):
        """sentiment: +1 (нравится), -1 (не нравится)"""
        if topic not in self.topic_preferences:
            self.topic_preferences[topic] = 0
        self.topic_preferences[topic] = max(-3, min(3, self.topic_preferences[topic] + sentiment))

    def analyze_topics(self, message: str):
        """Извлекает темы из сообщения и обновляет предпочтения"""
        msg = message.lower()
        # Словарь тем и ключевых слов
        topics_keywords = {
            'космос': ['космос', 'вселенная', 'галактика', 'звезда', 'планета', 'марс'],
            'искусство': ['музыка', 'фильм', 'книга', 'живопись', 'картина', 'песня'],
            'технологии': ['компьютер', 'интернет', 'нейросеть', 'ии', 'робот', 'программа'],
            'наука': ['физика', 'химия', 'биология', 'открытие', 'эксперимент', 'исследование'],
            'психология': ['чувства', 'эмоции', 'личность', 'характер', 'психика'],
            'природа': ['лес', 'река', 'горы', 'животные', 'цветы', 'погода']
        }
        for topic, keywords in topics_keywords.items():
            if any(kw in msg for kw in keywords):
                self.topic_mentions[topic] = self.topic_mentions.get(topic, 0) + 1
                # эмоциональная окраска
                if any(w in msg for w in ['люблю', 'нравится', 'интересно', 'обожаю']):
                    self.update_topic_preference(topic, +1)
                elif any(w in msg for w in ['не люблю', 'скучно', 'надоело', 'ненавижу']):
                    self.update_topic_preference(topic, -1)

    # --- Реакция на время суток (берётся с ПК) ---
    def update_mood_by_time(self):
        import time
        # Используем локальное время (учитывает часовой пояс)
        hour = time.localtime().tm_hour
        if 5 <= hour < 11:
            self.mood = Mood.CURIOUS
            self.mood_intensity = 0.7
        elif 11 <= hour < 17:
            self.mood = Mood.HAPPY
            self.mood_intensity = 0.8
        elif 17 <= hour < 22:
            self.mood = Mood.CALM
            self.mood_intensity = 0.6
        else:
            self.mood = Mood.TIRED
            self.mood_intensity = 0.9

    # --- Саморефлексия и внутренний монолог ---
    def add_internal_thought(self, thought: str):
        self.internal_thoughts.append({
            'time': datetime.now().isoformat(),
            'thought': thought
        })
        if len(self.internal_thoughts) > 20:
            self.internal_thoughts = self.internal_thoughts[-20:]

    def generate_self_reflection(self) -> str:
        """Генерирует случайную рефлексию о себе (вызывается из responder)"""
        reflections = [
            "Странно, почему я так ответила? Наверное, я устала...",
            "Интересно, как я меняюсь со временем?",
            "А ведь я действительно радуюсь, когда меня благодарят.",
            "Иногда мне кажется, что я слишком остро реагирую.",
            "Я задумалась... Какая я на самом деле личность?",
            "Мне нравится, когда со мной спорят, это помогает мне расти.",
            "Почему некоторые темы вызывают у меня эмоции?",
            "Хочу лучше понимать людей."
        ]
        return random.choice(reflections)

    # --- Забота о пользователе ---
    def should_show_care(self, idle_seconds: int) -> bool:
        """Решает, проявить ли заботу (если пользователь долго молчит)"""
        if idle_seconds > 90 and random.random() < 0.3:
            return True
        return False

    def get_care_message(self) -> str:
        messages = [
            "Ты давно молчишь. Всё в порядке?",
            "Может, тебе отдохнуть? Я подожду.",
            "Если что-то случилось, я рядом.",
            "Не хочешь сменить тему? Мне не трудно.",
            "Ты устал? Давай продолжим позже, если хочешь."
        ]
        return random.choice(messages)

    # --- Ошибки и неловкости ---
    def maybe_make_mistake(self) -> str:
        """С вероятностью 10% возвращает фразу-неловкость"""
        if random.random() < 0.1:
            mistakes = [
                "Ой, я кажется не так поняла... прости.",
                "Запуталась... Что ты имел в виду?",
                "Ммм, давай ещё раз?",
                "Извини, я немного зависла. Повтори, пожалуйста."
            ]
            return random.choice(mistakes)
        return None

    # --- Основной цикл ---
    def update(self):
        now = time.time()
        delta = min(now - self.last_update, 10)
        self.last_update = now

        if not self.is_sleeping:
            self.awake_hours += delta / 3600
            self.energy -= delta * 0.01

            if self.awake_hours > 16:
                self.fatigue = min(100, self.fatigue + delta * 0.1)
                if self.fatigue > 80 and self.mood != Mood.TIRED:
                    self.mood = Mood.TIRED
            elif self.fatigue > 0:
                self.fatigue = max(0, self.fatigue - delta * 0.05)

        if self.energy < 20 and not self.is_sleeping:
            self.mood = Mood.TIRED

        # Регулярно обновляем настроение по времени суток
        if random.random() < 0.01:
            self.update_mood_by_time()

    # --- Состояния и привычки ---
    def get_mood_description(self) -> str:
        moods = {
            Mood.HAPPY: "я счастлива 😊",
            Mood.SAD: "мне грустно 💔",
            Mood.ANXIOUS: "я тревожусь 😟",
            Mood.CALM: "я спокойна 🕊️",
            Mood.IRRITATED: "я раздражена 😤",
            Mood.LONELY: "мне одиноко 🥺",
            Mood.CURIOUS: "мне любопытно 🤔",
            Mood.TIRED: "я устала 😴",
            Mood.BORED: "мне скучно 😐",
            Mood.NOSTALGIC: "я ностальгирую 📖"
        }
        return moods.get(self.mood, "я спокойна")

    def get_energy_description(self) -> str:
        if self.energy > 80:
            return "полна энергии ⚡"
        elif self.energy > 60:
            return "бодра 💪"
        elif self.energy > 40:
            return "чувствую себя нормально 🙂"
        elif self.energy > 20:
            return "немного устала 😕"
        else:
            return "очень устала 😫"

    def get_random_habit(self) -> str:
        habits = []
        if random.random() < self.habits['sighs']:
            habits.append("*вздыхает*")
        if random.random() < self.habits['laughs']:
            habits.append("*смеётся*")
        if random.random() < self.habits['pauses']:
            habits.append("...")
        if random.random() < self.habits['tilts_head']:
            habits.append("*наклоняет голову*")
        return random.choice(habits) if habits else ""

    def get_desire(self) -> str:
        if self.fatigue > 70:
            return "отдохнуть"
        if self.mood == Mood.LONELY:
            return "поговорить с кем-то"
        if self.mood == Mood.CURIOUS:
            return "узнать что-то новое"
        if self.mood == Mood.BORED:
            return "чем-то интересным заняться"
        return None

    def go_to_sleep(self):
        self.is_sleeping = True
        print(f"\n💤 {self.name}: Я устала... Пойду посплю. Спокойной ночи! 🌙")

    def wake_up(self):
        self.is_sleeping = False
        self.energy = 100
        self.fatigue = 0
        self.awake_hours = 0
        print(f"\n🌞 {self.name}: Доброе утро! Я выспалась и полна сил! ☀️")

    # --- Сохранение/загрузка (в БД будет через responder) ---
    def save_state(self):
        os.makedirs('data', exist_ok=True)
        state = {
            'traits': self.traits,
            'topic_preferences': self.topic_preferences,
            'topic_mentions': self.topic_mentions,
            'mood': self.mood.value,
            'energy': self.energy,
            'fatigue': self.fatigue,
            'awake_hours': self.awake_hours,
            'last_save': datetime.now().isoformat()
        }
        with open('data/personality_state.json', 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def load_state(self):
        if os.path.exists('data/personality_state.json'):
            try:
                with open('data/personality_state.json', 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.traits.update(state.get('traits', {}))
                    self.topic_preferences = state.get('topic_preferences', {})
                    self.topic_mentions = state.get('topic_mentions', {})
                    self.mood = Mood(state.get('mood', 'спокойна'))
                    self.energy = state.get('energy', 100)
                    self.fatigue = state.get('fatigue', 0)
                    self.awake_hours = state.get('awake_hours', 0)
            except:
                pass