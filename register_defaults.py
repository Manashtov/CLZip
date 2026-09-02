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
    icon_path = root_dir / "assets" / "icon.ico"
    
    if exe_path.exists():
        target_command = f'"{exe_path}" "%1"'
        ico_target = f'"{icon_path}",0' if icon_path.exists() else f'"{exe_path}",0'
    else:
        # Modo desarrollo
        python_exe = Path(sys.executable).parent / "pythonw.exe"
        if not python_exe.exists():
            python_exe = Path(sys.executable)
        main_py = root_dir / "main.py"
        target_command = f'"{python_exe}" "{main_py}" "%1"'
        ico_target = f'"{icon_path}",0' if icon_path.exists() else f'"{python_exe}",0'

    print("=" * 60)
    print(" >>> REGISTRANDO CLZIP EN EL SISTEMA DE WINDOWS <<<")
    print("=" * 60)

    app_key_name = "CLZip.Application"
    prog_id = "CLZip.Archive"

    try:
        # 1. Registrar ProgID con el comando Open
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Archivo comprimido CLZip")
        
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}\DefaultIcon") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, ico_target)

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}\shell\open\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, target_command)

        # 2. Registrar Capacidades oficiales (Capabilities)
        cap_path = rf"Software\Clients\StartMenuInternet\{app_key_name}\Capabilities"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cap_path) as key:
            winreg.SetValueEx(key, "ApplicationName", 0, winreg.REG_SZ, "CLZip")
            winreg.SetValueEx(key, "ApplicationDescription", 0, winreg.REG_SZ, "Gestor de archivos y compresor de alta velocidad")

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"{cap_path}\FileAssociations") as key:
            for ext in EXTENSIONS:
                winreg.SetValueEx(key, ext, 0, winreg.REG_SZ, prog_id)

        # 3. Dar de alta en RegisteredApplications
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\RegisteredApplications") as key:
            winreg.SetValueEx(key, "CLZip", 0, winreg.REG_SZ, rf"Software\Clients\StartMenuInternet\{app_key_name}\Capabilities")

        # 4. Asignar OpenWithProgids para que Windows habilite el botón "Siempre"
        for ext in EXTENSIONS:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{ext}\OpenWithProgids") as key:
                winreg.SetValueEx(key, prog_id, 0, winreg.REG_NONE, b"")

        # 5. Notificar al Explorador de Windows
        import ctypes
        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)

        print("✓ Registro completado exitosamente.")
        print("\nPara fijarlo como predeterminado permanente:")
        print("1. Clic derecho en cualquier archivo .zip -> 'Abrir con' -> 'Elegir otra aplicación'.")
        print("2. Selecciona 'CLZip' y marca la casilla 'Usar siempre esta aplicación para abrir archivos .zip'.")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Error al registrar: {e}")

if __name__ == "__main__":
    register_system_capabilities()