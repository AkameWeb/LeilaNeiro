# main.py
"""
Лейла — точка входа.
Фикс предзагрузки c10.dll для PyTorch на Python 3.14 (Windows).
GUI с визуализацией мозга + текстовый чат.
"""
import os
import platform
import sys

# =========================================================
#  ФИКС для PyTorch на Python 3.14 / Windows
# =========================================================
if platform.system() == "Windows":
    try:
        import ctypes
        from importlib.util import find_spec

        spec = find_spec("torch")
        if spec and spec.origin:
            torch_dir = os.path.dirname(spec.origin)
            dll_path = os.path.join(torch_dir, "lib", "c10.dll")
            if os.path.exists(dll_path):
                ctypes.CDLL(os.path.normpath(dll_path))
                print("[FIX] c10.dll предзагружен")
    except Exception as e:
        print(f"[FIX] Предзагрузка c10.dll не удалась: {e}")


# =========================================================
#  PyQt5
# =========================================================
try:
    from PyQt5.QtWidgets import QApplication
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("[MAIN] PyQt5 не найден. Работаю в консольном режиме.")

from core.human_personality import HumanPersonality
from brain.human_responder import HumanResponder


# =========================================================
#  КОНСОЛЬНЫЙ РЕЖИМ
# =========================================================
def run_console(responder, personality):
    """Консольный режим (без графики)."""
    print("\n" + "=" * 55)
    print("💬 Текстовый режим. Команды:")
    print("   'статус'   — состояние Лейлы")
    print("   'нейроны'  — активные нейроны в консоль")
    print("   'спать'    — усыпить")
    print("   'разбуди'  — разбудить")
    print("   'пока'     — выход")
    print("=" * 55)
    print(f"\nЛейла: {responder.get_initiation_message()}")

    while True:
        try:
            user_input = input("\nВы: ").strip()
            if not user_input:
                continue

            if user_input.lower() in ['пока', 'выход', 'до свидания', 'exit', 'quit']:
                print("Лейла: Пока...")
                break

            if user_input.lower() in ['статус', 'как ты', 'состояние']:
                print(f"Лейла: {responder._get_status()}")
                continue

            if user_input.lower() in ['нейроны', 'нейрон', 'мозг', 'активность']:
                print("\n[Активность мозга]:")
                responder._show_active_neurons()
                continue

            if user_input.lower() in ['спать', 'ложись спать']:
                responder.p.go_to_sleep()
                print("Лейла: Спокойной ночи.")
                continue

            if user_input.lower() in ['разбуди', 'просыпайся']:
                if responder.p.is_sleeping:
                    responder.p.wake_up()
                    print("Лейла: Доброе утро!")
                else:
                    print("Лейла: Я и не сплю.")
                continue

            response = responder.generate_response(user_input)
            print(f"\nЛейла: {response}")
            responder.save_state()

        except KeyboardInterrupt:
            print("\n\nВыход...")
            break

    responder.save_state()
    personality.save_state()
    print("💾 Сохранено. До встречи!")


