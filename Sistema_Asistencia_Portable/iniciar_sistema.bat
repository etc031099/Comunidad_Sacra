@echo off
echo =============================================
echo    SISTEMA DE ASISTENCIA COMUNITARIO
echo    Sacra Familia - Versión Portable
echo =============================================

echo.
echo Iniciando sistema...
echo.

REM Verificar si existe el ejecutable
if exist "Sistema_Asistencia_Sacra_Familia.exe" (
    echo Ejecutando versión compilada...
    start "" "Sistema_Asistencia_Sacra_Familia.exe"
) else (
    echo Ejecutando versión Python...
    REM Intentar ejecutar con Python si está disponible
    python main.py
    if errorlevel 1 (
        echo ERROR: No se pudo iniciar el sistema
        echo Verifique que Python esté instalado
        pause
        exit /b 1
    )
)

echo Sistema iniciado correctamente.
echo Puede cerrar esta ventana.
