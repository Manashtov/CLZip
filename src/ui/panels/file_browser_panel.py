import os
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QMenu, QMessageBox, 
    QDialog, QLabel, QFormLayout, QDialogButtonBox, QHeaderView, QFileDialog
)
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt, QSettings, QFileInfo, pyqtSignal
import qtawesome as qta

from src.i18n.translator import tr
from src.core.compressor import ZstdEngine
from src.ui.themes import ThemeManager


class PropertiesDialog(QDialog):
    """Muestra los metadatos y atributos detallados del archivo o carpeta seleccionado."""
    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{tr('Propiedades de:')} {os.path.basename(path)}")
        self.setMinimumWidth(400)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        info = QFileInfo(path)
        is_dir = info.isDir()
        
        size_bytes = info.size()
        if is_dir:
            size_str = tr("Carpeta de archivos")
        else:
            if size_bytes < 1024:
                size_str = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.2f} KB ({size_bytes:,} bytes)"
            else:
                size_str = f"{size_bytes / (1024 * 1024):.2f} MB ({size_bytes:,} bytes)"
        
        created = info.birthTime().toString("yyyy-MM-dd HH:mm:ss") if hasattr(info, 'birthTime') else "-"
        modified = info.lastModified().toString("yyyy-MM-dd HH:mm:ss")
        accessed = info.lastRead().toString("yyyy-MM-dd HH:mm:ss")
        
        form.addRow(QLabel(f"<b>{tr('Nombre:')}</b>"), QLabel(info.fileName()))
        form.addRow(QLabel(f"<b>{tr('Tipo:')}</b>"), QLabel(tr("Carpeta") if is_dir else (f".{info.suffix().upper()}" if info.suffix() else tr("Archivo"))))
        form.addRow(QLabel(f"<b>{tr('Ubicación:')}</b>"), QLabel(info.absolutePath()))
        form.addRow(QLabel(f"<b>{tr('Tamaño:')}</b>"), QLabel(size_str))
        form.addRow(QLabel(f"<b>{tr('Creado:')}</b>"), QLabel(created))
        form.addRow(QLabel(f"<b>{tr('Modificado:')}</b>"), QLabel(modified))
        form.addRow(QLabel(f"<b>{tr('Último acceso:')}</b>"), QLabel(accessed))
        
        layout.addLayout(form)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btn_box.accepted.connect(self.accept)
        layout.addWidget(btn_box)


