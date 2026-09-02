# register_defaults.py
import sys
import winreg
from pathlib import Path

EXTENSIONS = [".zip", ".tar", ".zst", ".tzst", ".7z", ".rar", ".gz", ".bz2", ".xz"]

def register_system_capabilities():
    if sys.platform != "win32":
        print("Este script solo aplica a entornos Windows.")
        return

    root_dir = Path(__file__).resolve().parent
    exe_path = root_dir / "dist" / "CLZip" / "CLZip.exe"
    
    # Buscamos el icono específico de archivos comprimidos
    archive_ico = root_dir / "assets" / "archive_icon.ico"
    if not archive_ico.exists():
        archive_ico = root_dir / "assets" / "icon.ico" # Respaldo

    if exe_path.exists():
        target_command = f'"{exe_path}" "%1"'
        ico_target = f'"{archive_ico}",0'
    else:
        python_exe = Path(sys.executable).parent / "pythonw.exe"
        if not python_exe.exists():
            python_exe = Path(sys.executable)
        main_py = root_dir / "main.py"
        target_command = f'"{python_exe}" "{main_py}" "%1"'
        ico_target = f'"{archive_ico}",0'

    print("=" * 60)
    print(" >>> REGISTRANDO CLZIP EN EL SISTEMA DE WINDOWS <<<")
    print("=" * 60)

    app_key_name = "CLZip.Application"
    prog_id = "CLZip.Archive"

    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Archivo comprimido CLZip")
        
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}\DefaultIcon") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, ico_target)

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}\shell\open\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, target_command)

        cap_path = rf"Software\Clients\StartMenuInternet\{app_key_name}\Capabilities"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cap_path) as key:
            winreg.SetValueEx(key, "ApplicationName", 0, winreg.REG_SZ, "CLZip")
            winreg.SetValueEx(key, "ApplicationDescription", 0, winreg.REG_SZ, "Gestor de archivos y compresor de alta velocidad")

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"{cap_path}\FileAssociations") as key:
            for ext in EXTENSIONS:
                winreg.SetValueEx(key, ext, 0, winreg.REG_SZ, prog_id)

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\RegisteredApplications") as key:
            winreg.SetValueEx(key, "CLZip", 0, winreg.REG_SZ, rf"Software\Clients\StartMenuInternet\{app_key_name}\Capabilities")

        for ext in EXTENSIONS:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{ext}\OpenWithProgids") as key:
                winreg.SetValueEx(key, prog_id, 0, winreg.REG_NONE, b"")

        import ctypes
        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)

        print("✓ Registro completado exitosamente.")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Error al registrar: {e}")

if __name__ == "__main__":
    register_system_capabilities()