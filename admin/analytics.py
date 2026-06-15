"""Analytics page for GramAI activity."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout)
from theme import TEXT, TEXT_MUTED, PANEL, BORDER, PANEL_HI

class AnalyticsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.v = QVBoxLayout(self); self.v.setContentsMargins(30,28,30,28); self.v.setSpacing(16)

        head = QLabel("System Analytics")
        head.setStyleSheet(f"color:{TEXT}; font-size:26px; font-weight:800;")
        self.v.addWidget(head)
        sub = QLabel("Insights into citizen queries, trends, and system usage.")
        sub.setStyleSheet(f"color:{TEXT_MUTED}; font-size:14px;")
        self.v.addWidget(sub)

        grid = QGridLayout(); grid.setSpacing(18)
        
        # 1. Most Asked Questions
        maq_card = self._create_card("Most Asked Questions")
        grid.addWidget(maq_card, 0, 0)
        
        # 2. Most Requested Schemes
        mrs_card = self._create_card("Most Requested Schemes")
        grid.addWidget(mrs_card, 0, 1)
        
        # 3. Category Trends
        ct_card = self._create_card("Category Trends")
        grid.addWidget(ct_card, 1, 0)
        
        # 4. Daily Usage
        du_card = self._create_card("Daily Usage Patterns")
        grid.addWidget(du_card, 1, 1)

        self.v.addLayout(grid)
        self.v.addStretch(1)

    def _create_card(self, title):
        card = QFrame()
        card.setStyleSheet(f"QFrame {{background:{PANEL}; border:1px solid {BORDER}; border-radius:12px;}}")
        v = QVBoxLayout(card); v.setContentsMargins(20,20,20,20)
        t = QLabel(title)
        t.setStyleSheet(f"color:{TEXT}; font-size:16px; font-weight:700; border:none;")
        v.addWidget(t)
        
        # Placeholder for actual graphs/lists
        content = QLabel("Data currently gathering...")
        content.setStyleSheet(f"color:{TEXT_MUTED}; font-style:italic; border:none;")
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(content, 1)
        return card
