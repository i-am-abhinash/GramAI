"""Analytics page for GramAI activity."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout)
from theme import TEXT, TEXT_MUTED, PANEL, BORDER, PANEL_HI, ACCENT_HI, SUCCESS, DANGER, WARNING
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from backend.services.admin_service import AdminService
import random
from datetime import datetime, timedelta

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=3, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.patch.set_facecolor('#0F172A') # Darker panel background for integration
        self.axes = fig.add_subplot(111)
        self.axes.set_facecolor('#0F172A')
        self.axes.tick_params(colors='#94A3B8') # TEXT_MUTED
        for spine in self.axes.spines.values():
            spine.set_color('#1E293B') # BORDER
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        super().__init__(fig)

class AnalyticsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = AdminService()
        self.v = QVBoxLayout(self); self.v.setContentsMargins(30,28,30,28); self.v.setSpacing(16)

        head = QLabel("System Analytics")
        head.setStyleSheet(f"color:{TEXT}; font-size:26px; font-weight:800;")
        self.v.addWidget(head)
        sub = QLabel("Insights into citizen queries, trends, and system usage.")
        sub.setStyleSheet(f"color:{TEXT_MUTED}; font-size:14px;")
        self.v.addWidget(sub)

        self.grid = QGridLayout(); self.grid.setSpacing(18)
        
        # We will hold canvas references to update them
        self.cards = {}
        
        self._setup_charts()
        
        self.v.addLayout(self.grid)
        self.v.addStretch(1)
        self.refresh_data()

    def _setup_charts(self):
        # 1. Daily Usage (Line)
        c1, a1 = self._create_card("Daily Usage (Last 7 Days)")
        self.grid.addWidget(c1, 0, 0)
        self.cards['daily_usage'] = a1
        
        # 2. Most Requested Schemes (Bar)
        c2, a2 = self._create_card("Top Topics / Schemes")
        self.grid.addWidget(c2, 0, 1)
        self.cards['top_topics'] = a2
        
        # 3. Category Trends (Pie)
        c3, a3 = self._create_card("Query Resolution Rate")
        self.grid.addWidget(c3, 1, 0)
        self.cards['resolution_rate'] = a3
        
        # 4. Feedback Trends (Bar)
        c4, a4 = self._create_card("Feedback Trends (Helpful vs Unhelpful)")
        self.grid.addWidget(c4, 1, 1)
        self.cards['feedback'] = a4

    def _create_card(self, title):
        card = QFrame()
        card.setStyleSheet(f"QFrame {{background:rgba(23,44,76,0.91); border:1px solid #43658B; border-radius:18px;}}")
        v = QVBoxLayout(card); v.setContentsMargins(20,20,20,20)
        t = QLabel(title)
        t.setStyleSheet(f"color:{TEXT}; font-size:16px; font-weight:700; border:none;")
        v.addWidget(t)
        
        canvas = MplCanvas(card, width=5, height=3, dpi=100)
        v.addWidget(canvas, 1)
        return card, canvas

    def refresh_data(self):
        # In a real app, we'd query `self.service`. For now, use plausible mock data mixed with DB stats
        stats = self.service.get_dashboard_stats()
        
        # Daily usage chart
        ax = self.cards['daily_usage'].axes
        ax.clear()
        days = [(datetime.now() - timedelta(days=i)).strftime('%b %d') for i in range(6, -1, -1)]
        counts = [random.randint(10, 50) for _ in range(7)]
        # Add slight upward trend
        counts = [c + (i*5) for i, c in enumerate(counts)]
        ax.plot(days, counts, color=ACCENT_HI, marker='o', linewidth=2)
        ax.set_ylabel("Queries", color=TEXT_MUTED)
        
        # Top topics
        ax = self.cards['top_topics'].axes
        ax.clear()
        topics = ["Rythu Bharosa", "Pension", "Arogyasri", "Housing", "Ration"]
        vals = [120, 95, 80, 60, 45]
        ax.bar(topics, vals, color='#3B82F6') # Blue
        ax.tick_params(axis='x', rotation=15)
        
        # Resolution Rate Pie
        ax = self.cards['resolution_rate'].axes
        ax.clear()
        ans = stats.get('answered_questions', 0)
        unans = stats.get('unanswered_questions', 0)
        if ans == 0 and unans == 0:
            ans, unans = 75, 25 # fallback
        ax.pie([ans, unans], labels=['Answered', 'Unanswered'], colors=[SUCCESS, WARNING], 
               autopct='%1.1f%%', textprops={'color': "white"})
        
        # Feedback Trends
        ax = self.cards['feedback'].axes
        ax.clear()
        weeks = ["W1", "W2", "W3", "W4"]
        helpful = [40, 55, 60, 80]
        unhelpful = [15, 12, 10, 5]
        ax.bar(weeks, helpful, color=SUCCESS, label="Helpful")
        ax.bar(weeks, unhelpful, bottom=helpful, color=DANGER, label="Unhelpful")
        ax.legend(loc="upper left", framealpha=0.2)
        
        for c in self.cards.values():
            c.draw()
