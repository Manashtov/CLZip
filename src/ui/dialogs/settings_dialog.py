from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QWidget,
    QLabel,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QKeySequenceEdit,
    QMessageBox,
    QGroupBox,
    QFrame
)
from PyQt6.QtCore import Qt, QSettings, pyqtSignal
from PyQt6.QtGui import QKeySequence, QPixmap, QFont
import qtawesome as qta

from src.i18n.translator import tr
from src.ui.themes import ThemeManager, COLOR_PALETTES
from src.utils.helpers import get_app_root

DEFAULT_SHORTCUTS = {
    "compress": "Ctrl+Shift+A",
    "extract": "Ctrl+E",
    "copy": "Ctrl+C",
    "paste": "Ctrl+V",
    "select_all": "Ctrl+A",
    "delete": "Del",
    "properties": "Alt+Enter",
    "set_password": "Ctrl+P",
}

class SettingsDialog(QDialog):
    theme_updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_settings = QSettings("clzip", "MainWindow")
        self.shortcut_settings = QSettings("clzip", "Shortcuts")
        self.root_dir = get_app_root()

        self.dark_mode = self.main_settings.value("dark_mode", True, type=bool)
        self.current_palette = self.main_settings.value("palette", "Verde", type=str)

        self.resize(600, 480)
        self.setMinimumSize(560, 420)
        self.setFont(QFont("Segoe UI", 10))

        self._shortcut_edits: dict[str, QKeySequenceEdit] = {}

        self._build_ui()
        self._apply_dialog_style()
        self.retranslate_ui()
        self._load_current_values()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        self.tabs = QTabWidget(self)

        self.tab_shortcuts = QWidget()
        self.tab_shortcuts.setObjectName("TabContent")
        self._setup_shortcuts_tab(self.tab_shortcuts)
        
        self.tab_appearance = QWidget()
        self.tab_appearance.setObjectName("TabContent")
        self._setup_appearance_tab(self.tab_appearance)
        
        self.tab_info = QWidget()
        self.tab_info.setObjectName("TabContent")
        self._setup_info_tab(self.tab_info)
        
        self.tabs.addTab(self.tab_shortcuts, "")
        self.tabs.addTab(self.tab_appearance, "")
        self.tabs.addTab(self.tab_info, "")
        
        self._update_tab_icons()

        main_layout.addWidget(self.tabs)

        button_layout = QHBoxLayout()
        self.btn_reset = QPushButton()
        self.btn_cancel = QPushButton()
        self.btn_apply = QPushButton()
        self.btn_apply.setObjectName("BtnApply")

        button_layout.addWidget(self.btn_reset)
        button_layout.addStretch()
        button_layout.addWidget(self.btn_cancel)
        button_layout.addWidget(self.btn_apply)

        self.btn_reset.clicked.connect(self._reset_defaults)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_apply.clicked.connect(self._apply_changes)

        main_layout.addLayout(button_layout)

    def _update_tab_icons(self):
        pal = COLOR_PALETTES.get(self.current_palette, COLOR_PALETTES["Verde"])
        pri = pal["primary"]
        self.tabs.setTabIcon(0, qta.icon("fa5s.keyboard", color=pri))
        self.tabs.setTabIcon(1, qta.icon("fa5s.palette", color=pri))
        self.tabs.setTabIcon(2, qta.icon("fa5s.info-circle", color=pri))

    def _setup_shortcuts_tab(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(14, 18, 14, 14)
        layout.setSpacing(14)

        self.lbl_shortcuts_hint = QLabel(parent)
        self.lbl_shortcuts_hint.setWordWrap(True)
        layout.addWidget(self.lbl_shortcuts_hint)

        self.table_shortcuts = QTableWidget(len(DEFAULT_SHORTCUTS), 2, parent)
        self.table_shortcuts.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_shortcuts.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_shortcuts.verticalHeader().setVisible(False)
        self.table_shortcuts.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table_shortcuts.setShowGrid(False)
        
        self.table_shortcuts.verticalHeader().setDefaultSectionSize(46)

        row = 0
        for action_key in DEFAULT_SHORTCUTS.keys():
            item = QTableWidgetItem()
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item.setData(Qt.ItemDataRole.UserRole, action_key)
            self.table_shortcuts.setItem(row, 0, item)

            edit = QKeySequenceEdit(parent)
            self._shortcut_edits[action_key] = edit
            self.table_shortcuts.setCellWidget(row, 1, edit)
            row += 1

        layout.addWidget(self.table_shortcuts)

    def _setup_appearance_tab(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(18, 22, 18, 18)
        layout.setSpacing(18)

        self.grp_palette = QGroupBox(parent)
        box_layout = QVBoxLayout(self.grp_palette)
        box_layout.setContentsMargins(16, 28, 16, 20)

        self.lbl_palette_hint = QLabel(self.grp_palette)
        self.lbl_palette_hint.setWordWrap(True)
        box_layout.addWidget(self.lbl_palette_hint)

        self.combo_palette = QComboBox(self.grp_palette)
        self.combo_palette.addItems(list(COLOR_PALETTES.keys()))
        self.combo_palette.setFixedHeight(38)
        box_layout.addWidget(self.combo_palette)

        layout.addWidget(self.grp_palette)
        layout.addStretch()

    def _setup_info_tab(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        self.lbl_info_logo = QLabel(parent)
        logo_path = self.root_dir / "assets" / "icon_128.png"
        if not logo_path.exists():
            logo_path = self.root_dir / "assets" / "clzip_logo_128x128.png"
        if not logo_path.exists():
            logo_path = self.root_dir / "assets" / "icon_256.png"

        if logo_path.exists():
            pixmap = QPixmap(str(logo_path)).scaled(
                52, 52,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.lbl_info_logo.setPixmap(pixmap)
            self.lbl_info_logo.setFixedSize(52, 52)

        info_header_texts = QVBoxLayout()
        info_header_texts.setSpacing(4)

        lbl_app_name = QLabel("<b>CLZip</b> v1.0")
        lbl_app_name.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.lbl_app_desc = QLabel(parent)
        self.lbl_app_desc.setObjectName("SubtitleLabel")

        info_header_texts.addWidget(lbl_app_name)
        info_header_texts.addWidget(self.lbl_app_desc)

        header_layout.addWidget(self.lbl_info_logo)
        header_layout.addLayout(info_header_texts)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        self.lbl_author_tag = QLabel(f"<b>{tr('info_author')}</b> Manashtov")
        self.lbl_tech_tag = QLabel(f"<b>{tr('info_tech')}</b> Python 3, PyQt6, Zstandard, Pyzipper")
        self.lbl_license_tag = QLabel(f"<b>{tr('info_license')}</b> GPL-3.0")

        self.github_label = QLabel()
        self.github_label.setOpenExternalLinks(True)

        layout.addWidget(self.lbl_author_tag)
        layout.addWidget(self.lbl_tech_tag)
        layout.addWidget(self.lbl_license_tag)
        layout.addWidget(self.github_label)
        layout.addStretch()
        
        self._update_github_link()

    def _update_github_link(self):
        pal = COLOR_PALETTES.get(self.current_palette, COLOR_PALETTES["Verde"])
        pri = pal["primary"]
        self.github_label.setText(
            f'<b>GitHub:</b> <a href="https://github.com/Manashtov/CLZip" style="color: {pri}; text-decoration: none;">'
            f'github.com/Manashtov/CLZip</a>'
        )

    def retranslate_ui(self):
        self.setWindowTitle(tr("settings_title"))

        self.tabs.setTabText(0, f" {tr('tab_shortcuts')} ")
        self.tabs.setTabText(1, f" {tr('tab_appearance')} ")
        self.tabs.setTabText(2, f" {tr('tab_info')} ")

        self.lbl_shortcuts_hint.setText(tr("shortcuts_hint"))
        self.table_shortcuts.setHorizontalHeaderLabels([tr("col_action"), tr("col_shortcut")])

        action_labels = {
            "compress": tr("ctx_compress"),
            "extract": tr("ctx_extract"),
            "copy": tr("ctx_copy"),
            "paste": tr("ctx_paste"),
            "select_all": tr("ctx_select_all"),
            "delete": tr("ctx_delete"),
            "properties": tr("ctx_properties"),
            "set_password": tr("ctx_password")
        }

        for row in range(self.table_shortcuts.rowCount()):
            item = self.table_shortcuts.item(row, 0)
            if item:
                action_key = item.data(Qt.ItemDataRole.UserRole)
                item.setText(action_labels.get(action_key, action_key))

        self.grp_palette.setTitle(tr("palette_group"))
        self.lbl_palette_hint.setText(tr("palette_hint"))

        self.lbl_app_desc.setText(tr("info_app_desc"))
        self.lbl_author_tag.setText(f"<b>{tr('info_author')}</b> Manashtov")
        self.lbl_tech_tag.setText(f"<b>{tr('info_tech')}</b> Python 3, PyQt6, Zstandard, Pyzipper")
        self.lbl_license_tag.setText(f"<b>{tr('info_license')}</b> GPL-3.0")

        self.btn_reset.setText(tr("btn_reset"))
        self.btn_apply.setText(tr("btn_apply"))
        self.btn_cancel.setText(tr("btn_cancel"))

    def _apply_dialog_style(self):
        pal = COLOR_PALETTES.get(self.current_palette, COLOR_PALETTES["Verde"])
        pri = pal["primary"]
        hover = pal["hover"]
        light_hover = pal.get("light_hover", "rgba(82, 183, 116, 0.18)")
        text_on_pri = pal["text_on_pri"]

        if self.dark_mode:
            bg_pane = "#121316"
            bg_tab = "#18191f"
            text_main = "#e2e4e9"
            text_dim = "#9da1b0"
            border = "#2f323d"
            input_bg = "#18191f"
        else:
            bg_pane = "#ffffff"
            bg_tab = "#f5f6f8"
            text_main = "#2d3139"
            text_dim = "#6c6f85"
            border = "#d4d8e2"
            input_bg = "#ffffff"

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_pane};
                color: {text_main};
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }}
            QLabel {{
                color: {text_main};
                font-size: 13px;
            }}
            QLabel#SubtitleLabel {{
                color: {text_dim};
                font-size: 12px;
            }}
            QWidget#TabContent {{
                background-color: {bg_pane};
            }}
            QGroupBox {{
                font-weight: bold;
                color: {text_main};
                border: 2px solid {border};
                border-radius: 10px;
                margin-top: 12px;
                font-size: 13px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 6px;
                color: {pri};
            }}
            QComboBox {{
                background-color: {input_bg};
                border: 2px solid {border};
                border-radius: 8px;
                padding: 4px 12px;
                color: {text_main};
                font-size: 13px;
            }}
            QComboBox:hover {{
                border-color: {pri};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {input_bg};
                color: {text_main};
                border: 2px solid {pri};
                border-radius: 6px;
                outline: none;
                font-size: 13px;
            }}
            QComboBox QAbstractItemView::item {{
                min-height: 32px;
                padding-left: 8px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {light_hover};
            }}
            
            QTabWidget::pane {{
                border: 2px solid {border};
                background-color: {bg_pane};
                border-radius: 10px;
                top: -2px;
            }}
            QTabBar::tab {{
                background-color: {bg_tab};
                color: {text_dim};
                padding: 10px 18px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 4px;
                font-size: 13px;
            }}
            QTabBar::tab:hover {{
                color: {text_main};
            }}
            QTabBar::tab:selected {{
                background-color: {bg_pane};
                color: {pri};
                font-weight: bold;
                border-top: 3px solid {pri};
                border-left: 2px solid {border};
                border-right: 2px solid {border};
                border-bottom: 2px solid {bg_pane};
            }}

            QTableWidget {{
                background-color: {bg_pane};
                border: 2px solid {border};
                border-radius: 10px;
                color: {text_main};
                padding: 4px;
                font-size: 13px;
            }}
            QHeaderView::section {{
                background-color: transparent;
                color: {text_dim};
                padding: 8px;
                border: none;
                border-bottom: 2px solid {border};
                font-weight: bold;
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            
            QKeySequenceEdit {{
                background-color: {input_bg};
                color: {pri};
                border: 2px solid {border};
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 13px;
                min-height: 22px;
            }}
            QKeySequenceEdit:focus {{
                border-color: {pri};
            }}

            QScrollBar:vertical {{
                border: none;
                background-color: transparent;
                width: 12px;
                margin: 4px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {light_hover};
                min-height: 30px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {pri};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                height: 0px; background: none;
            }}

            QPushButton {{
                background-color: transparent;
                color: {text_main};
                border: 2px solid {pri};
                border-radius: 16px;
                padding: 6px 18px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {light_hover};
            }}
            QPushButton#BtnApply {{
                background-color: {pri};
                color: {text_on_pri};
            }}
            QPushButton#BtnApply:hover {{
                background-color: {hover};
            }}
        """)

    def _load_current_values(self):
        idx = self.combo_palette.findText(self.current_palette, Qt.MatchFlag.MatchFixedString)
        if idx >= 0:
            self.combo_palette.setCurrentIndex(idx)

        for action_key, default_seq in DEFAULT_SHORTCUTS.items():
            saved_val = self.shortcut_settings.value(action_key, default_seq)
            if action_key in self._shortcut_edits:
                self._shortcut_edits[action_key].setKeySequence(QKeySequence(saved_val))

    def _reset_defaults(self):
        idx = self.combo_palette.findText("Verde", Qt.MatchFlag.MatchFixedString)
        if idx >= 0:
            self.combo_palette.setCurrentIndex(idx)

        for action_key, default_seq in DEFAULT_SHORTCUTS.items():
            if action_key in self._shortcut_edits:
                self._shortcut_edits[action_key].setKeySequence(QKeySequence(default_seq))

    def _apply_changes(self):
        chosen_palette = self.combo_palette.currentText().strip()
        self.current_palette = chosen_palette
        self.main_settings.setValue("palette", chosen_palette)

        for action_key, edit in self._shortcut_edits.items():
            seq_str = edit.keySequence().toString()
            self.shortcut_settings.setValue(action_key, seq_str)

        self._apply_dialog_style()
        self._update_tab_icons()
        self._update_github_link()
        self.theme_updated.emit()

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(tr("btn_settings"))
        msg_box.setText(tr("settings_saved"))
        msg_box.setIcon(QMessageBox.Icon.NoIcon)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()