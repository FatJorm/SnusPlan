from PyQt6.QtWidgets import (QApplication, QLabel, QWidget, QPushButton,
                             QGridLayout, QVBoxLayout, QMainWindow, QHBoxLayout, QLineEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from accessories.Plan import Plan
from datetime import date, time, datetime, timedelta
import threading
import time
import sys

window_geometry = (200, 200, 400, 600)
button_geometry = (120, 50)
snus_button_geometry = (200, 200)


class WorkerThread(QThread):
    progress_update = pyqtSignal(int)

    def __init__(self):
        super(WorkerThread, self).__init__()
        self.stop_event = threading.Event()

    def run(self):
        self.progress_update.emit(0)
        now = datetime.now()
        daily_plan = plan._state['day_plan']
        if daily_plan:
            next_time = daily_plan[-1]
            if now > next_time:
                self.progress_update.emit(1)
            else:
                diff = next_time - now
                # This will wait for the duration of diff or until the stop_event is set
                self.stop_event.wait(diff.total_seconds())
                if not self.stop_event.is_set():
                    self.progress_update.emit(1)

    def stop(self):
        self.stop_event.set()  # This will interrupt the wait in the run method


class Setup(QWidget):
    def __init__(self, main_window, worker_thread):
        super().__init__()

        self.main_window = main_window
        self.worker_thread = worker_thread

        # Set background color for the main window
        self.setStyleSheet("background-color: #262626;")  # light gray background

        # Apply stylesheet
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 15px 32px;
                text-align: center;
                font-size: 16px;
                border: none;
                cursor: pointer;
                border-radius: 4px;
            }

            QPushButton:hover {
                background-color: #45a049;
            }

            QLineEdit {
                padding: 5px;
            }
        """)

        self.create_QBoxLayout()

    def create_QBoxLayout(self):
        # Create an outer vertical layout
        outer_v_layout = QVBoxLayout()

        # Settings Grid
        settings_grid = QGridLayout()
        cnt_label = QLabel("Current daily snus: ")
        cnt_label.setStyleSheet("QLabel { color: #FFFFFF; }")
        settings_grid.addWidget(cnt_label, 0, 0)

        cnt_box = QLineEdit()
        cnt_box.setStyleSheet("QLineEdit { color: #FFFFFF; }")
        cnt_box.setText(f"{plan._state['daily_dose']}")
        cnt_box.setPlaceholderText("Enter daily snus consumption")
        settings_grid.addWidget(cnt_box, 0, 1)

        # Add the settings grid to a QHBoxLayout to center it horizontally
        h_settings_layout = QHBoxLayout()
        h_settings_layout.addStretch()
        h_settings_layout.addLayout(settings_grid)
        h_settings_layout.addStretch()

        # Add the settings layout to the outer vertical layout
        outer_v_layout.addLayout(h_settings_layout)

        # OK and Back Buttons Layout
        h_ok_layout = QHBoxLayout()

        # Back Button
        back_btn = QPushButton("Back")
        back_btn.setFixedSize(*button_geometry)
        back_btn.clicked.connect(self.back_btn_clicked)  # Connect to your desired method or function
        h_ok_layout.addWidget(back_btn)  # Adding Back button to the left

        # Ok Button
        ok_btn = QPushButton("OK")
        ok_btn.setFixedSize(*button_geometry)
        ok_btn.clicked.connect(lambda: self.push_btn(int(cnt_box.text())))
        h_ok_layout.addStretch()  # stretch before button for centering
        h_ok_layout.addWidget(ok_btn)

        outer_v_layout.addStretch()

        # Add the OK and Back button layout below the settings grid in the outer vertical layout
        outer_v_layout.addLayout(h_ok_layout)

        self.setLayout(outer_v_layout)

    def back_btn_clicked(self):
        self.main_window.set_content(Window(self.main_window))

    def push_btn(self, no_of_snus):
        plan.setup(no_of_snus)
        self.stop_thread()
        self.worker_thread.start()

        self.main_window.set_content(Window(self.main_window))

    def stop_thread(self):
        if self.worker_thread.isRunning():
            self.worker_thread.stop()


class Window(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Set background color for the main window
        self.setStyleSheet("background-color: #262626;")  # light gray background

        # Apply stylesheet
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 15px 32px;
                text-align: center;
                font-size: 16px;
                border: none;
                cursor: pointer;
                border-radius: 4px;
            }

            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        self.create_Layout()

    def create_Layout(self):
        v_layout = QVBoxLayout()

        h_layout = QHBoxLayout()
        h_layout.addStretch()

        # Setup Button
        setup_btn = QPushButton("Setup")
        setup_btn.setStyleSheet("background-color: #86592d;")
        setup_btn.clicked.connect(self.push_setup_btn)
        setup_btn.setFixedSize(*button_geometry)
        h_layout.addWidget(setup_btn)

        # Main button
        self.main_btn = QPushButton("SNUS")
        self.main_btn.clicked.connect(self.push_main_btn)
        self.main_btn.setFixedSize(*snus_button_geometry)
        if self.time_for_next():
            self.main_btn.setEnabled(True)
            self.main_btn.setStyleSheet("background-color: #4CAF50;")
        else:
            self.main_btn.setEnabled(False)
            self.main_btn.setStyleSheet("background-color: #ff0000;")


        # Textbox (QLineEdit)
        self.next_snus_label = QLabel(self)
        self.next_snus_label.setStyleSheet("QLabel { color: #FFFFFF; }")
        self.next_snus_label.setText(f"Next snus: {plan.get_next_snus_time_string()}")

        v_layout.addLayout(h_layout)
        v_layout.addStretch()
        v_layout.addWidget(self.main_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        v_layout.addWidget(self.next_snus_label, alignment=Qt.AlignmentFlag.AlignCenter)  # Add the textbox below the main button
        v_layout.addStretch()

        self.setLayout(v_layout)

        self.worker_thread = WorkerThread()
        self.worker_thread.progress_update.connect(self.update_progress)

        self.worker_thread.start()

    def start_thread(self):
        self.main_btn.setEnabled(False)
        self.main_btn.setStyleSheet("background-color: #ff0000;")
        self.worker_thread.start()

    def update_progress(self, value):
        if value == 1:
            self.main_btn.setEnabled(True)
            self.main_btn.setStyleSheet("background-color: #4CAF50;")



    def time_for_next(self):
        now = datetime.now()
        day_plan = plan._state['day_plan']
        if day_plan:
            next = day_plan[-1]
            if now > next:
                return True
            else:
                return False
        else:
            return False



    def push_setup_btn(self):
        self.main_window.set_content(Setup(self.main_window, self.worker_thread))


    def push_main_btn(self):
        plan.get_next()
        self.next_snus_label.setText(f"Next snus: {plan.get_next_snus_time_string()}")
        self.start_thread()



class Main(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set background color for the main window
        self.setStyleSheet("background-color: #262626;")  # light gray background

        self.setGeometry(*window_geometry)
        self.setWindowTitle("Snus Manager")  # Giving the main window a title
        self.set_content(Window(self))
        self.show()

    def set_content(self, widget):
        self.setCentralWidget(widget)
        widget.show()




plan = Plan()
app = QApplication(sys.argv)
main = Main()
sys.exit(app.exec())
