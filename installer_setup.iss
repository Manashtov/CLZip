; =====================================================================
; CLZip - Inno Setup Installer Script
; Desarrollador: Manashtov
; Repositorio: https://github.com/Manashtov/CLZip
; Licencia: GPL-3.0
; =====================================================================

#define MyAppName "CLZip"
#define MyAppVersion "1.0"
#define MyAppPublisher "Manashtov"
#define MyAppURL "https://github.com/Manashtov/CLZip"
#define MyAppExeName "CLZip.exe"

[Setup]
; Identificador único de la aplicación (GUID)
AppId={{E8A42F35-1892-4B69-9D72-8C5B32A9C91B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
; Eliminamos AppVerName para que Windows muestre únicamente "CLZip" sin la versión al lado
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Rutas de instalación por defecto
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Arquitectura de 64 bits para Windows 10/11
ArchitecturesInstallIn64BitMode=x64compatible
ArchitecturesAllowed=x64compatible

; Configuración de salida
OutputDir=dist_installer
OutputBaseFilename=CLZip_Setup_v{#MyAppVersion}
SetupIconFile=assets\icon.ico
; Icono que se mostrará en "Aplicaciones instaladas" de Windows (puedes usar el general o el de archivo)
UninstallDisplayIcon={app}\assets\icon.ico

; Compresión optimizada
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

; Privilegios administrativos para instalación global en Program Files
PrivilegesRequired=admin

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Archivos empaquetados por PyInstaller desde la carpeta dist\CLZip (incluyendo la carpeta assets con los dos iconos)
Source: "dist\CLZip\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Acceso directo en el Menú Inicio
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icon.ico"
; Acceso directo para desinstalar
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
; Acceso directo en el Escritorio (opcional por el usuario)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icon.ico"; Tasks: desktopicon

[Run]
; Opción para ejecutar la aplicación al terminar el instalador
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Registra el identificador de programa ProgID utilizando el icono específico de archivos comprimidos
Root: HKLM; Subkey: "Software\Classes\CLZip.Archive"; ValueType: string; ValueName: ""; ValueData: "Archivo comprimido CLZip"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Classes\CLZip.Archive\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\assets\archive_icon.ico,0"
Root: HKLM; Subkey: "Software\Classes\CLZip.Archive\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\CLZip.exe"" ""%1"""

; Registra las capacidades del programa para Windows
Root: HKLM; Subkey: "Software\CLZip\Capabilities"; ValueType: string; ValueName: "ApplicationName"; ValueData: "CLZip"
Root: HKLM; Subkey: "Software\CLZip\Capabilities"; ValueType: string; ValueName: "ApplicationDescription"; ValueData: "Gestor de archivos CLZip"

; Asocia todas las extensiones soportadas a las capacidades del sistema
Root: HKLM; Subkey: "Software\CLZip\Capabilities\FileAssociations"; ValueType: string; ValueName: ".zip"; ValueData: "CLZip.Archive"
Root: HKLM; Subkey: "Software\CLZip\Capabilities\FileAssociations"; ValueType: string; ValueName: ".tar"; ValueData: "CLZip.Archive"
Root: HKLM; Subkey: "Software\CLZip\Capabilities\FileAssociations"; ValueType: string; ValueName: ".zst"; ValueData: "CLZip.Archive"
Root: HKLM; Subkey: "Software\CLZip\Capabilities\FileAssociations"; ValueType: string; ValueName: ".tzst"; ValueData: "CLZip.Archive"
Root: HKLM; Subkey: "Software\CLZip\Capabilities\FileAssociations"; ValueType: string; ValueName: ".7z"; ValueData: "CLZip.Archive"
Root: HKLM; Subkey: "Software\CLZip\Capabilities\FileAssociations"; ValueType: string; ValueName: ".rar"; ValueData: "CLZip.Archive"
Root: HKLM; Subkey: "Software\CLZip\Capabilities\FileAssociations"; ValueType: string; ValueName: ".gz"; ValueData: "CLZip.Archive"
Root: HKLM; Subkey: "Software\CLZip\Capabilities\FileAssociations"; ValueType: string; ValueName: ".bz2"; ValueData: "CLZip.Archive"
Root: HKLM; Subkey: "Software\CLZip\Capabilities\FileAssociations"; ValueType: string; ValueName: ".xz"; ValueData: "CLZip.Archive"

; Da de alta formal en RegisteredApplications para el panel de aplicaciones predeterminadas
Root: HKLM; Subkey: "Software\RegisteredApplications"; ValueType: string; ValueName: "CLZip"; ValueData: "Software\CLZip\Capabilities"; Flags: uninsdeletevalue