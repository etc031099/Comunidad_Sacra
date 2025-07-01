# 🏘️ Sistema de Asistencia Comunitario - Sacra Familia

## 📋 Descripción General

El **Sistema de Asistencia Comunitario** es una aplicación de escritorio desarrollada en Python con KivyMD que permite gestionar la asistencia, reuniones, faenas y penalizaciones de una comunidad. El sistema está diseñado para facilitar la administración de actividades comunitarias y el seguimiento de la participación de los miembros.

## 🎯 Características Principales

### 🔐 Autenticación y Seguridad
- Sistema de login con autenticación de usuarios
- Dashboard principal con resumen de actividades
- Control de acceso basado en roles

### 👥 Gestión de Miembros
- Registro y edición de miembros de la comunidad
- Historial completo de actividades por miembro
- Información personal y de contacto
- Estado de membresía

### 📅 Gestión de Reuniones
- Crear y programar reuniones comunitarias
- Asistencia automática a reuniones
- Registro de participantes
- Historial de reuniones

### 🛠️ Gestión de Faenas
- Crear y asignar faenas comunitarias
- Asignación de miembros a faenas específicas
- Control de asistencia a faenas
- Seguimiento de progreso

### ✅ Control de Asistencia
- Registro de asistencia a reuniones y faenas
- Estados: Presente, Ausente, Justificado
- Evidencias fotográficas para justificaciones
- Reportes de asistencia

### 💰 Sistema de Penalizaciones
- Penalizaciones automáticas por ausencias
- Multas configurables por tipo de evento
- Registro de pagos de penalizaciones
- Acordeón de penalizaciones por miembro
- Estado de pagos (Pendiente, Pagado, Cancelado)

### 📊 Reportes y Estadísticas
- Dashboard con KPIs principales
- Reportes de asistencia
- Estadísticas de participación
- Análisis de tendencias

### 🔔 Notificaciones
- Panel de notificaciones del sistema
- Alertas de eventos próximos
- Recordatorios de actividades

## 🏗️ Arquitectura del Proyecto

### Estructura de Carpetas
```
Programa Comunitario/
├── main.py                          # Punto de entrada de la aplicación
├── requirements.txt                 # Dependencias del proyecto
├── app/
│   ├── __init__.py
│   ├── db/
│   │   ├── __init__.py
│   │   └── conexion.py             # Gestión de conexiones a BD
│   ├── models/
│   │   ├── __init__.py
│   │   ├── usuario.py              # Modelo de usuario
│   │   ├── reunion.py              # Modelo de reunión
│   │   └── asistencia.py           # Modelo de asistencia
│   ├── screens/                    # Pantallas de la aplicación
│   │   ├── core/                   # Pantallas principales
│   │   ├── miembros/               # Gestión de miembros
│   │   ├── reuniones/              # Gestión de reuniones
│   │   ├── faenas/                 # Gestión de faenas
│   │   ├── asistencia/             # Control de asistencia
│   │   ├── penalizaciones/         # Sistema de penalizaciones
│   │   ├── justificaciones/        # Gestión de justificaciones
│   │   ├── notificaciones/         # Panel de notificaciones
│   │   └── reportes/               # Reportes y estadísticas
│   ├── kv/                         # Archivos de interfaz Kivy
│   ├── evidencias/                 # Almacenamiento de evidencias
│   └── test/                       # Pruebas unitarias
├── assets/                         # Recursos multimedia
│   ├── images/                     # Imágenes de la aplicación
│   └── fonts/                      # Fuentes personalizadas
├── venv/                          # Entorno virtual
└── *.sql                          # Scripts de base de datos
```

### Módulos Principales

#### 🔧 Core (Pantallas Principales)
- **Login**: Autenticación de usuarios
- **Dashboard**: Panel principal con KPIs y navegación

#### 👥 Miembros
- **Miembros**: Lista y gestión de miembros
- **MiembroForm**: Formulario de registro/edición
- **HistorialMiembro**: Historial de actividades por miembro

#### 📅 Reuniones
- **Reuniones**: Lista de reuniones programadas
- **CrearReunion**: Formulario para crear/editar reuniones

#### 🛠️ Faenas
- **Faenas**: Lista de faenas comunitarias
- **FaenaForm**: Formulario para crear/editar faenas
- **AsignarFaena**: Asignación de miembros a faenas

#### ✅ Asistencia
- **Asistencia**: Control de asistencia a reuniones
- **AsistenciaFaena**: Control de asistencia a faenas
- **AsistenciaMenu**: Menú de opciones de asistencia

#### 💰 Penalizaciones
- **Penalizaciones**: Gestión de multas y penalizaciones
- Sistema de acordeón por miembro
- Registro de pagos

#### 📋 Justificaciones
- **Justificaciones**: Gestión de justificaciones
- Subida de evidencias fotográficas

#### 🔔 Notificaciones
- **Notificaciones**: Panel de notificaciones del sistema

#### 📊 Reportes
- **Reportes**: Generación de reportes y estadísticas

## 🛠️ Tecnologías Utilizadas

### Frontend
- **KivyMD 2.3.1**: Framework de interfaz de usuario
- **Kivy**: Framework base para aplicaciones móviles y de escritorio
- **Pillow**: Procesamiento de imágenes

