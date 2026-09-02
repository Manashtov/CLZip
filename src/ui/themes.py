from PyQt6.QtCore import QSettings

COLOR_PALETTES = {
    "Verde": {"primary": "#52b774", "hover": "#439e62", "light_hover": "rgba(82, 183, 116, 0.18)", "text_on_pri": "#ffffff"},
    "Rosado": {"primary": "#e6608f", "hover": "#cf4b79", "light_hover": "rgba(230, 96, 143, 0.18)", "text_on_pri": "#ffffff"},
    "Azul electrico": {"primary": "#1e66f5", "hover": "#1752c4", "light_hover": "rgba(30, 102, 245, 0.18)", "text_on_pri": "#ffffff"},
    "Celeste": {"primary": "#06b6d4", "hover": "#0891b2", "light_hover": "rgba(6, 182, 212, 0.18)", "text_on_pri": "#ffffff"},
    "Amarillo": {"primary": "#eab308", "hover": "#ca8a04", "light_hover": "rgba(234, 179, 8, 0.18)", "text_on_pri": "#18191f"},
    "Rojo": {"primary": "#ef4444", "hover": "#dc2626", "light_hover": "rgba(239, 68, 68, 0.18)", "text_on_pri": "#ffffff"},
    "Morado": {"primary": "#a855f7", "hover": "#9333ea", "light_hover": "rgba(168, 85, 247, 0.18)", "text_on_pri": "#ffffff"},
    "Negro": {"primary": "#374151", "hover": "#1f2937", "light_hover": "rgba(55, 65, 81, 0.25)", "text_on_pri": "#ffffff"},
    "Naranjo": {"primary": "#f97316", "hover": "#ea580c", "light_hover": "rgba(249, 115, 22, 0.18)", "text_on_pri": "#ffffff"},
}

