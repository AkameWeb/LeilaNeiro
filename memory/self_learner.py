
import re
import json
import os


class SelfLearner:
    """Самообучение Лейлы новым словам"""

    def __init__(self):
        self.vocabulary = self.load_vocabulary()
        self.contexts = {}

    def load_vocabulary(self):
        """Загружает выученные слова"""
        if os.path.exists("data/vocabulary.json"):
            with open("data/vocabulary.json", "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def extract_new_words(self, text: str) -> list:
        """Извлекает новые слова из текста"""
        # Простые русские слова (можно расширять)
        words = re.findall(r'[а-яА-ЯёЁ]{4,}', text)

        new_words = []
        for word in words:
            word_lower = word.lower()
            if word_lower not in self.vocabulary:
                new_words.append(word_lower)

        return new_words

    def learn_word(self, word: str, context: str):
        """Учит новое слово"""
        self.vocabulary[word] = {
            'context': context,
            'usage_count': 1,
            'learned_at': str(datetime.now())
        }
        print(f"📖 Лейла выучила новое слово: {word}")

    def generate_sentence_with(self, word: str) -> str:
        """Генерирует предложение с выученным словом"""
        templates = [
            f"Я недавно узнала слово '{word}'. {self.vocabulary[word]['context']}",
            f"Знаешь, есть такое слово: {word}. {self.vocabulary[word]['context'][:50]}...",
            f"Сегодня я выучила '{word}'. Как думаешь, я правильно его использую?"
        ]
        import random
        return random.choice(templates)

    def save_vocabulary(self):
        """Сохраняет словарный запас"""
        with open("data/vocabulary.json", "w", encoding="utf-8") as f:
            json.dump(self.vocabulary, f, ensure_ascii=False, indent=2)