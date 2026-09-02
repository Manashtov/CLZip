import os
import sys
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
        
        bookmarks = [
            (tr("bm_home"), Path.home(), qta.icon("fa5s.user", color=palette_color)),
            (tr("bm_desktop"), Path.home() / "Desktop", qta.icon("fa5s.desktop", color=palette_color)),
            (tr("bm_documents"), Path.home() / "Documents", qta.icon("fa5s.folder", color=palette_color)),
            (tr("bm_downloads"), Path.home() / "Downloads", qta.icon("fa5s.download", color=palette_color)),
        ]

        # Detección multiplataforma de unidades y raíces de sistema
        if sys.platform == "win32":
            import ctypes
            import string
            bitmask = ctypes.windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    d = f"{letter}:\\"
                    bookmarks.append((f"({letter}:)", Path(d), qta.icon("fa5s.hdd", color=palette_color)))
                bitmask >>= 1
        elif sys.platform.startswith("linux"):
            bookmarks.append(("/ (Raíz)", Path("/"), qta.icon("fa5s.hdd", color=palette_color)))
            media = Path("/media") / Path.home().name
            if media.exists():
                for m in media.iterdir():
                    if m.is_dir():
                        bookmarks.append((m.name[:10], m, qta.icon("fa5s.hdd", color=palette_color)))
        elif sys.platform == "darwin":
            bookmarks.append(("Macintosh HD", Path("/"), qta.icon("fa5s.hdd", color=palette_color)))
            volumes = Path("/Volumes")
            if volumes.exists():
                for v in volumes.iterdir():
                    if v.is_dir() and v.name != "Macintosh HD":
                        bookmarks.append((v.name[:10], v, qta.icon("fa5s.hdd", color=palette_color)))

        for name, path, icon in bookmarks:
            if path.exists():
                item = QListWidgetItem(icon, f"  {name}")
                item.setData(Qt.ItemDataRole.UserRole, str(path))
                self.addItem(item)

    def _on_item_clicked(self, item: QListWidgetItem):
        path_str = item.data(Qt.ItemDataRole.UserRole)
        if path_str:
            self.path_selected.emit(Path(path_str))