### Backend
- **Python 3.x**: Lenguaje de programación principal
- **pyodbc**: Conexión a base de datos SQL Server
- **SQL Server**: Base de datos principal

### Base de Datos
- **SQL Server Express**: Motor de base de datos
- **Triggers SQL**: Automatización de penalizaciones
- **Stored Procedures**: Lógica de negocio en BD

## 📦 Instalación y Configuración

### Prerrequisitos
- Python 3.8 o superior
- SQL Server Express
- ODBC Driver 17 for SQL Server
- Windows 10/11

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone [URL_DEL_REPOSITORIO]
   cd "Programa Comunitario"
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar base de datos**
   - Ejecutar los scripts SQL en el orden correcto:
     - `nueva_tabla_asistencia_diaria.sql`
     - `modificar_tabla_reunion.sql`
     - `crear_trigger_final.sql`
     - `actualizar_trigger_evidencias.sql`

5. **Configurar conexión a BD**
   - Editar `app/db/conexion.py` con los datos de tu servidor SQL Server

6. **Ejecutar la aplicación**
   ```bash
   python main.py
   ```

## 🗄️ Configuración de Base de Datos

### Estructura Principal
- **MiembroComunidad**: Información de miembros
- **Reunion**: Reuniones programadas
- **Faena**: Faenas comunitarias
- **Asistencia**: Registro de asistencia
- **Penalizaciones**: Sistema de multas
- **PagosPenalizaciones**: Registro de pagos
- **Justificaciones**: Justificaciones con evidencias

### Triggers Automáticos
- **TRG_Penalizacion_Ausencia_Reunion**: Crea penalizaciones automáticas por ausencias
- **TR_Penalizaciones_ValidarEvento**: Valida existencia de eventos
- **TR_PagosPenalizaciones_ValidarTipo**: Valida tipos de pago
- **TR_PagosPenalizaciones_UpdateEstado**: Actualiza estado al pagar

## 🚀 Uso del Sistema

### 1. Inicio de Sesión
- Ingresar credenciales de usuario
- Acceder al dashboard principal

### 2. Gestión de Miembros
- Registrar nuevos miembros
- Editar información existente
- Ver historial de actividades

### 3. Programación de Eventos
- Crear reuniones comunitarias
- Programar faenas
- Asignar miembros a actividades

### 4. Control de Asistencia
- Registrar asistencia a eventos
- Gestionar justificaciones
- Subir evidencias fotográficas

### 5. Gestión de Penalizaciones
- Ver penalizaciones por miembro
- Registrar pagos de multas
- Consultar estados de pago

### 6. Reportes
- Generar reportes de asistencia
- Ver estadísticas de participación
- Analizar tendencias

## 🔧 Características Técnicas

### Pool de Conexiones
- Gestión eficiente de conexiones a BD
- Reutilización de conexiones
- Manejo automático de timeouts

### Modularidad
- Arquitectura modular por funcionalidad
- Separación de lógica de BD y UI
- Componentes reutilizables

### Interfaz de Usuario
- Diseño Material Design con KivyMD
- Navegación intuitiva
- Responsive design

### Gestión de Evidencias
- Almacenamiento de imágenes
- Validación de formatos
- Organización por eventos

## 📊 Funcionalidades Avanzadas

### Sistema de Penalizaciones Automáticas
- Generación automática de multas por ausencias
- Valor configurable por tipo de evento
- Prevención de duplicados
- Estados de pago (Pendiente, Pagado, Cancelado)

### Dashboard con KPIs
- Total de miembros activos
- Reuniones programadas
- Faenas en progreso
- Penalizaciones pendientes

### Gestión de Evidencias
- Subida de fotos para justificaciones
- Validación de formatos de imagen
- Almacenamiento organizado

## 🧪 Pruebas

### Pruebas Unitarias
- Archivos de prueba en `app/test/`
- Validación de funcionalidades principales
- Pruebas de integración con BD

### Scripts de Prueba
- `test_penalizaciones.sql`: Prueba del sistema de penalizaciones
- `verificar_faenas.py`: Validación de faenas
- `test_faenas.py`: Pruebas de funcionalidad de faenas

## 🔄 Mantenimiento

### Actualizaciones de Base de Datos
- Scripts SQL para modificaciones
- Migración de datos
- Actualización de triggers

### Logs y Monitoreo
- Registro de errores de conexión
- Monitoreo de performance
- Debugging de problemas

## 🤝 Contribución

### Estructura de Desarrollo
- Código modular y bien documentado
- Separación clara de responsabilidades
- Estándares de codificación consistentes

### Flujo de Trabajo
1. Crear rama para nueva funcionalidad
2. Implementar cambios
3. Ejecutar pruebas
4. Crear pull request
5. Revisión de código

## 📝 Licencia

Este proyecto es desarrollado para la comunidad Sacra Familia. Todos los derechos reservados.

## 👥 Equipo de Desarrollo

- **Desarrollador Principal**: [Nombre]
- **Comunidad**: Sacra Familia
- **Versión**: 1.0.0

## 📞 Soporte

Para soporte técnico o consultas sobre el sistema, contactar al equipo de desarrollo.

---

**Sistema de Asistencia Comunitario - Sacra Familia**  
*Gestionando la participación comunitaria de manera eficiente y transparente* 