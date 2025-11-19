# Script PowerShell para ejecutar entrenar.py desde el directorio raiz del proyecto
$scriptPath = $MyInvocation.MyCommand.Path
$scriptDir = Split-Path -Parent $scriptPath
# Desde scripts/ -> tesis/ -> static/ -> moduloPrincipal/ -> raiz (4 niveles arriba)
$projectRoot = (Get-Item (Join-Path $scriptDir "..\..\..\..")).FullName

Write-Host "Cambiando al directorio raiz: $projectRoot"
Set-Location $projectRoot

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "manage.py")) {
    Write-Host "ERROR: No se encontro manage.py. Verifica la ruta del proyecto." -ForegroundColor Red
    exit 1
}

Write-Host "Ejecutando entrenar.py..." -ForegroundColor Green
python -m moduloPrincipal.static.tesis.scripts.entrenar $args

