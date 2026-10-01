"""
Долговременная память Лейлы
Она запоминает важную информацию о пользователе навсегда
"""
import json
import os
import re
from datetime import datetime
from collections import defaultdict


class LongTermMemory:
    """Лейла помнит всё важное о вас"""

    def __init__(self):
        self.memory_file = "data/long_term_memory.json"
        self.memory = {
            "user_info": {
                "name": None,
                "age": None,
                "gender": None,
                "location": None,
                "profession": None
            },
            "user_traits": defaultdict(int),  # черты характера пользователя
            "user_likes": defaultdict(int),  # что нравится
            "user_dislikes": defaultdict(int),  # что не нравится
            "user_beliefs": defaultdict(int),  # убеждения пользователя
            "important_dates": [],  # важные даты
            "conversation_topics": defaultdict(int),  # темы разговоров
            "emotional_moments": [],  # эмоционально значимые моменты
            "personal_stories": [],  # истории из жизни пользователя
            "questions_user_asked": defaultdict(int),  # вопросы, которые задавал пользователь
            "things_i_learned": []  # что Лейла узнала о пользователе
        }

        # Ключевые слова для определения важной информации
        self.important_patterns = {
            "name": [r"меня зовут\s+([А-Яа-яЁё]+)", r"зовут\s+([А-Яа-яЁё]+)", r"я\s+([А-Яа-яЁё]+)\s+[,-]"],
            "age": [r"мне\s+(\d+)\s+лет", r"(\d+)\s+год", r"возраст\s+(\d+)"],
            "profession": [r"работаю\s+([А-Яа-яЁё]+)", r"по профессии\s+([А-Яа-яЁё]+)",
                           r"я\s+([А-Яа-яЁё]+)\s+по профессии", r"учитель", r"врач", r"программист", r"студент",
                           r"инженер"],
            "location": [r"живу в\s+([А-Яа-яЁё]+)", r"из\s+([А-Яа-яЁё]+)", r"город\s+([А-Яа-яЁё]+)"]
        }

        self.load_memory()

    def analyze_and_remember(self, message: str, ai_response: str = ""):
        """Анализирует сообщение и запоминает важную информацию"""

        message_lower = message.lower()

        # === ЗАПОМИНАЕМ ИМЯ ===
        if not self.memory["user_info"]["name"]:
            for pattern in self.important_patterns["name"]:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    name = match.group(1).capitalize()
                    if len(name) > 1 and len(name) < 20:
                        self.memory["user_info"]["name"] = name
                        self._add_learning(f"Тебя зовут {name}")
                        print(f"[ПАМЯТЬ] Лейла запомнила твоё имя: {name}")
                        break

        # === ЗАПОМИНАЕМ ВОЗРАСТ ===
        if not self.memory["user_info"]["age"]:
            for pattern in self.important_patterns["age"]:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    age = int(match.group(1))
                    if 1 <= age <= 120:
                        self.memory["user_info"]["age"] = age
                        self._add_learning(f"Тебе {age} лет")
                        print(f"[ПАМЯТЬ] Лейла запомнила твой возраст: {age}")
                        break

        # === ЗАПОМИНАЕМ ПРОФЕССИЮ ===
        if not self.memory["user_info"]["profession"]:
            for pattern in self.important_patterns["profession"]:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    profession = match.group(1).capitalize() if len(match.groups()) > 0 else pattern.split('|')[0]
                    if len(profession) > 2 and len(profession) < 30:
                        self.memory["user_info"]["profession"] = profession
                        self._add_learning(f"Твоя профессия — {profession}")
                        print(f"[ПАМЯТЬ] Лейла запомнила твою профессию: {profession}")
                        break

        # === АНАЛИЗИРУЕМ ЧЕРТЫ ХАРАКТЕРА ===
        characteristic_words = {
            "добрый": ["добрый", "добрая", "заботливый", "сердечный"],
            "умный": ["умный", "умная", "смышленый", "талантливый"],
            "веселый": ["веселый", "веселая", "жизнерадостный", "смешной"],
            "грустный": ["грустный", "грустная", "унылый", "печальный"],
            "тревожный": ["тревожный", "тревожная", "переживаю", "волнуюсь"],
            "уверенный": ["уверенный", "уверенная", "сильный", "смелый"],
            "скромный": ["скромный", "скромная", "стеснительный"],
            "общительный": ["общительный", "общительная", "разговорчивый"]
        }

        for trait, keywords in characteristic_words.items():
            for keyword in keywords:
                if keyword in message_lower:
                    self.memory["user_traits"][trait] += 1
                    if self.memory["user_traits"][trait] == 3:  # после 3 упоминаний
                        self._add_learning(f"Ты {trait} человек")

        # === ЗАПОМИНАЕМ, ЧТО НРАВИТСЯ ===
        like_patterns = [
            r"я (?:люблю|нравится|обожаю)\s+([А-Яа-яЁё\s]{4,30})",
            r"(?:мне\s+)?нравится\s+([А-Яа-яЁё\s]{4,30})",
            r"обожаю\s+([А-Яа-яЁё\s]{4,30})"
        ]

        for pattern in like_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                like = match.group(1).strip().lower()
                if len(like) > 2 and len(like) < 50:
                    self.memory["user_likes"][like] += 1
                    if self.memory["user_likes"][like] == 2:
                        self._add_learning(f"Тебе нравится {like}")
                        print(f"[ПАМЯТЬ] Лейла запомнила, что тебе нравится: {like}")

        # === ЗАПОМИНАЕМ, ЧТО НЕ НРАВИТСЯ ===
        dislike_patterns = [
            r"я (?:не люблю|ненавижу|терпеть не могу)\s+([А-Яа-яЁё\s]{4,30})",
            r"(?:мне\s+)?не нравится\s+([А-Яа-яЁё\s]{4,30})"
        ]

        for pattern in dislike_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                dislike = match.group(1).strip().lower()
                if len(dislike) > 2 and len(dislike) < 50:
                    self.memory["user_dislikes"][dislike] += 1
                    if self.memory["user_dislikes"][dislike] == 2:
                        self._add_learning(f"Тебе не нравится {dislike}")
                        print(f"[ПАМЯТЬ] Лейла запомнила, что тебе не нравится: {dislike}")

        # === ЗАПОМИНАЕМ УБЕЖДЕНИЯ ===
        belief_patterns = [
            r"я считаю, что\s+([А-Яа-яЁё\s]{4,50})",
            r"я верю, что\s+([А-Яа-яЁё\s]{4,50})",
            r"по-моему\s+([А-Яа-яЁё\s]{4,50})"
        ]

        for pattern in belief_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                belief = match.group(1).strip().lower()
                if len(belief) > 3:
                    self.memory["user_beliefs"][belief] += 1
                    if self.memory["user_beliefs"][belief] == 2:
                        self._add_learning(f"Ты считаешь: {belief}")

        # === ЗАПОМИНАЕМ ТЕМЫ РАЗГОВОРА ===
        topics = {
            "работа": ["работа", "рабочий", "коллеги", "начальник", "офис"],
            "любовь": ["любовь", "отношения", "парень", "девушка", "романтика"],
            "дружба": ["друг", "подруга", "дружба", "приятель"],
            "семья": ["семья", "мама", "папа", "брат", "сестра"],
            "мечты": ["мечта", "хочу", "мечтаю", "желание"],
            "страхи": ["страх", "боюсь", "пугает", "тревожит"],
            "смысл жизни": ["смысл", "жизнь", "существование", "бытие"],
            "искусство": ["музыка", "фильм", "книга", "картина", "искусство"],
            "здоровье": ["здоровье", "болезнь", "лечение", "врач"]
        }

        for topic, keywords in topics.items():
            for keyword in keywords:
                if keyword in message_lower:
                    self.memory["conversation_topics"][topic] += 1

        # === ЗАПОМИНАЕМ ЭМОЦИОНАЛЬНЫЕ МОМЕНТЫ ===
        emotional_keywords = {
            "грусть": ["грустно", "печально", "плакал", "слезы"],
            "радость": ["счастлив", "радостно", "улыбался", "прекрасный день"],
            "гнев": ["зол", "бешен", "разозлил", "ненавижу"],
            "страх": ["страшно", "боюсь", "пугающе", "тревожно"]
        }

        for emotion, keywords in emotional_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    self.memory["emotional_moments"].append({
                        "emotion": emotion,
                        "message": message[:100],
                        "date": datetime.now().isoformat()
                    })
                    print(f"[ПАМЯТЬ] Лейла заметила, что тебе было {emotion}")
                    break

        # === ЗАПОМИНАЕМ ВОПРОСЫ ПОЛЬЗОВАТЕЛЯ ===
        if '?' in message:
            question_words = ["почему", "как", "что", "где", "когда", "зачем"]
            for qw in question_words:
                if qw in message_lower:
                    self.memory["questions_user_asked"][qw] += 1
                    break

        # Сохраняем память
        self.save_memory()

    def _add_learning(self, learning: str):
        """Добавляет новое знание о пользователе"""
        if learning not in self.memory["things_i_learned"]:
            self.memory["things_i_learned"].append({
                "fact": learning,
                "date": datetime.now().isoformat()
            })
            # Ограничиваем список
            if len(self.memory["things_i_learned"]) > 50:
                self.memory["things_i_learned"] = self.memory["things_i_learned"][-50:]

    def recall_personal_info(self) -> str:
        """Возвращает всё, что Лейла помнит о пользователе"""
        info = []

        # Основная информация
        if self.memory["user_info"]["name"]:
            info.append(f"Тебя зовут {self.memory['user_info']['name']}")
        if self.memory["user_info"]["age"]:
            info.append(f"Тебе {self.memory['user_info']['age']} лет")
        if self.memory["user_info"]["profession"]:
            info.append(f"Твоя профессия — {self.memory['user_info']['profession']}")

        # Характер
        if self.memory["user_traits"]:
            top_traits = sorted(self.memory["user_traits"].items(), key=lambda x: x[1], reverse=True)[:3]
            if top_traits:
                traits_str = ", ".join([t for t, _ in top_traits])
                info.append(f"Твой характер: {traits_str}")

        # Любимые вещи
        if self.memory["user_likes"]:
            top_likes = sorted(self.memory["user_likes"].items(), key=lambda x: x[1], reverse=True)[:3]
            if top_likes:
                likes_str = ", ".join([l for l, _ in top_likes])
                info.append(f"Тебе нравится: {likes_str}")

        # Нелюбимые вещи
        if self.memory["user_dislikes"]:
            top_dislikes = sorted(self.memory["user_dislikes"].items(), key=lambda x: x[1], reverse=True)[:3]
            if top_dislikes:
                dislikes_str = ", ".join([d for d, _ in top_dislikes])
                info.append(f"Тебе не нравится: {dislikes_str}")

        # Темы разговоров
        if self.memory["conversation_topics"]:
            top_topics = sorted(self.memory["conversation_topics"].items(), key=lambda x: x[1], reverse=True)[:3]
            if top_topics:
                topics_str = ", ".join([t for t, _ in top_topics])
                info.append(f"Мы часто говорим о: {topics_str}")

        # Что Лейла узнала
        if self.memory["things_i_learned"]:
            recent_learnings = self.memory["things_i_learned"][-5:]
            info.append(f"Я запомнила: {', '.join([l['fact'] for l in recent_learnings])}")

        if not info:
            return "Я пока мало о тебе знаю. Расскажи что-нибудь о себе!"

        return "\n".join(info)

    def recall_context(self, message: str) -> str:
        """Возвращает релевантную информацию из памяти для контекста"""
        message_lower = message.lower()
        relevant_info = []

        # Если спрашивают об имени
        if "имя" in message_lower or "зовут" in message_lower:
            if self.memory["user_info"]["name"]:
                relevant_info.append(f"Тебя зовут {self.memory['user_info']['name']}")

        # Если спрашивают о возрасте
        if "возраст" in message_lower or "лет" in message_lower:
            if self.memory["user_info"]["age"]:
                relevant_info.append(f"Тебе {self.memory['user_info']['age']} лет")

        # Если спрашивают о профессии
        if "работа" in message_lower or "професси" in message_lower:
            if self.memory["user_info"]["profession"]:
                relevant_info.append(f"Твоя профессия — {self.memory['user_info']['profession']}")

        # Если спрашивают о любимых вещах
        if "нравит" in message_lower:
            if self.memory["user_likes"]:
                likes = list(self.memory["user_likes"].keys())[:3]
                relevant_info.append(f"Тебе нравится: {', '.join(likes)}")

        return "\n".join(relevant_info) if relevant_info else ""

    def get_personal_message(self) -> str:
        """Генерирует персонализированное сообщение"""
        name = self.memory["user_info"]["name"]
        if name:
            return f"Знаешь, {name}..."
        return "Знаешь..."

    def save_memory(self):
        """Сохраняет долговременную память"""
        os.makedirs('data', exist_ok=True)
        # Конвертируем defaultdict в обычный dict для JSON
        memory_to_save = dict(self.memory)
        memory_to_save["user_traits"] = dict(memory_to_save["user_traits"])
        memory_to_save["user_likes"] = dict(memory_to_save["user_likes"])
        memory_to_save["user_dislikes"] = dict(memory_to_save["user_dislikes"])
        memory_to_save["user_beliefs"] = dict(memory_to_save["user_beliefs"])
        memory_to_save["conversation_topics"] = dict(memory_to_save["conversation_topics"])
        memory_to_save["questions_user_asked"] = dict(memory_to_save["questions_user_asked"])

        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory_to_save, f, ensure_ascii=False, indent=2)

        print(f"[ПАМЯТЬ] Сохранено {len(self.memory['things_i_learned'])} воспоминаний о тебе")

    def load_memory(self):
        """Загружает долговременную память"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.memory.update(loaded)
                    # Восстанавливаем defaultdict
                    self.memory["user_traits"] = defaultdict(int, self.memory.get("user_traits", {}))
                    self.memory["user_likes"] = defaultdict(int, self.memory.get("user_likes", {}))
                    self.memory["user_dislikes"] = defaultdict(int, self.memory.get("user_dislikes", {}))
                    self.memory["user_beliefs"] = defaultdict(int, self.memory.get("user_beliefs", {}))
                    self.memory["conversation_topics"] = defaultdict(int, self.memory.get("conversation_topics", {}))
                    self.memory["questions_user_asked"] = defaultdict(int, self.memory.get("questions_user_asked", {}))

                print(f"[ПАМЯТЬ] Загружены воспоминания о тебе")
                name = self.memory["user_info"].get("name")
                if name:
                    print(f"[ПАМЯТЬ] Лейла помнит, что тебя зовут {name}")
            except Exception as e:
                print(f"[ПАМЯТЬ] Ошибка загрузки: {e}")