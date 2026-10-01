# fly_brain_interface.py

import os
import csv
import random
import numpy as np
import torch
import snntorch as snn

# Эмбеддер для текста
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDER_AVAILABLE = True
except ImportError:
    EMBEDDER_AVAILABLE = False
    print("[EMBEDDER] sentence-transformers не установлен. Работаю на ключевых словах.")


class FlyBrainInterface:
    def __init__(self, num_neurons=16384, connectome_path="data/male-cns.csv"):
        self.num_neurons = num_neurons
        self.connectome_path = connectome_path

        print("[FLY BRAIN] Инициализация...")

        # === ЭМБЕДДЕР ТЕКСТА ===
        self.embedder = None
        if EMBEDDER_AVAILABLE:
            try:
                print("[EMBEDDER] Загрузка модели (может занять время)...")
                self.embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                print("[EMBEDDER] ✅ Модель загружена")
            except Exception as e:
                print(f"[EMBEDDER] ❌ Ошибка: {e}")
                self.embedder = None

        # === КОННЕКТОМ (связи) ===
        self.connections = self._load_connectome()

        # === СПАЙКОВЫЕ НЕЙРОНЫ ===
        self.lif = snn.Leaky(beta=0.9)
        self.mem = torch.rand(num_neurons) * 0.1  # начальное лёгкое возбуждение

        # === СЛУЧАЙНОЕ РАСПРЕДЕЛЕНИЕ ГРУПП ===
        self.stimulus_map = self._build_random_stimulus_map()

        # === ЭТАЛОННЫЕ ЭМОЦИИ ===
        self.emotion_references = self._build_emotion_references()

        print(f"[FLY BRAIN] ✅ Готов. Нейронов: {num_neurons}, связей: {len(self.connections)}")

    def _load_connectome(self):
        """Загружает связи из CSV (если есть)."""
        if not os.path.exists(self.connectome_path):
            return []
        connections = []
        try:
            with open(self.connectome_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        pre = int(row.get('pre_id', row.get('pre', 0)))
                        post = int(row.get('post_id', row.get('post', 0)))
                        weight = float(row.get('weight', 1.0))
                        if pre < self.num_neurons and post < self.num_neurons:
                            connections.append((pre, post, weight))
                    except (ValueError, KeyError):
                        continue
        except Exception as e:
            print(f"[FLY BRAIN] Ошибка CSV: {e}")
        return connections

    def _build_random_stimulus_map(self):
        """Случайное распределение нейронов по группам."""
        all_ids = list(range(self.num_neurons))
        random.shuffle(all_ids)
        n = self.num_neurons // 4
        return {
            "danger":   all_ids[:n],
            "joy":      all_ids[n:2 * n],
            "interest": all_ids[2 * n:3 * n],
            "calm":     all_ids[3 * n:]
        }

    def _build_emotion_references(self):
        """Эталонные фразы для каждой эмоции — для сравнения паттернов."""
        return {
            "danger": [
                "мне страшно", "я боюсь", "это опасно", "мне угрожают",
                "тревожно на душе", "жутко", "паника"
            ],
            "joy": [
                "я счастлив", "ура", "мне весело", "отличные новости",
                "прекрасный день", "радость", "класс"
            ],
            "interest": [
                "интересно", "расскажи подробнее", "хочу узнать",
                "любопытно", "как это работает", "почему"
            ],
            "calm": [
                "спокойно", "тихо", "умиротворение", "мирно",
                "хорошо", "уютно", "расслабленно"
            ]
        }

    # =========================================================
    #  КОДИРОВАНИЕ ТЕКСТА В СПАЙКИ
    # =========================================================
    def text_to_spikes(self, text: str) -> torch.Tensor:
        """
        Преобразует текст в вектор спайков (num_neurons).
        Использует эмбеддинг → rate encoding.
        """
        if self.embedder is None:
            # Fallback: случайные спайки
            return torch.rand(self.num_neurons) * 0.5

        try:
            # Эмбеддинг текста (вектор ~384 чисел)
            embedding = self.embedder.encode(text, convert_to_numpy=True)

            # Rate encoding: значения эмбеддинга → возбуждение нейронов
            spikes = np.zeros(self.num_neurons)
            for i, val in enumerate(embedding):
                idx = i % self.num_neurons
                spikes[idx] += abs(float(val))

            # Нормализация
            max_val = np.max(spikes)
            if max_val > 0:
                spikes = spikes / max_val

            # Усиливаем контраст (что активнее — то активнее)
            spikes = np.power(spikes, 0.5)

            return torch.tensor(spikes, dtype=torch.float32)
        except Exception as e:
            print(f"[EMBEDDER] Ошибка кодирования: {e}")
            return torch.rand(self.num_neurons) * 0.5

    def process_text(self, text: str, intensity: float = 1.0):
        """Обрабатывает текст через нейроны (главный метод)."""
        # 1. Текст → спайки
        spikes = self.text_to_spikes(text) * intensity

        # 2. Подаём в LIF-сеть
        spk_out, self.mem = self.lif(spikes, self.mem)

        # 3. Распространяем по связям (если есть)
        self._propagate_spikes(spk_out)

        # 4. Шум для "жизни"
        self.mem = torch.clamp(self.mem + torch.rand(self.num_neurons) * 0.02, 0, 1)

        active = int(torch.sum(self.mem > 0.3).item())
        print(f"[FLY BRAIN] Текст обработан. Активных нейронов: {active}")
        return active

    # Обратная совместимость
    def process_stimulus(self, stimulus_type: str, intensity: float = 1.0):
        """Старый метод — стимул по названию группы."""
        if stimulus_type not in self.stimulus_map:
            return 0
        input_spikes = torch.zeros(self.num_neurons)
        for nid in self.stimulus_map[stimulus_type]:
            if nid < self.num_neurons:
                input_spikes[nid] = intensity
        spk_out, self.mem = self.lif(input_spikes, self.mem)
        self._propagate_spikes(spk_out)
        self.mem = torch.clamp(self.mem + torch.rand(self.num_neurons) * 0.02, 0, 1)
        return int(torch.sum(spk_out).item())

    def _propagate_spikes(self, spk_out):
        """Распространяет спайки по связям."""
        active = torch.nonzero(spk_out).flatten().tolist()

        if not self.connections:
            # Без коннектома — случайное возбуждение
            for _ in range(30):
                idx = random.randint(0, self.num_neurons - 1)
                self.mem[idx] = min(1.0, float(self.mem[idx]) + 0.1)
            return

        for pre in active[:100]:
            for (p, post, w) in self.connections:
                if p == pre and post < self.num_neurons:
                    self.mem[post] = min(1.0, float(self.mem[post]) + 0.1 * w)

    def step(self):
        """Один шаг симуляции без стимула."""
        input_spikes = torch.zeros(self.num_neurons)
        spk_out, self.mem = self.lif(input_spikes, self.mem)
        self.mem = torch.clamp(self.mem + torch.rand(self.num_neurons) * 0.015, 0, 1)
        return int(torch.sum(spk_out).item())

    # =========================================================
    #  АНАЛИЗ ПАТТЕРНОВ
    # =========================================================
    def get_group_scores(self) -> dict:
        """Возвращает активность каждой группы нейронов (по паттерну)."""
        mem = self.mem
        mem_np = mem.numpy() if hasattr(mem, 'numpy') else np.array(mem, dtype=float)

        scores = {}
        for group, ids in self.stimulus_map.items():
            valid = [i for i in ids if i < len(mem_np)]
            if valid:
                # Среднее + максимум (паттерн важнее среднего)
                mean_val = float(np.mean([mem_np[i] for i in valid]))
                max_val = float(np.max([mem_np[i] for i in valid]))
                scores[group] = 0.5 * mean_val + 0.5 * max_val
            else:
                scores[group] = 0.0
        return scores

    def compare_with_emotion(self, text: str) -> dict:
        """
        Сравнивает текущий паттерн активности с эталонами эмоций.
        Возвращает уверенность по каждой эмоции.
        """
        if self.embedder is None:
            return {emotion: 0.25 for emotion in self.emotion_references}

        # Эмбеддинг текущего текста
        current_emb = self.embedder.encode(text, convert_to_numpy=True)

        similarities = {}
        for emotion, phrases in self.emotion_references.items():
            # Эмбеддинги эталонных фраз
            ref_embs = self.embedder.encode(phrases, convert_to_numpy=True)

            # Косинусное сходство с каждой эталонной фразой
            sims = []
            for ref_emb in ref_embs:
                sim = np.dot(current_emb, ref_emb) / (
                    np.linalg.norm(current_emb) * np.linalg.norm(ref_emb) + 1e-6
                )
                sims.append(sim)

            similarities[emotion] = float(max(sims))  # максимум сходства

        # Нормализация
        total = sum(max(0, s) for s in similarities.values()) + 1e-6
        normalized = {k: max(0, v) / total for k, v in similarities.items()}
        return normalized

    def get_dominant_state(self) -> str:
        """Определяет доминирующее состояние."""
        scores = self.get_group_scores()
        if not scores:
            return "neutral"
        dominant = max(scores, key=scores.get)
        if scores[dominant] < 0.25:
            return "neutral"
        return dominant

    def get_active_neurons(self, threshold=0.3):
        mem = self.mem
        mem_np = mem.numpy() if hasattr(mem, 'numpy') else np.array(mem, dtype=float)
        return [i for i, v in enumerate(mem_np) if float(v) > threshold]

    def print_active_neurons(self, top_n=15):
        active = self.get_active_neurons(threshold=0.3)
        total = len(active)
        if total == 0:
            print("[NEURONS] Активность: покой")
            return
        shown = active[:top_n]
        neurons_str = ", ".join([f"N{i}" for i in shown])
        if total > top_n:
            neurons_str += f" ... (+{total - top_n})"
        bar_len = min(40, total // 8)
        bar = "█" * bar_len + "░" * (40 - bar_len)
        print(f"[NEURONS]  Активных: {total:4d} | {bar} | {neurons_str}")