# src/ui/panels/file_browser_panel.py
import os
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QMenu, QMessageBox, 
    QHeaderView, QFileDialog
)
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt, QSettings, QFileInfo, pyqtSignal
import qtawesome as qta

from src.i18n.translator import tr
from src.core.compressor import ZstdEngine
from src.ui.themes import ThemeManager
from src.ui.dialogs.properties_dialog import PropertiesDialog
from src.utils.helpers import move_to_trash, format_bytes


class FileBrowserPanel(QWidget):
    open_directory_requested = pyqtSignal(Path)
    compress_requested = pyqtSignal(list)
    extract_to_requested = pyqtSignal(str, str)
    password_requested = pyqtSignal(str)
    remove_password_requested = pyqtSignal(str)
    path_changed = pyqtSignal(str)
    file_selected = pyqtSignal(str)

    ARCHIVE_EXTS = {'.zip', '.tar', '.zst', '.tar.zst', '.7z', '.rar', '.gz', '.bz2', '.xz'}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_directory = Path.home()
        self.history = []
        self.history_index = -1
        self.preview_archive_path: Path | None = None
        self.settings = QSettings("clzip", "FileBrowser")
        self.shortcut_settings = QSettings("clzip", "Shortcuts")
        
        self._setup_ui()
        self._setup_persistent_actions()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.tree = QTreeWidget(self)
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.setMouseTracking(True)
        
        self.tree.setHeaderLabels([tr("col_name"), tr("col_size"), tr("col_type"), tr("col_modified")])
        
        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.sectionResized.connect(self._save_column_widths)
        
        self.tree.itemClicked.connect(self._on_item_clicked)
        self.tree.doubleClicked.connect(self._on_double_clicked)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        
        main_layout.addWidget(self.tree)
        self._restore_column_widths()

    def _setup_persistent_actions(self):
        self.act_extract = QAction(self)
        self.act_extract.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.act_extract.triggered.connect(self._trigger_extract_action)
        self.tree.addAction(self.act_extract)

        self.act_compress = QAction(self)
        self.act_compress.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.act_compress.triggered.connect(self._trigger_compress_action)
        self.tree.addAction(self.act_compress)

        self.act_set_password = QAction(self)
        self.act_set_password.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.act_set_password.triggered.connect(self._trigger_password_action)
        self.tree.addAction(self.act_set_password)

        self.act_delete = QAction(self)
        self.act_delete.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.act_delete.triggered.connect(self._trigger_delete_action)
        self.tree.addAction(self.act_delete)

        self.act_rename = QAction(self)
        self.act_rename.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.act_rename.triggered.connect(self._trigger_rename_action)
        self.tree.addAction(self.act_rename)

        self.act_properties = QAction(self)
        self.act_properties.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.act_properties.triggered.connect(self._trigger_properties_action)
        self.tree.addAction(self.act_properties)

        self.act_refresh = QAction(self)
        self.act_refresh.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.act_refresh.setShortcut(QKeySequence("F5"))
        self.act_refresh.triggered.connect(self.refresh)
        self.tree.addAction(self.act_refresh)

        self.update_action_shortcuts()

    def update_action_shortcuts(self):
        sh_extract = self.shortcut_settings.value("extract", "Ctrl+E")
        sh_compress = self.shortcut_settings.value("compress", "Ctrl+Shift+A")
        sh_delete = self.shortcut_settings.value("delete", "Del")
        sh_props = self.shortcut_settings.value("properties", "Alt+Return")
        sh_password = self.shortcut_settings.value("set_password", "Ctrl+P")

        self.act_extract.setShortcut(QKeySequence(sh_extract))
        self.act_compress.setShortcut(QKeySequence(sh_compress))
        self.act_set_password.setShortcut(QKeySequence(sh_password))
        self.act_delete.setShortcut(QKeySequence(sh_delete))
        self.act_rename.setShortcut(QKeySequence("F2"))
        self.act_properties.setShortcut(QKeySequence(sh_props))

    def _trigger_extract_action(self):
        selected = self.get_selected_paths()
        if selected and selected[0].lower().endswith(tuple(self.ARCHIVE_EXTS)):
            self.handle_extract_to_dialog(selected[0])
        elif self.preview_archive_path:
            self.handle_extract_to_dialog(str(self.preview_archive_path))

    def _trigger_compress_action(self):
        selected = self.get_selected_paths()
        if selected and not self.preview_archive_path:
            self.compress_requested.emit(selected)

    def _trigger_password_action(self):
        selected = self.get_selected_paths()
        if len(selected) == 1 and selected[0].lower().endswith(tuple(self.ARCHIVE_EXTS)):
            self.password_requested.emit(selected[0])

    def _trigger_delete_action(self):
        selected = self.get_selected_paths()
        if selected and not self.preview_archive_path:
            self.handle_delete(selected)

    def _trigger_rename_action(self):
        selected = self.get_selected_paths()
        if len(selected) == 1 and not self.preview_archive_path:
            self.handle_rename(selected[0])

    def _trigger_properties_action(self):
        selected = self.get_selected_paths()
        if len(selected) == 1 and not self.preview_archive_path:
            self.handle_properties(selected[0])

    def populate(self, path: Path, record_history: bool = True):
        self.preview_archive_path = None
        p = Path(path).resolve()
        if not p.exists() or not p.is_dir():
            return
            
        self.current_directory = p
        self.tree.clear()
        
        mw_settings = QSettings("clzip", "MainWindow")
        pal_name = mw_settings.value("palette", "Verde", type=str)
        pri_color = ThemeManager.get_primary_color(pal_name)

        try:
            entries = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            return

        for entry in entries:
            try:
                is_dir = entry.is_dir()
                ext = entry.suffix.lower()
                
                if is_dir:
                    icon = qta.icon("fa5s.folder", color="#f9e2af")
                    type_str = "Folder" if tr("col_name") == "Name" else "Carpeta"
                    size_str = ""
                elif ext in self.ARCHIVE_EXTS:
                    if ZstdEngine.is_archive_encrypted(entry):
                        icon = qta.icon("fa5s.lock", color="#e5a93b")
                        type_str = "ZIP (Protegido)"
                    else:
                        icon = qta.icon("fa5s.file-archive", color=pri_color)
                        type_str = "Compressed Archive File"
                    
                    sz = entry.stat().st_size
                    size_str = format_bytes(sz)
                else:
                    icon = qta.icon("fa5s.file", color="#a6adc8")
                    type_str = entry.suffix.upper()[1:] + " File" if entry.suffix else "File"
                    sz = entry.stat().st_size
                    size_str = format_bytes(sz)

                mtime = QFileInfo(str(entry)).lastModified().toString("yyyy-MM-dd HH:mm")

                item = QTreeWidgetItem([entry.name, size_str, type_str, mtime])
                item.setIcon(0, icon)
                item.setData(0, Qt.ItemDataRole.UserRole, str(entry))
                self.tree.addTopLevelItem(item)
            except Exception:
                continue

        if record_history:
            if self.history_index < len(self.history) - 1:
                self.history = self.history[:self.history_index + 1]
            self.history.append(self.current_directory)
            self.history_index = len(self.history) - 1
            
        self.path_changed.emit(str(self.current_directory))

    def preview_archive(self, archive_path: Path):
        """Muestra el contenido interno de un archivo comprimido sin descomprimirlo."""
        p = Path(archive_path).resolve()
        if not p.exists():
            return

        try:
            items = ZstdEngine.inspect_archive(p)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo previsualizar el archivo:\n{str(e)}")
            return

        self.preview_archive_path = p
        self.tree.clear()

        # Item de retroceso para volver a la carpeta superior (funciona a 1 solo clic)
        back_item = QTreeWidgetItem([".. [Volver]", "", "Carpeta", ""])
        back_item.setIcon(0, qta.icon("fa5s.arrow-left", color="#e5a93b"))
        back_item.setData(0, Qt.ItemDataRole.UserRole, "__BACK__")
        self.tree.addTopLevelItem(back_item)

        for it in items:
            name = it["name"]
            is_dir = it["is_dir"]
            size_str = "" if is_dir else format_bytes(it["size"])
            type_str = "Carpeta" if is_dir else "Fichero comprimido"
            mtime = it["mtime"]
            icon = qta.icon("fa5s.folder", color="#f9e2af") if is_dir else qta.icon("fa5s.file", color="#a6adc8")

            tree_item = QTreeWidgetItem([name, size_str, type_str, mtime])
            tree_item.setIcon(0, icon)
            tree_item.setData(0, Qt.ItemDataRole.UserRole, f"__INTERNAL__{name}")
            self.tree.addTopLevelItem(tree_item)

        self.path_changed.emit(f"📦 {p.name} (Vista previa)")

    def refresh(self):
        if self.preview_archive_path:
            self.preview_archive(self.preview_archive_path)
        else:
            self.populate(self.current_directory, record_history=False)

    def retranslate_ui(self):
        self.tree.setHeaderLabels([tr("col_name"), tr("col_size"), tr("col_type"), tr("col_modified")])

    def get_selected_paths(self) -> list:
        paths = []
        for item in self.tree.selectedItems():
            p = item.data(0, Qt.ItemDataRole.UserRole)
            if p and not p.startswith("__"):
                paths.append(p)
        return paths

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        if not item:
            return
        path_str = item.data(0, Qt.ItemDataRole.UserRole)
        if path_str == "__BACK__":
            self.populate(self.current_directory)

    def _on_double_clicked(self, index):
        item = self.tree.currentItem()
        if not item:
            return
        path_str = item.data(0, Qt.ItemDataRole.UserRole)
        if not path_str:
            return
            
        if path_str == "__BACK__":
            self.populate(self.current_directory)
            return

        if path_str.startswith("__INTERNAL__"):
            return

        path_obj = Path(path_str)
        if path_obj.is_dir():
            self.open_directory_requested.emit(path_obj)
        else:
            self.file_selected.emit(path_str)
            if path_str.lower().endswith(tuple(self.ARCHIVE_EXTS)):
                self.preview_archive(path_obj)

    def show_context_menu(self, position):
        if self.preview_archive_path:
            menu = QMenu(self)
            act_extract_all = menu.addAction(qta.icon('fa5s.folder-open', color='#2ecc71'), tr("ctx_extract"))
            act_extract_all.triggered.connect(lambda: self.handle_extract_to_dialog(str(self.preview_archive_path)))
            act_back = menu.addAction(qta.icon('fa5s.arrow-left', color='#e5a93b'), "Volver a la carpeta")
            act_back.triggered.connect(lambda: self.populate(self.current_directory))
            menu.exec(self.tree.viewport().mapToGlobal(position))
            return

        selected_paths = self.get_selected_paths()
        menu = QMenu(self)
        pri = ThemeManager.get_primary_color()
        self.update_action_shortcuts()

        if not selected_paths:
            act_refresh = menu.addAction(qta.icon('fa5s.sync-alt', color=pri), tr("btn_refresh"))
            act_refresh.setShortcut(QKeySequence("F5"))
            act_refresh.triggered.connect(self.refresh)
            
            act_new_folder = menu.addAction(qta.icon('fa5s.folder-plus', color=pri), "Nueva carpeta")
            act_new_folder.setShortcut(QKeySequence("Ctrl+Shift+N"))
            act_new_folder.triggered.connect(self.handle_create_folder)
            
            menu.exec(self.tree.viewport().mapToGlobal(position))
            return

        is_single = len(selected_paths) == 1
        first_path = selected_paths[0]
        is_archive = is_single and first_path.lower().endswith(tuple(self.ARCHIVE_EXTS))

        if is_archive:
            act_preview = menu.addAction(qta.icon('fa5s.eye', color=pri), "Ver contenido")
            act_preview.triggered.connect(lambda: self.preview_archive(Path(first_path)))

            act_extract_folder = menu.addAction(qta.icon('fa5s.folder-open', color=pri), tr("ctx_extract"))
            act_extract_folder.setShortcut(self.act_extract.shortcut())
            act_extract_folder.triggered.connect(lambda: self.handle_extract_to_dialog(first_path))

            act_password = menu.addAction(qta.icon('fa5s.key', color=pri), tr("ctx_password"))
            act_password.setShortcut(self.act_set_password.shortcut())
            act_password.triggered.connect(lambda: self.password_requested.emit(first_path))

            if ZstdEngine.is_archive_encrypted(Path(first_path)):
                act_remove_pwd = menu.addAction(qta.icon('fa5s.unlock', color='#e5a93b'), tr("ctx_remove_password"))
                act_remove_pwd.triggered.connect(lambda: self.remove_password_requested.emit(first_path))

            menu.addSeparator()

        act_compress = menu.addAction(qta.icon('fa5s.file-archive', color=pri), tr("ctx_compress"))
        act_compress.setShortcut(self.act_compress.shortcut())
        act_compress.triggered.connect(lambda: self.compress_requested.emit(selected_paths))
        
        menu.addSeparator()

        act_delete = menu.addAction(qta.icon('fa5s.trash-alt', color='#e74c3c'), tr("ctx_delete"))
        act_delete.setShortcut(self.act_delete.shortcut())
        act_delete.triggered.connect(lambda: self.handle_delete(selected_paths))

        if is_single:
            act_rename = menu.addAction(qta.icon('fa5s.edit', color=pri), "Cambiar nombre")
            act_rename.setShortcut(self.act_rename.shortcut())
            act_rename.triggered.connect(lambda: self.handle_rename(first_path))

            menu.addSeparator()
            act_props = menu.addAction(qta.icon('fa5s.info-circle', color=pri), tr("ctx_properties"))
            act_props.setShortcut(self.act_properties.shortcut())
            act_props.triggered.connect(lambda: self.handle_properties(first_path))

        menu.exec(self.tree.viewport().mapToGlobal(position))

    def handle_extract_to_dialog(self, archive_path: str):
        dir_dest = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de destino", str(self.current_directory))
        if dir_dest:
            self.extract_to_requested.emit(archive_path, dir_dest)

    def handle_create_folder(self):
        curr = str(self.current_directory)
        base_name = "Nueva Carpeta"
        candidate = os.path.join(curr, base_name)
        counter = 1
        while os.path.exists(candidate):
            candidate = os.path.join(curr, f"{base_name} ({counter})")
            counter += 1
        try:
            os.makedirs(candidate)
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def handle_delete(self, paths: list):
        msg = tr("ctx_delete_confirm", count=len(paths))
        reply = QMessageBox.question(
            self, 
            tr("ctx_delete"),
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            for p in paths:
                move_to_trash(Path(p))
            self.refresh()

    def handle_rename(self, path: str):
        from PyQt6.QtWidgets import QInputDialog
        old_name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(self, "Renombrar", "Nuevo nombre:", text=old_name)
        if ok and new_name and new_name != old_name:
            new_path = os.path.join(os.path.dirname(path), new_name)
            try:
                os.rename(path, new_path)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def handle_properties(self, path: str):
        target = Path(path)
        if target.exists():
            dlg = PropertiesDialog(target, self)
            dlg.exec()

    def _save_column_widths(self):
        for i in range(self.tree.columnCount()):
            self.settings.setValue(f"col_width_{i}", self.tree.columnWidth(i))

    def _restore_column_widths(self):
        for i in range(self.tree.columnCount()):
            val = self.settings.value(f"col_width_{i}", type=int)
            if val and val > 0:
                self.tree.setColumnWidth(i, val)
            else:
                if i == 0:
                    self.tree.setColumnWidth(0, 320)
                else:
                    self.tree.setColumnWidth(i, 110)