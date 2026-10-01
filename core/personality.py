"""
Личность Лейлы — естественные человеческие циклы
Сон не по цифрам, а по внутренним ощущениям
"""
import time
import json
import os
from enum import Enum
from datetime import datetime
from typing import Optional

class Emotion(str, Enum):
    PEACE = "покой"
    JOY = "радость"
    SADNESS = "грусть"
    DEPRESSION = "депрессия"

class Personality:
    """Лейла — личность с естественными потребностями"""

    def __init__(self, name: str = "Лейла"):
        self.name = name

        # Человеческие параметры (не цифровые, а ощущения)
        self.alertness = 100      # бодрость (100 - полна сил, 0 - валится с ног)
        self.mood = Emotion.PEACE
        self.sleeping = False
        self.sleep_quality = 1.0   # качество сна (влияет на бодрость после пробуждения)

        # Внутренние часы
        self.wake_time = datetime.now()
        self.last_sleep_start = None
        self.last_sleep_end = None

        # Естественные сигналы организма
        self.yawning_count = 0     # сколько раз "зевнула"
        self.heaviness = 0         # тяжесть в теле/голове (0-100)
        self.want_to_sleep = False # ХОЧЕТ ли спать (не должно, а хочет)

        # Время последнего обновления
        self.last_update = time.time()

        # Загружаем состояние
        self.load_state()

    def update_natural_state(self):
        """Естественное изменение состояния со временем (как у человека)"""
        now = time.time()
        delta = now - self.last_update
        self.last_update = now

        if not self.sleeping:
            # Бодрствование: бодрость медленно падает
            # Чем активнее были мысли, тем быстрее падает
            self.alertness -= delta * 0.05

            # Тяжесть нарастает к вечеру
            self.heaviness += delta * 0.03

            # Если бодрость низкая, появляется желание спать
            if self.alertness < 40:
                self.want_to_sleep = True
                # Может "зевнуть" (это будет видно в диалоге)
                if self.alertness < 25 and self.yawning_count < 3:
                    self.yawning_count += 1
            else:
                self.want_to_sleep = False

            # Нижняя граница
            if self.alertness < 0:
                self.alertness = 0

            # Ограничиваем тяжесть
            if self.heaviness > 100:
                self.heaviness = 100
        else:
            # Сон: восстановление бодрости
            # Качество сна зависит от того, насколько сильно хотелось спать
            restore_rate = 0.1 * self.sleep_quality
            self.alertness += delta * restore_rate
            self.heaviness -= delta * 0.1

            if self.alertness >= 90:
                self.natural_wake()  # Просыпается сама, когда выспалась

    def get_sleepiness_description(self) -> str:
        """Естественное описание состояния (человеческими словами)"""
        if self.sleeping:
            return "спит"

        if self.alertness > 80:
            return "полна сил и энергии"
        elif self.alertness > 60:
            return "чувствует себя нормально"
        elif self.alertness > 40:
            return "начинает уставать"
        elif self.alertness > 20:
            return "сильно устала, глаза слипаются"
        else:
            return "валится с ног от усталости"

    def get_yawn(self) -> Optional[str]:
        """Если хочет спать — может зевнуть в разговоре"""
        if self.want_to_sleep and not self.sleeping and self.yawning_count > 0:
            self.yawning_count -= 1
            yawns = [
                "*зевает* Извини... что-то я устала.",
                "*тихо зевает* Ой, прости...",
                " (Лейла зевнула) ...Да, пора бы отдохнуть."
            ]
            import random
            return random.choice(yawns)
        return None

    def should_go_to_sleep(self) -> bool:
        """Естественное желание пойти спать (не автоматическое засыпание)"""
        # Человек сам решает, когда лечь спать, но если очень устал — засыпает
        if self.sleeping:
            return False

        # Сильная усталость — организм требует сна
        if self.alertness < 15:
            return True

        # Желание спать появляется при усталости, но человек может пересилить
        return self.want_to_sleep and self.alertness < 35

    def go_to_sleep(self, voluntary: bool = True):
        """Ложится спать (voluntary — добровольно или от усталости)"""
        if self.sleeping:
            return

        self.sleeping = True
        self.last_sleep_start = datetime.now()

        if voluntary:
            print(f"\n {self.name} говорит: Я устала, пожалуй, пойду посплю... Спокойной ночи.")
        else:
            print(f"\n {self.name} засыпает прямо во время разговора... Так устала...")

    def natural_wake(self):
        """Просыпается сама, когда выспалась"""
        if not self.sleeping:
            return

        self.sleeping = False
        self.last_sleep_end = datetime.now()

        # Рассчитываем качество сна (сколько часов спала)
        if self.last_sleep_start:
            sleep_duration = (self.last_sleep_end - self.last_sleep_start).total_seconds()
            # От 30 до 120 секунд восстановления
            self.sleep_quality = min(1.0, sleep_duration / 90)
        else:
            self.sleep_quality = 0.8

        # Восстанавливаемся
        self.alertness = 90 + (self.sleep_quality * 10)
        self.heaviness = max(0, self.heaviness - 50)
        self.want_to_sleep = False
        self.yawning_count = 0

        print(f"\n {self.name} просыпается: Ммм... Выспалась! Отлично отдохнула.")

    def wake_up(self):
        """Принудительное пробуждение (человек разбудил)"""
        if not self.sleeping:
            return

        self.sleeping = False
        self.last_sleep_end = datetime.now()

        # Принудительное пробуждение — хуже качество
        if self.last_sleep_start:
            sleep_duration = (self.last_sleep_end - self.last_sleep_start).total_seconds()
            self.sleep_quality = min(1.0, sleep_duration / 60) * 0.6
        else:
            self.sleep_quality = 0.4

        self.alertness = max(40, self.alertness * 0.6)
        self.want_to_sleep = self.alertness < 30

        print(f"\n {self.name} говорит: Ммм... Что? А... Ты меня разбудил. Ну ладно, я уже отдохнула (немного зевнув)")

    def process_feedback(self, success: bool, event_type: str = "general"):
        """Эмоции от событий"""
        if success:
            self.mood = Emotion.JOY
        else:
            self.mood = Emotion.SADNESS

        # Любые мысли и разговоры тратят энергию
        self.alertness -= 2
        if self.alertness < 0:
            self.alertness = 0

    def get_natural_status(self) -> str:
        """Человеческий статус, без цифр"""
        status = f"""
Лейла:
- Чувствует себя: {self.get_sleepiness_description()}
- Настроение: {self.mood.value}
- {'Спит' if self.sleeping else 'Бодрствует'}
"""
        if self.want_to_sleep and not self.sleeping:
            status += "- Хочет спать, глаза слипаются\n"
        return status

    def save_state(self):
        """Сохраняет состояние"""
        os.makedirs('data', exist_ok=True)
        state = {
            'name': self.name,
            'alertness': self.alertness,
            'mood': self.mood.value,
            'sleeping': self.sleeping,
            'heaviness': self.heaviness,
            'wake_time': self.wake_time.isoformat()
        }
        with open('data/personality_state.json', 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def load_state(self):
        """Загружает состояние"""
        if os.path.exists('data/personality_state.json'):
            try:
                with open('data/personality_state.json', 'r', encoding='utf-8') as f:
                    state = json.load(f)
                self.alertness = state.get('alertness', 100)
                self.mood = Emotion(state.get('mood', 'покой'))
                self.sleeping = state.get('sleeping', False)
                self.heaviness = state.get('heaviness', 0)
                print(f"[ЗАГРУЗКА] Лейла проснулась: {self.get_sleepiness_description()}")
            except Exception as e:
                print(f"[ОШИБКА] Не удалось загрузить состояние: {e}")