"""Clarification screen for ambiguous semantic queries."""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QFrame
from theme import TEXT, ACCENT_HI, PANEL, BORDER, BG

class ClarificationScreen(QWidget):
    option_selected = pyqtSignal(str) # Emits the name of the scheme selected
    cancelled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        v = QVBoxLayout(self)
        v.setContentsMargins(40, 40, 40, 40)
        v.setSpacing(20)

        # Header
        t1 = QLabel("Did you mean:")
        t1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t1.setStyleSheet(f"color: {TEXT}; font-size: 32px; font-weight: 700;")
        v.addWidget(t1)

        t2 = QLabel("మీకు ఈ పథకాలలో ఏది కావాలి?")
        t2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t2.setStyleSheet(f"color: {ACCENT_HI}; font-size: 20px;")
        v.addWidget(t2)

        # Options Container
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none; background: transparent;")
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(15)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        
        v.addWidget(self.scroll, stretch=1)

        # Cancel Button
        cancel = QPushButton("Cancel")
        cancel.setObjectName("Ghost")
        cancel.setFixedWidth(180)
        cancel.setFixedHeight(48)
        cancel.clicked.connect(self.cancelled.emit)
        v.addWidget(cancel, alignment=Qt.AlignmentFlag.AlignHCenter)

    def set_options(self, options_list):
        """Populates the list of buttons for clarification."""
        # Clear existing
        for i in reversed(range(self.scroll_layout.count())): 
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Create new buttons
        for idx, option_name in enumerate(options_list):
            btn = QPushButton(f"{idx + 1}. {option_name}")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {PANEL};
                    border: 1px solid {BORDER};
                    border-radius: 18px;
                    color: {TEXT};
                    font-size: 22px;
                    text-align: left;
                    padding: 20px;
                }}
                QPushButton:hover {{
                    border: 1px solid {ACCENT_HI};
                    background: {BG};
                }}
            """)
            # Capture the value correctly in the lambda
            btn.clicked.connect(lambda checked, name=option_name: self.option_selected.emit(name))
            self.scroll_layout.addWidget(btn)
