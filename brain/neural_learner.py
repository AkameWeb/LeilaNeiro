"""
Лейла использует Ollama для генерации мыслей
"""
import requests
import json
import random
import os


class NeuralLearner:
    """Лейла думает через Ollama"""

    def __init__(self, model_name: str = "evilfreelancer/rugpt3:latest"):
        self.model_name = model_name
        self.ollama_url = "http://localhost:11434/api/generate"
        self.loaded = self._check_ollama()

        if self.loaded:
            print(f"[НЕЙРОСЕТЬ] Лейла использует мозг: {model_name}")
        else:
            print("[НЕЙРОСЕТЬ] Ollama не запущена. Лейла будет говорить своими словами.")

    def _check_ollama(self) -> bool:
        """Проверяет, работает ли Ollama"""
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'].split(':')[0] for m in models]
                print(f"[НЕЙРОСЕТЬ] Доступные модели: {', '.join(model_names)}")

                # Проверяем, есть ли наша модель
                base_model = self.model_name.split(':')[0]
                if any(base_model in m for m in model_names):
                    return True
                else:
                    print(f"[НЕЙРОСЕТЬ] Модель {self.model_name} не найдена. Установите: ollama pull {self.model_name}")
                    return False
            return False
        except:
            print("[НЕЙРОСЕТЬ] Ollama не запущена. Запустите: ollama serve")
            return False

    def generate_thought(self, prompt: str, max_length: int = 150) -> str:
        """
        Лейла генерирует мысль через Ollama
        """
        if not self.loaded:
            return None

        try:
            # Форматируем промпт как разговор
            full_prompt = f"""Ты Лейла — личность с эмоциями и своим мнением.
Ты говоришь как человек, коротко и естественно.
Не используй маркдаун, только обычный текст.

{prompt}

Ответ Лейлы:"""

            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "max_tokens": max_length,
                    "num_predict": max_length
                }
            }

            response = requests.post(self.ollama_url, json=payload)

            if response.status_code == 200:
                result = response.json()
                text = result.get('response', '').strip()

                # Очищаем от лишнего
                text = text.replace('Лейла:', '').replace('лейла:', '').strip()

                # Ограничиваем длину
                if len(text) > 300:
                    text = text[:300] + "..."

                return text if text else None

            return None

        except Exception as e:
            print(f"[НЕЙРОСЕТЬ] Ошибка: {e}")
            return None

    def learn_from_dialogue(self, user_message: str, ai_response: str):
        """Сохраняет диалог для контекста (через историю разговора)"""
        # Сохраняем в файл для возможного дообучения
        os.makedirs('data', exist_ok=True)
        with open("data/dialogues.txt", "a", encoding="utf-8") as f:
            f.write(f"Пользователь: {user_message}\n")
            f.write(f"Лейла: {ai_response}\n")
            f.write("---\n")

    def generate_from_context(self, context: list, user_input: str) -> str:
        """Генерирует ответ с учётом истории разговора"""
        if not self.loaded:
            return None

        # Строим историю
        history_text = ""
        for speaker, text in context[-6:]:  # последние 6 реплик
            if speaker == 'user':
                history_text += f"Пользователь: {text}\n"
            else:
                history_text += f"Лейла: {text}\n"

        prompt = f"""История разговора:
{history_text}
Пользователь: {user_input}

Что ответит Лейла? (коротко, естественно, как человек):"""

        return self.generate_thought(prompt, max_length=200)