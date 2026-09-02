import os
import sys
import shutil
from pathlib import Path

def get_app_root() -> Path:
    """Retorna la raíz del proyecto compatible con PyInstaller, Nuitka y desarrollo."""
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    if "__compiled__" in globals() or getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent.parent

def format_bytes(size: int) -> str:
    """Formatea bytes a formato legible (KB, MB, GB, etc.)."""
    if size < 1024:
        return f"{size} B"
    for unit in ["KB", "MB", "GB", "TB"]:
        size /= 1024.0
        if size < 1024.0:
            return f"{size:.2f} {unit}"
    return f"{size:.2f} PB"

def check_free_space(dest_path: Path, required_bytes: int) -> tuple[bool, int, int]:
    """
    Verifica si hay suficiente espacio en disco en la partición de destino.
    Retorna: (hay_espacio, espacio_libre, espacio_requerido)
    """
    dest = Path(dest_path).resolve()
    while not dest.exists():
        dest = dest.parent
    usage = shutil.disk_usage(dest)
    return usage.free >= required_bytes, usage.free, required_bytes

def move_to_trash(path: Path) -> bool:
    """Mueve un archivo o carpeta a la Papelera de Reciclaje (Windows / macOS / Linux)."""
    path = Path(path).resolve()
    if not path.exists():
        return False

    # Intento 1: Uso de send2trash si está disponible
    try:
        import send2trash
        send2trash.send2trash(str(path))
        return True
    except ImportError:
        pass

    # Intento 2: Papelera nativa en Windows
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            class SHFILEOPSTRUCTW(ctypes.Structure):
                _fields_ = [
                    ("hwnd", wintypes.HWND),
                    ("wFunc", wintypes.UINT),
                    ("pFrom", wintypes.LPCWSTR),
                    ("pTo", wintypes.LPCWSTR),
                    ("fFlags", wintypes.WORD),
                    ("fAnyOperationsAborted", wintypes.BOOL),
                    ("hNameMappings", wintypes.LPVOID),
                    ("lpszProgressTitle", wintypes.LPCWSTR),
                ]

            file_op = SHFILEOPSTRUCTW()
            file_op.hwnd = None
            file_op.wFunc = 0x0003  # FO_DELETE
            file_op.pFrom = str(path) + "\0\0"
            file_op.pTo = None
            file_op.fFlags = 0x0040 | 0x0010 | 0x0004 | 0x0400  # FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT | FOF_NOERRORUI
            file_op.fAnyOperationsAborted = False
            file_op.hNameMappings = None
            file_op.lpszProgressTitle = None

            result = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(file_op))
            if result == 0:
                return True
        except Exception:
            pass

    # Intento 3: Papelera freedesktop en Linux (~/.local/share/Trash)
    if sys.platform.startswith("linux"):
        try:
            trash_dir = Path.home() / ".local" / "share" / "Trash" / "files"
            trash_dir.mkdir(parents=True, exist_ok=True)
            target = trash_dir / path.name
            counter = 1
            while target.exists():
                target = trash_dir / f"{path.stem}_{counter}{path.suffix}"
                counter += 1
            shutil.move(str(path), str(target))
            return True
        except Exception:
            pass

    # Intento 4: Papelera en macOS (~/.Trash)
    if sys.platform == "darwin":
        try:
            trash_dir = Path.home() / ".Trash"
            if trash_dir.exists():
                target = trash_dir / path.name
                counter = 1
                while target.exists():
                    target = trash_dir / f"{path.stem}_{counter}{path.suffix}"
                    counter += 1
                shutil.move(str(path), str(target))
                return True
        except Exception:
            pass

    # Respaldo: Eliminación permanente si la papelera no está disponible
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    else:
        path.unlink(missing_ok=True)
    return True