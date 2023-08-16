from PyQt6.QtWidgets import (QApplication, QLabel, QWidget, QPushButton,
                             QGridLayout, QVBoxLayout, QMainWindow, QHBoxLayout, QLineEdit)
from PyQt6.QtCore import Qt
from accessories.Plan import Plan
from datetime import date, time, datetime, timedelta
import sys

window_geometry = (200, 200, 400, 600)

class Setup(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

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

    # ... [rest of the Setup class remains unchanged]

class Window(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

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

    # ... [rest of the Window class remains unchanged]

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(*window_geometry)
        self.setWindowTitle("Snus Manager")  # Giving the main window a title
        self.set_content(Window(self))
        self.show()

    # ... [rest of the Main class remains unchanged]

# ... [rest of the code remains unchanged]
