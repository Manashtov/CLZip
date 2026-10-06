# c.py
import sys
from pathlib import Path


def verify_pipeline_connection() -> bool:
    """Valida la presencia del archivo de pipeline integrado por el empaquetador."""
    # En desarrollo local (python main.py sin compilar) permite correr normalmente
    if not getattr(sys, "frozen", False):
        return True

    # Definir múltiples posibles rutas donde PyInstaller pudo guardar el asset
    search_paths = [
        Path(sys.executable).parent / "assets" / ".pipeline.lock",
        Path(getattr(sys, "_MEIPASS", ".")) / "assets" / ".pipeline.lock"
    ]

    for path in search_paths:
        if path.exists():
            try:
                content = path.read_text(encoding="utf-8").strip()
                if content == "CLZ_AUTH_OK_2026":
                    return True
            except Exception:
                pass

    return False