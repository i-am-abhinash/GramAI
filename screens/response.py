"""Responsive, scrollable answer screen with the shared GramAI glass styling."""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
                             QScrollArea, QSizePolicy)
from widgets.components import GlassButton
from widgets.aurora import AuroraSurface

LABEL="background:transparent;border:none;color:#F4FAFF;"
MUTED="background:transparent;border:none;color:#B9D1EA;"
CARD=("QFrame#ResponseCard {background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
      "stop:0 #0D2947,stop:.55 #111C39,stop:1 #21143F);"
      "border:1px solid #347BA9;border-radius:22px;}"
      "QLabel {background:transparent;border:none;}")

class ResponseScreen(QWidget):
    ask_again=pyqtSignal()
    return_home=pyqtSignal()
    replay_audio=pyqtSignal(str)
    submit_feedback=pyqtSignal(str,str,bool)

    def __init__(self,parent=None):
        super().__init__(parent)
        self.language='te'
        self.current_question=""
        self.current_response=""
        root=QVBoxLayout(self);root.setContentsMargins(0,0,0,0)
        surface=AuroraSurface();root.addWidget(surface)
        outer=QVBoxLayout(surface);outer.setContentsMargins(38,14,38,20);outer.setSpacing(8)

        scroll=QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea {background:transparent;border:none;} QScrollArea > QWidget > QWidget {background:transparent;} QScrollBar:vertical {background:#0B1730;width:9px;} QScrollBar::handle:vertical {background:#397DAB;border-radius:4px;min-height:30px;}")
        outer.addWidget(scroll,1)
        content=QWidget();content.setStyleSheet("background:transparent;")
        scroll.setWidget(content)
        v=QVBoxLayout(content);v.setContentsMargins(18,6,18,8);v.setSpacing(13)

        self.title_label=QLabel("ఇదిగో మీ సమాధానం")
        title=self.title_label
        title.setStyleSheet(LABEL+"font-size:28px;font-weight:750;")
        v.addWidget(title)

        question_card=QFrame();question_card.setObjectName("ResponseCard");question_card.setStyleSheet(CARD)
        q=QVBoxLayout(question_card);q.setContentsMargins(22,13,22,15);q.setSpacing(5)
        self.qtag=QLabel("YOU ASKED")
        qtag=self.qtag;qtag.setStyleSheet(MUTED+"font-size:12px;font-weight:800;letter-spacing:1px;")
        q.addWidget(qtag)
        self.q_lbl=QLabel("...");self.q_lbl.setWordWrap(True)
        self.q_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.q_lbl.setStyleSheet(LABEL+"font-size:21px;")
        q.addWidget(self.q_lbl)
        v.addWidget(question_card)

        answer_card=QFrame();answer_card.setObjectName("ResponseCard");answer_card.setStyleSheet(CARD)
        a=QVBoxLayout(answer_card);a.setContentsMargins(22,15,22,18);a.setSpacing(12)
        head=QHBoxLayout();head.setSpacing(12)
        self.answer_badge=QLabel("GRAMAI ANSWER")
        badge=self.answer_badge;badge.setStyleSheet("background:transparent;border:none;color:#65DFFF;font-size:13px;font-weight:800;letter-spacing:1px;")
        head.addWidget(badge);head.addStretch()
        self.speaker_btn=GlassButton("🔊  Listen Again",pill=True)
        self.speaker_btn.setMinimumSize(155,44)
        self.speaker_btn.clicked.connect(self._on_replay_clicked)
        head.addWidget(self.speaker_btn)
        a.addLayout(head)

        self.ans_lbl=QLabel("...")
        self.ans_lbl.setWordWrap(True)
        self.ans_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.ans_lbl.setAlignment(Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft)
        self.ans_lbl.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Preferred)
        self.ans_lbl.setStyleSheet(LABEL+"font-size:20px;")
        a.addWidget(self.ans_lbl)

        self.source_box=QFrame();self.source_box.setObjectName("SourceBox")
        self.source_box.setStyleSheet("QFrame#SourceBox {background:#102541;border:1px solid #326D99;border-radius:14px;} QLabel {background:transparent;border:none;}")
        source_layout=QVBoxLayout(self.source_box);source_layout.setContentsMargins(15,9,15,10);source_layout.setSpacing(4)
        self.source_title=QLabel("Source Information")
        source_title=self.source_title
        source_title.setStyleSheet(MUTED+"font-size:13px;font-weight:700;")
        source_layout.addWidget(source_title)
        self.source_details=QLabel("")
        self.source_details.setWordWrap(True)
        self.source_details.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.source_details.setStyleSheet(MUTED+"font-size:14px;")
        source_layout.addWidget(self.source_details)
        a.addWidget(self.source_box)
        v.addWidget(answer_card)

        feedback=QHBoxLayout();feedback.setSpacing(9)
        self.fb_lbl=QLabel("Was this helpful?")
        self.fb_lbl.setStyleSheet(MUTED+"font-size:16px;")
        self.up_btn=GlassButton("👍 Helpful",pill=True)
        self.down_btn=GlassButton("👎 Not Helpful",pill=True)
        for btn in (self.up_btn,self.down_btn):
            btn.setMinimumSize(132,43)
        self.up_btn.clicked.connect(lambda:self._submit_feedback(True))
        self.down_btn.clicked.connect(lambda:self._submit_feedback(False))
        feedback.addWidget(self.fb_lbl);feedback.addWidget(self.up_btn);feedback.addWidget(self.down_btn)
        v.addStretch(1)

        self.speaking_anim=QLabel("🔊  Speaking...")
        self.speaking_anim.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speaking_anim.setStyleSheet("background:transparent;color:#8AE6FF;font-size:17px;font-weight:600;")
        outer.addWidget(self.speaking_anim)
        self.speaking_anim.setMaximumHeight(27)

        actions=QHBoxLayout();actions.setSpacing(10)
        actions.addLayout(feedback)
        actions.addStretch(1)
        home=GlassButton("⌂  Return Home",pill=True)
        again=GlassButton("🎤  Ask Another Question",pill=True)
        for b in (home,again):b.setMinimumSize(195,48)
        home.clicked.connect(self.return_home.emit)
        again.clicked.connect(self.ask_again.emit)
        actions.addWidget(home);actions.addWidget(again)
        outer.addLayout(actions)

    def set_language(self,language):
        self.language='en' if language=='en' else 'te'
        en=self.language=='en'
        self.title_label.setText('Here is your answer' if en else 'ఇదిగో మీ సమాధానం')
        self.qtag.setText('YOU ASKED' if en else 'మీ ప్రశ్న')
        self.answer_badge.setText('GRAMAI ANSWER' if en else 'గ్రామ్‌ఏఐ సమాధానం')
        self.source_title.setText('Source Information' if en else 'మూల సమాచారం')
        self.speaker_btn.setText('🔊 Listen Again' if en else '🔊 మళ్లీ వినండి')
        self.fb_lbl.setText('Was this helpful?' if en else 'ఇది మీకు సహాయపడిందా?')
        self.up_btn.setText('👍 Helpful' if en else '👍 సహాయపడింది')
        self.down_btn.setText('👎 Not Helpful' if en else '👎 సహాయపడలేదు')

    def set_data(self,question,answer,source=None):
        self.q_lbl.setText(question)
        self.ans_lbl.setText(answer)
        self.current_question=question
        self.current_response=answer
        self.fb_lbl.setText("Was this helpful?" if self.language=="en" else "ఇది మీకు సహాయపడిందా?")
        self.up_btn.show();self.down_btn.show()
        if source and source.get("name"):
            self.source_box.show()
            details=["• Portal: "+str(source.get("name"))]
            if source.get("url"):details.append("• URL: "+str(source["url"]))
            if source.get("date"):details.append("• Updated: "+str(source["date"]))
            self.source_details.setText("\n".join(details))
        else:
            self.source_box.hide()

    def _submit_feedback(self,is_helpful):
        self.submit_feedback.emit(self.current_question,self.current_response,is_helpful)
        self.up_btn.hide();self.down_btn.hide()
        self.fb_lbl.setText(("✓ Thank you for your feedback!" if is_helpful else "✓ Feedback sent for admin review.") if self.language=="en" else ("✓ మీ అభిప్రాయానికి ధన్యవాదాలు!" if is_helpful else "✓ మీ అభిప్రాయం పంపబడింది."))

    def _on_replay_clicked(self):
        if self.current_response:
            self.replay_audio.emit(self.current_response)
