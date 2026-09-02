import os
import sys
import datetime
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTabWidget, QWidget, QCheckBox, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox
)
from PyQt6.QtCore import Qt
import qtawesome as qta
from src.utils.helpers import format_bytes

class PropertiesDialog(QDialog):
    """Ventana de propiedades compacta y multiplataforma."""
    def __init__(self, target_path: Path, parent=None):
        super().__init__(parent)
        self.target_path = Path(target_path).resolve()
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle(f"Propiedades: {self.target_path.name}")
        self.setFixedSize(360, 440)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        tabs = QTabWidget()
        
        tab_general = QWidget()
        self._setup_general_tab(tab_general)
        tabs.addTab(tab_general, "General")

        tab_security = QWidget()
        self._setup_security_tab(tab_security)
        tabs.addTab(tab_security, "Seguridad")

        tab_sharing = QWidget()
        self._setup_sharing_tab(tab_sharing)
        tabs.addTab(tab_sharing, "Compartir")

        layout.addWidget(tabs)

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        
        btn_ok = QPushButton("Aceptar")
        btn_ok.setFixedWidth(80)
        btn_ok.clicked.connect(self.accept)
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedWidth(80)
        btn_cancel.clicked.connect(self.reject)

        btn_box.addWidget(btn_ok)
        btn_box.addWidget(btn_cancel)
        layout.addLayout(btn_box)

    def _setup_general_tab(self, tab: QWidget):
        vbox = QVBoxLayout(tab)
        vbox.setContentsMargins(12, 12, 12, 12)
        vbox.setSpacing(6)

        header = QHBoxLayout()
        lbl_icon = QLabel()
        if self.target_path.is_dir():
            lbl_icon.setPixmap(qta.icon("fa5s.folder", color="#e5a93b").pixmap(30, 30))
        else:
            lbl_icon.setPixmap(qta.icon("fa5s.file-archive", color="#52b774").pixmap(30, 30))
        
        txt_name = QLineEdit(self.target_path.name)
        header.addWidget(lbl_icon)
        header.addWidget(txt_name)
        vbox.addLayout(header)
        vbox.addWidget(self._create_separator())

        is_dir = self.target_path.is_dir()
        file_count, dir_count, total_size = 0, 0, 0

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
            type_str = "Carpeta de archivos"
        else:
            total_size = self.target_path.stat().st_size
            type_str = f"Archivo {self.target_path.suffix.upper() or 'desconocido'}"

        stat = self.target_path.stat()
        mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M:%S")

        size_human = format_bytes(total_size)
        size_formatted = f"{size_human} ({total_size:,} bytes)"

        vbox.addLayout(self._build_row("Tipo:", type_str))
        vbox.addLayout(self._build_row("Ubicación:", str(self.target_path.parent)))
        vbox.addLayout(self._build_row("Tamaño:", size_formatted))

        if is_dir:
            vbox.addLayout(self._build_row("Contenido:", f"{file_count} arch., {dir_count} carp."))

        vbox.addWidget(self._create_separator())
        vbox.addLayout(self._build_row("Modificado:", mtime))
        vbox.addWidget(self._create_separator())

        attr_layout = QHBoxLayout()
        lbl_attr = QLabel("Atributos:")
        lbl_attr.setFixedWidth(75)
        chk_readonly = QCheckBox("Solo lectura")
        chk_hidden = QCheckBox("Oculto")

        # Comprobación de atributos multiplataforma
        if sys.platform == "win32":
            try:
                import ctypes
                attrs = ctypes.windll.kernel32.GetFileAttributesW(str(self.target_path))
                chk_hidden.setChecked(bool(attrs & 2))
                chk_readonly.setChecked(bool(attrs & 1))
            except Exception:
                chk_hidden.setChecked(self.target_path.name.startswith("."))
        else:
            chk_hidden.setChecked(self.target_path.name.startswith("."))
            chk_readonly.setChecked(not os.access(self.target_path, os.W_OK))

        attr_layout.addWidget(lbl_attr)
        attr_layout.addWidget(chk_readonly)
        attr_layout.addWidget(chk_hidden)
        attr_layout.addStretch()
        vbox.addLayout(attr_layout)
        vbox.addStretch()

    def _setup_security_tab(self, tab: QWidget):
        vbox = QVBoxLayout(tab)
        vbox.setContentsMargins(12, 12, 12, 12)
        vbox.setSpacing(6)

        vbox.addWidget(QLabel("<b>Permisos del Archivo / Carpeta:</b>"))
        
        table = QTableWidget(4, 2)
        table.setHorizontalHeaderLabels(["Permiso", "Estado"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        perms = [
            ("Lectura", os.access(self.target_path, os.R_OK)),
            ("Escritura", os.access(self.target_path, os.W_OK)),
            ("Ejecución", os.access(self.target_path, os.X_OK)),
            ("Control Total", os.access(self.target_path, os.R_OK) and os.access(self.target_path, os.W_OK))
        ]

        for i, (name, val) in enumerate(perms):
            table.setItem(i, 0, QTableWidgetItem(name))
            st_item = QTableWidgetItem("Permitido" if val else "Denegado")
            st_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(i, 1, st_item)

        vbox.addWidget(table)
        vbox.addStretch()

    def _setup_sharing_tab(self, tab: QWidget):
        vbox = QVBoxLayout(tab)
        vbox.setContentsMargins(12, 12, 12, 12)
        box = QGroupBox("Recurso Compartido")
        vbox_b = QVBoxLayout(box)
        vbox_b.addWidget(QLabel(f"<b>Ruta local:</b> {self.target_path}"))
        vbox_b.addWidget(QLabel("Estado: No compartido en red local"))
        vbox.addWidget(box)
        vbox.addStretch()

    def _build_row(self, label: str, value: str) -> QHBoxLayout:
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setFixedWidth(75)
        lbl.setStyleSheet("color: #718096; font-weight: 500;")
        val = QLabel(value)
        val.setWordWrap(True)
        row.addWidget(lbl)
        row.addWidget(val, 1)
        return row

    def _create_separator(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #cbd5e1;")
        return line