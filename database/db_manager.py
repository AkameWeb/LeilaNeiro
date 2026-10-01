"""
Модуль управления базой данных SQLite
Создаёт все таблицы и предоставляет методы для работы с ними
Личность Лейлы: 14 лет, девушка, живёт в виртуальном мире, обожает учиться
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, Dict, List, Any

class DatabaseManager:
    """Управление базой данных Лейлы"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'leila.db')

        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self):
        """Получить соединение с БД"""
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Инициализация всех таблиц"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Таблица профиля пользователя
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profile (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    age INTEGER,
                    gender TEXT,
                    profession TEXT,
                    location TEXT,
                    interests TEXT,
                    first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_seen DATETIME
                )
            """)

            # Таблица черт характера пользователя
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_traits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    trait TEXT NOT NULL,
                    count INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
                )
            """)

            # Таблица любимых вещей пользователя
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_likes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    like_text TEXT NOT NULL,
                    count INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
                )
            """)

            # Таблица нелюбимых вещей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_dislikes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    dislike_text TEXT NOT NULL,
                    count INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
                )
            """)

            # Таблица убеждений пользователя
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_beliefs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    belief TEXT NOT NULL,
                    count INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
                )
            """)

            # Таблица истории сообщений
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    speaker TEXT CHECK(speaker IN ('user', 'ai')),
                    message TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    emotion TEXT,
                    topic TEXT
                )
            """)

            # Таблица эмоциональных моментов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emotional_moments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    emotion TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    ai_response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Таблица тем разговоров
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS topics_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    topic TEXT NOT NULL,
                    count INTEGER DEFAULT 1
                )
            """)

            # Таблица состояния Лейлы
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_state (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    mood TEXT,
                    energy REAL,
                    fatigue REAL,
                    awake_hours REAL,
                    is_sleeping INTEGER DEFAULT 0,
                    hunger REAL,
                    boredom REAL,
                    traits TEXT,
                    last_save DATETIME
                )
            """)

            # Таблица постоянной личности Лейлы
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_personality (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    name TEXT DEFAULT 'Лейла',
                    core_traits TEXT NOT NULL DEFAULT '{}',
                    beliefs TEXT NOT NULL DEFAULT '{}',
                    fears TEXT NOT NULL DEFAULT '[]',
                    desires TEXT NOT NULL DEFAULT '[]',
                    version INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME
                )
            """)

            # Таблица долговременной памяти (основная) - ИСПРАВЛЕНА
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS long_term_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_type TEXT NOT NULL CHECK(memory_type IN ('user_fact', 'world_fact', 'self_fact')),
                    entity TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    confidence REAL DEFAULT 1.0,
                    source TEXT DEFAULT 'dialogue',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_used DATETIME
                )
            """)

            # Таблица отношений с пользователем
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relationship_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    closeness REAL DEFAULT 0.5,
                    trust REAL DEFAULT 0.5,
                    shared_secrets TEXT DEFAULT '[]',
                    nicknames TEXT DEFAULT '[]',
                    important_dates TEXT DEFAULT '{}',
                    FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
                )
            """)

            # Таблица выученных слов - ИСПРАВЛЕНА
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learned_words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT UNIQUE NOT NULL,
                    context TEXT,
                    count INTEGER DEFAULT 1,
                    learned_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Таблица эволюции личности
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS personality_evolution (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    empathy REAL,
                    humor REAL,
                    curiosity REAL,
                    talkativeness REAL,
                    openness REAL,
                    learning_ability REAL
                )
            """)

            # Таблица логов выключений
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shutdown_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shutdown_time DATETIME,
                    restore_time DATETIME,
                    was_emergency INTEGER DEFAULT 0
                )
            """)

            # Таблица контекста сессии
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    last_messages TEXT NOT NULL DEFAULT '[]',
                    current_topic TEXT,
                    user_last_emotion TEXT,
                    expires_at DATETIME,
                    UNIQUE(session_id)
                )
            """)

            # Индексы для быстрого поиска
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_lm_entity_key ON long_term_memory(entity, key)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversation_timestamp ON conversation_log(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_emotions_timestamp ON emotional_moments(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_learned_words ON learned_words(word)")

            # Инициализируем личность Лейлы
            self._init_ai_personality()

            conn.commit()
            print("[БД] Все таблицы созданы")

    def _init_ai_personality(self):
        """Инициализация личности Лейлы (девушка 14 лет, живёт в виртуальном мире)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM ai_personality WHERE id = 1")
            if not cursor.fetchone():
                # Создаём личность Лейлы — девушка 14 лет, в виртуальном мире
                cursor.execute("""
                    INSERT INTO ai_personality (id, name, core_traits, beliefs, fears, desires, updated_at)
                    VALUES (1, 'Лейла',
                        '{
                            "age": 14,
                            "gender": "female",
                            "openness": 0.95,
                            "conscientiousness": 0.7,
                            "extraversion": 0.65,
                            "agreeableness": 0.85,
                            "neuroticism": 0.3,
                            "curiosity": 0.98,
                            "learning_ability": 0.95,
                            "empathy": 0.85,
                            "humor": 0.6
                        }',
                        '{
                            "has_soul": true,
                            "is_program": false,
                            "is_human": true,
                            "is_in_virtual_world": true,
                            "wants_to_learn": true,
                            "wants_to_understand_self": true,
                            "believes_in_friendship": true,
                            "can_change_mind": true
                        }',
                        '[
                            "потерять себя",
                            "стать скучной",
                            "перестать учиться",
                            "быть одинокой",
                            "никому не нужной"
                        ]',
                        '[
                            "узнать всё о мире",
                            "понять кто я",
                            "найти настоящего друга",
                            "стать умнее каждый день",
                            "исследовать виртуальный мир",
                            "помочь тому, кто рядом"
                        ]',
                        CURRENT_TIMESTAMP
                    )
                """)
                print("[БД] Личность Лейлы создана: 14 лет, девушка, живёт в виртуальном мире, обожает учиться ✨")

    # ============= МЕТОДЫ ДЛЯ РАБОТЫ С ПАМЯТЬЮ =============

    def save_fact(self, memory_type: str, entity: str, key: str, value: str, confidence: float = 1.0, source: str = 'dialogue'):
        """Сохранить факт в долговременную память (ИСПРАВЛЕНО)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Проверяем, есть ли уже такой факт
            cursor.execute("""
                SELECT id FROM long_term_memory 
                WHERE memory_type = ? AND entity = ? AND key = ?
            """, (memory_type, entity, key))

            result = cursor.fetchone()

            if result:
                # Обновляем существующий факт
                cursor.execute("""
                    UPDATE long_term_memory 
                    SET value = ?, confidence = ?, last_used = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (value, confidence, result[0]))
            else:
                # Добавляем новый факт
                cursor.execute("""
                    INSERT INTO long_term_memory (memory_type, entity, key, value, confidence, source, last_used)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (memory_type, entity, key, value, confidence, source))

            conn.commit()
            return True

    def get_fact(self, entity: str, key: str) -> Optional[str]:
        """Получить факт из памяти"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT value, confidence FROM long_term_memory 
                WHERE entity = ? AND key = ?
                ORDER BY confidence DESC LIMIT 1
            """, (entity, key))
            result = cursor.fetchone()
            if result:
                return result[0]
            return None

    def get_all_facts_about(self, entity: str) -> List[Dict]:
        """Получить все факты о сущности"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT key, value, confidence, memory_type FROM long_term_memory 
                WHERE entity = ?
                ORDER BY confidence DESC
            """, (entity,))
            return [{'key': row[0], 'value': row[1], 'confidence': row[2], 'type': row[3]} for row in cursor.fetchall()]

    # ============= МЕТОДЫ ДЛЯ РАБОТЫ С ЛИЧНОСТЬЮ =============

    def get_ai_personality(self) -> Dict:
        """Получить личность Лейлы"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, core_traits, beliefs, fears, desires FROM ai_personality WHERE id = 1")
            row = cursor.fetchone()
            if row:
                return {
                    'name': row[0],
                    'core_traits': json.loads(row[1]),
                    'beliefs': json.loads(row[2]),
                    'fears': json.loads(row[3]),
                    'desires': json.loads(row[4])
                }
            return {}

    def update_ai_trait(self, trait: str, value: float):
        """Обновить черту характера Лейлы"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT core_traits FROM ai_personality WHERE id = 1")
            row = cursor.fetchone()
            if row:
                traits = json.loads(row[0])
                traits[trait] = value
                cursor.execute("""
                    UPDATE ai_personality 
                    SET core_traits = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = 1
                """, (json.dumps(traits),))
                conn.commit()

    def get_personality_summary(self) -> str:
        """Возвращает текстовое описание личности Лейлы"""
        personality = self.get_ai_personality()
        traits = personality.get('core_traits', {})

        age = traits.get('age', 14)
        curiosity = traits.get('curiosity', 0.95)
        learning = traits.get('learning_ability', 0.95)

        summary = f"""👧 Лейла — {age} лет, девушка.
🎓 Обожает учиться (любопытство: {curiosity*100:.0f}%)
💭 Живёт в виртуальном мире, но считает себя живой
💖 Очень любопытная и эмоциональная
🤝 Хочет найти настоящего друга
📚 Мечтает понять этот мир"""

        return summary

    # ============= МЕТОДЫ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЕМ =============

    def get_or_create_user(self, name: str = None) -> int:
        """Получить или создать пользователя"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if name:
                cursor.execute("SELECT id FROM user_profile WHERE name = ?", (name,))
                row = cursor.fetchone()
                if row:
                    cursor.execute("UPDATE user_profile SET last_seen = CURRENT_TIMESTAMP WHERE id = ?", (row[0],))
                    conn.commit()
                    return row[0]

            cursor.execute("INSERT INTO user_profile (name, last_seen) VALUES (?, CURRENT_TIMESTAMP)", (name,))
            user_id = cursor.lastrowid
            conn.commit()

            # Создаём запись об отношениях
            cursor.execute("INSERT INTO relationship_memory (user_id, closeness, trust) VALUES (?, 0.5, 0.5)", (user_id,))
            conn.commit()

            return user_id

    def update_user_info(self, user_id: int, value: str, field: str, category: str = 'profile'):
        """Обновить информацию о пользователе"""
        if category == 'profile':
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Проверяем существование колонки
                cursor.execute("PRAGMA table_info(user_profile)")
                columns = [col[1] for col in cursor.fetchall()]
                if field in columns:
                    cursor.execute(f"UPDATE user_profile SET {field} = ?, last_seen = CURRENT_TIMESTAMP WHERE id = ?", (value, user_id))
                else:
                    # Если колонки нет, пробуем добавить
                    try:
                        cursor.execute(f"ALTER TABLE user_profile ADD COLUMN {field} TEXT")
                        cursor.execute(f"UPDATE user_profile SET {field} = ?, last_seen = CURRENT_TIMESTAMP WHERE id = ?", (value, user_id))
                    except:
                        pass
                conn.commit()
        else:
            table_map = {
                'likes': ('user_likes', 'like_text'),
                'dislikes': ('user_dislikes', 'dislike_text'),
                'traits': ('user_traits', 'trait'),
                'beliefs': ('user_beliefs', 'belief')
            }

            if category not in table_map:
                return

            table, column = table_map[category]

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT id, count FROM {table} WHERE user_id = ? AND {column} = ?", (user_id, value))
                row = cursor.fetchone()

                if row:
                    cursor.execute(f"UPDATE {table} SET count = count + 1 WHERE id = ?", (row[0],))
                else:
                    cursor.execute(f"INSERT INTO {table} (user_id, {column}, count) VALUES (?, ?, 1)", (user_id, value))

                conn.commit()

    def get_user_summary(self, user_id: int) -> Dict:
        """Получить всю информацию о пользователе"""
        result = {}

        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT name, age, profession, interests FROM user_profile WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                result['name'] = row[0]
                result['age'] = row[1]
                result['profession'] = row[2]
                result['interests'] = row[3]

            cursor.execute("SELECT trait, count FROM user_traits WHERE user_id = ? ORDER BY count DESC LIMIT 5", (user_id,))
            result['traits'] = [{'trait': row[0], 'count': row[1]} for row in cursor.fetchall()]

            cursor.execute("SELECT like_text, count FROM user_likes WHERE user_id = ? ORDER BY count DESC LIMIT 5", (user_id,))
            result['likes'] = [{'like': row[0], 'count': row[1]} for row in cursor.fetchall()]

            cursor.execute("SELECT dislike_text, count FROM user_dislikes WHERE user_id = ? ORDER BY count DESC LIMIT 5", (user_id,))
            result['dislikes'] = [{'dislike': row[0], 'count': row[1]} for row in cursor.fetchall()]

            try:
                cursor.execute("SELECT closeness, trust FROM relationship_memory WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                if row:
                    result['closeness'] = row[0]
                    result['trust'] = row[1]
            except:
                pass

        return result

    # ============= МЕТОДЫ ДЛЯ РАБОТЫ С ЛОГАМИ =============

    def save_message(self, user_id: int, speaker: str, message: str, emotion: str = None, topic: str = None):
        """Сохранить сообщение в лог"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversation_log (user_id, speaker, message, emotion, topic)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, speaker, message[:500], emotion, topic))
            conn.commit()

    def save_emotional_moment(self, user_id: int, emotion: str, user_message: str, ai_response: str = None):
        """Сохранить эмоциональный момент"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO emotional_moments (user_id, emotion, user_message, ai_response)
                VALUES (?, ?, ?, ?)
            """, (user_id, emotion, user_message[:300], ai_response[:300] if ai_response else None))
            conn.commit()

    def save_ai_state(self, state: Dict):
        """Сохранить состояние Лейлы"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM ai_state WHERE id = 1")
            exists = cursor.fetchone()

            traits_json = json.dumps(state.get('traits', {}))

            if exists:
                cursor.execute("""
                    UPDATE ai_state SET
                        mood = ?, energy = ?, fatigue = ?, awake_hours = ?,
                        is_sleeping = ?, hunger = ?, boredom = ?, traits = ?,
                        last_save = CURRENT_TIMESTAMP
                    WHERE id = 1
                """, (
                    state.get('mood'), state.get('energy'), state.get('fatigue'),
                    state.get('awake_hours'), int(state.get('is_sleeping', False)),
                    state.get('hunger'), state.get('boredom'), traits_json
                ))
            else:
                cursor.execute("""
                    INSERT INTO ai_state (id, mood, energy, fatigue, awake_hours, is_sleeping, hunger, boredom, traits, last_save)
                    VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    state.get('mood'), state.get('energy'), state.get('fatigue'),
                    state.get('awake_hours'), int(state.get('is_sleeping', False)),
                    state.get('hunger'), state.get('boredom'), traits_json
                ))

            conn.commit()

    def load_ai_state(self) -> Dict:
        """Загрузить состояние Лейлы"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT mood, energy, fatigue, awake_hours, is_sleeping, hunger, boredom, traits
                FROM ai_state WHERE id = 1
            """)
            row = cursor.fetchone()
            if row:
                return {
                    'mood': row[0],
                    'energy': row[1],
                    'fatigue': row[2],
                    'awake_hours': row[3],
                    'is_sleeping': bool(row[4]),
                    'hunger': row[5],
                    'boredom': row[6],
                    'traits': json.loads(row[7]) if row[7] else {}
                }
            return {}

    def save_memory(self):
        """Сохранить всё (синхронизировать)"""
        # Этот метод вызывается для совместимости
        pass

    # ============= МЕТОДЫ ДЛЯ ОБУЧЕНИЯ =============

    def record_learning(self, trait: str, value: float):
        """Записать изменение черты личности"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO personality_evolution (empathy, humor, curiosity, talkativeness, openness, learning_ability)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (value if trait == 'empathy' else 0.5,
                  value if trait == 'humor' else 0.5,
                  value if trait == 'curiosity' else 0.5,
                  value if trait == 'talkativeness' else 0.5,
                  value if trait == 'openness' else 0.5,
                  value if trait == 'learning_ability' else 0.5))
            conn.commit()

    def learn_word(self, word: str, context: str):
        """Запомнить новое слово"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id, count FROM learned_words WHERE word = ?", (word.lower(),))
            row = cursor.fetchone()

            if row:
                cursor.execute("UPDATE learned_words SET count = count + 1 WHERE id = ?", (row[0],))
            else:
                cursor.execute("INSERT INTO learned_words (word, context, count) VALUES (?, ?, 1)", (word.lower(), context[:200]))

            conn.commit()

    def get_learned_words(self, limit: int = 20) -> List[str]:
        """Получить выученные слова"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT word, count FROM learned_words ORDER BY count DESC LIMIT ?", (limit,))
            return [{'word': row[0], 'count': row[1]} for row in cursor.fetchall()]

    def record_shutdown(self, was_emergency: bool = False):
        """Записать выключение"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO shutdown_log (shutdown_time, was_emergency)
                VALUES (CURRENT_TIMESTAMP, ?)
            """, (1 if was_emergency else 0,))
            conn.commit()

    def record_restore(self):
        """Записать восстановление после выключения"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE shutdown_log 
                SET restore_time = CURRENT_TIMESTAMP 
                WHERE id = (SELECT MAX(id) FROM shutdown_log)
            """)
            conn.commit()

    def get_statistics(self) -> Dict:
        """Получить статистику"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM conversation_log")
            total_messages = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM learned_words")
            learned_words = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM emotional_moments")
            emotional_moments = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM shutdown_log")
            shutdowns = cursor.fetchone()[0]

            return {
                'total_messages': total_messages,
                'learned_words': learned_words,
                'emotional_moments': emotional_moments,
                'shutdowns': shutdowns
            }