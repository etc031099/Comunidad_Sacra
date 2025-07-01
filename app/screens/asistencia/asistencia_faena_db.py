from app.db.conexion import obtener_conexion
from datetime import datetime, timedelta

def obtener_faenas():
    conexion = obtener_conexion()
    faenas = []
    if conexion:
        try:
            cursor = conexion.cursor()
            query = """
                SELECT idFaena, nombre, descripcion, fecha_inicio, fecha_fin, 
                       ubicacion, estado, tipo 
                FROM Faena 
                ORDER BY fecha_inicio DESC
            """
            cursor.execute(query)
            resultados = cursor.fetchall()
            for r in resultados:
                faenas.append({
                    'idFaena': r[0],
                    'nombre': r[1],
                    'descripcion': r[2],
                    'fecha_inicio': r[3],
                    'fecha_fin': r[4],
                    'ubicacion': r[5],
                    'estado': r[6],
                    'tipo': r[7]
                })
        finally:
            conexion.close()
    return faenas

def obtener_miembros_asignados(id_faena):
    conexion = obtener_conexion()
    miembros = []
    if conexion:
        try:
            cursor = conexion.cursor()
            query = """
                SELECT DISTINCT m.ID, m.Nombre, m.Apellido_Paterno, m.Apellido_Materno
                FROM MiembroComunidad m
                INNER JOIN AsignacionFaena asig ON m.ID = asig.idMiembro
                WHERE asig.idFaena = ?
                ORDER BY m.Apellido_Paterno, m.Apellido_Materno, m.Nombre
            """
            cursor.execute(query, (id_faena,))
            resultados = cursor.fetchall()
            for r in resultados:
                miembros.append({
                    'ID': r[0],
                    'Nombre': f"{r[1]} {r[2]} {r[3]}",
                    'estado_asistencia': 'Sin registrar',
                    'hora_entrada': None,
                    'justificacion': None
                })
        finally:
            conexion.close()
    return miembros

def obtener_asistencias_fecha(id_faena, fecha):
    conexion = obtener_conexion()
    miembros = []
    if conexion:
        try:
            cursor = conexion.cursor()
            query = """
                SELECT m.ID, m.Nombre, m.Apellido_Paterno, m.Apellido_Materno,
                       afd.estado_asistencia, afd.hora_entrada, afd.justificacion
                FROM MiembroComunidad m
                INNER JOIN AsignacionFaena asig ON m.ID = asig.idMiembro
                LEFT JOIN AsistenciaFaenaDiaria afd ON (
                    m.ID = afd.idMiembro AND 
                    afd.idFaena = ? AND 
                    afd.fecha_asistencia = ?
                )
                WHERE asig.idFaena = ?
                ORDER BY m.Apellido_Paterno, m.Apellido_Materno, m.Nombre
            """
            cursor.execute(query, (id_faena, fecha, id_faena))
            resultados = cursor.fetchall()
            for r in resultados:
                miembros.append({
                    'ID': r[0],
                    'Nombre': f"{r[1]} {r[2]} {r[3]}",
                    'estado_asistencia': r[4] or 'Sin registrar',
                    'hora_entrada': r[5],
                    'justificacion': r[6]
                })
        finally:
            conexion.close()
    return miembros

def guardar_justificacion(id_faena, miembro_id, fecha, descripcion):
    conexion = obtener_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE AsistenciaFaenaDiaria 
                SET estado_asistencia = 'Justificado',
                    justificacion = ?,
                    fecha_actualizacion = GETDATE()
                WHERE idFaena = ? AND idMiembro = ? AND fecha_asistencia = ?
            """, (descripcion, id_faena, miembro_id, fecha))
            cursor.execute("""
                SELECT idAsistenciaDiaria 
                FROM AsistenciaFaenaDiaria 
                WHERE idFaena = ? AND idMiembro = ? AND fecha_asistencia = ?
            """, (id_faena, miembro_id, fecha))
            resultado = cursor.fetchone()
            if resultado:
                id_asistencia_diaria = resultado[0]
                cursor.execute("""
                    INSERT INTO EvidenciasJustificacion 
                    (tipo_registro, id_registro, ruta_archivo, tipo_archivo, descripcion, fecha_subida)
                    VALUES ('FAENA', ?, 'SIN_ARCHIVO', 'TEXTO', ?, GETDATE())
                """, (id_asistencia_diaria, descripcion))
            conexion.commit()
        finally:
            conexion.close()

def marcar_tardanza(id_faena, miembro_id, fecha):
    conexion = obtener_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE AsistenciaFaenaDiaria 
                SET estado_asistencia = 'Tardanza',
                    fecha_actualizacion = GETDATE()
                WHERE idFaena = ? AND idMiembro = ? AND fecha_asistencia = ?
            """, (id_faena, miembro_id, fecha))
            conexion.commit()
        finally:
            conexion.close() 