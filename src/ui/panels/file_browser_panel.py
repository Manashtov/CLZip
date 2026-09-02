import os
import sys
import shutil
import subprocess
import datetime
from pathlib import Path
from PyQt6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QMenu, QMessageBox, 
    QInputDialog, QLineEdit, QDialog, QVBoxLayout, QLabel, QPushButton, QApplication
)
from PyQt6.QtCore import pyqtSignal, Qt, QPoint, QSettings, QMimeData, QUrl
from PyQt6.QtGui import QCursor, QDragEnterEvent, QDropEvent, QKeyEvent, QKeySequence
import qtawesome as qta


from src.core.compressor import ZstdEngine
from src.i18n.translator import tr
from src.ui.dialogs.properties_dialog import PropertiesDialog
from src.ui.dialogs.checksum_dialog import ChecksumDialog
from src.ui.dialogs.settings_dialog import DEFAULT_SHORTCUTS
from src.utils.helpers import format_bytes, move_to_trash
from src.ui.themes import ThemeManager


ARCHIVE_EXTS = {
    ".zip", ".7z", ".rar", ".zst", ".tzst", 
    ".tar", ".gz", ".tgz", ".bz2", ".tbz2", ".xz", ".txz", 
    ".part001", ".001"
}

class FileBrowserPanel(QTreeWidget):
    open_directory_requested = pyqtSignal(Path)
    compress_requested = pyqtSignal()
    extract_requested = pyqtSignal()
    items_dropped = pyqtSignal(list)
    password_changed = pyqtSignal(str)
    recrypt_requested = pyqtSignal(Path, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_directory: Path = Path.home()
        self.settings = QSettings("clzip", "FileBrowser")
        self.shortcut_settings = QSettings("clzip", "Shortcuts")
        self._clipboard_paths: list[Path] = []
        
        self.setAcceptDrops(True)
        self.setRootIsDecorated(False)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.itemDoubleClicked.connect(self._on_double_click)
        self.header().sectionResized.connect(self._save_column_widths)
        
        self.retranslate_ui()
        self._restore_column_widths()

    def get_shortcut(self, action_key: str) -> QKeySequence:
        val = self.shortcut_settings.value(action_key, DEFAULT_SHORTCUTS.get(action_key, ""))
        return QKeySequence(val)

    def retranslate_ui(self):
        state = self.header().saveState()
        self.setHeaderLabels([
            tr("col_name"),
            tr("col_size"),
            tr("col_type"),
            tr("col_modified")
        ])
        self.header().restoreState(state)

    def _save_column_widths(self, logicalIndex, oldSize, newSize):
        self.settings.setValue("header_state", self.header().saveState())

    def _restore_column_widths(self):
        state = self.settings.value("header_state")
        if state:
            self.header().restoreState(state)
        else:
            self.header().resizeSection(0, 220)
            self.header().resizeSection(1, 90)
            self.header().resizeSection(2, 110)
            self.header().resizeSection(3, 130)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        paths = [Path(url.toLocalFile()) for url in event.mimeData().urls() if url.toLocalFile()]
        if paths:
            self.items_dropped.emit(paths)

    def keyPressEvent(self, event: QKeyEvent):
        key_comb = QKeySequence(event.keyCombination().toCombined())

        if key_comb == self.get_shortcut("properties"):
            self._show_properties()
            event.accept()
            return
        elif key_comb == self.get_shortcut("copy"):
            self.copy_selected()
            event.accept()
            return
        elif key_comb == self.get_shortcut("paste"):
            self.paste_items()
            event.accept()
            return
        elif key_comb == self.get_shortcut("extract"):
            self.extract_requested.emit()
            event.accept()
            return
        elif key_comb == self.get_shortcut("select_all"):
            self.selectAll()
            event.accept()
            return
        elif key_comb == self.get_shortcut("delete"):
            self._delete_selected()
            event.accept()
            return
        elif key_comb == self.get_shortcut("compress"):
            self.compress_requested.emit()
            event.accept()
            return
        elif key_comb == self.get_shortcut("set_password"):
            self._change_password_dialog()
            event.accept()
            return

        super().keyPressEvent(event)

    def refresh(self):
        self.populate(self.current_directory)

    def populate(self, directory: Path):
        self.current_directory = Path(directory).resolve()
        self.clear()
        
        try:
            entries = list(self.current_directory.iterdir())
        except Exception as e:
            QMessageBox.warning(self, "Error", tr("err_access_folder", error=str(e)))
            return

        entries.sort(key=lambda x: (not x.is_dir(), x.name.lower()))

        for entry in entries:
            is_dir = entry.is_dir()
            ext = entry.suffix.lower()

            if is_dir:
                icon = qta.icon("fa5s.folder", color="#f9e2af")
                type_str = "Folder" if tr("col_name") == "Name" else "Carpeta"
                size_str = ""
            elif ext in ARCHIVE_EXTS:
                is_encrypted = ZstdEngine.is_archive_encrypted(entry)

                if is_encrypted:
                    icon = qta.icon("fa5s.lock", color="#e5a93b")
                    type_str = "ZIP (Password)" if tr("col_name") == "Name" else "ZIP (Protegido)"
                else:
                    # Leer la paleta activa configurada en la aplicación
                    mw_settings = QSettings("clzip", "MainWindow")
                    pal_name = mw_settings.value("palette", "Verde", type=str)
                    pri_color = ThemeManager.get_primary_color(pal_name)
                    
                    icon = qta.icon("fa5s.file-archive", color=pri_color)
                    type_str = f"{ext.upper()[1:]} Archive"

                try:
                    size_str = format_bytes(entry.stat().st_size)
                except OSError:
                    size_str = "N/A"
            else:
                icon = qta.icon("fa5s.file", color="#a6adc8")
                type_str = ext[1:].upper() if ext else "File"
                try:
                    size_str = format_bytes(entry.stat().st_size)
                except OSError:
                    size_str = "N/A"

            try:
                mtime = datetime.datetime.fromtimestamp(entry.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            except OSError:
                mtime = "N/A"

            item = QTreeWidgetItem([entry.name, size_str, type_str, mtime])
            item.setIcon(0, icon)
            item.setData(0, Qt.ItemDataRole.UserRole, str(entry))
            self.addTopLevelItem(item)

    def get_selected_paths(self) -> list[Path]:
        return [Path(item.data(0, Qt.ItemDataRole.UserRole)) for item in self.selectedItems()]

    def _on_double_click(self, item: QTreeWidgetItem, col: int):
        p = Path(item.data(0, Qt.ItemDataRole.UserRole))
        if p.is_dir():
            self.open_directory_requested.emit(p)
        elif p.suffix.lower() in ARCHIVE_EXTS:
            self.extract_requested.emit()

    def copy_selected(self):
        sel = self.get_selected_paths()
        if not sel:
            return
        self._clipboard_paths = sel
        clipboard = QApplication.clipboard()
        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile(str(p)) for p in sel])
        clipboard.setMimeData(mime)

    def paste_items(self):
        clipboard = QApplication.clipboard()
        mime = clipboard.mimeData()
        paths_to_paste = []

        if mime and mime.hasUrls():
            paths_to_paste = [Path(u.toLocalFile()) for u in mime.urls() if u.toLocalFile()]
        elif self._clipboard_paths:
            paths_to_paste = self._clipboard_paths

        if not paths_to_paste:
            return

        for src in paths_to_paste:
            if not src.exists():
                continue
            dest = self.current_directory / src.name
            if dest.exists():
                stem = src.stem
                ext = src.suffix
                counter = 1
                while dest.exists():
                    dest = self.current_directory / f"{stem}_copy{counter}{ext}"
                    counter += 1

            try:
                if src.is_dir():
                    shutil.copytree(src, dest)
                else:
                    shutil.copy2(src, dest)
            except Exception as e:
                QMessageBox.warning(self, "Error", tr("err_paste", name=src.name, error=str(e)))

        self.refresh()

    def _show_properties(self):
        sel = self.get_selected_paths()
        target = sel[0] if sel else self.current_directory
        PropertiesDialog(target, self).exec()

    def _show_context_menu(self, pos: QPoint):
        menu = QMenu(self)
        sel = self.get_selected_paths()

        sh_comp = self.get_shortcut("compress").toString()
        sh_extr = self.get_shortcut("extract").toString()
        sh_copy = self.get_shortcut("copy").toString()
        sh_paste = self.get_shortcut("paste").toString()
        sh_selall = self.get_shortcut("select_all").toString()
        sh_del = self.get_shortcut("delete").toString()
        sh_prop = self.get_shortcut("properties").toString()
        sh_pwd = self.get_shortcut("set_password").toString()

        act_comp = menu.addAction(qta.icon("fa5s.file-archive", color="#52b774"), f"{tr('ctx_compress')}\t{sh_comp}")
        act_comp.triggered.connect(self.compress_requested.emit)

        if sel and any(p.suffix.lower() in ARCHIVE_EXTS for p in sel):
            act_extract = menu.addAction(qta.icon("fa5s.box-open", color="#e5a93b"), f"{tr('ctx_extract')}\t{sh_extr}")
            act_extract.triggered.connect(self.extract_requested.emit)

        menu.addSeparator()

        act_copy = menu.addAction(qta.icon("fa5s.copy", color="#89b4fa"), f"{tr('ctx_copy')}\t{sh_copy}")
        act_copy.triggered.connect(self.copy_selected)
        if not sel:
            act_copy.setEnabled(False)

        act_paste = menu.addAction(qta.icon("fa5s.paste", color="#89b4fa"), f"{tr('ctx_paste')}\t{sh_paste}")
        act_paste.triggered.connect(self.paste_items)

        act_select_all = menu.addAction(qta.icon("fa5s.check-double", color="#89b4fa"), f"{tr('ctx_select_all')}\t{sh_selall}")
        act_select_all.triggered.connect(self.selectAll)

        menu.addSeparator()

        menu.addAction(qta.icon("fa5s.key", color="#f9e2af"), f"{tr('ctx_password')}\t{sh_pwd}").triggered.connect(self._change_password_dialog)

        if sel and sel[0].is_file():
            menu.addAction(qta.icon("fa5s.check-circle", color="#89b4fa"), tr("ctx_checksum")).triggered.connect(
                lambda: ChecksumDialog(sel[0], self).exec()
            )

        menu.addSeparator()
        menu.addAction(qta.icon("fa5s.terminal"), tr("ctx_open_terminal")).triggered.connect(self._open_terminal)
        menu.addAction(qta.icon("fa5s.folder-open"), tr("ctx_open_folder")).triggered.connect(self._open_in_os)

        menu.addSeparator()

        act_del = menu.addAction(qta.icon("fa5s.trash-alt", color="#f38ba8"), f"{tr('ctx_delete')}\t{sh_del}")
        act_del.triggered.connect(self._delete_selected)
        if not sel:
            act_del.setEnabled(False)

        act_prop = menu.addAction(qta.icon("fa5s.info-circle"), f"{tr('ctx_properties')}\t{sh_prop}")
        act_prop.triggered.connect(self._show_properties)

        menu.exec(QCursor.pos())

    def _change_password_dialog(self):
        sel = self.get_selected_paths()
        target_archive = sel[0] if (sel and sel[0].suffix.lower() in ARCHIVE_EXTS) else None

        title = tr("pwd_protect_title", name=target_archive.name) if target_archive else tr("pwd_set_title")
        prompt = (
            tr("pwd_protect_prompt", name=target_archive.name)
            if target_archive
            else tr("pwd_set_prompt")
        )

        pwd, ok = QInputDialog.getText(
            self, 
            title, 
            prompt, 
            QLineEdit.EchoMode.Password
        )
        if ok:
            pwd_clean = pwd.strip()
            if target_archive:
                current_pwd = ""
                if ZstdEngine.is_archive_encrypted(target_archive):
                    curr, curr_ok = QInputDialog.getText(
                        self, 
                        tr("pwd_current_title"), 
                        tr("pwd_current_prompt"), 
                        QLineEdit.EchoMode.Password
                    )
                    if not curr_ok:
                        return
                    current_pwd = curr.strip()

                self.recrypt_requested.emit(target_archive, pwd_clean, current_pwd)
            else:
                self.password_changed.emit(pwd_clean)
                dlg = QDialog(self)
                dlg.setWindowTitle(tr("pwd_set_title"))
                dlg.setFixedSize(280, 100)
                v = QVBoxLayout(dlg)
                msg = tr("pwd_active") if pwd_clean else tr("pwd_cleared")
                v.addWidget(QLabel(msg))
                btn = QPushButton("OK")
                btn.clicked.connect(dlg.accept)
                v.addWidget(btn)
                dlg.exec()

    def _open_terminal(self):
        cwd = str(self.current_directory)
        if sys.platform == "win32":
            subprocess.Popen(["cmd.exe", "/K", f"cd /d {cwd}"])
        else:
            subprocess.Popen(["x-terminal-emulator"], cwd=cwd)

    def _open_in_os(self):
        cwd = str(self.current_directory)
        if sys.platform == "win32":
            os.startfile(cwd)
        else:
            subprocess.Popen(["xdg-open", cwd])

    def _delete_selected(self):
        """Mueve los elementos seleccionados a la Papelera de Reciclaje de forma segura."""
        sel = self.get_selected_paths()
        if not sel:
            return
        if QMessageBox.question(self, tr("ctx_delete"), tr("ctx_delete_confirm", count=len(sel))) == QMessageBox.StandardButton.Yes:
            for p in sel:
                try:
                    success = move_to_trash(p)
                    if not success:
                        QMessageBox.warning(self, "Error", tr("ctx_delete_error", name=p.name, error="No se pudo mover a la papelera"))
                except Exception as e:
                    QMessageBox.warning(self, "Error", tr("ctx_delete_error", name=p.name, error=str(e)))
            self.refresh()