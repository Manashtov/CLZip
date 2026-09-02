from pathlib import Path
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton
from src.core.hasher import ChecksumEngine

class ChecksumDialog(QDialog):
    def __init__(self, file_path: Path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setWindowTitle(f"Sumas de Verificación - {file_path.name}")
        self.setFixedWidth(460)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        hashes = ChecksumEngine.calculate_hashes(file_path)

        for algo, val in hashes.items():
            txt = QLineEdit(val)
            txt.setReadOnly(True)
            form.addRow(QLabel(f"<b>{algo}:</b>"), txt)

        layout.addLayout(form)
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)