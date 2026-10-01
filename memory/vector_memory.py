"""
Модуль памяти ИИ
Использует векторную базу данных для хранения и поиска воспоминаний
"""
import time
import uuid
from typing import List, Dict, Optional
from datetime import datetime
import chromadb
from chromadb.utils import embedding_functions


class VectorMemory:
    """
    Векторная память на основе ChromaDB
    Позволяет хранить и искать воспоминания по смыслу
    """

    def __init__(self, persist_directory: str = "./data/chroma_db"):
        # Инициализация клиента ChromaDB с постоянным хранением
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Создаём embedding функцию на основе русскоязычной модели
        # Если не работает, используем стандартную
        try:
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="intfloat/multilingual-e5-small"
            )
        except:
            print("[ПАМЯТЬ] Использую стандартную embedding функцию")
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction()

        # Создаём коллекции для разных типов памяти
        self.episodic_memory = self.client.get_or_create_collection(
            name="episodic",  # эпизодическая память (события, диалоги)
            embedding_function=self.embedding_fn
        )

        self.semantic_memory = self.client.get_or_create_collection(
            name="semantic",  # семантическая память (факты, знания)
            embedding_function=self.embedding_fn
        )

    def remember_event(self, content: str, metadata: Optional[Dict] = None) -> str:
        """
        Запоминает событие/диалог (эпизодическая память)

        Args:
            content: текст воспоминания
            metadata: дополнительные данные (эмоция, время и т.д.)

        Returns:
            id сохранённого воспоминания
        """
        event_id = str(uuid.uuid4())

        if metadata is None:
            metadata = {}

        metadata['timestamp'] = datetime.now().isoformat()
        metadata['type'] = 'event'

        self.episodic_memory.add(
            documents=[content],
            metadatas=[metadata],
            ids=[event_id]
        )

        return event_id

    def remember_fact(self, fact: str, metadata: Optional[Dict] = None) -> str:
        """
        Запоминает факт (семантическая память)

        Args:
            fact: факт для запоминания
            metadata: дополнительные данные
        """
        fact_id = str(uuid.uuid4())

        if metadata is None:
            metadata = {}

        metadata['timestamp'] = datetime.now().isoformat()
        metadata['type'] = 'fact'

        self.semantic_memory.add(
            documents=[fact],
            metadatas=[metadata],
            ids=[fact_id]
        )

        return fact_id

    def recall_similar(self, query: str, n_results: int = 5, memory_type: str = "both") -> List[Dict]:
        """
        Поиск похожих воспоминаний по смыслу

        Args:
            query: поисковый запрос
            n_results: количество результатов
            memory_type: "episodic", "semantic" или "both"

        Returns:
            список воспоминаний с метаданными
        """
        results = []

        if memory_type in ["episodic", "both"]:
            try:
                episodic_results = self.episodic_memory.query(
                    query_texts=[query],
                    n_results=n_results
                )
                if episodic_results['documents'][0]:
                    for i in range(len(episodic_results['documents'][0])):
                        results.append({
                            'content': episodic_results['documents'][0][i],
                            'metadata': episodic_results['metadatas'][0][i],
                            'type': 'episodic',
                            'distance': episodic_results['distances'][0][i] if 'distances' in episodic_results else None
                        })
            except Exception as e:
                print(f"[ПАМЯТЬ] Ошибка поиска в эпизодической памяти: {e}")

        if memory_type in ["semantic", "both"]:
            try:
                semantic_results = self.semantic_memory.query(
                    query_texts=[query],
                    n_results=n_results
                )
                if semantic_results['documents'][0]:
                    for i in range(len(semantic_results['documents'][0])):
                        results.append({
                            'content': semantic_results['documents'][0][i],
                            'metadata': semantic_results['metadatas'][0][i],
                            'type': 'semantic',
                            'distance': semantic_results['distances'][0][i] if 'distances' in semantic_results else None
                        })
            except Exception as e:
                print(f"[ПАМЯТЬ] Ошибка поиска в семантической памяти: {e}")

        # Сортируем по расстоянию (чем меньше - тем похожее)
        results.sort(key=lambda x: x.get('distance', 1.0))

        return results[:n_results]

    def get_recent_events(self, limit: int = 10) -> List[Dict]:
        """
        Получает последние события (по метаданным)
        Это временное решение - в ChromaDB нет прямой сортировки по timestamp
        """
        try:
            # Получаем все эпизоды (это неэффективно для больших БД, но для прототипа ок)
            all_events = self.episodic_memory.get()
            if not all_events['documents']:
                return []

            # Создаём список с сортировкой
            events = []
            for i in range(len(all_events['documents'])):
                events.append({
                    'content': all_events['documents'][i],
                    'metadata': all_events['metadatas'][i]
                })

            # Сортируем по timestamp
            events.sort(key=lambda x: x['metadata'].get('timestamp', ''), reverse=True)
            return events[:limit]
        except Exception as e:
            print(f"[ПАМЯТЬ] Ошибка получения последних событий: {e}")
            return []

    def clear_all(self):
        """Очищает всю память (осторожно!)"""
        self.client.delete_collection("episodic")
        self.client.delete_collection("semantic")
        self.episodic_memory = self.client.create_collection("episodic", embedding_function=self.embedding_fn)
        self.semantic_memory = self.client.create_collection("semantic", embedding_function=self.embedding_fn)
        print("[ПАМЯТЬ] Вся память очищена")