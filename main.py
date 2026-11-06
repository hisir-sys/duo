import sys
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import *
import core

STYLE = """
* { font-family:'Inter','Segoe UI','Noto Sans',sans-serif; font-size:13px; color:#1f2430; }
QMainWindow, QWidget#root { background:#080d17; color:#e8eef8; }
QFrame#card { background:#101827; border:1px solid #243247; border-radius:14px; }
QTextBrowser, QPlainTextEdit, QTableWidget, QListWidget, QComboBox, QLineEdit {
  background:#0b1220; color:#e8eef8; border:1px solid #29384f; border-radius:10px; padding:7px; selection-background-color:#24456b; }
QListWidget { border:none; } QListWidget::item { padding:9px; border-radius:8px; }
QListWidget::item:selected { background:#1f2430; color:#fff; }
QHeaderView::section { background:#172235; border:none; padding:7px; color:#9fb0c8; }
QPushButton { background:#172235; color:#e8eef8; border:1px solid #30425d; border-radius:10px; padding:8px 14px; }
QPushButton:hover { background:#20314a; border-color:#4d709a; }
QPushButton#primary { background:#2563eb; color:#fff; border:none; font-weight:600; }
QPushButton#primary:hover { background:#3478ff; }
QLabel { color:#e8eef8; } QLabel#logo { font-size:17px; font-weight:700; } QLabel#muted { color:#8ea1bc; }
"""
LABEL = {"claude": "Claude", "chatgpt": "ChatGPT"}


class Worker(QThread):
    ok, err, prog, chunk = Signal(object), Signal(str), Signal(str), Signal(str)

    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def run(self):
        try:
            self.ok.emit(self.fn(self.prog.emit, self.chunk.emit))
        except Exception as e:
            self.err.emit(str(e))


def card():
    f = QFrame()
    f.setObjectName("card")
    return f


