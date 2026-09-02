import os
import sys
import shutil
from pathlib import Path
import PyInstaller.__main__

def build():
    root_dir = Path(__file__).resolve().parent
    main_script = root_dir / "main.py"
    assets_dir = root_dir / "assets"
    icon_file = assets_dir / "icon.ico"
    dist_dir = root_dir / "dist"
    build_dir = root_dir / "build"

    print("=" * 60)
    print(" >>> GENERANDO DISTRIBUCIÓN LIMPIA (SIN PACKER) <<<")
    print("=" * 60)

    sep = ";" if sys.platform == "win32" else ":"

    # Usamos --onedir para generar binarios transparentes sin packer en memoria
    args = [
        str(main_script),
        "--name=CLZip",
        "--onedir",
        "--windowed",
        "--clean",
        "--noconfirm",
        "--hidden-import=pyzipper",
        "--hidden-import=zstandard",
        "--hidden-import=py7zr",
        "--hidden-import=qtawesome",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=PyQt6.QtGui",
    ]

    if assets_dir.exists():
        args.append(f"--add-data={assets_dir}{sep}assets")

    possible_locales = [
        root_dir / "src" / "i18n" / "locales",
        root_dir / "src" / "i18n",
        root_dir / "locales"
    ]
    for loc in possible_locales:
        if loc.exists() and any(loc.glob("*.json")):
            args.append(f"--add-data={loc}{sep}src/i18n/locales")
            args.append(f"--add-data={loc}{sep}src/i18n")
            args.append(f"--add-data={loc}{sep}locales")
            break

    if icon_file.exists():
        args.append(f"--icon={icon_file}")

    PyInstaller.__main__.run(args)

    if build_dir.exists():
        shutil.rmtree(build_dir, ignore_errors=True)
    spec_file = root_dir / "CLZip.spec"
    if spec_file.exists():
        spec_file.unlink(missing_ok=True)

    print("\n" + "=" * 60)
    print(f" ✓ ¡CARPETA PORTABLE GENERADA CON ÉXITO!")
    print(f" Ubicación: {dist_dir / 'CLZip'}")
    print("=" * 60)

if __name__ == "__main__":
    build()