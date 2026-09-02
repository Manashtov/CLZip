import os
from pathlib import Path

from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QSplitter,
    QMessageBox,
    QFileDialog,
    QInputDialog
)

from src.utils.helpers import get_app_root, check_free_space, format_bytes
from src.i18n import translator
from src.i18n.translator import tr
from src.ui.themes import ThemeManager
from src.ui.panels.file_browser_panel import FileBrowserPanel
from src.ui.panels.sidebar_panel import SidebarPanel
from src.ui.panels.toolbar_panel import ToolBarPanel
from src.ui.panels.status_panel import StatusPanel
from src.ui.dialogs.settings_dialog import SettingsDialog
from src.ui.dialogs.compress_dialog import CompressDialog
from src.ui.worker import CompressionWorker
from src.core.compressor import ZstdEngine


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.root_dir = get_app_root()
        self.settings = QSettings("clzip", "MainWindow")
        self.shortcut_settings = QSettings("clzip", "Shortcuts")
        self.worker = None

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
        
        self.file_browser.tree.setFocus()

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
        self.file_browser.path_changed.connect(self.path_bar.setText)
        self.sidebar_panel.path_selected.connect(self.navigate_to)

        # Operaciones del explorador
        self.file_browser.compress_requested.connect(self._start_compress)
        self.file_browser.extract_to_requested.connect(self._start_extract)
        self.file_browser.password_requested.connect(self._on_password_requested)
        self.file_browser.remove_password_requested.connect(self._on_remove_password_requested)

        # Barra de herramientas
        self.toolbar_panel.extract_requested.connect(self._on_toolbar_extract)
        self.toolbar_panel.home_requested.connect(lambda: self.navigate_to(Path.home()))
        self.toolbar_panel.up_requested.connect(self._go_up)
        self.toolbar_panel.refresh_requested.connect(self.file_browser.refresh)
        self.toolbar_panel.theme_toggled.connect(self._toggle_theme)
        self.toolbar_panel.lang_toggled.connect(self._toggle_language)
        self.toolbar_panel.settings_requested.connect(self._open_settings)

    def _on_toolbar_extract(self):
        selected = self.file_browser.get_selected_paths()
        archive = None
        if selected and selected[0].lower().endswith(tuple(self.file_browser.ARCHIVE_EXTS)):
            archive = selected[0]
        elif self.file_browser.preview_archive_path:
            archive = str(self.file_browser.preview_archive_path)

        if archive:
            dest = QFileDialog.getExistingDirectory(self, tr("dlg_extract_select_dest"), str(self.file_browser.current_directory))
            if dest:
                self._start_extract(archive, dest)

    def _on_password_requested(self, archive_path: str):
        arc_p = Path(archive_path)
        is_enc = ZstdEngine.is_archive_encrypted(arc_p)
        curr_pwd = ""

        if is_enc:
            pwd_cur, ok_cur = QInputDialog.getText(
                self, tr("pwd_current_title"), tr("pwd_current_prompt"), QLineEdit.EchoMode.Password
            )
            if not ok_cur:
                return
            curr_pwd = pwd_cur

        new_pwd, ok_new = QInputDialog.getText(
            self, tr("pwd_protect_title", name=arc_p.name), tr("pwd_protect_prompt", name=arc_p.name), QLineEdit.EchoMode.Password
        )
        if not ok_new:
            return

        self._execute_recrypt(arc_p, new_pwd.strip(), curr_pwd)

    def _on_remove_password_requested(self, archive_path: str):
        arc_p = Path(archive_path)
        pwd_cur, ok_cur = QInputDialog.getText(
            self, tr("pwd_remove_title", name=arc_p.name), tr("pwd_current_prompt"), QLineEdit.EchoMode.Password
        )
        if not ok_cur or not pwd_cur:
            return

        self._execute_recrypt(arc_p, "", pwd_cur)

    def _execute_recrypt(self, arc_p: Path, new_password: str, current_password: str):
        self.worker = CompressionWorker(
            mode="recrypt",
            sources=[arc_p],
            dest=arc_p.parent,
            password=new_password,
            current_password=current_password
        )
        self.worker.progress_changed.connect(self.status_panel.set_progress)
        self.worker.operation_finished.connect(lambda el, ct: self._on_operation_finished(el, ct, is_recrypt=True))
        self.worker.error_occurred.connect(lambda err: QMessageBox.critical(self, "Error", err))
        self.worker.start()

    def _start_compress(self, paths: list):
        if not paths:
            return
        dlg = CompressDialog(len(paths), self)
        if dlg.exec():
            opts = dlg.get_options()
            first_base = os.path.basename(paths[0].rstrip('/\\'))
            fmt = opts.get("format", "zip")
            dest_path = self.file_browser.current_directory / f"{first_base}.{fmt}"

            self.worker = CompressionWorker(
                mode="compress",
                sources=[Path(p) for p in paths],
                dest=Path(dest_path),
                level=opts.get("level", 3),
                split_mb=opts.get("split_mb", 0),
                password=opts.get("password", ""),
                format_type=fmt
            )
            self.worker.progress_changed.connect(self.status_panel.set_progress)
            self.worker.operation_finished.connect(lambda el, ct: self._on_operation_finished(el, ct))
            self.worker.error_occurred.connect(lambda err: QMessageBox.critical(self, "Error", err))
            self.worker.start()

    def _start_extract(self, archive_path: str, dest_dir: str):
        if not archive_path or not dest_dir:
            return

        out_path = Path(dest_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        pwd = ""
        if ZstdEngine.is_archive_encrypted(Path(archive_path)):
            pwd, ok = QInputDialog.getText(
                self, tr("pwd_current_title"), tr("pwd_current_prompt"), QLineEdit.EchoMode.Password
            )
            if not ok:
                return

        # Comprobación previa de espacio libre en disco
        required_size = ZstdEngine.get_uncompressed_size(Path(archive_path), pwd)
        has_space, free_bytes, req_bytes = check_free_space(out_path, required_size)

        if not has_space:
            QMessageBox.critical(
                self,
                "Espacio insuficiente",
                f"No hay suficiente espacio en disco para extraer el archivo.\n\n"
                f"Espacio necesario: {format_bytes(req_bytes)}\n"
                f"Espacio disponible: {format_bytes(free_bytes)}"
            )
            return

        self.worker = CompressionWorker(
            mode="decompress",
            sources=[Path(archive_path)],
            dest=out_path,
            password=pwd
        )
        self.worker.progress_changed.connect(self.status_panel.set_progress)
        self.worker.operation_finished.connect(lambda el, ct: self._on_operation_finished(el, ct))
        self.worker.error_occurred.connect(lambda err: QMessageBox.critical(self, "Error", err))
        self.worker.start()

    def _on_operation_finished(self, elapsed: float, affected_count: int, is_recrypt: bool = False):
        self.status_panel.set_completed(elapsed, affected_count, is_recrypt=is_recrypt)
        self.file_browser.refresh()

    def navigate_to(self, path: Path):
        p = Path(path).resolve()
        if p.exists() and p.is_dir():
            self.file_browser.populate(p)
            self.path_bar.setText(str(p))
            self.status_panel.set_ready()
        else:
            self._silent_message("Error", f"No se puede acceder a la ruta especificada:\n{p}")

    def _go_up(self):
        if self.file_browser.preview_archive_path:
            self.file_browser.populate(self.file_browser.current_directory)
            return

        current = self.file_browser.current_directory
        parent = current.parent
        if parent and parent != current:
            self.navigate_to(parent)

    def _on_path_entered(self):
        target = Path(self.path_bar.text().strip())
        if target.exists() and target.is_dir():
            self.navigate_to(target)
            self.file_browser.tree.setFocus()
        else:
            self._silent_message("Ruta Inválida", f"La ruta no existe o no es una carpeta válida:\n{target}")
            self.path_bar.setText(str(self.file_browser.current_directory))

    def _toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.settings.setValue("dark_mode", self.dark_mode)
        self._apply_current_theme()

    def _apply_current_theme(self):
        sheet = ThemeManager.get_theme(self.dark_mode, self.current_palette)
        self.setStyleSheet(sheet)
        self.toolbar_panel.update_theme_icons(self.dark_mode, self.current_palette)
        
        pri = ThemeManager.get_primary_color(self.current_palette)
        self.sidebar_panel.populate_bookmarks(pri)

    def _toggle_language(self):
        cur = translator.get_locale()
        new_lang = "en" if cur == "es" else "es"
        translator.set_locale(new_lang)

        self.toolbar_panel.retranslate_ui()
        self.file_browser.retranslate_ui()

        pri = ThemeManager.get_primary_color(self.current_palette)
        self.sidebar_panel.populate_bookmarks(pri)
        self.file_browser.refresh()

    def _open_settings(self):
        dlg = SettingsDialog(self)
        dlg.theme_updated.connect(self._sync_settings)
        dlg.exec()

    def _sync_settings(self):
        self.current_palette = self.settings.value("palette", self.current_palette, type=str)
        self._apply_current_theme()
        self.file_browser.update_action_shortcuts()
        self.file_browser.populate(self.file_browser.current_directory)

    def _silent_message(self, title: str, text: str):
        box = QMessageBox(self)
        box.setWindowTitle(title)
        box.setText(text)
        box.setIcon(QMessageBox.Icon.NoIcon)
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.exec()