from app.db.conexion import obtener_conexion
from datetime import datetime, timedelta
import os
import shutil
import logging

def obtener_miembros():
    """Obtiene la lista de todos los miembros de la comunidad"""
    conexion = obtener_conexion()
    miembros = []
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT ID, nombre, Apellido_Paterno, Apellido_Materno
                FROM MiembroComunidad
                ORDER BY nombre, Apellido_Paterno, Apellido_Materno
            """)
            columnas = [column[0] for column in cursor.description]
            miembros = [dict(zip(columnas, row)) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error al obtener miembros: {e}")
        finally:
            conexion.close()
    return miembros

def obtener_faenas():
    """Obtiene la lista de todas las faenas"""
    conexion = obtener_conexion()
    faenas = []
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT idFaena, nombre
                FROM Faena
                ORDER BY nombre
            """)
            columnas = [column[0] for column in cursor.description]
            faenas = [dict(zip(columnas, row)) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error al obtener faenas: {e}")
        finally:
            conexion.close()
    return faenas

def obtener_reuniones():
    """Obtiene la lista de todas las reuniones"""
    conexion = obtener_conexion()
    reuniones = []
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_reunion, titulo
                FROM Reunion
                ORDER BY titulo
            """)
            columnas = [column[0] for column in cursor.description]
            reuniones = [dict(zip(columnas, row)) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error al obtener reuniones: {e}")
        finally:
            conexion.close()
    return reuniones

def obtener_fechas_faena(id_faena):
    """Obtiene las fechas de inicio y fin de una faena"""
    conexion = obtener_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT fecha_inicio, fecha_fin
                FROM Faena
                WHERE idFaena = ?
            """, (id_faena,))
            resultado = cursor.fetchone()
            return resultado
        except Exception as e:
            logging.error(f"Error al obtener fechas de faena: {e}")
            return None
        finally:
            conexion.close()
    return None

def obtener_fechas_con_justificaciones_faena(id_faena):
    """Devuelve una lista de fechas (date) donde existen justificaciones para la faena dada."""
    conexion = obtener_conexion()
    fechas = []
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute('''
                SELECT DISTINCT afd.fecha_asistencia
                FROM AsistenciaFaenaDiaria afd
                WHERE afd.idFaena = ? AND afd.estado_asistencia = 'Justificado'
                ORDER BY afd.fecha_asistencia
            ''', (id_faena,))
            fechas = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error al obtener fechas con justificaciones de faena: {e}")
        finally:
            conexion.close()
    return fechas

