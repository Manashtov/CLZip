# CLZip 🗜️

Un gestor y compresor de archivos moderno, intuitivo y de alto rendimiento diseñado para Windows, desarrollado con Python y PyQt6.

CLZip ofrece una interfaz gráfica limpia y accesible, soporte para múltiples formatos de compresión (ZIP, TAR, Zstandard), cifrado seguro AES-256 mediante contraseña, y personalización completa de temas (claro/oscuro).


Link instalación
https://github.com/Manashtov/CLZip/releases/tag/1.0


---

## 🚀 Características Principales

- **Compresión de alta velocidad:** Soporte nativo para compresión y descompresión con Zstandard (`.zst`), estándar ZIP y paquetes TAR.
- **Seguridad robusta:** Soporte para cifrado y protección mediante contraseñas usando **AES-256** (pyzipper).
- **Interfaz moderna y reactiva:** Diseñada en PyQt6 con soporte completo para cambio dinámico de tema claro y tema oscuro.
- **Explorador integrado:** Navegador de archivos local con panel lateral de accesos rápidos a carpetas del sistema.
- **Internacionalización (i18n):** Interfaz disponible en español e inglés con cambio dinámico.
- **Progreso en tiempo real:** Diálogos con telemetría y porcentaje de avance durante operaciones pesadas de compresión/extracción.

---

## 🛠️ Requisitos e Instalación para Desarrollo

### Requisitos previos
- Windows 10 o Windows 11 (64-bit)
- Python 3.10 o superior
- Inno Setup 6 (para compilar el instalador)

### Configuración del entorno
1. Clonar el repositorio:
   ```bash
   git clone [https://github.com/Manashtov/CLZip.git](https://github.com/Manashtov/CLZip.git)
   cd CLZip

2. Instalar dependencias:
    pip install -r requirements.txt

3. Ejecutar en desarrollo:
    py main.py

📦 Compilación y Empaquetado

El proyecto incluye scripts automatizados para generar el binario congelado y el instalador de Windows:
Compilación manual con PyInstaller:
    pyinstaller CLZip.spec

Pipeline de empaquetado completo:
Ejecutar el script de PowerShell en la raíz del proyecto para limpiar temporales, compilar el binario y generar 

el instalador con Inno Setup:
    .\build_installer.ps1
    El instalador final se generará en el directorio dist_installer/.

🔒 Seguridad e Integridad

CLZip es software de código abierto. Ningún dato de usuario es recopilado, telemetrado ni transmitido a servidores externos. Todo el procesamiento de compresión y cifrado ocurre localmente en la máquina del usuario.

Las versiones publicadas en Releases se compilan de forma transparente y reproducible mediante pipelines automatizados de integración continua (CI) en GitHub Actions.
📄 Licencia

Este proyecto está bajo la Licencia GNU General Public License v3.0 (GPL-3.0). Consulta el archivo LICENSE para más detalles.

Desarrollado por Manashtov.

----------------------------------------------------------------------------------------------------------------


CLZip 🗜️ (English)

Link Release:
https://github.com/Manashtov/CLZip/releases/tag/1.0

A modern, intuitive, and high-performance archive manager and compression utility designed for Windows, built with Python and PyQt6.

CLZip delivers a clean, accessible graphical interface, multi-format compression support (ZIP, TAR, Zstandard), secure AES-256 password protection, and seamless light/dark theme customization.
🚀 Key Features

    High-speed compression: Native support for Zstandard (.zst), standard ZIP archives, and TAR containers.

    Robust security: Built-in password protection with AES-256 encryption powered by pyzipper.

    Modern UI: Built on PyQt6 with dynamic light and dark theme switching.

    Integrated file browser: Built-in local file navigation with a sidebar for rapid access to system directories.

    Internationalization (i18n): Fully translated interface supporting English and Spanish.

    Real-time feedback: Progress dialogs with telemetry and percentage tracking for heavy archive jobs.

🛠️ Development & Installation Requirements
Prerequisites

    Windows 10 or Windows 11 (64-bit)

    Python 3.10+

    Inno Setup 6 (for packaging the final installer)

Setup

Clone the repository:
    git clone [https://github.com/Manashtov/CLZip.git](https://github.com/Manashtov/CLZip.git)
cd CLZip

Install dependencies:
    pip install -r requirements.txt

Run locally:
    python main.py

📦 Build & Packaging

The project provides automated build configurations for freezing the Python runtime and creating a standard Windows setup executable:

Build binary via PyInstaller:
    pyinstaller CLZip.spec

Full packaging pipeline:
Run the PowerShell script from the repository root to clean caches, freeze dependencies, and invoke Inno Setup:
    .\build_installer.ps1
The resulting setup executable is placed in the dist_installer/ directory.

🔒 Security & Verification

CLZip is free and open-source software. No user data or telemetry is collected or transmitted to external servers. All compression, extraction, and cryptographic routines execute entirely on the local machine.

Official distribution binaries are built transparently and reproducibly using continuous integration (CI) workflows via GitHub Actions.
📄 License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0). See the LICENSE file for full terms.

Developed by Manashtov.
