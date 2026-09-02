import sys
from pathlib import Path

from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QIcon, QColor, QFont
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QSplitter,
    QMessageBox
)

from src.utils.helpers import get_app_root
from src.i18n import translator
from src.i18n.translator import tr
from src.ui.themes import ThemeManager
from src.ui.panels.file_browser_panel import FileBrowserPanel
from src.ui.panels.sidebar_panel import SidebarPanel
from src.ui.panels.toolbar_panel import ToolBarPanel
from src.ui.panels.status_panel import StatusPanel
from src.ui.dialogs.settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.root_dir = get_app_root()
        self.settings = QSettings("clzip", "MainWindow")

        self._setup_window_icon()

        self.setWindowTitle("clzip - Gestor de Archivos")
        self.resize(1100, 700)
        self.setMinimumSize(850, 520)
        
        self.setFont(QFont("Segoe UI", 10))

        self.dark_mode = self.settings.value("dark_mode", True, type=bool)
        self.current_palette = self.settings.value("palette", "Verde", type=str)

        self._build_ui()
        self._connect_signals()

        self._apply_current_theme()
        self.navigate_to(Path.home())
        
        self.file_browser.setFocus()

    def _setup_window_icon(self):
        ico_file = self.root_dir / "assets" / "icon.ico"
        png_backup = self.root_dir / "assets" / "icon_256.png"

        if ico_file.exists():
            self.setWindowIcon(QIcon(str(ico_file)))
        elif png_backup.exists():
            self.setWindowIcon(QIcon(str(png_backup)))

    def _build_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(6, 4, 6, 4)
        main_layout.setSpacing(4)

        self.toolbar_panel = ToolBarPanel(self)
        self.addToolBar(self.toolbar_panel)

        self.path_bar = QLineEdit(self)
        self.path_bar.setFixedHeight(28)
        self.path_bar.setPlaceholderText("Ruta del directorio...")
        self.path_bar.returnPressed.connect(self._on_path_entered)
        main_layout.addWidget(self.path_bar)

        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.splitter.setHandleWidth(4)

        self.sidebar_panel = SidebarPanel(self)
        self.file_browser = FileBrowserPanel(self)

        self.splitter.addWidget(self.sidebar_panel)
        self.splitter.addWidget(self.file_browser)

        self.splitter.setSizes([160, 840])
        main_layout.addWidget(self.splitter, stretch=1)

        self.status_panel = StatusPanel(self)
        main_layout.addWidget(self.status_panel)

    def _connect_signals(self):
        self.file_browser.open_directory_requested.connect(self.navigate_to)
        self.sidebar_panel.path_selected.connect(self.navigate_to)

        self.toolbar_panel.extract_requested.connect(self.file_browser.extract_requested.emit)
        self.toolbar_panel.home_requested.connect(lambda: self.navigate_to(Path.home()))
        self.toolbar_panel.up_requested.connect(self._go_up)
        self.toolbar_panel.refresh_requested.connect(self.file_browser.refresh)
        self.toolbar_panel.theme_toggled.connect(self._toggle_theme)
        self.toolbar_panel.lang_toggled.connect(self._toggle_language)
        self.toolbar_panel.settings_requested.connect(self._open_settings)

    def navigate_to(self, path: Path):
        p = Path(path).resolve()
        if p.exists() and p.is_dir():
            self.file_browser.populate(p)
            self.path_bar.setText(str(p))
            self.status_panel.set_ready()
        else:
            self._silent_message("Error", f"No se puede acceder a la ruta especificada:\n{p}")

    def _go_up(self):
        current = self.file_browser.current_directory
        parent = current.parent
        if parent and parent != current:
            self.navigate_to(parent)

    def _on_path_entered(self):
        target = Path(self.path_bar.text().strip())
        if target.exists() and target.is_dir():
            self.navigate_to(target)
            self.file_browser.setFocus()
        else:
            self._silent_message("Ruta Inválida", f"La ruta no existe o no es una carpeta válida:\n{target}")
            self.path_bar.setText(str(self.file_browser.current_directory))

    def _toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.settings.setValue("dark_mode", self.dark_mode)
        self._apply_current_theme()

    def _apply_current_theme(self):
        try:
            primary_color = ThemeManager.get_primary_color(self.current_palette)
        except TypeError:
            primary_color = ThemeManager.get_primary_color()

        c = QColor(primary_color)
        hover_bg = f"rgba({c.red()}, {c.green()}, {c.blue()}, 0.18)"
        selected_bg = f"rgba({c.red()}, {c.green()}, {c.blue()}, 0.32)"

        if self.dark_mode:
            bg_pane = "#181825"
            bg_alt = "#1e1e2e"
            text_main = "#cdd6f4"
            text_dim = "#a6adc8"
            border = "#313244"
            scroll_bg = "#45475a"
        else:
            bg_pane = "#eff1f5"
            bg_alt = "#ffffff"
            text_main = "#4c4f69"
            text_dim = "#6c6f85"
            border = "#ccd0da"
            scroll_bg = "#cfd4df"

        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {bg_pane};
                color: {text_main};
                font-family: 'Segoe UI', sans-serif;
            }}
            QToolBar {{
                background-color: {bg_alt};
                border-bottom: 1px solid {border};
                spacing: 4px;
                padding: 2px;
            }}
            QToolButton {{
                background-color: transparent;
                border-radius: 4px;
                padding: 5px;
                color: {text_main};
            }}
            QToolButton:hover {{
                background-color: {hover_bg};
                border: 1px solid {primary_color};
            }}
            QLineEdit {{
                background-color: {bg_alt};
                border: 1px solid {border};
                border-radius: 4px;
                padding: 4px 8px;
                color: {text_main};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {primary_color};
            }}
            QTreeWidget, QListWidget {{
                background-color: {bg_alt};
                border: 1px solid {border};
                border-radius: 4px;
                alternate-background-color: {bg_pane};
                color: {text_main};
                outline: none;
            }}
            QTreeWidget::item:hover, QListWidget::item:hover {{
                background-color: {hover_bg};
                color: {text_main};
            }}
            QTreeWidget::item:selected, QListWidget::item:selected {{
                background-color: {selected_bg};
                color: {text_main};
                border-left: 2px solid {primary_color};
            }}
            QHeaderView::section {{
                background-color: {bg_pane};
                color: {text_dim};
                padding: 4px;
                border: none;
                border-bottom: 1px solid {border};
            }}
            QSplitter::handle {{
                background-color: {border};
            }}
            
            QScrollBar:vertical {{
                border: none;
                background-color: transparent;
                width: 12px;
                margin: 4px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {scroll_bg};
                min-height: 30px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {primary_color};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                height: 0px; background: none;
            }}
            
            QScrollBar:horizontal {{
                border: none;
                background-color: transparent;
                height: 12px;
                margin: 4px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {scroll_bg};
                min-width: 30px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {primary_color};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                width: 0px; background: none;
            }}
        """)

        self.toolbar_panel.update_theme_icons(self.dark_mode, self.current_palette)
        self.sidebar_panel.populate_bookmarks(primary_color)

    def _toggle_language(self):
        cur = translator.get_locale()
        new_lang = "en" if cur == "es" else "es"
        translator.set_locale(new_lang)

        self.toolbar_panel.retranslate_ui()
        self.file_browser.retranslate_ui()

        try:
            pri = ThemeManager.get_primary_color(self.current_palette)
        except TypeError:
            pri = ThemeManager.get_primary_color()
        self.sidebar_panel.populate_bookmarks(pri)
        self.file_browser.refresh()

    def _open_settings(self):
        dlg = SettingsDialog(self)
        dlg.theme_updated.connect(self._sync_settings)
        dlg.exec()

    def _sync_settings(self):
        """Aplica la nueva paleta en vivo mientras la ventana de configuración sigue abierta."""
        # 1. Obtener la nueva paleta guardada
        self.current_palette = self.settings.value("palette", self.current_palette, type=str)
        
        # 2. Re-aplicar estilos QSS e íconos de toolbar/sidebar
        self._apply_current_theme()
        
        # 3. Forzar al explorador de archivos a regenerar todos los íconos con la nueva paleta
        self.file_browser.populate(self.file_browser.current_directory)

    def _silent_message(self, title: str, text: str):
        box = QMessageBox(self)
        box.setWindowTitle(title)
        box.setText(text)
        box.setIcon(QMessageBox.Icon.NoIcon)
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.exec()