
import random
from brain.neural_learner import NeuralLearner


class SmartResponder:
    """Лейла думает и говорит сама"""

    def __init__(self, belief_system, emotion_engine):
        self.beliefs = belief_system
        self.emotions = emotion_engine
        self.neural = NeuralLearner(model_name="evilfreelancer/rugpt3:latest")  # или tinyllama:1.1b

        # История разговора для контекста
        self.conversation_history = []

    def generate_response(self, user_input: str, memory_context: list) -> str:
        """Лейла генерирует ответ"""

        # Пробуем через Ollama
        if self.neural.loaded:
            response = self.neural.generate_from_context(
                self.conversation_history,
                user_input
            )

            if response:
                # Сохраняем в историю
                self.conversation_history.append(('user', user_input))
                self.conversation_history.append(('ai', response))

                # Ограничиваем историю
                if len(self.conversation_history) > 10:
                    self.conversation_history = self.conversation_history[-10:]

                # Учимся
                self.neural.learn_from_dialogue(user_input, response)

                return response

        # Запасные ответы (если Ollama не работает)
        return self._fallback_response(user_input)

    def _fallback_response(self, user_input: str) -> str:
        """Запасные ответы"""
        fallbacks = [
            "Я думаю над этим...",
            "Интересная мысль. А что ты сам думаешь?",
            "Ммм... Давай поговорим об этом.",
            "Я слушаю. Продолжай.",
            "Хм... Я запомнила это."
        ]
        return random.choice(fallbacks)

    def get_initiation_message(self) -> str:
        """Лейла сама начинает разговор"""
        if self.neural.loaded:
            response = self.neural.generate_thought(
                "Ты Лейла. Напиши одно предложение, чтобы начать разговор с другом. Это может быть вопрос или интересная мысль:",
                max_length=80
            )
            if response:
                return response

        starters = [
            "О чём ты хочешь поговорить?",
            "У меня есть мысль... Слушай, как думаешь, что такое счастье?",
            "Я сегодня много думала. А ты?",
            "Знаешь, я хочу тебя кое о чём спросить...",
            "Как твои дела? У меня всё как обычно."
        ]
        return random.choice(starters)