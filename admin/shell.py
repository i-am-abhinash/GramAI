"""Admin shell: sidebar + stacked admin pages."""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel,
                             QPushButton, QStackedWidget, QButtonGroup)
from theme import PANEL, BORDER, ACCENT_HI, TEXT, TEXT_MUTED
from admin.dashboard      import DashboardPage
from admin.unanswered     import UnansweredPage
from admin.schemes        import SchemesPage
from admin.pending_reviews import PendingReviewsPage
from admin.sync_logs      import SyncLogsPage
from admin.faq            import FaqPage
from admin.query_logs     import QueryLogsPage
from admin.settings       import SettingsPage
from admin.analytics      import AnalyticsPage
from admin.feedback       import FeedbackPage

class AdminShell(QWidget):
    logout = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QHBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # Sidebar
        side = QFrame(); side.setObjectName("Sidebar"); side.setFixedWidth(250)
        sv = QVBoxLayout(side); sv.setContentsMargins(16,20,16,20); sv.setSpacing(6)

        brand = QLabel("GramAI Admin")
        brand.setStyleSheet(f"color:{ACCENT_HI}; font-size:18px; font-weight:800; padding:6px 8px 14px;")
        sv.addWidget(brand)

        self.stack = QStackedWidget()
        self.stack.addWidget(DashboardPage())               # 0
        self.stack.addWidget(UnansweredPage())              # 1
        self.stack.addWidget(PendingReviewsPage())          # 2
        self.stack.addWidget(AnalyticsPage())               # 3
        self.stack.addWidget(FeedbackPage())                # 4
        self.stack.addWidget(SchemesPage())                 # 5
        self.stack.addWidget(SyncLogsPage())                # 6
        self.stack.addWidget(QueryLogsPage())               # 7
        self.stack.addWidget(SettingsPage())                # 8

        items = [("📊  Dashboard",0), ("🛎  Unanswered Questions",1), ("✅  Verify Information",2),
                 ("📈  Analytics",3), ("💬  Feedback Review",4), ("📄  Imported Schemes",5),
                 ("🔄  Sync Logs",6), ("📜  Query Logs",7), ("⚙️  Settings",8)]
                 
        self._group = QButtonGroup(self); self._group.setExclusive(True)
        for label, idx in items:
            b = QPushButton(label); b.setObjectName("NavItem"); b.setCheckable(True)
            b.clicked.connect(lambda _=False, i=idx: self._switch_tab(i))
            self._group.addButton(b)
            sv.addWidget(b)
        self._group.buttons()[0].setChecked(True)

        sv.addStretch(1)
        
        # User role display
        from backend.services.auth_service import AuthService
        u = AuthService.get_current_user()
        if u:
            rn = QLabel(f"Logged in as:\n{u['full_name']}\n{u['designation']}")
            rn.setStyleSheet(f"color:{TEXT_MUTED}; font-size:12px; margin-bottom:10px;")
            sv.addWidget(rn)

        out = QPushButton("⎋  Secure Logout"); out.setObjectName("NavItem")
        out.clicked.connect(self.logout.emit)
        sv.addWidget(out)

        root.addWidget(side)
        root.addWidget(self.stack, 1)

    def _switch_tab(self, idx):
        # Dynamically refresh data by recreating the widget
        old_widget = self.stack.widget(idx)
        self.stack.removeWidget(old_widget)
        old_widget.deleteLater()
        
        if idx == 0: new_widget = DashboardPage()
        elif idx == 1: new_widget = UnansweredPage()
        elif idx == 2: new_widget = PendingReviewsPage()
        elif idx == 3: new_widget = AnalyticsPage()
        elif idx == 4: new_widget = FeedbackPage()
        elif idx == 5: new_widget = SchemesPage()
        elif idx == 6: new_widget = SyncLogsPage()
        elif idx == 7: new_widget = QueryLogsPage()
        elif idx == 8: new_widget = SettingsPage()
        
        self.stack.insertWidget(idx, new_widget)
        self.stack.setCurrentIndex(idx)
