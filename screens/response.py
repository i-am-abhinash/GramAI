"""Response screen: shows user question + AI answer with replay / ask-again actions."""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton
from theme import PANEL, PANEL_HI, BORDER, ACCENT, ACCENT_HI, TEXT, TEXT_MUTED
from widgets.components import GlassButton
from widgets.aurora import AuroraSurface

class ResponseScreen(QWidget):
    ask_again    = pyqtSignal()
    return_home  = pyqtSignal()
    replay_audio = pyqtSignal(str) # Emits the response text to be replayed
    submit_feedback = pyqtSignal(str, str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_response = ""
        root=QVBoxLayout(self);root.setContentsMargins(0,0,0,0)
        surface=AuroraSurface();root.addWidget(surface)
        v=QVBoxLayout(surface); v.setContentsMargins(60, 40, 60, 30); v.setSpacing(18)

        title = QLabel("Here is your answer")
        title.setStyleSheet(f"color: {TEXT}; font-size: 26px; font-weight: 700;")
        v.addWidget(title)

        # Question card
        self.q_card = self._card(
            badge="YOU ASKED",
            badge_color=ACCENT_HI,
            text="...",
            bg=PANEL_HI,
        )
        self.q_lbl = self.q_card.findChild(QLabel, "DynamicText")
        v.addWidget(self.q_card)

        # Answer card
        ans_card = QFrame(); ans_card.setObjectName("Card")
        ans_card.setStyleSheet(f"""
            QFrame#Card {{
                background: {PANEL};
                border: 1px solid {ACCENT};
                border-radius: 18px;
            }}
        """)
        a = QVBoxLayout(ans_card); a.setContentsMargins(22,18,22,18); a.setSpacing(10)
        head = QHBoxLayout()
        badge = QLabel("GRAMAI ANSWER")
        badge.setStyleSheet(f"color: {ACCENT_HI}; font-size: 12px; font-weight: 800; letter-spacing: 1px;")
        head.addWidget(badge); head.addStretch(1)
        
        self.speaker_btn = GlassButton("🔊  Replay",pill=True); self.speaker_btn.setObjectName("Ghost")
        self.speaker_btn.clicked.connect(self._on_replay_clicked)
        head.addWidget(self.speaker_btn)
        a.addLayout(head)

        self.ans_lbl = QLabel("...")
        self.ans_lbl.setWordWrap(True)
        self.ans_lbl.setStyleSheet(f"color: {TEXT}; font-size: 22px; line-height: 1.6;")
        a.addWidget(self.ans_lbl)

        # Source Transparency Box
        self.source_box = QFrame()
        self.source_box.setStyleSheet(f"background: rgba(31,58,96,0.92); border: 1px solid #43658B; border-radius: 20px;")
        s_layout = QVBoxLayout(self.source_box); s_layout.setContentsMargins(14,14,14,14); s_layout.setSpacing(4)
        
        s_title = QLabel("Source Information:")
        s_title.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 14px; font-weight: bold;")
        s_layout.addWidget(s_title)
        
        self.source_details = QLabel("")
        self.source_details.setWordWrap(True)
        self.source_details.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 14px;")
        s_layout.addWidget(self.source_details)
        
        a.addWidget(self.source_box)

        v.addWidget(ans_card)

        # Feedback UI
        self.fb_layout = QHBoxLayout(); self.fb_layout.setSpacing(10)
        self.fb_lbl = QLabel("Was this helpful?")
        self.fb_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 16px;")
        
        self.up_btn = GlassButton("👍 Helpful",pill=True)

        self.up_btn.clicked.connect(lambda: self._submit_feedback(True))
        
        self.down_btn = GlassButton("👎 Not Helpful",pill=True)

        self.down_btn.clicked.connect(lambda: self._submit_feedback(False))
        
        self.fb_layout.addStretch(1); self.fb_layout.addWidget(self.fb_lbl); self.fb_layout.addWidget(self.up_btn); self.fb_layout.addWidget(self.down_btn); self.fb_layout.addStretch(1)
        v.addLayout(self.fb_layout)

        # Speaking Animation Container
        self.speaking_anim = QLabel("🔊 Speaking...")
        self.speaking_anim.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speaking_anim.setStyleSheet(f"color: {ACCENT_HI}; font-size: 22px; font-weight: 500; margin-top: 20px;")
        v.addWidget(self.speaking_anim)

        v.addStretch(1)

        # Actions
        actions = QHBoxLayout(); actions.setSpacing(14)
        again = GlassButton("🎤  Ask Another Question",pill=True); again.setObjectName("Primary")
        again.setFixedHeight(64)

        again.clicked.connect(self.ask_again.emit)
        home = GlassButton("🏠  Return Home",pill=True); home.setObjectName("Ghost")
        home.setFixedHeight(64)

        home.clicked.connect(self.return_home.emit)
        actions.addStretch(1); actions.addWidget(home); actions.addWidget(again); actions.addStretch(1)
        v.addLayout(actions)

    def set_data(self, question, answer, source=None):
        self.q_lbl.setText(question)
        self.ans_lbl.setText(answer)
        self.current_question = question
        self.current_response = answer
        self.fb_lbl.setText("Was this helpful?")
        self.up_btn.show()
        self.down_btn.show()
        
        if source and source.get("name"):
            self.source_box.show()
            s_text = f"• Portal: {source.get('name')}\n• URL: {source.get('url')}\n• Updated: {source.get('date')}"
            self.source_details.setText(s_text)
        else:
            self.source_box.hide()

    def _submit_feedback(self, is_helpful):
        self.submit_feedback.emit(self.current_question, self.current_response, is_helpful)
        self.up_btn.hide()
        self.down_btn.hide()
        if is_helpful:
            self.fb_lbl.setText("✅ Thank you for your feedback!")
        else:
            self.fb_lbl.setText("🚩 Feedback sent for admin review.")

    def _on_replay_clicked(self):
        if self.current_response:
            self.replay_audio.emit(self.current_response)

    def _card(self, badge, badge_color, text, bg):
        c = QFrame(); c.setObjectName("Card")
        c.setStyleSheet(f"""
            QFrame#Card {{ background: {bg}; border: 1px solid {BORDER}; border-radius: 18px; }}
        """)
        l = QVBoxLayout(c); l.setContentsMargins(22,16,22,16); l.setSpacing(8)
        b = QLabel(badge); b.setStyleSheet(f"color: {badge_color}; font-size: 14px; font-weight: 800; letter-spacing: 1px;")
        t = QLabel(text); t.setObjectName("DynamicText"); t.setWordWrap(True); t.setStyleSheet(f"color: {TEXT}; font-size: 20px;")
        l.addWidget(b); l.addWidget(t)
        return c
