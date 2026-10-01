# brain/human_responder.py
"""
Лейла — 14-летняя девочка.
НЕЙРОНЫ РЕАЛЬНО АНАЛИЗИРУЮТ ТЕКСТ через эмбеддинги.
LLM только облекает намерение в слова.
"""
import os
import json
import random
import time
import requests
import re
from core.human_personality import HumanPersonality, Mood
from database.db_manager import DatabaseManager

# Спайковый слой (с эмбеддингами)
try:
    from fly_brain_interface import FlyBrainInterface
    FLY_BRAIN_AVAILABLE = True
except ImportError:
    FLY_BRAIN_AVAILABLE = False
    print("[FLY BRAIN] Модуль не найден. Работаю без нейронов.")

# Декодер намерений
try:
    from core.intent_decoder import IntentDecoder
    INTENT_AVAILABLE = True
except ImportError:
    INTENT_AVAILABLE = False
    print("[INTENT] Модуль не найден. Использую нейтральное намерение.")

# Визуализатор
try:
    from brain_visualizer import start_visualizer_thread
    VISUALIZER_AVAILABLE = True
except ImportError:
    VISUALIZER_AVAILABLE = False
    print("[VISUALIZER] Модуль не найден. Работаю без графики.")


class HumanResponder:
    def __init__(self, personality: HumanPersonality):
        self.p = personality
        self.db = DatabaseManager()
        self.conversation_history = []
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "llama3.1:8b"
        self.ollama_available = self._check_ollama()

        self.user_mood_history = []
        self.last_user_mood = "нейтральное"
        self.user_id = self.db.get_or_create_user()
        self.ai_personality = self.db.get_ai_personality()
        self.was_shutdown = False
        self.last_reflection_time = time.time()

        # === НЕЙРОННЫЙ СЛОЙ ===
        self.fly_brain = None
        self.intent_decoder = None
        self.visualizer = None

        print(f"[INIT] FLY_BRAIN={FLY_BRAIN_AVAILABLE}, INTENT={INTENT_AVAILABLE}, VISUALIZER={VISUALIZER_AVAILABLE}")

        # 1. Спайковый мозг
        if FLY_BRAIN_AVAILABLE:
            try:
                self.fly_brain = FlyBrainInterface(num_neurons=16384)
                print("[FLY BRAIN] ✅ Спайковый слой активирован (16384 нейрона)")
            except Exception as e:
                print(f"[FLY BRAIN] ❌ {e}")
                self.fly_brain = None

        # 2. Декодер намерений
        if self.fly_brain and INTENT_AVAILABLE:
            try:
                self.intent_decoder = IntentDecoder(self.fly_brain)
                print("[INTENT] ✅ Декодер намерений активирован")
            except Exception as e:
                print(f"[INTENT] ❌ {e}")

        # 3. Визуализатор
        if self.fly_brain and VISUALIZER_AVAILABLE:
            try:
                self.visualizer = start_visualizer_thread(self.fly_brain)
                print("[VISUALIZER] ✅ Виджет мозга создан")
            except Exception as e:
                import traceback
                print(f"[VISUALIZER] ❌ Ошибка: {e}")
                traceback.print_exc()
                self.visualizer = None
        elif not self.fly_brain:
            print("[VISUALIZER] ⏭ Нет fly_brain")
        elif not VISUALIZER_AVAILABLE:
            print("[VISUALIZER] ⏭ Модуль brain_visualizer не найден")

        print(f"[ЛИЧНОСТЬ] Лейла: 14 лет")
        print(f"[ХАРАКТЕР] Эмпатия:{self.p.traits['empathy']:.1f}, Критичность:{self.p.traits['judgmental']:.1f}")

        saved_state = self.db.load_ai_state()
        if saved_state:
            print(f"[ВОССТАНОВЛЕНИЕ] Лейла помнит состояние")

        if self.ollama_available:
            print(f"[НЕЙРОСЕТЬ] LLM: {self.model}")
        else:
            print("[НЕЙРОСЕТЬ] ОШИБКА: Ollama не доступна!")

    def _check_ollama(self) -> bool:
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=3)
            if r.status_code == 200:
                models = r.json().get('models', [])
                return any(self.model.split(':')[0] in m.get('name', '') for m in models)
            return False
        except:
            return False

    def _generate(self, prompt: str, max_length: int = 80) -> str:
        """LLM: только формулировка. Не решает что сказать."""
        if not self.ollama_available:
            return None
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.6,
                    "top_p": 0.85,
                    "num_predict": max_length,
                    "repeat_penalty": 1.2,
                    "stop": ["\n\n", "Пользователь:", "Лейла:", "Намерение:", "Ответ:"]
                }
            }
            resp = requests.post(self.ollama_url, json=payload, timeout=60)
            if resp.status_code == 200:
                text = resp.json().get('response', '').strip()
                text = text.replace('Лейла:', '').replace('лейла:', '').strip()
                text = text.replace('"', '').strip()
                return text if len(text) > 2 else None
            return None
        except Exception as e:
            print(f"[LLM] Ошибка: {e}")
            return None

    def _detect_user_mood(self, message: str) -> str:
        """Быстрая проверка настроения для статистики."""
        msg = message.lower()
        moods = {
            'грусть': ['грустно', 'печально', 'плохо', 'уныло', 'тяжело', 'обидно', 'плачу'],
            'радость': ['радостно', 'счастлив', 'отлично', 'круто', 'супер', 'ура', 'весело'],
            'злость': ['бесит', 'злюсь', 'раздражает', 'ненавижу', 'злой'],
            'страх': ['страшно', 'боюсь', 'пугает', 'тревожно', 'опасно'],
            'усталость': ['устал', 'спать', 'вымотан', 'нет сил']
        }
        for mood, kws in moods.items():
            for kw in kws:
                if kw in msg:
                    return mood
        return "нейтральное"

    def _send_stimulus(self, user_input: str):
        """
        Устаревший метод (для совместимости с визуализатором).
        Теперь текст обрабатывается напрямую в generate_response.
        """
        return None

    def _run_brain_steps(self, steps: int = 10):
        """Прокручиваем нейроны, чтобы активность распространилась."""
        if not self.fly_brain:
            return
        try:
            for _ in range(steps):
                if hasattr(self.fly_brain, 'step'):
                    self.fly_brain.step()
        except Exception as e:
            print(f"[FLY BRAIN] Ошибка шага: {e}")

    def _show_active_neurons(self):
        if not self.fly_brain:
            return
        try:
            self.fly_brain.print_active_neurons(top_n=15)
        except Exception as e:
            print(f"[FLY BRAIN] Ошибка визуализации: {e}")

    def _get_bio_state(self) -> str:
        if not self.fly_brain:
            return "neutral"
        try:
            return self.fly_brain.get_dominant_state()
        except:
            return "neutral"

    def generate_response(self, user_input: str) -> str:
        """ГЛАВНЫЙ МЕТОД: нейроны анализируют текст → LLM формулирует."""
        self.db.save_message(self.user_id, 'user', user_input)
        user_mood = self._detect_user_mood(user_input)

        # Команды
        action_result = self._check_for_actions(user_input)
        if action_result:
            self.db.save_message(self.user_id, 'ai', action_result, self.p.mood.value)
            return action_result

        # === ЭТАП 1: Текст идёт напрямую в нейроны ===
        if self.fly_brain:
            try:
                self.fly_brain.process_text(user_input, intensity=1.0)
                # Логируем в визуализатор
                if self.visualizer:
                    try:
                        # Определяем доминирующую группу для визуализации
                        scores = self.fly_brain.get_group_scores()
                        dom = max(scores, key=scores.get) if scores else "neutral"
                        self.visualizer.log_stimulus(dom, 1.0)
                    except Exception as e:
                        print(f"[VISUALIZER] Ошибка лога: {e}")
            except Exception as e:
                print(f"[FLY BRAIN] Ошибка обработки текста: {e}")

        # === ЭТАП 2: Прогоняем SNN ===
        self._run_brain_steps(steps=10)

        # === ЭТАП 3: Показываем активность ===
        print()
        self._show_active_neurons()

        # === ЭТАП 4: Декодируем НАМЕРЕНИЕ ===
        intent = None
        if self.intent_decoder:
            try:
                intent = self.intent_decoder.decode(user_input)
                print(f"[INTENT] {intent['intent']} | тон: {intent['tone']} | группа: {intent['dominant_group']}")
                print(f"         нейроны: {intent.get('neural_raw', {})}")
                print(f"         семантика: {intent.get('semantic_raw', {})}")
            except Exception as e:
                print(f"[INTENT] Ошибка декодирования: {e}")

        if intent is None:
            intent = {
                "intent": "ответить по существу",
                "tone": "нейтральный",
                "length": "короткий",
                "emotion": "спокойствие",
                "urgency": 0.5,
                "dominant_group": "neutral",
                "mean_activity": 0.0,
                "std_activity": 0.0,
                "groups": {}
            }

        # === ЭТАП 5: Обновляем личность ===
        self.p.process_user_feedback(user_input)
        self.p.analyze_topics(user_input)
        self.p.update()

        # Саморефлексия (редко)
        if time.time() - self.last_reflection_time > 180 and random.random() < 0.15:
            self.last_reflection_time = time.time()
            reflection = self.p.generate_self_reflection()
            self.p.add_internal_thought(reflection)
            print(f"[РЕФЛЕКСИЯ] {reflection}")

        # Неловкость (10% шанс)
        mistake = self.p.maybe_make_mistake()
        if mistake:
            self.db.save_message(self.user_id, 'ai', mistake, self.p.mood.value)
            return mistake

        # === ЭТАП 6: Сохраняем историю ===
        self.conversation_history.append(('user', user_input, time.time()))
        if len(self.conversation_history) > 8:
            self.conversation_history = self.conversation_history[-8:]

        context = self._build_context()
        facts = self.db.get_all_facts_about('user')

        # === ЭТАП 7: LLM облекает НАМЕРЕНИЕ в слова ===
        prompt = self._build_prompt(user_input, context, facts, user_mood, intent)
        response = self._generate(prompt, max_length=80)

        if response:
            habit = self.p.get_random_habit()
            if habit and random.random() < 0.2:
                response = f"{habit} {response}"
            self.db.save_message(self.user_id, 'ai', response, self.p.mood.value)
            return response

        return "*задумчиво* Ммм... не знаю, что сказать."

    def _check_for_actions(self, user_input: str) -> str:
        cmd = user_input.lower().strip()
        if cmd in ['спать', 'ложись спать']:
            self.p.go_to_sleep()
            return "Спокойной ночи."
        if cmd in ['разбуди', 'просыпайся']:
            if self.p.is_sleeping:
                self.p.wake_up()
                return "Доброе утро! Я проснулась."
            return "Я и не сплю."
        if cmd in ['статус', 'как ты', 'состояние']:
            return self._get_status()
        if cmd in ['нейроны', 'нейрон', 'активность', 'мозг']:
            if self.fly_brain:
                self._show_active_neurons()
                return "Смотри, что происходит в мозге "
            return "Нейронный слой не подключён."
        return None

    def _get_status(self) -> str:
        if self.p.is_sleeping:
            return "Я сплю."
        mood = self.p.get_mood_description()
        energy = self.p.get_energy_description()
        status = f"{mood}, {energy}"
        if self.p.fatigue > 70:
            status += " Сильно устала."
        bio_state = self._get_bio_state()
        if bio_state != "neutral":
            bio_ru = {
                "danger": "чувствую угрозу",
                "joy": "радостно",
                "interest": "любопытно",
                "calm": "спокойно",
                "excited": "возбуждена",
                "stressed": "напряжена",
                "inspired": "вдохновлена",
                "attached": "привязана",
                "apathetic": "апатична"
            }
            status += f" Внутренне: {bio_ru.get(bio_state, bio_state)}."
        return status

    def _build_context(self) -> str:
        if not self.conversation_history:
            return ""
        ctx = ""
        for speaker, text, _ in self.conversation_history[-4:]:
            name = "Пользователь" if speaker == 'user' else "Ты"
            ctx += f"{name}: {text}\n"
        return ctx

    def _build_prompt(self, user_input: str, context: str, facts: list, user_mood: str, intent: dict) -> str:
        """LLM получает НАМЕРЕНИЕ и только облекает его в слова."""
        facts_str = ""
        if facts:
            for f in facts[:3]:
                if f['key'] == 'name':
                    facts_str += f"- Пользователя зовут {f['value']}\n"

        prompt = f"""Ты — Лейла. Ты живой собеседник.

КРИТИЧНО: Твоё НАМЕРЕНИЕ уже определено нейронами мозга. Ты НЕ решаешь, что сказать.
Твоя задача — ОБЛЕЧЬ намерение в естественные короткие слова.

НАМЕРЕНИЕ (от нейронов):
- Действие: {intent['intent']}
- Тон: {intent['tone']}
- Эмоция: {intent['emotion']}
- Срочность: {intent['urgency']}
- Длина: {intent['length']}

ПРАВИЛА:
1. Следуй намерению точно. Если намерение "успокоить" — успокой. Если "порадоваться" — порадуйся.
2. Не выдумывай личную жизнь (нет кровати, книг, друзей, парня).
3. Не начинай с "Привет".
4. Строй диалог.
5. Если не знаешь о чём речь — скажи "не знаю".

{facts_str}
{context}
Пользователь: {user_input}

Ответ (только слова, без пояснений):"""
        return prompt

    def get_initiation_message(self) -> str:
        user_info = self.db.get_user_summary(self.user_id)
        name = user_info.get('name')
        if name:
            prompt = f"Ты Лейла, 14 лет. Короткое приветствие (1-3 слова) для {name}."
        else:
            prompt = "Ты Лейла, 14 лет. Короткое приветствие (1-3 слова)."
        gen = self._generate(prompt, max_length=15)
        if gen and len(gen) < 30:
            return gen
        return "Привет."

    def check_if_was_off(self) -> bool:
        return self.was_shutdown

    def record_shutdown(self):
        try:
            self.db.record_shutdown(was_emergency=True)
        except:
            pass
        self.was_shutdown = True

    def save_state(self):
        state = {
            'mood': self.p.mood.value,
            'energy': self.p.energy,
            'fatigue': self.p.fatigue,
            'awake_hours': self.p.awake_hours,
            'is_sleeping': self.p.is_sleeping,
            'traits': self.p.traits
        }
        try:
            self.db.save_ai_state(state)
            self.p.save_state()
            print("[СОХРАНЕНИЕ] Лейла сохранена в БД")
        except:
            pass