# =========================================================
#  GUI-РЕЖИМ
# =========================================================
def run_gui(responder, personality, app):
    """GUI-режим с визуализацией мозга. app — уже созданный QApplication."""
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTextEdit, QLineEdit, QPushButton, QLabel
    )
    from PyQt5.QtGui import QFont

    class LeilaWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Лейла")
            self.resize(1200, 700)
            self.setStyleSheet("background-color: #1a1a1a; color: white;")

            central = QWidget()
            self.setCentralWidget(central)
            main_layout = QHBoxLayout(central)

            # === ЛЕВАЯ ЧАСТЬ: ЧАТ ===
            left_widget = QWidget()
            left_layout = QVBoxLayout(left_widget)



            self.chat_area = QTextEdit()
            self.chat_area.setReadOnly(True)
            self.chat_area.setFont(QFont("Arial", 11))
            self.chat_area.setStyleSheet(
                "background-color: #2b2b2b; color: #e0e0e0; padding: 5px;"
            )
            left_layout.addWidget(self.chat_area)

            input_layout = QHBoxLayout()
            self.input_entry = QLineEdit()
            self.input_entry.setFont(QFont("Arial", 11))
            self.input_entry.setStyleSheet(
                "background-color: #3c3c3c; color: white; padding: 5px;"
            )
            self.input_entry.returnPressed.connect(self.send_message)
            input_layout.addWidget(self.input_entry)

            send_btn = QPushButton("Отправить")
            send_btn.setStyleSheet(
                "background-color: #4a4a4a; color: white; padding: 5px 10px;"
            )
            send_btn.clicked.connect(self.send_message)
            input_layout.addWidget(send_btn)

            left_layout.addLayout(input_layout)
            main_layout.addWidget(left_widget, 1)

            # === ПРАВАЯ ЧАСТЬ: МОЗГ ===
            right_widget = QWidget()
            right_layout = QVBoxLayout(right_widget)

            brain_label = QLabel(" Мозг Лейлы")
            brain_label.setStyleSheet("font-size: 14px; padding: 5px; color: #88ff88;")
            right_layout.addWidget(brain_label)

            if responder.visualizer:
                right_layout.addWidget(responder.visualizer)
            else:
                no_viz = QLabel("Визуализатор не подключён")
                no_viz.setStyleSheet("color: #888;")
                right_layout.addWidget(no_viz)

            main_layout.addWidget(right_widget, 1)

            # Приветствие
            self.display("Лейла", responder.get_initiation_message())

        def display(self, speaker, text):
            if speaker == "Лейла":
                self.chat_area.append(f" Лейла: {text}")
            else:
                self.chat_area.append(f" Вы: {text}")
            self.chat_area.ensureCursorVisible()

        def send_message(self):
            user_text = self.input_entry.text().strip()
            if not user_text:
                return
            self.input_entry.clear()
            self.display("Вы", user_text)

            if user_text.lower() in ['пока', 'выход', 'до свидания']:
                self.close()
                return

            if user_text.lower() in ['статус', 'как ты', 'состояние']:
                self.display("Лейла", responder._get_status())
                return

            if user_text.lower() in ['нейроны', 'мозг']:
                responder._show_active_neurons()
                self.display("Лейла", "Смотри на активность мозга 🧠")
                return

            if user_text.lower() in ['спать', 'ложись спать']:
                responder.p.go_to_sleep()
                self.display("Лейла", "Спокойной ночи.")
                return

            if user_text.lower() in ['разбуди', 'просыпайся']:
                if responder.p.is_sleeping:
                    responder.p.wake_up()
                    self.display("Лейла", "Доброе утро!")
                else:
                    self.display("Лейла", "Я и не сплю.")
                return

            response = responder.generate_response(user_text)
            self.display("Лейла", response)
            responder.save_state()

    window = LeilaWindow()
    window.show()
    sys.exit(app.exec_())


# =========================================================
#  MAIN
# =========================================================
def main():
    print("=" * 55)
    print("✨ ЗАПУСК ЛЕЙЛЫ ✨")
    print("Нейроны ведут диалог, LLM формулирует")
    print("=" * 55)

    # QApplication создаём ПЕРВЫМ делом
    app = None
    if PYQT_AVAILABLE:
        app = QApplication(sys.argv)

    personality = HumanPersonality(name="Лейла")
    responder = HumanResponder(personality)

    # Режим
    if "--console" in sys.argv:
        mode = "--console"
    elif app is not None:
        mode = "--gui"
    else:
        mode = "--console"

    if mode == "--gui" and app is not None:
        print("[MAIN] GUI-режим с визуализацией")
        run_gui(responder, personality, app)
    else:
        print("[MAIN] Консольный режим")
        run_console(responder, personality)


if __name__ == "__main__":
    main()