class ThemeManager:
    @staticmethod
    def get_current_palette_name() -> str:
        settings = QSettings("clzip", "Appearance")
        return settings.value("palette", "Verde")

    @staticmethod
    def get_primary_color(palette_name: str = None) -> str:
        if palette_name is None or palette_name not in COLOR_PALETTES:
            palette_name = ThemeManager.get_current_palette_name()
        return COLOR_PALETTES.get(palette_name, COLOR_PALETTES["Verde"])["primary"]

    @staticmethod
    def set_palette(name: str):
        if name in COLOR_PALETTES:
            settings = QSettings("clzip", "Appearance")
            settings.setValue("palette", name)

    @staticmethod
    def get_theme(dark_mode: bool = True, palette_name: str = None) -> str:
        if palette_name is None or palette_name not in COLOR_PALETTES:
            palette_name = ThemeManager.get_current_palette_name()

        pal = COLOR_PALETTES.get(palette_name, COLOR_PALETTES["Verde"])
        pri = pal["primary"]
        hover = pal["hover"]
        light_hover = pal.get("light_hover", "rgba(82, 183, 116, 0.18)")
        text_on_pri = pal["text_on_pri"]

        if dark_mode:
            return f"""
            QMainWindow, QDialog, QWidget {{
                background-color: #121316;
                color: #e2e4e9;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
            }}
            QLabel {{
                color: #e2e4e9;
                font-size: 10pt;
            }}
            QToolBar {{
                background-color: #18191f;
                border-bottom: 1px solid #282a32;
                padding: 4px;
                spacing: 6px;
            }}
            QToolButton {{
                background: transparent;
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 4px 8px;
                color: #e2e4e9;
                font-size: 10pt;
            }}
            QToolButton:hover {{
                background: #242630;
                border-color: #353844;
            }}
            QTreeWidget, QListWidget, QTextEdit {{
                background-color: #16171d;
                color: #e2e4e9;
                border: 1px solid #262830;
                border-radius: 8px;
                alternate-background-color: #1a1b22;
                outline: none;
                font-size: 10pt;
            }}
            QTreeWidget::item, QListWidget::item {{
                padding: 4px 0px;
                border-radius: 4px;
            }}
            QTreeWidget::item:hover, QListWidget::item:hover {{
                background-color: {light_hover};
            }}
            QTreeWidget::item:selected, QTreeWidget::item:selected:active, QTreeWidget::item:selected:!active,
            QListWidget::item:selected, QListWidget::item:selected:active, QListWidget::item:selected:!active {{
                background-color: {pri};
                color: {text_on_pri};
            }}
            QHeaderView::section {{
                background-color: #121316;
                color: #9da1b0;
                padding: 6px;
                border: none;
                border-right: 1px solid #262830;
                border-bottom: 1px solid #262830;
                font-weight: bold;
                font-size: 10pt;
            }}
            QLineEdit, QComboBox, QSpinBox, QKeySequenceEdit {{
                background-color: #18191f;
                color: #e2e4e9;
                border: 1px solid #2f323d;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 10pt;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QKeySequenceEdit:focus {{
                border: 1px solid {pri};
            }}
            QComboBox {{
                border-radius: 8px;
                padding: 6px 12px;
                background-color: #18191f;
                color: #e2e4e9;
                font-size: 10pt;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 26px;
                border-left-width: 0px;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #18191f;
                color: #e2e4e9;
                border: 1px solid #2f323d;
                border-radius: 8px;
                padding: 6px;
                outline: none;
                font-size: 10pt;
            }}
            QComboBox QAbstractItemView::item {{
                border-radius: 6px;
                padding: 6px 10px;
                min-height: 24px;
                color: #e2e4e9;
                background-color: transparent;
                font-size: 10pt;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {light_hover};
                color: #ffffff;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {pri};
                color: {text_on_pri};
            }}
            QPushButton {{
                background-color: #242630;
                color: #e2e4e9;
                border: 1px solid #353844;
                border-radius: 8px;
                padding: 6px 16px;
                font-weight: bold;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: #2f323f;
                border-color: {pri};
            }}
            QPushButton#primaryBtn {{
                background-color: {pri};
                color: {text_on_pri};
                border: none;
                font-size: 10pt;
            }}
            QPushButton#primaryBtn:hover {{
                background-color: {hover};
            }}
            QTabWidget::pane {{
                border: 1px solid #282a32;
                border-radius: 8px;
                background-color: #18191f;
            }}
            QTabBar::tab {{
                background: #121316;
                color: #9da1b0;
                padding: 8px 18px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
                font-size: 10pt;
            }}
            QTabBar::tab:selected {{
                background: #18191f;
                color: {pri};
                font-weight: bold;
                border-bottom: 2px solid {pri};
            }}
            QProgressBar {{
                border: 1px solid #2f323d;
                border-radius: 6px;
                text-align: center;
                height: 14px;
                background-color: #121316;
                color: #ffffff;
                font-size: 8pt;
            }}
            QProgressBar::chunk {{
                background-color: {pri};
                border-radius: 5px;
            }}
            QMenu {{
                background-color: #18191f;
                color: #e2e4e9;
                border: 1px solid #2f323d;
                border-radius: 8px;
                padding: 6px;
                font-size: 10pt;
            }}
            QMenu::item {{
                padding: 6px 22px;
                border-radius: 6px;
                font-size: 10pt;
            }}
            QMenu::item:hover {{
                background-color: {light_hover};
            }}
            QMenu::item:selected {{
                background-color: {pri};
                color: {text_on_pri};
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: #2a2d36;
                min-height: 28px;
                border-radius: 5px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {pri};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
                background: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
            QScrollBar:horizontal {{
                background: transparent;
                height: 10px;
                margin: 0px;
                border-radius: 5px;
            }}
            QScrollBar::handle:horizontal {{
                background: #2a2d36;
                min-width: 28px;
                border-radius: 5px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {pri};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
                background: none;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}
            """
        else:
            return f"""
            QMainWindow, QDialog, QWidget {{
                background-color: #f5f6f8;
                color: #2d3139;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
            }}
            QLabel {{
                color: #2d3139;
                font-size: 10pt;
            }}
            QToolBar {{
                background-color: #ebeef3;
                border-bottom: 1px solid #d4d8e2;
                padding: 4px;
                spacing: 6px;
            }}
            QToolButton {{
                background: transparent;
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 4px 8px;
                color: #2d3139;
                font-size: 10pt;
            }}
            QToolButton:hover {{
                background: #dfe3ec;
                border-color: #c7cdd9;
            }}
            QTreeWidget, QListWidget, QTextEdit {{
                background-color: #ffffff;
                color: #1e2025;
                border: 1px solid #d4d8e2;
                border-radius: 8px;
                alternate-background-color: #f8f9fb;
                outline: none;
                font-size: 10pt;
            }}
            QTreeWidget::item, QListWidget::item {{
                padding: 4px 0px;
                border-radius: 4px;
            }}
            QTreeWidget::item:hover, QListWidget::item:hover {{
                background-color: {light_hover};
            }}
            QTreeWidget::item:selected, QTreeWidget::item:selected:active, QTreeWidget::item:selected:!active,
            QListWidget::item:selected, QListWidget::item:selected:active, QListWidget::item:selected:!active {{
                background-color: {pri};
                color: {text_on_pri};
            }}
            QHeaderView::section {{
                background-color: #ebeef3;
                color: #4a505e;
                padding: 6px;
                border: none;
                border-right: 1px solid #d4d8e2;
                border-bottom: 1px solid #d4d8e2;
                font-weight: bold;
                font-size: 10pt;
            }}
            QLineEdit, QComboBox, QSpinBox, QKeySequenceEdit {{
                background-color: #ffffff;
                color: #1e2025;
                border: 1px solid #c7cdd9;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 10pt;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QKeySequenceEdit:focus {{
                border: 1px solid {pri};
            }}
            QComboBox {{
                border-radius: 8px;
                padding: 6px 12px;
                background-color: #ffffff;
                color: #1e2025;
                font-size: 10pt;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 26px;
                border-left-width: 0px;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #ffffff;
                color: #1e2025;
                border: 1px solid #d4d8e2;
                border-radius: 8px;
                padding: 6px;
                outline: none;
                font-size: 10pt;
            }}
            QComboBox QAbstractItemView::item {{
                border-radius: 6px;
                padding: 6px 10px;
                min-height: 24px;
                color: #1e2025;
                background-color: transparent;
                font-size: 10pt;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {light_hover};
                color: #1e2025;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {pri};
                color: {text_on_pri};
            }}
            QPushButton {{
                background-color: #e3e6ed;
                color: #2d3139;
                border: 1px solid #c7cdd9;
                border-radius: 8px;
                padding: 6px 16px;
                font-weight: bold;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: #d6dae3;
                border-color: {pri};
            }}
            QPushButton#primaryBtn {{
                background-color: {pri};
                color: {text_on_pri};
                border: none;
                font-size: 10pt;
            }}
            QPushButton#primaryBtn:hover {{
                background-color: {hover};
            }}
            QTabWidget::pane {{
                border: 1px solid #d4d8e2;
                border-radius: 8px;
                background-color: #ffffff;
            }}
            QTabBar::tab {{
                background: #ebeef3;
                color: #4a505e;
                padding: 8px 18px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
                font-size: 10pt;
            }}
            QTabBar::tab:selected {{
                background: #ffffff;
                color: {pri};
                font-weight: bold;
                border-bottom: 2px solid {pri};
            }}
            QProgressBar {{
                border: 1px solid #d4d8e2;
                border-radius: 6px;
                text-align: center;
                height: 14px;
                background-color: #ebeef3;
                color: #1e2025;
                font-size: 8pt;
            }}
            QProgressBar::chunk {{
                background-color: {pri};
                border-radius: 5px;
            }}
            QMenu {{
                background-color: #ffffff;
                color: #1e2025;
                border: 1px solid #d4d8e2;
                border-radius: 8px;
                padding: 6px;
                font-size: 10pt;
            }}
            QMenu::item {{
                padding: 6px 22px;
                border-radius: 6px;
                font-size: 10pt;
            }}
            QMenu::item:hover {{
                background-color: {light_hover};
            }}
            QMenu::item:selected {{
                background-color: {pri};
                color: {text_on_pri};
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: #cfd4df;
                min-height: 28px;
                border-radius: 5px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {pri};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
                background: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
            QScrollBar:horizontal {{
                background: transparent;
                height: 10px;
                margin: 0px;
                border-radius: 5px;
            }}
            QScrollBar::handle:horizontal {{
                background: #cfd4df;
                min-width: 28px;
                border-radius: 5px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {pri};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
                background: none;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}
            """