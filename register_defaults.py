import sys
import winreg
from pathlib import Path

# Extensiones que manejará CLZip
EXTENSIONS = [".zip", ".zst", ".tzst", ".7z", ".rar", ".tar", ".gz", ".bz2", ".xz"]

def register_clzip():
    root_dir = Path(__file__).resolve().parent
    
    # Busca si existe el .exe compilado en dist/, o si no, usa el intérprete de Python
    exe_path = root_dir / "dist" / "CLZip_Portable.exe"
    icon_path = root_dir / "assets" / "icon.ico"
    
    if exe_path.exists():
        target_command = f'"{exe_path}" "%1"'
        ico_target = str(icon_path) if icon_path.exists() else str(exe_path)
    else:
        # Modo desarrollo: usa pythonw.exe para no abrir consola negra
        python_exe = Path(sys.executable).parent / "pythonw.exe"
        if not python_exe.exists():
            python_exe = Path(sys.executable)
        main_py = root_dir / "main.py"
        target_command = f'"{python_exe}" "{main_py}" "%1"'
        ico_target = str(icon_path) if icon_path.exists() else str(python_exe)

    print("=" * 60)
    print(" >>> ASOCIANDO CLZIP COMO PROGRAMA PREDETERMINADO <<<")
    print("=" * 60)
    print(f"Comando registrado: {target_command}")

    prog_id = "CLZip.Archive"

    try:
        # 1. Crear el identificador de programa ProgID
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Archivo comprimido CLZip")

        # 2. Asignar el icono
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}\DefaultIcon") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'"{ico_target}",0')

        # 3. Asignar el comando de apertura al hacer doble clic (Open)
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}\shell\open\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, target_command)

        # 4. Asociar cada extensión a CLZip
        for ext in EXTENSIONS:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{ext}") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, prog_id)
            print(f"  ✓ Extensión {ext} asociada.")

        # 5. Notificar al Explorador de Windows para que refresque los iconos de inmediato
        import ctypes
        SHCNE_ASSOCCHANGED = 0x08000000
        SHCNF_IDLIST = 0x0000
        ctypes.windll.shell32.SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_IDLIST, None, None)

        print("\n" + "=" * 60)
        print(" ✓ ¡REGISTRO COMPLETADO CON ÉXITO!")
        print(" Ahora tus archivos .zip, .zst, .rar, etc., se abrirán con CLZip.")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error al registrar en Windows: {e}")

if __name__ == "__main__":
    register_clzip()