from app.db.conexion import obtener_conexion
from datetime import datetime, timedelta
import logging

def obtener_eventos_proximos():
    """Obtiene eventos próximos (reuniones y faenas) en los siguientes 7 días"""
    conexion = obtener_conexion()
    eventos = []
    if conexion:
        try:
            cursor = conexion.cursor()
            fecha_hoy = datetime.now().date()
            fecha_limite = fecha_hoy + timedelta(days=7)
            
            # Obtener reuniones próximas
            cursor.execute("SELECT titulo, fecha FROM Reunion WHERE fecha BETWEEN ? AND ?", (fecha_hoy, fecha_limite))
            reuniones = [{"nombre": r[0], "fecha": r[1], "tipo": "Reunión"} for r in cursor.fetchall()]

            # Obtener faenas próximas
            cursor.execute("SELECT nombre, fecha_inicio FROM Faena WHERE fecha_inicio BETWEEN ? AND ?", (fecha_hoy, fecha_limite))
            faenas = [{"nombre": r[0], "fecha": r[1], "tipo": "Faena"} for r in cursor.fetchall()]
            
            # Combinar y ordenar por fecha
            eventos = sorted(reuniones + faenas, key=lambda x: x['fecha'])
            
        except Exception as e:
            logging.error(f"Error al obtener eventos próximos: {e}")
        finally:
            conexion.close()
    return eventos

def obtener_penalizaciones_pendientes():
    """Obtiene las penalizaciones pendientes de pago"""
    conexion = obtener_conexion()
    penalizaciones = []
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT m.Nombre + ' ' + m.Apellido_Paterno, p.tipo_penalizacion, p.valor, p.fecha_aplicacion
                FROM Penalizaciones p
                JOIN MiembroComunidad m ON p.id_miembro = m.ID
                WHERE p.estado = 'PENDIENTE'
                ORDER BY p.fecha_aplicacion DESC
            """)
            penalizaciones = cursor.fetchall()
            
        except Exception as e:
            logging.error(f"Error al obtener penalizaciones pendientes: {e}")
        finally:
            conexion.close()
    return penalizaciones

def obtener_miembros_con_inasistencias():
    """Obtiene miembros con más de 3 inasistencias en los últimos 30 días"""
    conexion = obtener_conexion()
    miembros = []
    if conexion:
        try:
            cursor = conexion.cursor()
            fecha_limite = (datetime.now() - timedelta(days=30)).date()
            cursor.execute('''
                SELECT m.ID, m.Nombre + ' ' + m.Apellido_Paterno,
                       COUNT(*) as Faltas,
                       MAX(a.fecha_registro) as UltimaFalta
                FROM MiembroComunidad m
                JOIN Asistencia a ON m.ID = a.id_comunero
                WHERE a.estado_asistencia = 'Ausente' AND a.fecha_registro >= ?
                GROUP BY m.ID, m.Nombre, m.Apellido_Paterno
                HAVING COUNT(*) > 3
            ''', (fecha_limite,))
            miembros = cursor.fetchall()
            
        except Exception as e:
            logging.error(f"Error al obtener miembros con inasistencias: {e}")
        finally:
            conexion.close()
    return miembros

def obtener_detalles_inasistencias_miembro(id_miembro, fecha_limite):
    """Obtiene los detalles de inasistencias de un miembro específico"""
    conexion = obtener_conexion()
    faltas_detalle = []
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute('''
                SELECT r.titulo, a.fecha_registro
                FROM Asistencia a
                JOIN Reunion r ON a.id_reunion = r.id_reunion
                WHERE a.id_comunero = ? AND a.estado_asistencia = 'Ausente' AND a.fecha_registro >= ?
                ORDER BY a.fecha_registro DESC
            ''', (id_miembro, fecha_limite))
            faltas_detalle = cursor.fetchall()
            
        except Exception as e:
            logging.error(f"Error al obtener detalles de inasistencias: {e}")
        finally:
            conexion.close()
    return faltas_detalle 