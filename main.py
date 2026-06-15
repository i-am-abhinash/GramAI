"""
GramAI - AI Powered Rural Assistance System
Entry point. Run with: python main.py
Requires: PyQt6  (pip install PyQt6)
"""
import sys
from PyQt6.QtWidgets import QApplication
from app_window import MainWindow
from theme import APP_QSS


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("GramAI")
    app.setStyleSheet(APP_QSS)
    win = MainWindow()
    win.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
