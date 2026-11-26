"""Evidence review for curated scheme drafts. Legacy rows remain quarantined."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QComboBox, QTextEdit, QCheckBox, QHBoxLayout, QMessageBox
from admin.glass import GlassDialog, glass_button, confirm
from backend.services.official_knowledge_service import OfficialKnowledgeService, FIELDS


class OfficialKnowledgeDialog(GlassDialog):
    def __init__(self,parent,user_id):
        super().__init__(parent,"Official Scheme Knowledge","Import curated drafts. Check all facts and both languages against official sources before publication.",930)
        self.resize(930,680)
        self.user_id = user_id
        self.service = OfficialKnowledgeService()
        bar = QHBoxLayout()
        seed = glass_button("Import researched drafts")
        seed.clicked.connect(self._import)
        bar.addWidget(seed)
        self.combo = QComboBox()
        self.combo.currentIndexChanged.connect(self._load)
        bar.addWidget(self.combo,1)
        self.body.addLayout(bar)
        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.body.addWidget(self.details,1)
        self.checked = QCheckBox("I checked the official sources, active status, exclusions, and both language versions.")
        self.checked.stateChanged.connect(self._buttons)
        self.body.addWidget(self.checked)
        row = QHBoxLayout()
        self.status = QLabel("")
        self.status.setWordWrap(True)
        row.addWidget(self.status,1)
        self.withdraw = glass_button("Reject / Withdraw","red")
        self.withdraw.clicked.connect(lambda: self._decide(False))
        row.addWidget(self.withdraw)
        self.publish = glass_button("Publish verified version","green")
        self.publish.clicked.connect(lambda: self._decide(True))
        row.addWidget(self.publish)
        self.body.addLayout(row)
        self.version = None
        self._refresh()

    def _error(self,exc):
        QMessageBox.warning(self,"Knowledge base",str(exc))

    def _import(self):
        try:
            count = self.service.import_drafts(self.user_id)
            self._refresh()
            QMessageBox.information(self,"Draft import",f"{count} new drafts imported. Existing revisions were not overwritten. Nothing has been published.")
        except Exception as exc:
            self._error(exc)

    def _refresh(self):
        self.combo.blockSignals(True)
        self.combo.clear()
        try:
            for v in self.service.list_versions(self.user_id):
                self.combo.addItem(f"{v['name']} — {v['status']}",v["id"])
        except Exception as exc:
            self._error(exc)
        finally:
            self.combo.blockSignals(False)
        self._load()

    def _load(self,*args):
        self.version = None
        self.checked.setChecked(False)
        self.details.clear()
        try:
            vid = self.combo.currentData()
            if vid is None:
                self.details.setPlainText("No official drafts yet. Use Import researched drafts.")
                return
            v,te,ev = self.service.details(self.user_id,vid)
            self.version = v
            lines = [v["name"],str((te or {}).get("name","")),v["jurisdiction"],"Main source: "+v["source_url"],
                     "Status: "+v["status"],"Review due: "+str(v["review_due_at"] or "Not published"),""]
            for f in FIELDS:
                lines += [f.replace("_"," ").upper(),"English: "+str(v[f]),"Telugu: "+str((te or {}).get(f,"Missing"))]
                for e in ev:
                    if e["field_name"] == f:
                        lines += ["Source: "+e["evidence_url"],"Evidence note (paraphrase): "+e["evidence_excerpt"],"Checked: "+str(e["checked_at"])]
                lines.append("")
            self.details.setPlainText("\n".join(lines))
        except Exception as exc:
            self._error(exc)
        finally:
            self._buttons()

    def _buttons(self,*args):
        status = (self.version or {}).get("status","")
        self.publish.setEnabled(status == "draft" and self.checked.isChecked())
        self.withdraw.setEnabled(status in ("draft","published"))
        self.status.setText("Review expires after 30 days." if status == "draft" else status.capitalize())

    def _decide(self,publish):
        if not self.version:
            return
        action = "Publish" if publish else "Withdraw"
        if not confirm(self,action+" revision","Confirmed facts will be available to villagers for up to 30 days." if publish else "Remove this revision from citizen answers? Its history will remain.",action,"green" if publish else "red"):
            return
        try:
            self.service.decide(self.user_id,self.version["id"],publish,self.checked.isChecked())
            self._refresh()
        except Exception as exc:
            self._error(exc)