class FileBrowserPanel(QWidget):
    """Panel de exploración basado en QTreeWidget con diseño limpio, hover e iconos temáticos."""
    open_directory_requested = pyqtSignal(Path)
    compress_requested = pyqtSignal(list)
    extract_to_requested = pyqtSignal(str, str)
    path_changed = pyqtSignal(str)
    file_selected = pyqtSignal(str)

    ARCHIVE_EXTS = {'.zip', '.tar', '.zst', '.tar.zst'}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_directory = Path.home()
        self.history = []
        self.history_index = -1
        self.settings = QSettings("clzip", "FileBrowser")
        
        self._setup_ui()

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
        
        self.tree.setHeaderLabels([tr("Name"), tr("Size"), tr("Type"), tr("Date Modified")])
        
        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.sectionResized.connect(self._save_column_widths)
        
        self.tree.doubleClicked.connect(self._on_double_clicked)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        
        main_layout.addWidget(self.tree)
        self._restore_column_widths()

    def populate(self, path: Path, record_history: bool = True):
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
                    type_str = tr("Carpeta")
                    size_str = ""
                elif ext in self.ARCHIVE_EXTS:
                    if ZstdEngine.is_archive_encrypted(str(entry)):
                        icon = qta.icon("fa5s.lock", color="#e5a93b")
                        type_str = "ZIP (Protegido)"
                    else:
                        icon = qta.icon("fa5s.file-archive", color=pri_color)
                        type_str = "Compressed Archive File"
                    
                    sz = entry.stat().st_size
                    size_str = f"{sz / (1024 * 1024):.2f} MiB" if sz >= 1024*1024 else f"{sz / 1024:.2f} KiB"
                else:
                    icon = qta.icon("fa5s.file", color="#a6adc8")
                    type_str = entry.suffix.upper()[1:] + " File" if entry.suffix else "File"
                    sz = entry.stat().st_size
                    size_str = f"{sz / (1024 * 1024):.2f} MiB" if sz >= 1024*1024 else f"{sz / 1024:.2f} KiB"

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

    def refresh(self):
        self.populate(self.current_directory, record_history=False)

    def retranslate_ui(self):
        self.tree.setHeaderLabels([tr("Name"), tr("Size"), tr("Type"), tr("Date Modified")])

    def get_selected_paths(self) -> list:
        paths = []
        for item in self.tree.selectedItems():
            p = item.data(0, Qt.ItemDataRole.UserRole)
            if p:
                paths.append(p)
        return paths

    def _on_double_clicked(self, index):
        item = self.tree.itemAt(index.row(), 0) if hasattr(self.tree, 'itemAt') else self.tree.currentItem()
        if not item:
            item = self.tree.currentItem()
        if not item:
            return
        path_str = item.data(0, Qt.ItemDataRole.UserRole)
        if not path_str:
            return
            
        path_obj = Path(path_str)
        if path_obj.is_dir():
            self.open_directory_requested.emit(path_obj)
        else:
            self.file_selected.emit(path_str)
            if path_str.lower().endswith(tuple(self.ARCHIVE_EXTS)):
                self.handle_extract_to_dialog(path_str)

    def show_context_menu(self, position):
        selected_paths = self.get_selected_paths()
        menu = QMenu(self)
        
        if not selected_paths:
            act_refresh = menu.addAction(qta.icon('fa5s.sync-alt', color='#2ecc71'), tr("Actualizar"))
            act_refresh.setShortcut(QKeySequence("F5"))
            act_refresh.triggered.connect(self.refresh)
            
            act_new_folder = menu.addAction(qta.icon('fa5s.folder-plus', color='#2ecc71'), tr("Nueva carpeta"))
            act_new_folder.setShortcut(QKeySequence("Ctrl+Shift+N"))
            act_new_folder.triggered.connect(self.handle_create_folder)
            
            menu.exec(self.tree.viewport().mapToGlobal(position))
            return

        is_single = len(selected_paths) == 1
        first_path = selected_paths[0]
        is_archive = is_single and first_path.lower().endswith(tuple(self.ARCHIVE_EXTS))

        if is_archive:
            act_extract_folder = menu.addAction(qta.icon('fa5s.folder-open', color='#2ecc71'), tr("📁 Extraer en carpeta..."))
            act_extract_folder.setShortcut(QKeySequence("Ctrl+E"))
            act_extract_folder.triggered.connect(lambda: self.handle_extract_to_dialog(first_path))
            menu.addSeparator()

        act_compress = menu.addAction(qta.icon('fa5s.file-archive', color='#2ecc71'), tr("🗜️ Comprimir seleccionados..."))
        act_compress.setShortcut(QKeySequence("Ctrl+Shift+C"))
        act_compress.triggered.connect(lambda: self.compress_requested.emit(selected_paths))
        
        menu.addSeparator()

        act_delete = menu.addAction(qta.icon('fa5s.trash-alt', color='#e74c3c'), tr("Eliminar"))
        act_delete.setShortcut(QKeySequence("Del"))
        act_delete.triggered.connect(lambda: self.handle_delete(selected_paths))

        if is_single:
            act_rename = menu.addAction(qta.icon('fa5s.edit', color='#2ecc71'), tr("Cambiar nombre"))
            act_rename.setShortcut(QKeySequence("F2"))
            act_rename.triggered.connect(lambda: self.handle_rename(first_path))

            menu.addSeparator()
            act_props = menu.addAction(qta.icon('fa5s.info-circle', color='#2ecc71'), tr("ℹ️ Propiedades"))
            act_props.setShortcut(QKeySequence("Alt+Enter"))
            act_props.triggered.connect(lambda: self.handle_properties(first_path))

        menu.exec(self.tree.viewport().mapToGlobal(position))

    def handle_extract_to_dialog(self, archive_path: str):
        dir_dest = QFileDialog.getExistingDirectory(self, tr("Seleccionar carpeta de destino"), str(self.current_directory))
        if dir_dest:
            self.extract_to_requested.emit(archive_path, dir_dest)

    def handle_create_folder(self):
        curr = str(self.current_directory)
        base_name = tr("Nueva Carpeta")
        candidate = os.path.join(curr, base_name)
        counter = 1
        while os.path.exists(candidate):
            candidate = os.path.join(curr, f"{base_name} ({counter})")
            counter += 1
        try:
            os.makedirs(candidate)
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, tr("Error"), str(e))

    def handle_delete(self, paths: list):
        reply = QMessageBox.question(
            self, 
            tr("Confirmar eliminación"),
            f"{tr('¿Desea eliminar los elementos seleccionados?')}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            for p in paths:
                try:
                    if os.path.isdir(p):
                        shutil.rmtree(p)
                    else:
                        os.remove(p)
                except Exception as e:
                    QMessageBox.warning(self, tr("Error"), f"{p}: {str(e)}")
            self.refresh()

    def handle_rename(self, path: str):
        from PyQt6.QtWidgets import QInputDialog
        old_name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(self, tr("Renombrar"), tr("Nuevo nombre:"), text=old_name)
        if ok and new_name and new_name != old_name:
            new_path = os.path.join(os.path.dirname(path), new_name)
            try:
                os.rename(path, new_path)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, tr("Error"), str(e))

    def handle_properties(self, path: str):
        if os.path.exists(path):
            dlg = PropertiesDialog(path, self)
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