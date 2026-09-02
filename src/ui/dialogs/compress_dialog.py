from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QCheckBox, QSpinBox, QGroupBox
)
import qtawesome as qta

class CompressDialog(QDialog):
    def __init__(self, item_count: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Comprimir / Compress")
        self.setFixedWidth(380)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        lbl_info = QLabel(f"Elementos a comprimir: <b>{item_count}</b>")
        layout.addWidget(lbl_info)

        # Formato de Salida
        layout.addWidget(QLabel("Formato del archivo:"))
        self.combo_format = QComboBox()
        self.combo_format.addItem("Archivo Estándar (.zip)", "zip")
        self.combo_format.addItem("Zstandard Ultrarrápido (.zst)", "zst")
        layout.addWidget(self.combo_format)

        # Nivel
        layout.addWidget(QLabel("Nivel de compresión:"))
        self.combo_level = QComboBox()
        self.combo_level.addItem("Rápido (Nivel 3)", 3)
        self.combo_level.addItem("Equilibrado (Nivel 9)", 9)
        self.combo_level.addItem("Ultra (Nivel 19)", 19)
        self.combo_level.setCurrentIndex(1)
        layout.addWidget(self.combo_level)

        # Contraseña AES-256 Directa
        sec_box = QGroupBox("Seguridad y Cifrado (AES-256)")
        sec_layout = QVBoxLayout(sec_box)
        self.txt_pass = QLineEdit()
        self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_pass.setPlaceholderText("Escriba la contraseña (o dejar en blanco)")
        sec_layout.addWidget(self.txt_pass)
        layout.addWidget(sec_box)

        # Volúmenes
        vol_box = QGroupBox("Dividir en partes")
        vol_layout = QHBoxLayout(vol_box)
        self.chk_split = QCheckBox("Activar:")
        self.spin_split = QSpinBox()
        self.spin_split.setRange(5, 102400)
        self.spin_split.setValue(100)
        self.spin_split.setSuffix(" MB")
        self.spin_split.setEnabled(False)
        self.chk_split.toggled.connect(self.spin_split.setEnabled)
        vol_layout.addWidget(self.chk_split)
        vol_layout.addWidget(self.spin_split)
        layout.addWidget(vol_box)

        # Botones
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton(qta.icon("fa5s.check", color="#52b774"), "Comprimir")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def get_options(self):
        return {
            "format": self.combo_format.currentData(),
            "level": self.combo_level.currentData(),
            "password": self.txt_pass.text().strip(),
            "split_mb": self.spin_split.value() if self.chk_split.isChecked() else 0
        }