import os
import sys
import datetime
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTabWidget, QWidget, QCheckBox, QPushButton, QFrame
)
from PyQt6.QtCore import Qt
import qtawesome as qta
from src.utils.helpers import format_bytes

class PropertiesDialog(QDialog):
    """Ventana de propiedades idéntica al cuadro de diálogo de Windows/PeaZip."""
    def __init__(self, target_path: Path, parent=None):
        super().__init__(parent)
        self.target_path = Path(target_path).resolve()
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle(f"Propiedades de {self.target_path.name}")
        self.setFixedSize(380, 520)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)

        # Tabs superiores (General, Compartir, Seguridad, etc.)
        tabs = QTabWidget()
        tab_general = QWidget()
        self._setup_general_tab(tab_general)
        tabs.addTab(tab_general, "General")
        tabs.addTab(QWidget(), "Seguridad")
        tabs.addTab(QWidget(), "Personalizar")
        layout.addWidget(tabs)

        # Botones inferiores (Aceptar, Cancelar, Aplicar)
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        
        btn_ok = QPushButton("Aceptar")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_apply = QPushButton("Aplicar")
        btn_apply.setEnabled(False)

        btn_box.addWidget(btn_ok)
        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_apply)
        layout.addLayout(btn_box)

    def _setup_general_tab(self, tab: QWidget):
        vbox = QVBoxLayout(tab)
        vbox.setSpacing(10)

        # Cabecera: Icono + Nombre editable
        header_layout = QHBoxLayout()
        lbl_icon = QLabel()
        if self.target_path.is_dir():
            lbl_icon.setPixmap(qta.icon("fa5s.folder", color="#e5a93b").pixmap(40, 40))
        else:
            lbl_icon.setPixmap(qta.icon("fa5s.file-archive", color="#52b774").pixmap(40, 40))
        
        txt_name = QLineEdit(self.target_path.name)
        header_layout.addWidget(lbl_icon)
        header_layout.addWidget(txt_name)
        vbox.addLayout(header_layout)
        vbox.addWidget(self._create_separator())

        # Métricas del archivo / carpeta
        is_dir = self.target_path.is_dir()
        file_count = 0
        dir_count = 0
        total_size = 0

        if is_dir:
            for root, dirs, files in os.walk(self.target_path):
                dir_count += len(dirs)
                file_count += len(files)
                for f in files:
                    fp = Path(root) / f
                    try:
                        total_size += fp.stat().st_size
                    except OSError:
                        pass
            type_str = f"Carpeta de archivos ({self.target_path.suffix or '.0'})"
        else:
            total_size = self.target_path.stat().st_size
            type_str = f"Archivo {self.target_path.suffix.upper()}"

        stat = self.target_path.stat()
        created_time = datetime.datetime.fromtimestamp(stat.st_ctime).strftime("%A, %d de %B de %Y, %H:%M:%S")
        
        size_human = format_bytes(total_size)
        size_formatted = f"{size_human} ({total_size:,} bytes)".replace(",", ".")

        vbox.addLayout(self._build_row("Tipo:", type_str))
        vbox.addLayout(self._build_row("Ubicación:", str(self.target_path.parent)))
        vbox.addLayout(self._build_row("Tamaño:", size_formatted))
        vbox.addLayout(self._build_row("Tamaño en disco:", size_formatted))

        if is_dir:
            vbox.addLayout(self._build_row("Contiene:", f"{file_count} archivos, {dir_count} carpetas"))

        vbox.addWidget(self._create_separator())
        vbox.addLayout(self._build_row("Creado:", created_time))
        vbox.addWidget(self._create_separator())

        # Atributos
        attr_layout = QHBoxLayout()
        lbl_attr = QLabel("Atributos:")
        lbl_attr.setFixedWidth(80)
        chk_readonly = QCheckBox("Solo lectura")
        chk_hidden = QCheckBox("Oculto")

        # Comprobar si está oculto (Windows/Linux)
        if sys.platform == "win32":
            import ctypes
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(self.target_path))
            chk_hidden.setChecked(bool(attrs & 2))
        else:
            chk_hidden.setChecked(self.target_path.name.startswith("."))

        attr_layout.addWidget(lbl_attr)
        attr_layout.addWidget(chk_readonly)
        attr_layout.addWidget(chk_hidden)
        attr_layout.addStretch()
        vbox.addLayout(attr_layout)
        vbox.addStretch()

    def _build_row(self, label: str, value: str) -> QHBoxLayout:
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setFixedWidth(100)
        lbl.setStyleSheet("color: #718096; font-weight: 500;")
        val = QLabel(value)
        val.setWordWrap(True)
        val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        row.addWidget(lbl)
        row.addWidget(val, 1)
        return row

    def _create_separator(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #cbd5e1;")
        return line