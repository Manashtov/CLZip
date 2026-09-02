from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QTimer
from src.i18n.translator import tr

class StatusPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 2)
        layout.setSpacing(3)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid rgba(82, 183, 116, 0.3);
                border-radius: 4px;
                text-align: center;
                height: 12px;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background-color: #52b774;
                border-radius: 3px;
            }
        """)

        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.progress_bar)
        layout.addWidget(self.lbl_status)

        # Temporizador para ocultar suavemente el mensaje de éxito
        self.cleanup_timer = QTimer(self)
        self.cleanup_timer.setSingleShot(True)
        self.cleanup_timer.timeout.connect(self.clear)

    def set_progress(self, val: int, speed: float, elapsed: int, eta: int, stage_key: str = ""):
        self.cleanup_timer.stop()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(val)
        
        elapsed_str = f"{elapsed // 60:02d}:{elapsed % 60:02d}"
        eta_str = f"{eta // 60:02d}:{eta % 60:02d}"
        stage_text = tr(stage_key) if stage_key else tr("status_zip_stage")

        lbl_vel = tr("status_vel")
        lbl_el = tr("status_elapsed")
        lbl_rem = tr("status_remaining")

        self.lbl_status.setText(
            f"{stage_text}: {val}% | {lbl_vel}: {speed:.1f} MB/s | {lbl_el}: {elapsed_str} | {lbl_rem}: {eta_str}"
        )

    def set_completed(self, elapsed: float, count: int = 0, is_recrypt: bool = False):
        self.cleanup_timer.stop()
        
        # 1. Fijar la barra de progreso visible al 100%
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(100)

        # 2. Mostrar el mensaje de éxito con icono y tiempo
        if is_recrypt and count > 0:
            msg = tr("recrypt_success", count=count)
        else:
            time_display = f"{elapsed:.2f}" if elapsed >= 0.01 else "< 0.01"
            msg = tr("status_completed", time=time_display)

        self.lbl_status.setText(f"<b>{msg}</b>")

        # 3. Mantener el mensaje y la barra visibles durante 3.5 segundos
        self.cleanup_timer.start(3500)

    def set_ready(self, item_count: int = 0):
        """No borra si hay un mensaje de éxito recién mostrado."""
        if not self.cleanup_timer.isActive():
            self.progress_bar.setVisible(False)
            self.lbl_status.setText("")

    def clear(self):
        self.progress_bar.setVisible(False)
        self.lbl_status.setText("")