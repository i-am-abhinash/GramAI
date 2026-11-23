"""Admin shell: sidebar + stacked admin pages."""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel,
                             QPushButton, QStackedWidget, QButtonGroup)
from theme import PANEL, BORDER, ACCENT_HI, TEXT, TEXT_MUTED
from widgets.components import GlassButton, ToastNotification
from widgets.aurora import AuroraSurface
from admin.dashboard      import DashboardPage
from admin.unanswered     import UnansweredPage
from admin.schemes        import SchemesPage
from admin.pending_reviews import PendingReviewsPage
from admin.feedback       import FeedbackPage

class AdminShell(QWidget):
    logout = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QHBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        self.root = root

        # Sidebar
        side = QFrame(); side.setObjectName("Sidebar"); side.setFixedWidth(268)
        side.setStyleSheet("QFrame#Sidebar {background:#071329; border-right:1px solid #285174;}")
        self.sidebar = side
        sv = QVBoxLayout(side); sv.setContentsMargins(16,24,16,18); sv.setSpacing(7)
        self.sv = sv

        brand = QLabel("✦  GramAI Studio")
        brand.setStyleSheet(f"color:{ACCENT_HI}; font-family: Segoe UI Variable; font-size:20px; font-weight:800; padding:8px 6px 12px;")
        brand.setMinimumHeight(55)
        sv.addWidget(brand)

        # Keep the admin interface focused on the five essential workflows.
        # Technical pages and their backend services remain untouched.
        self.page_factories = (
            DashboardPage,
            UnansweredPage,
            PendingReviewsPage,
            FeedbackPage,
            SchemesPage,
        )
        self.stack = QStackedWidget()
        for factory in self.page_factories:
            self.stack.addWidget(factory())

        items = [
            ("📊  Dashboard", 0),
            ("🛎  Unanswered Questions", 1),
            ("✅  Verify Information", 2),
            ("💬  Feedback Review", 3),
            ("📄  Government Schemes", 4),
        ]

        self._group = QButtonGroup(self); self._group.setExclusive(True)
        for label, idx in items:
            b = GlassButton(label, pill=True); b.setCheckable(True)
            b.setMinimumHeight(46)
            b.setToolTip(label.strip())
            b.clicked.connect(lambda _=False, i=idx: self._switch_tab(i))
            self._group.addButton(b)
            sv.addWidget(b)
        self._group.buttons()[0].setChecked(True)

        sv.addStretch(1)
        
        self.rn = QLabel("")
        self.rn.setStyleSheet(f"color:{TEXT_MUTED}; font-size:12px; margin-bottom:10px;")
        self.rn.hide()
        sv.addWidget(self.rn)

        out = GlassButton("⎋  Secure Logout", pill=True)
        out.setMinimumHeight(46)
        out.clicked.connect(self.logout.emit)
        sv.addWidget(out)

        root.addWidget(side)
        side.hide()
        content = AuroraSurface()
        cv = QVBoxLayout(content)
        cv.setContentsMargins(24, 18, 24, 20)
        top = QHBoxLayout()
        toggle = GlassButton("☰", pill=False)
        toggle.setToolTip("Show or hide admin navigation")
        toggle.setFixedSize(52, 46)
        toggle.clicked.connect(lambda: side.setVisible(not side.isVisible()))
        top.addWidget(toggle)
        title = QLabel("GramAI  /  Admin Studio")
        title.setStyleSheet("font-family: Segoe UI Variable; font-size: 21px; font-weight: 750; color: #7DDEFF;")
        top.addWidget(title)
        top.addStretch()
        cv.addLayout(top)
        self.stack.setStyleSheet("QStackedWidget { background: transparent; border: none; }")
        cv.addWidget(self.stack, 1)
        root.addWidget(content, 1)

        self.toast = ToastNotification(self)

    def set_user_session(self, user_session):
        self.user_session = user_session
        if self.user_session:
            self.rn.setText(f"Logged in as:\n{self.user_session.get('full_name', '')}\n{self.user_session.get('designation', '')}")
            self.rn.show()
        else:
            from backend.services.auth_service import AuthService
            u = AuthService.get_current_user()
            if u:
                self.rn.setText(f"Logged in as:\n{u.get('full_name', '')}\n{u.get('designation', '')}")
                self.rn.show()
            else:
                self.rn.hide()

        # Remove previous logout button if it exists
        for i in reversed(range(self.sv.count())):
            widget = self.sv.itemAt(i).widget()
            if widget and hasattr(widget, 'text') and "Logout" in widget.text():
                widget.deleteLater()

        out = GlassButton("⎋  Secure Logout", pill=True)
        out.setMinimumHeight(46)
        out.clicked.connect(self.logout.emit)
        self.sv.addWidget(out)

    def _switch_tab(self, idx):
        # Refresh only the selected, visible page.
        if not 0 <= idx < len(self.page_factories):
            return
        old_widget = self.stack.widget(idx)
        new_widget = self.page_factories[idx]()
        self.stack.removeWidget(old_widget)
        self.stack.insertWidget(idx, new_widget)
        old_widget.deleteLater()
        self.stack.setCurrentIndex(idx)
        self.sidebar.hide()

    def show_toast(self, message: str, level="success"):
        self.toast.show_toast(message, level)
