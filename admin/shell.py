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
        self.root = QHBoxLayout(self); self.root.setContentsMargins(0,0,0,0); self.root.setSpacing(0)

        # Sidebar
        side = QFrame(); side.setObjectName("Sidebar"); side.setFixedWidth(286)
        self.sv = QVBoxLayout(side); self.sv.setContentsMargins(20,28,20,22); self.sv.setSpacing(9)

        brand = QLabel("✦  GramAI Studio")
        brand.setStyleSheet(f"color:{ACCENT_HI}; font-size:22px; font-weight:800; padding:10px 8px 22px;")
        self.sv.addWidget(brand)

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
            self.sv.addWidget(b)
        self._group.buttons()[0].setChecked(True)

        self.sv.addStretch(1)
        
        self.rn = QLabel("")
        self.rn.setStyleSheet(f"color:{TEXT_MUTED}; font-size:12px; margin-bottom:10px;")
        self.rn.hide()
        self.sv.addWidget(self.rn)
        
        self.root.addWidget(side)
        self.root.addWidget(self.stack, 1)

        # Global Toast
        from widgets.components import ToastNotification
        self.toast = ToastNotification(self)

    def set_user_session(self, user_session):
        self.user_session = user_session
        if self.user_session:
            self.rn.setText(f"Logged in as:\n{self.user_session['full_name']}\n{self.user_session['designation']}")
            self.rn.show()
        else:
            self.rn.hide()

        # Remove previous logout button if it exists
        for i in reversed(range(self.sv.count())):
            widget = self.sv.itemAt(i).widget()
            if widget and widget.text() == "⎋  Secure Logout":
                widget.deleteLater()

        out = QPushButton("⎋  Secure Logout"); out.setObjectName("NavItem")
        out.clicked.connect(self.logout.emit)
        self.sv.addWidget(out)

    def _switch_tab(self, idx):
        widget = self.stack.widget(idx)
        if hasattr(widget, 'refresh_data'):
            widget.refresh_data()
        self.stack.setCurrentIndex(idx)
        
    def show_toast(self, message: str, level="success"):
        self.toast.show_toast(message, level)
