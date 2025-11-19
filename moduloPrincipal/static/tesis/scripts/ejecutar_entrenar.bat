@echo off
REM Script para ejecutar entrenar.py desde el directorio raiz del proyecto
REM Desde scripts/ -> tesis/ -> static/ -> moduloPrincipal/ -> raiz (4 niveles arriba)
cd /d "%~dp0\..\..\..\.."

REM Verificar que estamos en el directorio correcto
if not exist "manage.py" (
    echo ERROR: No se encontro manage.py. Verifica la ruta del proyecto.
    exit /b 1
)

echo Ejecutando entrenar.py...
python -m moduloPrincipal.static.tesis.scripts.entrenar %*