def obtener_justificaciones_faena(id_faena, fecha_especifica=None):
    """Obtiene las justificaciones de una faena"""
    conexion = obtener_conexion()
    justificaciones = []
    if conexion:
        try:
            cursor = conexion.cursor()
            
            if fecha_especifica:
                # Cargar justificaciones para fecha específica
                query = '''
                SELECT afd.idAsistenciaDiaria, mc.ID, mc.nombre, mc.Apellido_Paterno, mc.Apellido_Materno, 
                       afd.estado_asistencia, afd.idFaena, f.nombre as nombre_faena, 
                       afd.fecha_asistencia, afd.justificacion, afd.fecha_actualizacion,
                       ej.idEvidencia, ej.ruta_archivo, ej.tipo_archivo, ej.descripcion, ej.fecha_subida
                FROM AsistenciaFaenaDiaria afd
                JOIN MiembroComunidad mc ON afd.idMiembro = mc.ID
                JOIN Faena f ON afd.idFaena = f.idFaena
                LEFT JOIN EvidenciasJustificacion ej ON ej.id_registro = afd.idAsistenciaDiaria AND ej.tipo_registro = 'FAENA'
                WHERE afd.idFaena = ? AND afd.fecha_asistencia = ? AND afd.estado_asistencia = 'Justificado'
                ORDER BY mc.Apellido_Paterno, mc.Apellido_Materno, mc.nombre
                '''
                cursor.execute(query, (id_faena, fecha_especifica))
            else:
                # Cargar todas las justificaciones de la faena
                query = '''
                SELECT afd.idAsistenciaDiaria, mc.ID, mc.nombre, mc.Apellido_Paterno, mc.Apellido_Materno, 
                       afd.estado_asistencia, afd.idFaena, f.nombre as nombre_faena, 
                       afd.fecha_asistencia, afd.justificacion, afd.fecha_actualizacion,
                       ej.idEvidencia, ej.ruta_archivo, ej.tipo_archivo, ej.descripcion, ej.fecha_subida
                FROM AsistenciaFaenaDiaria afd
                JOIN MiembroComunidad mc ON afd.idMiembro = mc.ID
                JOIN Faena f ON afd.idFaena = f.idFaena
                LEFT JOIN EvidenciasJustificacion ej ON ej.id_registro = afd.idAsistenciaDiaria AND ej.tipo_registro = 'FAENA'
                WHERE afd.idFaena = ? AND afd.estado_asistencia = 'Justificado'
                ORDER BY afd.fecha_asistencia DESC, mc.Apellido_Paterno, mc.Apellido_Materno, mc.nombre
                '''
                cursor.execute(query, (id_faena,))
            
            columnas = [column[0] for column in cursor.description]
            justificaciones = [dict(zip(columnas, row)) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error al obtener justificaciones de faena: {e}")
        finally:
            conexion.close()
    return justificaciones

def obtener_justificaciones_reunion(id_reunion):
    """Obtiene las justificaciones de una reunión"""
    conexion = obtener_conexion()
    justificaciones = []
    if conexion:
        try:
            cursor = conexion.cursor()
            query = '''
            SELECT a.id_asistencia, mc.ID, mc.nombre, mc.Apellido_Paterno, mc.Apellido_Materno, 
                   a.estado_asistencia, a.id_reunion, r.titulo as nombre_reunion,
                   a.fecha_registro as fecha_asistencia, a.justificacion, a.fecha_actualizacion,
                   ej.idEvidencia, ej.ruta_archivo, ej.tipo_archivo, ej.descripcion, ej.fecha_subida
            FROM Asistencia a
            JOIN MiembroComunidad mc ON a.id_comunero = mc.ID
            JOIN Reunion r ON a.id_reunion = r.id_reunion
            LEFT JOIN EvidenciasJustificacion ej ON ej.id_registro = a.id_asistencia AND ej.tipo_registro = 'REUNION'
            WHERE a.id_reunion = ? AND a.estado_asistencia = 'Justificado'
            ORDER BY a.fecha_registro DESC, mc.Apellido_Paterno, mc.Apellido_Materno, mc.nombre
            '''
            cursor.execute(query, (id_reunion,))
            
            columnas = [column[0] for column in cursor.description]
            justificaciones = [dict(zip(columnas, row)) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error al obtener justificaciones de reunión: {e}")
        finally:
            conexion.close()
    return justificaciones

def obtener_id_registro_faena(id_miembro, id_faena, fecha_especifica=None):
    """Obtiene el ID del registro de asistencia para una faena"""
    conexion = obtener_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            if fecha_especifica:
                query = '''
                    SELECT idAsistenciaDiaria 
                    FROM AsistenciaFaenaDiaria 
                    WHERE idMiembro = ? AND idFaena = ? AND fecha_asistencia = ?
                '''
                params = (id_miembro, id_faena, fecha_especifica)
            else:
                query = '''
                    SELECT idAsistenciaDiaria 
                    FROM AsistenciaFaenaDiaria 
                    WHERE idMiembro = ? AND idFaena = ?
                '''
                params = (id_miembro, id_faena)
            
            cursor.execute(query, params)
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            logging.error(f"Error al obtener ID de registro de faena: {e}")
            return None
        finally:
            conexion.close()
    return None

def obtener_id_registro_reunion(id_miembro, id_reunion):
    """Obtiene el ID del registro de asistencia para una reunión"""
    conexion = obtener_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute('SELECT id_asistencia FROM Asistencia WHERE id_comunero = ? AND id_reunion = ?', (id_miembro, id_reunion))
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            logging.error(f"Error al obtener ID de registro de reunión: {e}")
            return None
        finally:
            conexion.close()
    return None

def guardar_evidencia(tipo_registro, id_registro, descripcion, archivo, tipo_archivo, id_evidencia_existente=None):
    """Guarda o actualiza una evidencia de justificación"""
    conexion = obtener_conexion()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        
        if id_evidencia_existente:
            # Actualizar evidencia existente
            cursor.execute("""
                UPDATE EvidenciasJustificacion 
                SET descripcion = ?, ruta_archivo = ?, tipo_archivo = ?
                WHERE idEvidencia = ?
            """, (descripcion, archivo, tipo_archivo, id_evidencia_existente))
        else:
            # Insertar nueva evidencia
            cursor.execute("""
                INSERT INTO EvidenciasJustificacion 
                (tipo_registro, id_registro, descripcion, ruta_archivo, tipo_archivo, fecha_subida)
                VALUES (?, ?, ?, ?, ?, GETDATE())
            """, (tipo_registro, id_registro, descripcion, archivo, tipo_archivo))
        
        conexion.commit()
        return True
    except Exception as e:
        logging.error(f"Error al guardar evidencia: {e}")
        if conexion:
            conexion.rollback()
        return False
    finally:
        if conexion:
            conexion.close()

def guardar_archivo_evidencia(archivo_origen, directorio_evidencias):
    """Guarda el archivo en el directorio de evidencias y retorna la ruta relativa"""
    if not archivo_origen:
        return None
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = f"evidencia_{timestamp}{os.path.splitext(archivo_origen)[1]}"
        ruta_destino = os.path.join(directorio_evidencias, nombre_archivo)
        shutil.copy2(archivo_origen, ruta_destino)
        return os.path.relpath(ruta_destino, directorio_evidencias)
    except Exception as e:
        logging.error(f"Error al guardar archivo de evidencia: {e}")
        return None 