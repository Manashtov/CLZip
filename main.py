import sys
import os
import ctypes
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, qInstallMessageHandler, QtMsgType

from src.ui.main_window import MainWindow
from src.utils.helpers import get_app_root



def qt_message_filter(mode, context, message):
    # Suprime el mensaje interno de punto <= 0 generado por cálculos en estilos QSS
    if "setPointSize" in message or "Point size <= 0" in message:
        return
    # Imprime otros errores relevantes normalmente
    if mode in (QtMsgType.QtWarningMsg, QtMsgType.QtCriticalMsg, QtMsgType.QtFatalMsg):
        sys.stderr.write(f"{message}\n")


def setup_windows_app_id():
    if os.name == "nt":
        try:
            my_app_id = "manashtov.clzip.filemanager.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)
        except Exception:
            pass


def main():
    # Instalar filtro antes de iniciar Qt
    qInstallMessageHandler(qt_message_filter)
    setup_windows_app_id()

    app = QApplication(sys.argv)
    app.setApplicationName("CLZip")
    app.setOrganizationName("clzip")

    base_font = QFont("Segoe UI", 10)
    app.setFont(base_font)

    root_dir = get_app_root()
    ico_path = root_dir / "assets" / "icon.ico"
    png_path = root_dir / "assets" / "icon_256.png"

    if ico_path.exists():
        app.setWindowIcon(QIcon(str(ico_path)))
    elif png_path.exists():
        app.setWindowIcon(QIcon(str(png_path)))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()