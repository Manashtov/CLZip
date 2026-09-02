from pathlib import Path
from PyQt6.QtWidgets import QToolBar, QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QPixmap
import qtawesome as qta
from src.i18n.translator import tr
from src.ui.themes import ThemeManager

class ToolBarPanel(QToolBar):
    extract_requested = pyqtSignal()
    home_requested = pyqtSignal()
    up_requested = pyqtSignal()
    refresh_requested = pyqtSignal()
    theme_toggled = pyqtSignal()
    lang_toggled = pyqtSignal()
    settings_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.setIconSize(QSize(20, 20))
        self.dark_mode = True

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)

        # 1. Logo oficial de la marca
        self._setup_brand_logo()

        # 2. Acciones principales
        self.act_extract = self.addAction(qta.icon("fa5s.box-open", color="#e5a93b"), tr("btn_extract"))
        self.act_extract.triggered.connect(self.extract_requested.emit)

        self.addSeparator()

        pri = ThemeManager.get_primary_color()
        self.act_home = self.addAction(qta.icon("fa5s.home", color=pri), tr("btn_home"))
        self.act_home.triggered.connect(self.home_requested.emit)

        self.act_up = self.addAction(qta.icon("fa5s.arrow-up", color=pri), tr("btn_up"))
        self.act_up.triggered.connect(self.up_requested.emit)

        self.act_refresh = self.addAction(qta.icon("fa5s.sync-alt", color=pri), tr("btn_refresh"))
        self.act_refresh.triggered.connect(self.refresh_requested.emit)

        self.addSeparator()

        # 3. Botones de personalización
        self.act_theme = self.addAction(qta.icon("fa5s.moon", color="#cdd6f4"), tr("btn_theme"))
        self.act_theme.triggered.connect(self.theme_toggled.emit)

        self.act_lang = self.addAction(qta.icon("fa5s.globe", color="#cdd6f4"), tr("btn_lang"))
        self.act_lang.triggered.connect(self.lang_toggled.emit)

        self.act_settings = self.addAction(qta.icon("fa5s.cog", color="#cdd6f4"), tr("btn_settings"))
        self.act_settings.triggered.connect(self.settings_requested.emit)

    def _setup_brand_logo(self):
        possible_paths = [
            Path(__file__).resolve().parent.parent.parent.parent / "assets" / "icon.png",
            Path(__file__).resolve().parent.parent.parent.parent / "assets" / "icon_48.png",
            Path(__file__).resolve().parent.parent.parent.parent / "assets" / "icon_32.png",
            Path("assets/icon.png").resolve(),
            Path("assets/icon_32.png").resolve(),
        ]

        icon_file = next((p for p in possible_paths if p.exists()), None)

        container = QWidget(self)
        container.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(6, 2, 8, 2)
        layout.setSpacing(6)

        self.lbl_logo = QLabel()
        self.lbl_logo.setFixedSize(24, 24)
        self.lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_logo.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)

        if icon_file:
            pixmap = QPixmap(str(icon_file)).scaled(
                24, 24, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.lbl_logo.setPixmap(pixmap)
        else:
            pri = ThemeManager.get_primary_color()
            ico = qta.icon("fa5s.file-archive", color=pri)
            self.lbl_logo.setPixmap(ico.pixmap(22, 22))

        pri = ThemeManager.get_primary_color()
        self.lbl_title = QLabel("<b>clzip</b>")
        self.lbl_title.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {pri}; margin-right: 4px;")
        self.lbl_title.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)

        layout.addWidget(self.lbl_logo)
        layout.addWidget(self.lbl_title)
        self.addWidget(container)
        self.addSeparator()

    def update_theme_icons(self, dark_mode: bool, palette_name: str = None):
        self.dark_mode = dark_mode
        pri = ThemeManager.get_primary_color(palette_name)

        self.lbl_title.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {pri}; margin-right: 4px;")

        if dark_mode:
            utility_color = "#e2e4e9"
            theme_icon_name = "fa5s.moon"
        else:
            utility_color = "#2d3139"
            theme_icon_name = "fa5s.sun"

        self.act_home.setIcon(qta.icon("fa5s.home", color=pri))
        self.act_up.setIcon(qta.icon("fa5s.arrow-up", color=pri))
        self.act_refresh.setIcon(qta.icon("fa5s.sync-alt", color=pri))
        self.act_theme.setIcon(qta.icon(theme_icon_name, color=utility_color))
        self.act_lang.setIcon(qta.icon("fa5s.globe", color=utility_color))
        self.act_settings.setIcon(qta.icon("fa5s.cog", color=utility_color))

    def retranslate_ui(self):
        self.act_extract.setText(tr("btn_extract"))
        self.act_home.setText(tr("btn_home"))
        self.act_up.setText(tr("btn_up"))
        self.act_refresh.setText(tr("btn_refresh"))
        self.act_theme.setText(tr("btn_theme"))
        self.act_lang.setText(tr("btn_lang"))
        self.act_settings.setText(tr("btn_settings"))