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
AppVerName={#MyAppName} {#MyAppVersion}
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
UninstallDisplayIcon={app}\{#MyAppExeName}

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
; Archivos empaquetados por PyInstaller desde la carpeta dist\CLZip
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