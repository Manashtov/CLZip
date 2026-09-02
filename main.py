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

    if ico_path.exists() and sys.platform == "win32":
        app.setWindowIcon(QIcon(str(ico_path)))
    elif png_path.exists():
        app.setWindowIcon(QIcon(str(png_path)))

    window = MainWindow()

    # Si Windows pasa un archivo por argumento (doble clic)
    if len(sys.argv) > 1:
        target_path = Path(sys.argv[1]).resolve()
        if target_path.exists():
            if target_path.is_file():
                # Abre la carpeta contenedora y previsualiza el archivo
                window.navigate_to(target_path.parent)
                window.file_browser.preview_archive(target_path)
            elif target_path.is_dir():
                window.navigate_to(target_path)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


# Comando para eliminar build, dist, .exe, Carpeta innosetup y limpiar todo rastro de compilación para editar
# El proyecto antes de subirlo al repositorio
# Remove-Item -Recurse -Force -ErrorAction SilentlyContinue build, dist, Output, *.spec.bak; Get-ChildItem -Recurse -Include __pycache__, *.pyc, *.pyo | Remove-Item -Recurse -Force

# Eliminar el caché
# 

# Si se compila con el script dedicado en innosetup:
# python build_clean_dist.py 


# Si PowerShell arroja un error:
# Set-ExecutionPolicy RemoteSigned -Scope Process