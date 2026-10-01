# core/intent_decoder.py

import numpy as np


class IntentDecoder:
    def __init__(self, fly_brain):
        self.fly_brain = fly_brain

    def decode(self, user_input: str) -> dict:

        # === 1. Активность групп нейронов ===
        group_scores = self.fly_brain.get_group_scores()

        # === 2. Семантический анализ текста ===
        emotion_scores = self.fly_brain.compare_with_emotion(user_input)

        # === 3. Комбинируем: 40% нейроны + 60% семантика ===
        combined = {}
        for emotion in ["danger", "joy", "interest", "calm"]:
            neural = group_scores.get(emotion, 0.0)
            semantic = emotion_scores.get(emotion, 0.0)
            combined[emotion] = 0.4 * neural + 0.6 * semantic

        # === 4. Общие метрики ===
        mem = self.fly_brain.mem
        mem_np = mem.numpy() if hasattr(mem, 'numpy') else np.array(mem, dtype=float)
        mean_activity = float(np.mean(mem_np))
        std_activity = float(np.std(mem_np))

        # === 5. Определяем доминирующую эмоцию ===
        dominant = max(combined, key=combined.get)
        dominant_value = combined[dominant]

        # === 6. Формируем намерение ===
        intent = self._decide_intent(dominant, dominant_value, mean_activity, std_activity, user_input)

        intent['groups'] = {k: round(v, 2) for k, v in combined.items()}
        intent['neural_raw'] = {k: round(v, 2) for k, v in group_scores.items()}
        intent['semantic_raw'] = {k: round(v, 2) for k, v in emotion_scores.items()}
        intent['dominant_group'] = dominant
        intent['mean_activity'] = round(mean_activity, 2)
        intent['std_activity'] = round(std_activity, 2)

        return intent

    def _decide_intent(self, dominant, value, mean, std, user_input):
        msg = user_input.lower()

        # Базовая логика по доминирующей эмоции
        if dominant == "danger" and value > 0.25:
            intent_text = "успокоить"
            tone = "тёплый"
            emotion = "забота"
            urgency = min(1.0, value)

        elif dominant == "joy" and value > 0.25:
            intent_text = "порадоваться"
            tone = "энергичный"
            emotion = "радость"
            urgency = min(1.0, value)

        elif dominant == "interest" and value > 0.25:
            intent_text = "проявить любопытство"
            tone = "заинтересованный"
            emotion = "интерес"
            urgency = min(1.0, value)

        elif dominant == "calm" and value > 0.25:
            intent_text = "поддержать спокойный разговор"
            tone = "спокойный"
            emotion = "умиротворение"
            urgency = 0.3

        else:
            intent_text = "ответить по существу"
            tone = "нейтральный"
            emotion = "спокойствие"
            urgency = 0.5

        # Корректировка по возбуждению
        if mean > 0.5:
            tone = "возбуждённый"
            length = "короткий"
        elif mean < 0.15:
            tone = "тихий"
            length = "средний"
        else:
            length = "короткий"

        # Корректировка по хаосу
        if std > 0.3:
            tone = "хаотичный"

        return {
            "intent": intent_text,
            "tone": tone,
            "length": length,
            "emotion": emotion,
            "urgency": round(urgency, 2),
        }