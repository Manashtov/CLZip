# =====================================================================
# Build & Package Script para CLZip
# =====================================================================

Write-Host "[1/4] Limpiando caches y compilaciones anteriores..." -ForegroundColor Cyan
Get-ChildItem -Path . -Include __pycache__, *.pyc -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "build", "dist", "dist_installer" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "[2/4] Preparando carpeta de distribucion..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "dist\CLZip" | Out-Null

Write-Host "[3/4] Compilando ejecutable con PyInstaller..." -ForegroundColor Cyan
pyinstaller --noconsole --onedir --name "CLZip" `
    --icon="assets/icon.ico" `
    --add-data "assets;assets" `
    --collect-all qtawesome `
    --distpath "dist" `
    --workpath "build" `
    --clean `
    main.py

if (-not (Test-Path "dist\CLZip\CLZip.exe")) {
    Write-Host "Error: No se pudo compilar CLZip.exe. Abortando empaquetado." -ForegroundColor Red
    exit 1
}

Write-Host "[4/4] Empaquetando instalador con Inno Setup..." -ForegroundColor Cyan
$isccPaths = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe",
    "${env:LOCALAPPDATA}\Programs\Inno Setup 6\ISCC.exe"
)

$iscc = $isccPaths | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($iscc) {
    & $iscc installer_setup.iss
    Write-Host "`nInstalador generado con éxito en 'dist_installer\'" -ForegroundColor Green
} else {
    Write-Host "`nNo se encontró ISCC.exe. Abre 'installer_setup.iss' manualmente en Inno Setup Compiler para generar el instalador." -ForegroundColor Yellow
}

# .\build_installer.ps1 para que funcione