# brain_visualizer.py

import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from collections import deque


class BrainVisualizer(QWidget):
    """Виджет визуализации мозга — встраивается в главное окно."""

    def __init__(self, fly_brain, grid_size=(128, 128), parent=None):
        super().__init__(parent)
        self.fly_brain = fly_brain
        self.grid_size = grid_size
        self.num_neurons = fly_brain.num_neurons

        self.stimulus_log = deque(maxlen=8)
        self.group_activity = {"danger": 0.0, "interest": 0.0, "calm": 0.0, "joy": 0.0}
        self.last_stimulus_text = "—"

        self.setStyleSheet("background-color: #1a1a1a;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Статус
        self.status_label = QLabel(" Активность мозга")
        self.status_label.setStyleSheet("color: #88ff88; font-size: 12px; padding: 3px;")
        layout.addWidget(self.status_label)

        # Фигура matplotlib
        self.fig = Figure(figsize=(6, 5), facecolor='#1a1a1a')
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        # Левая панель — heatmap
        self.ax_brain = self.fig.add_subplot(1, 2, 1)
        self.ax_brain.set_facecolor('#1a1a1a')
        self.ax_brain.set_title('Карта нейронов', color='white', fontsize=10)
        self.brain_matrix = np.zeros(grid_size)
        self.im = self.ax_brain.imshow(
            self.brain_matrix, cmap='hot', vmin=0, vmax=1, interpolation='nearest'
        )
        self.ax_brain.set_xticks([])
        self.ax_brain.set_yticks([])

        # Правая панель — бар-чарт групп
        self.ax_groups = self.fig.add_subplot(1, 2, 2)
        self.ax_groups.set_facecolor('#1a1a1a')
        self.ax_groups.set_title('Группы', color='white', fontsize=10)

        group_names = list(self.group_activity.keys())
        self.ax_groups.set_xticks(range(len(group_names)))
        self.ax_groups.set_xticklabels(group_names, color='white', fontsize=8)

        colors = ['#ff4444', '#44aaff', '#44ff88', '#ffcc44']
        self.bars = self.ax_groups.bar(
            range(len(group_names)),
            list(self.group_activity.values()),
            color=colors
        )
        self.ax_groups.set_ylim(0, 1.0)
        self.ax_groups.tick_params(colors='white', labelsize=8)

        self.fig.subplots_adjust(bottom=0.18, left=0.08, right=0.98, top=0.92, wspace=0.3)

        # Лог стимулов внизу
        self.log_text = self.fig.text(
            0.02, 0.02, '', color='#88ff88', fontsize=8,
            family='monospace', va='bottom'
        )

        self.canvas.draw()

        # Таймер обновления
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_view)
        self.timer.start(200)

    def update_view(self):
        try:
            mem = self.fly_brain.mem
            mem_np = mem.numpy() if hasattr(mem, 'numpy') else np.array(mem, dtype=float)

            total = self.grid_size[0] * self.grid_size[1]
            if len(mem_np) >= total:
                matrix = mem_np[:total].reshape(self.grid_size)
            else:
                padded = np.zeros(total)
                padded[:len(mem_np)] = mem_np
                matrix = padded.reshape(self.grid_size)

            self.im.set_array(matrix)

            for group, ids in self.fly_brain.stimulus_map.items():
                if group in self.group_activity and ids:
                    valid = [i for i in ids if i < len(mem_np)]
                    if valid:
                        self.group_activity[group] = float(np.mean([mem_np[i] for i in valid]))

            for bar, val in zip(self.bars, self.group_activity.values()):
                bar.set_height(val)

            if self.stimulus_log:
                log_lines = " | ".join(list(self.stimulus_log))
                self.log_text.set_text(f"Стимулы: {log_lines}")

            active = int(np.sum(mem_np > 0.3))
            mean_v = float(np.mean(mem_np))
            self.status_label.setText(
                f" Активных: {active} | Возбуждение: {mean_v:.2f} | Стимул: {self.last_stimulus_text}"
            )

            self.canvas.draw_idle()
        except Exception:
            pass

    def log_stimulus(self, stimulus_type: str, intensity: float = 1.0):
        self.stimulus_log.append(f"{stimulus_type}({intensity:.1f})")
        self.last_stimulus_text = stimulus_type


def start_visualizer_thread(fly_brain):
    """Возвращает виджет визуализатора (не поток)."""
    return BrainVisualizer(fly_brain)