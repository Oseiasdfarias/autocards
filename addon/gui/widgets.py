"""Editor dos campos do prompt (spec §7.2): liga/desliga, arrastar para reordenar, campo próprio."""
from __future__ import annotations

import uuid

from aqt.qt import (QAbstractItemView, QHBoxLayout, QInputDialog, QListWidget, QListWidgetItem,
                    QPlainTextEdit, QPushButton, Qt, QVBoxLayout, QWidget, pyqtSignal)

from ..core.i18n import tr
from ..core.model import PromptField

ROLE = Qt.ItemDataRole.UserRole


class PromptFieldsEditor(QWidget):
    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._texts: dict[str, str] = {}
        self._loading = False
        self.list = QListWidget()
        self.list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.list.currentItemChanged.connect(self._on_select)
        self.list.itemChanged.connect(lambda _i: self._emit())
        self.list.model().rowsMoved.connect(lambda *_: self._emit())
        self.text = QPlainTextEdit()
        self.text.textChanged.connect(self._on_text)
        add = QPushButton(tr("gen.add_field"))
        add.clicked.connect(self._ask_new_field)
        left = QVBoxLayout()
        left.addWidget(self.list)
        left.addWidget(add)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.addLayout(left, 1)
        row.addWidget(self.text, 2)

    def _emit(self) -> None:
        if not self._loading:
            self.changed.emit()

    def set_fields(self, fields: list[PromptField]) -> None:
        self._loading = True
        self.list.clear()
        self._texts = {}
        for f in fields:
            self._append(f)
        self._loading = False
        if fields:
            self.list.setCurrentRow(0)
        else:
            self.text.setPlainText("")

    def _append(self, f: PromptField) -> None:
        item = QListWidgetItem(f.title)
        item.setData(ROLE, f.key)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsDragEnabled)
        item.setCheckState(Qt.CheckState.Checked if f.enabled else Qt.CheckState.Unchecked)
        self._texts[f.key] = f.text
        self.list.addItem(item)

    def fields(self) -> list[PromptField]:
        out = []
        for i in range(self.list.count()):
            it = self.list.item(i)
            key = it.data(ROLE)
            out.append(PromptField(key, it.text(), self._texts.get(key, ""),
                                   it.checkState() == Qt.CheckState.Checked))
        return out

    def _item(self, key: str) -> QListWidgetItem | None:
        for i in range(self.list.count()):
            if self.list.item(i).data(ROLE) == key:
                return self.list.item(i)
        return None

    def add_field(self, title: str, text: str = "") -> None:
        self._append(PromptField("custom_" + uuid.uuid4().hex[:8], title, text))
        self.list.setCurrentRow(self.list.count() - 1)
        self._emit()

    def set_enabled(self, key: str, enabled: bool) -> None:
        it = self._item(key)
        if it:
            it.setCheckState(Qt.CheckState.Checked if enabled else Qt.CheckState.Unchecked)

    def move(self, key: str, row: int) -> None:
        it = self._item(key)
        if it is None:
            return
        self.list.insertItem(row, self.list.takeItem(self.list.row(it)))
        self._emit()

    def _ask_new_field(self) -> None:
        title, ok = QInputDialog.getText(self, tr("gen.add_field"), tr("gen.field_name"))
        if ok and title.strip():
            self.add_field(title.strip())

    def _on_select(self, cur, _prev) -> None:
        self._loading = True
        self.text.setPlainText(self._texts.get(cur.data(ROLE), "") if cur else "")
        self.text.setEnabled(cur is not None)
        self._loading = False

    def _on_text(self) -> None:
        cur = self.list.currentItem()
        if cur is not None and not self._loading:
            self._texts[cur.data(ROLE)] = self.text.toPlainText()
            self._emit()
