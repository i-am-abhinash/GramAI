from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QWidget, QFrame
from theme import PANEL, PANEL_HI, BORDER, ACCENT_HI, TEXT, TEXT_MUTED, ACCENT

class SchemeDetailModal(QDialog):
    read_aloud_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(700, 600)
        
        self.v = QVBoxLayout(self)
        self.v.setContentsMargins(0,0,0,0)
        
        self.card = QFrame()
        self.card.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL};
                border: 2px solid {BORDER};
                border-radius: 20px;
            }}
        """)
        self.cv = QVBoxLayout(self.card)
        self.cv.setContentsMargins(30,30,30,30)
        self.cv.setSpacing(16)
        
        # Header
        head = QHBoxLayout()
        self.title_lbl = QLabel()
        self.title_lbl.setWordWrap(True)
        self.title_lbl.setStyleSheet(f"color: {TEXT}; font-size: 24px; font-weight: 800; border: none;")
        head.addWidget(self.title_lbl, 1)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(40, 40)
        close_btn.setStyleSheet(f"background: {PANEL_HI}; color: {TEXT}; border-radius: 20px; font-weight: bold; border: none;")
        close_btn.clicked.connect(self.accept)
        head.addWidget(close_btn)
        self.cv.addLayout(head)
        
        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        self.scroll_layout = QVBoxLayout(container)
        self.scroll_layout.setContentsMargins(0,0,10,0)
        self.scroll_layout.setSpacing(14)
        
        self.desc_lbl = QLabel()
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setStyleSheet(f"color: {TEXT}; font-size: 16px; border: none;")
        self.scroll_layout.addWidget(self.desc_lbl)
        
        self.eligibility_lbl = QLabel()
        self.eligibility_lbl.setWordWrap(True)
        self.eligibility_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 15px; border: none;")
        self.scroll_layout.addWidget(self.eligibility_lbl)
        
        self.scroll_layout.addStretch(1)
        scroll.setWidget(container)
        self.cv.addWidget(scroll, 1)
        
        # Actions
        actions = QHBoxLayout()
        read_btn = QPushButton("🔊 Read Aloud")
        read_btn.setStyleSheet(f"""
            QPushButton {{
                background: {PANEL_HI}; border: 1px solid {ACCENT}; color: {ACCENT_HI}; 
                padding: 12px 24px; border-radius: 12px; font-size: 16px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {ACCENT}; color: #000; }}
        """)
        read_btn.clicked.connect(self._emit_read_aloud)
        actions.addStretch(1)
        actions.addWidget(read_btn)
        
        self.cv.addLayout(actions)
        self.v.addWidget(self.card)

    def set_data(self, title, description, eligibility):
        self.title_lbl.setText(title)
        self.desc_lbl.setText(f"<b>Description:</b><br>{description}")
        self.eligibility_lbl.setText(f"<b>Eligibility:</b><br>{eligibility}")
        self.full_text = f"{title}. {description}. Eligibility: {eligibility}"
        
    def _emit_read_aloud(self):
        self.read_aloud_requested.emit(self.full_text)
