import os
import string
import ctypes
from pathlib import Path
from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtCore import pyqtSignal, Qt, QSize
import qtawesome as qta
from src.i18n.translator import tr
from src.ui.themes import ThemeManager

class SidebarPanel(QListWidget):
    path_selected = pyqtSignal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIconSize(QSize(18, 18))
        self.setFixedWidth(150)
        self.itemClicked.connect(self._on_item_clicked)
        self.populate_bookmarks()

    def populate_bookmarks(self, palette_color: str = None):
        if palette_color is None:
            palette_color = ThemeManager.get_primary_color()

        self.clear()
        
        # Marcadores estándar que sincronizan su color con la paleta activa
        bookmarks = [
            (tr("bm_home"), Path.home(), qta.icon("fa5s.user", color=palette_color)),
            (tr("bm_desktop"), Path.home() / "Desktop", qta.icon("fa5s.desktop", color=palette_color)),
            (tr("bm_documents"), Path.home() / "Documents", qta.icon("fa5s.folder", color=palette_color)),
            (tr("bm_downloads"), Path.home() / "Downloads", qta.icon("fa5s.download", color=palette_color)),
        ]

        # Detección de unidades de disco en Windows
        if os.name == "nt":
            drives = []
            bitmask = ctypes.windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    drives.append(f"{letter}:\\")
                bitmask >>= 1
            for d in drives:
                bookmarks.append((f"({d[:2]})", Path(d), qta.icon("fa5s.hdd", color=palette_color)))

        for name, path, icon in bookmarks:
            if path.exists():
                item = QListWidgetItem(icon, f"  {name}")
                item.setData(Qt.ItemDataRole.UserRole, str(path))
                self.addItem(item)

    def _on_item_clicked(self, item: QListWidgetItem):
        path_str = item.data(Qt.ItemDataRole.UserRole)
        if path_str:
            self.path_selected.emit(Path(path_str))