class Win(QMainWindow):
    def __init__(s):
        super().__init__()
        s.setWindowTitle("DuoAI")
        s.resize(1360, 840)
        s.cfg, s.proj, s.atts, s.rec, s.w, s.dirty, s.loading = core.get_cfg(), None, [], None, None, False, False

        # header: logo, per-AI status + model switcher + sign in/out
        hd = card()
        hl = QHBoxLayout(hd)
        logo = QLabel("DUO · AI")
        logo.setObjectName("logo")
        hl.addWidget(logo)
        hl.addStretch()
        s.pv = {}
        for p in ("claude", "chatgpt"):
            st, mc, bt = QLabel(), QComboBox(), QPushButton()
            mc.setEditable(True)
            mc.setMinimumWidth(200)
            mc.addItems(core.MODELS[p])
            mc.setCurrentText(s.cfg[core.MK[p]])
            mc.currentTextChanged.connect(lambda t, p=p: s.set_model(p, t))
            bt.clicked.connect(lambda _, p=p: s.toggle_login(p))
            s.pv[p] = (st, mc, bt)
            for w in (st, mc, bt):
                hl.addWidget(w)
            hl.addSpacing(14)
        s.sync_login()

        # sidebar
        s.plist = QListWidget()
        s.plist.itemClicked.connect(s.open_item)
        side = card()
        side.setFixedWidth(220)
        sl = QVBoxLayout(side)
        nb = QPushButton("+ New project")
        nb.clicked.connect(s.new)
        sl.addWidget(nb)
        sl.addWidget(s.plist)

        # centre
        s.view = QTextBrowser()
        s.view.setOpenExternalLinks(True)
        s.table = QTableWidget(0, 3)
        s.table.setHorizontalHeaderLabels(["Task", "Assigned to", "Instructions"])
        s.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        s.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        s.table.setColumnWidth(1, 130)
        s.table.setMaximumHeight(170)
        s.prompt = QPlainTextEdit()
        s.prompt.setPlaceholderText("Describe what you want built. Both AIs share the work and the memory...")
        s.prompt.setFixedHeight(84)
        s.review, s.think, s.code = QCheckBox("Pause to review plan"), QCheckBox("Claude thinking"), QCheckBox("Coding mode")
        s.review.setChecked(True)
        s.code.setChecked(s.cfg["coding"])
        s.code.toggled.connect(lambda v: (s.cfg.update(coding=v), core.set_cfg(s.cfg)))
        s.lead = QComboBox()
        s.lead.addItems(["claude", "chatgpt"])
        s.lead.setCurrentText(s.cfg["lead"])
        s.lead.currentTextChanged.connect(lambda v: (s.cfg.update(lead=v), core.set_cfg(s.cfg)))
        s.attlbl, s.status = QLabel(""), QLabel("")
        s.attlbl.setObjectName("muted")
        s.status.setObjectName("muted")
        opts = QHBoxLayout()
        for w in (s.code, s.think, s.review, QLabel("Lead:"), s.lead, s.attlbl):
            opts.addWidget(w)
        opts.addStretch()
        opts.addWidget(s.status)
        s.mic = QPushButton("Mic")
        s.mic.clicked.connect(s.toggle_mic)
        acts = QHBoxLayout()
        for text, fn, prim in (("Improve prompt", s.do_improve, 0), ("Attach", s.attach, 0), (None, None, 0),
                               ("+ Task", lambda: s.add_row(), 0), ("- Task", s.del_row, 0),
                               ("Plan with lead AI", s.do_plan, 0), ("Run tasks", s.do_run, 1), ("Export code", s.export, 0)):
            if text is None:
                acts.addWidget(s.mic)
                continue
            b = QPushButton(text)
            b.clicked.connect(fn)
            b.setObjectName("primary" if prim else "")
            acts.addWidget(b)
        centre = QWidget()
        cl = QVBoxLayout(centre)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.addWidget(s.view, 1)
        cl.addWidget(s.table)
        cl.addWidget(s.prompt)
        cl.addLayout(opts)
        cl.addLayout(acts)

        # live-synced global memory.md panel
        mp = card()
        mp.setFixedWidth(290)
        ml = QVBoxLayout(mp)
        ml.addWidget(QLabel("🌐  memory.md  (global, live sync)"))
        s.memtxt = QPlainTextEdit(core.get_mem())
        s.memtxt.textChanged.connect(lambda: setattr(s, "dirty", s.dirty or not s.loading))
        ml.addWidget(s.memtxt)
        s.mem_save = QPushButton("Save memory")
        s.mem_save.clicked.connect(s.save_memory)
        ml.addWidget(s.mem_save)
        s.memtimer = QTimer(s)
        s.memtimer.timeout.connect(s.sync_mem)
        s.memtimer.start(1500)

        root = QWidget()
        root.setObjectName("root")
        rl = QVBoxLayout(root)
        body = QHBoxLayout()
        for w, f in ((side, 0), (centre, 1), (mp, 0)):
            body.addWidget(w, f)
        rl.addWidget(hd)
        rl.addLayout(body, 1)
        s.setCentralWidget(root)
        s.refresh()

    # ---- login / models / memory
    def sync_login(s):
        for p, (st, mc, bt) in s.pv.items():
            on = bool(core.get_key(p))
            st.setText(f"● {LABEL[p]}")
            st.setStyleSheet(f"font-weight:600;color:{'#16a34a' if on else '#9aa3b5'};")
            bt.setText("Sign out" if on else "Sign in")

    def toggle_login(s, p):
        st, mc, bt = s.pv[p]
        if core.get_key(p):
            core.del_key(p)
        else:
            key, ok = QInputDialog.getText(s, "Sign in", f"{LABEL[p]} API key:", QLineEdit.Password)
            if not ok or not key.strip():
                return
            try:
                core.set_key(p, key.strip())
                ids, cur = core.list_models(p, strict=True), mc.currentText()
                mc.blockSignals(True)
                mc.clear()
                mc.addItems(ids)
                mc.setCurrentText(cur)
                mc.blockSignals(False)
            except Exception as e:
                core.del_key(p)
                mc.blockSignals(False)
                QMessageBox.warning(s, "Sign in failed", f"Could not securely sign in: {e}")
        s.sync_login()

    def set_model(s, p, t):
        if t.strip():
            s.cfg[core.MK[p]] = t.strip()
            core.set_cfg(s.cfg)

    def save_memory(s):
        try:
            core.set_mem(s.memtxt.toPlainText())
            s.dirty = False
            s.status.setText("Memory saved.")
        except Exception as e:
            QMessageBox.warning(s, "Memory", str(e))

    def sync_mem(s):
        disk, cur = core.get_mem(), s.memtxt.toPlainText()
        if s.dirty:
            if cur != disk:
                core.set_mem(cur)
            s.dirty = False
        elif disk != cur:
            s.loading = True
            s.memtxt.setPlainText(disk)
            s.loading = False

    # ---- projects
    def refresh(s):
        s.plist.clear()
        for p in core.list_projects():
            it = QListWidgetItem(p["name"])
            it.setData(Qt.UserRole, p["id"])
            s.plist.addItem(it)

    def new(s):
        name, ok = QInputDialog.getText(s, "New project", "Project name:")
        if ok and name.strip():
            s.proj, s.atts = core.new_project(name.strip()), []
            s.show_proj()
            s.refresh()

    def open_item(s, it):
        s.proj = next(p for p in core.list_projects() if p["id"] == it.data(Qt.UserRole))
        s.atts = []
        s.show_proj()

    def show_proj(s):
        s.prompt.setPlainText(s.proj.get("prompt", ""))
        s.table.setRowCount(0)
        for t in s.proj["tasks"]:
            s.add_row(t)
        s.view.setMarkdown("\n\n---\n\n".join(s.proj["log"]) or f"# {s.proj['name']}\n\nNo results yet.")
        s.attlbl.setText("")

    def ensure(s):
        if not s.proj:
            s.proj = core.new_project(s.prompt.toPlainText().strip()[:40] or "Untitled")
            s.refresh()
        s.proj["prompt"] = s.prompt.toPlainText().strip()
        s.proj["tasks"] = s.read_table()
        core.save_project(s.proj)

    # ---- task table
    def add_row(s, t=None):
        t = t or {"title": "", "assignee": "claude", "instructions": ""}
        r = s.table.rowCount()
        s.table.insertRow(r)
        s.table.setItem(r, 0, QTableWidgetItem(t["title"]))
        c = QComboBox()
        c.addItems(["claude", "chatgpt"])
        c.setCurrentText(t["assignee"])
        s.table.setCellWidget(r, 1, c)
        s.table.setItem(r, 2, QTableWidgetItem(t["instructions"]))

    def del_row(s):
        if s.table.currentRow() >= 0:
            s.table.removeRow(s.table.currentRow())

    def read_table(s):
        out = []
        for r in range(s.table.rowCount()):
            g = lambda c: s.table.item(r, c).text() if s.table.item(r, c) else ""
            if g(0).strip():
                out.append({"title": g(0), "assignee": s.table.cellWidget(r, 1).currentText(),
                            "instructions": g(2), "output": ""})
        return out

    # ---- actions
    def busy(s, fn, done):
        if s.w and s.w.isRunning():
            return
        s.w = Worker(fn)
        s.plist.setEnabled(False)
        s.prompt.setEnabled(False)
        s.table.setEnabled(False)
        s.w.finished.connect(lambda: (s.plist.setEnabled(True), s.prompt.setEnabled(True), s.table.setEnabled(True)))
        s.w.prog.connect(s.status.setText)
        s.w.chunk.connect(s.stream)
        s.w.ok.connect(done)
        s.w.err.connect(lambda e: (s.status.setText(""), QMessageBox.warning(s, "Error", e)))
        s.w.start()

    def stream(s, t):
        s.view.moveCursor(QTextCursor.End)
        s.view.insertPlainText(t)

    def do_improve(s):
        if s.prompt.toPlainText().strip():
            s.status.setText("Improving prompt...")
            prompt, cfg = s.prompt.toPlainText(), dict(s.cfg)
            s.busy(lambda cb, ch: core.improve(prompt, cfg), s.improved)

    def improved(s, t):
        s.prompt.setPlainText(t)
        s.status.setText("Prompt improved - edit if you like.")

    def do_plan(s):
        if s.prompt.toPlainText().strip():
            s.ensure()
            s.status.setText("Planning...")
            goal, atts, cfg = s.proj["prompt"], list(s.atts), dict(s.cfg)
            s.busy(lambda cb, ch: core.plan(goal, atts, cfg), s.planned)

    def planned(s, tasks):
        s.table.setRowCount(0)
        for t in tasks:
            s.add_row(t)
        s.status.setText("Plan ready - edit it, then Run tasks." if s.review.isChecked() else "")
        if not s.review.isChecked():
            QTimer.singleShot(100, s.do_run)

    def do_run(s):
        s.ensure()
        if not s.proj["tasks"]:
            QMessageBox.information(s, "No tasks", "Add tasks or use 'Plan with lead AI'.")
            return
        project = s.proj
        goal, tasks = project["prompt"], [dict(t) for t in project["tasks"]]
        atts, cfg, thinking = list(s.atts), dict(s.cfg), s.think.isChecked()

        def job(cb, ch):
            results = core.run_tasks(goal, tasks, atts, cfg, thinking, cb, ch)
            cb("Preparing memory suggestions for your approval...")
            try:
                facts = core.suggest_memory(goal, results, cfg)
            except Exception:
                facts = []
            return results, facts
        s.view.moveCursor(QTextCursor.End)
        s.busy(job, lambda result: s.ran(project, result))

    def ran(s, project, result):
        tasks, facts = result
        project["log"].append(f"## Request\n{project['prompt']}\n\n" + "\n\n".join(
            f"### {t['title']} - {t['assignee']}\n\n{t['output']}" for t in tasks))
        project["tasks"] = tasks
        core.save_project(project)
        if s.proj and s.proj["id"] == project["id"]:
            s.view.setMarkdown("\n\n---\n\n".join(project["log"]))
        if facts:
            preview = "\n".join("• " + fact for fact in facts)
            choice = QMessageBox.question(s, "Approve memory updates?",
                "DuoAI suggests adding these facts to shared memory:\n\n" + preview +
                "\n\nAdd these facts? You can edit memory in the right panel.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if choice == QMessageBox.Yes:
                core.add_mem(facts)
                s.memtxt.setPlainText(core.get_mem())
        s.status.setText("Tasks complete. Memory suggestions require your approval.")

    def export(s):
        if s.proj:
            try:
                files = core.export_code(s.proj)
                QMessageBox.information(s, "Export code", "\n".join(files) if files else
                                        "No files found. (Code blocks need a path=... label; Coding mode adds it.)")
            except Exception as e:
                QMessageBox.warning(s, "Export failed", str(e))

    def attach(s):
        files, _ = QFileDialog.getOpenFileNames(s, "Attach images, PDFs, Word or code files")
        if not files:
            return
        try:
            loaded = [core.load_att(path) for path in files]
            s.atts += loaded
            s.attlbl.setText(f"{len(s.atts)} attached")
        except Exception as e:
            QMessageBox.warning(s, "Attachment failed", str(e))

    def toggle_mic(s):
        try:
            if s.rec is None:
                s.rec = core.Recorder()
                s.rec.start()
                s.mic.setText("Stop")
            else:
                path, s.rec = s.rec.stop(), None
                s.mic.setText("Mic")
                s.status.setText("Transcribing...")
                s.busy(lambda cb, ch: core.transcribe(path), lambda t: (s.prompt.appendPlainText(t), s.status.setText("")))
        except Exception as e:
            s.rec = None
            s.mic.setText("Mic")
            QMessageBox.warning(s, "Voice", f"{e}\n\nVoice needs sounddevice and a signed-in ChatGPT key.")


if __name__ == "__main__":
    smoke_test = "--smoke-test" in sys.argv
    app = QApplication([])
    app.setStyleSheet(STYLE)
    w = Win()
    if smoke_test:
        w.close()
        sys.exit(0)
    w.show()
    sys.exit(app.exec())
