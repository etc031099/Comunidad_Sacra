# =============================================
# SCRIPT PARA CREAR EJECUTABLE DEL SISTEMA
# Sistema de Asistencia Comunitario - Sacra Familia
# =============================================

import os
import sys
import subprocess
from pathlib import Path

def crear_ejecutable():
    """
    Crea un ejecutable del sistema usando PyInstaller
    """
    print("🔧 Creando ejecutable del sistema...")
    
    # 1. Verificar que PyInstaller esté instalado
    try:
        import PyInstaller
        print("✅ PyInstaller ya está instalado")
    except ImportError:
        print("📦 Instalando PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # 2. Crear directorios necesarios si no existen
    Path("config").mkdir(exist_ok=True)
    Path("evidencias").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    Path("backups").mkdir(exist_ok=True)
    
    # 3. Crear archivo de configuración básico si no existe
    if not os.path.exists("config/produccion.ini"):
        config_content = """# Configuración básica del sistema
DB_SERVER = "L_PC\\SQLEXPRESS"
DB_NAME = "COMUNIDADSACRA1"
DB_DRIVER = "ODBC Driver 17 for SQL Server"
APP_TITLE = "Sistema de Asistencia - Sacra Familia"
"""
        with open("config/produccion.ini", "w", encoding="utf-8") as f:
            f.write(config_content)
        print("✅ Archivo de configuración creado")
    
    # 4. Crear archivo spec personalizado
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Verificar qué archivos existen
import os
datas = []

# Agregar archivos KV si existen
if os.path.exists('app/kv'):
    for file in os.listdir('app/kv'):
        if file.endswith('.kv'):
            datas.append(('app/kv/' + file, 'app/kv'))

# Agregar imágenes si existen
if os.path.exists('assets/images'):
    for file in os.listdir('assets/images'):
        if file.endswith(('.jpg', '.png', '.ico')):
            datas.append(('assets/images/' + file, 'assets/images'))

# Agregar fuentes si existen
if os.path.exists('assets/fonts'):
    for file in os.listdir('assets/fonts'):
        if file.endswith(('.ttf', '.otf')):
            datas.append(('assets/fonts/' + file, 'assets/fonts'))

# Agregar configuración si existe
if os.path.exists('config'):
    for file in os.listdir('config'):
        if file.endswith('.ini'):
            datas.append(('config/' + file, 'config'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'kivy',
        'kivymd',
        'pyodbc',
        'PIL',
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'docutils',
        'filetype',
        'Pygments',
        'pypiwin32',
        'pywin32',
        'sqlite3'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Sistema_Asistencia_Sacra_Familia',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)
"""
    
    with open("sistema_asistencia.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("✅ Archivo .spec creado")
    
    # 5. Crear ejecutable
    print("🔨 Compilando ejecutable...")
    result = subprocess.run([
        "pyinstaller",
        "--clean",
        "sistema_asistencia.spec"
    ])
    
    if result.returncode == 0:
        print("✅ Ejecutable creado exitosamente!")
        print("📁 Ubicación: dist/Sistema_Asistencia_Sacra_Familia.exe")
        
        # 6. Crear script de instalación
        crear_script_instalacion()
        
    else:
        print("❌ Error al crear el ejecutable")
        return False
    
    return True

def crear_script_instalacion():
    """
    Crea un script de instalación simple
    """
    instalador_content = """@echo off
echo =============================================
echo    INSTALADOR DEL SISTEMA DE ASISTENCIA
echo    Sacra Familia
echo =============================================

echo.
echo Instalando el sistema en su computadora...
echo.

REM Crear directorio de instalación
if not exist "C:\\Program Files\\Sistema Asistencia" mkdir "C:\\Program Files\\Sistema Asistencia"

REM Copiar archivos
copy "dist\\Sistema_Asistencia_Sacra_Familia.exe" "C:\\Program Files\\Sistema Asistencia\\"

REM Crear directorios necesarios
if not exist "C:\\Program Files\\Sistema Asistencia\\evidencias" mkdir "C:\\Program Files\\Sistema Asistencia\\evidencias"
if not exist "C:\\Program Files\\Sistema Asistencia\\logs" mkdir "C:\\Program Files\\Sistema Asistencia\\logs"
if not exist "C:\\Program Files\\Sistema Asistencia\\backups" mkdir "C:\\Program Files\\Sistema Asistencia\\backups"
if not exist "C:\\Program Files\\Sistema Asistencia\\config" mkdir "C:\\Program Files\\Sistema Asistencia\\config"

REM Crear acceso directo en escritorio
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%USERPROFILE%\\Desktop\\Sistema Asistencia.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "C:\\Program Files\\Sistema Asistencia\\Sistema_Asistencia_Sacra_Familia.exe" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "C:\\Program Files\\Sistema Asistencia" >> CreateShortcut.vbs
echo oLink.Description = "Sistema de Asistencia Comunitario - Sacra Familia" >> CreateShortcut.vbs
echo oLink.IconLocation = "C:\\Program Files\\Sistema Asistencia\\Sistema_Asistencia_Sacra_Familia.exe, 0" >> CreateShortcut.vbs
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
echo C:\\Program Files\\Sistema Asistencia\\
echo.
echo Credenciales por defecto:
echo DNI: 12345678
echo Contraseña: admin123
echo.
echo IMPORTANTE: Cambie estas credenciales después
echo de la primera instalación.
echo.
pause
"""
    
    with open("instalar_sistema.bat", "w", encoding="utf-8") as f:
        f.write(instalador_content)
    
    print("✅ Script de instalación creado: instalar_sistema.bat")

def crear_version_portable():
    """
    Crea una versión portable que no requiere instalación
    """
    print("📦 Creando versión portable...")
    
    # Crear carpeta portable
    portable_dir = "Sistema_Asistencia_Portable"
    if os.path.exists(portable_dir):
        import shutil
        shutil.rmtree(portable_dir)
    
    os.makedirs(portable_dir)
    
    # Copiar ejecutable
    if os.path.exists("dist/Sistema_Asistencia_Sacra_Familia.exe"):
        import shutil
        shutil.copy("dist/Sistema_Asistencia_Sacra_Familia.exe", portable_dir)
        print("✅ Ejecutable copiado a versión portable")
    else:
        print("⚠️ No se encontró el ejecutable, creando script de inicio alternativo")
    
    # Crear carpetas necesarias
    os.makedirs(f"{portable_dir}/evidencias", exist_ok=True)
    os.makedirs(f"{portable_dir}/logs", exist_ok=True)
    os.makedirs(f"{portable_dir}/backups", exist_ok=True)
    os.makedirs(f"{portable_dir}/config", exist_ok=True)
    os.makedirs(f"{portable_dir}/data", exist_ok=True)
    
    # Crear script de inicio portable
    portable_script = """@echo off
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
"""
    
    with open(f"{portable_dir}/iniciar_sistema.bat", "w", encoding="utf-8") as f:
        f.write(portable_script)
    
    # Crear README para versión portable
    readme_portable = """# 🚀 SISTEMA DE ASISTENCIA COMUNITARIO - VERSIÓN PORTABLE

## 📋 Instrucciones de Uso

### Inicio Rápido
1. **Doble clic** en `iniciar_sistema.bat`
2. **O doble clic** directamente en `Sistema_Asistencia_Sacra_Familia.exe` (si existe)

### Credenciales por Defecto
- **DNI**: 12345678
- **Contraseña**: admin123

### Carpetas del Sistema
- `evidencias/` - Evidencias fotográficas
- `logs/` - Archivos de registro
- `backups/` - Copias de seguridad
- `config/` - Archivos de configuración
- `data/` - Base de datos (si usa SQLite)

### Requisitos del Sistema
- Windows 10/11
- Python 3.8+ (si no hay ejecutable)
- Conexión a la base de datos SQL Server (o SQLite local)
- Permisos de escritura en la carpeta

### Notas Importantes
- Esta es una versión portable que no requiere instalación
- Puede copiarse a cualquier ubicación
- Los datos se guardan en las carpetas locales
- Mantenga una copia de seguridad de la carpeta completa

### Solución de Problemas
1. Si no inicia, verifique que Python esté instalado
2. Si hay errores de conexión, verifique la configuración de BD
3. Si faltan archivos, copie la carpeta completa del proyecto

### Soporte
Para soporte técnico, contactar al administrador del sistema.
"""
    
    with open(f"{portable_dir}/README.txt", "w", encoding="utf-8") as f:
        f.write(readme_portable)
    
    # Copiar archivos importantes
    if os.path.exists("main.py"):
        import shutil
        shutil.copy("main.py", portable_dir)
    
    if os.path.exists("requirements.txt"):
        import shutil
        shutil.copy("requirements.txt", portable_dir)
    
    print(f"✅ Versión portable creada en: {portable_dir}/")

def crear_version_simple():
    """
    Crea una versión simple sin ejecutable
    """
    print("📁 Creando versión simple...")
    
    simple_dir = "Sistema_Asistencia_Simple"
    if os.path.exists(simple_dir):
        import shutil
        shutil.rmtree(simple_dir)
    
    os.makedirs(simple_dir)
    
    # Copiar archivos principales
    archivos_importantes = [
        "main.py",
        "requirements.txt",
        "app/",
        "assets/",
        "evidencias/",
        "logs/",
        "backups/"
    ]
    
    for archivo in archivos_importantes:
        if os.path.exists(archivo):
            if os.path.isdir(archivo):
                import shutil
                shutil.copytree(archivo, f"{simple_dir}/{archivo}")
            else:
                import shutil
                shutil.copy(archivo, simple_dir)
    
    # Crear script de inicio simple
    inicio_simple = """@echo off
echo =============================================
echo    SISTEMA DE ASISTENCIA COMUNITARIO
echo    Sacra Familia - Versión Simple
echo =============================================

echo.
echo Verificando Python...
python --version
if errorlevel 1 (
    echo ERROR: Python no está instalado
    echo Descargue Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Instalando dependencias...
pip install -r requirements.txt

echo.
echo Iniciando sistema...
python main.py

pause
"""
    
    with open(f"{simple_dir}/iniciar_sistema.bat", "w", encoding="utf-8") as f:
        f.write(inicio_simple)
    
    print(f"✅ Versión simple creada en: {simple_dir}/")

if __name__ == "__main__":
    print("🚀 CREADOR DE EJECUTABLE - SISTEMA DE ASISTENCIA")
    print("=" * 50)
    
    # Crear ejecutable
    if crear_ejecutable():
        # Crear versión portable
        crear_version_portable()
        
        print("\n🎉 PROCESO COMPLETADO!")
        print("\n📁 Archivos creados:")
        print("- dist/Sistema_Asistencia_Sacra_Familia.exe (Ejecutable principal)")
        print("- instalar_sistema.bat (Instalador)")
        print("- Sistema_Asistencia_Portable/ (Versión portable)")
        
        print("\n📋 Próximos pasos:")
        print("1. Probar el ejecutable en la computadora objetivo")
        print("2. Distribuir la versión portable o el instalador")
        print("3. Configurar la base de datos")
        print("4. Capacitar a los usuarios")
    else:
        print("⚠️ Error al crear ejecutable, creando versión simple...")
        crear_version_simple()
        print("\n📁 Versión simple creada:")
        print("- Sistema_Asistencia_Simple/ (Versión sin ejecutable)")
        print("\n📋 Para usar:")
        print("1. Copiar la carpeta Sistema_Asistencia_Simple")
        print("2. Ejecutar iniciar_sistema.bat")
        print("3. El sistema instalará las dependencias automáticamente") 