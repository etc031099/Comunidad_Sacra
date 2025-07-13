@echo off
echo =============================================
echo    INSTALADOR DEL SISTEMA DE ASISTENCIA
echo    Sacra Familia
echo =============================================

echo.
echo Instalando el sistema en su computadora...
echo.

REM Crear directorio de instalación
if not exist "C:\Program Files\Sistema Asistencia" mkdir "C:\Program Files\Sistema Asistencia"

REM Copiar archivos
copy "dist\Sistema_Asistencia_Sacra_Familia.exe" "C:\Program Files\Sistema Asistencia\"

REM Crear directorios necesarios
if not exist "C:\Program Files\Sistema Asistencia\evidencias" mkdir "C:\Program Files\Sistema Asistencia\evidencias"
if not exist "C:\Program Files\Sistema Asistencia\logs" mkdir "C:\Program Files\Sistema Asistencia\logs"
if not exist "C:\Program Files\Sistema Asistencia\backups" mkdir "C:\Program Files\Sistema Asistencia\backups"
if not exist "C:\Program Files\Sistema Asistencia\config" mkdir "C:\Program Files\Sistema Asistencia\config"

REM Crear acceso directo en escritorio
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%USERPROFILE%\Desktop\Sistema Asistencia.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "C:\Program Files\Sistema Asistencia\Sistema_Asistencia_Sacra_Familia.exe" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "C:\Program Files\Sistema Asistencia" >> CreateShortcut.vbs
echo oLink.Description = "Sistema de Asistencia Comunitario - Sacra Familia" >> CreateShortcut.vbs
echo oLink.IconLocation = "C:\Program Files\Sistema Asistencia\Sistema_Asistencia_Sacra_Familia.exe, 0" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

cscript //nologo CreateShortcut.vbs
del CreateShortcut.vbs

echo.
echo =============================================
echo    INSTALACIÓN COMPLETADA
echo =============================================
echo.
echo El sistema ha sido instalado exitosamente.
echo Puede acceder al sistema desde el acceso directo
echo en su escritorio o desde:
echo C:\Program Files\Sistema Asistencia\
echo.
echo Credenciales por defecto:
echo DNI: 12345678
echo Contraseña: admin123
echo.
echo IMPORTANTE: Cambie estas credenciales después
echo de la primera instalación.
echo.
pause
