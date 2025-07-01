from app.db.conexion import obtener_conexion
from datetime import datetime

def obtener_reuniones():
    conexion = obtener_conexion()
    reuniones = []
    if conexion:
        try:
            cursor = conexion.cursor()
            query = """
                SELECT id_reunion, fecha, titulo, hora_inicio, descripcion
                FROM Reunion
                ORDER BY fecha DESC
            """
            cursor.execute(query)
            resultados = cursor.fetchall()
            for r in resultados:
                reuniones.append({
                    'id_reunion': r[0],
                    'fecha': r[1],
                    'titulo': r[2],
                    'hora_inicio': r[3],
                    'descripcion': r[4]
                })
        finally:
            conexion.close()
    return reuniones

def obtener_miembros_asignados(id_reunion):
    conexion = obtener_conexion()
    miembros = []
    if conexion:
        try:
            cursor = conexion.cursor()
            query = """
                SELECT m.ID, m.Nombre, m.Apellido_Paterno, m.Apellido_Materno,
                       a.estado_asistencia, a.hora_entrada, a.justificacion
                FROM MiembroComunidad m
                LEFT JOIN Asistencia a ON (m.ID = a.id_comunero AND a.id_reunion = ?)
                ORDER BY m.Apellido_Paterno, m.Apellido_Materno, m.Nombre
            """
            cursor.execute(query, (id_reunion,))
            resultados = cursor.fetchall()
            for r in resultados:
                miembros.append({
                    'ID': r[0],
                    'Nombre': f"{r[1]} {r[2]} {r[3]}",
                    'estado_asistencia': r[4],
                    'hora_entrada': r[5],
                    'justificacion': r[6]
                })
        finally:
            conexion.close()
    return miembros

def cambiar_estado_miembro(id_reunion, miembro_id, presente):
    conexion = obtener_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_asistencia FROM Asistencia 
                WHERE id_reunion = ? AND id_comunero = ?
            """, (id_reunion, miembro_id))
            resultado = cursor.fetchone()
            if resultado:
                cursor.execute("""
                    UPDATE Asistencia
                    SET estado_asistencia = ?, 
                        hora_entrada = ?, 
                        fecha_actualizacion = GETDATE()
                    WHERE id_reunion = ? AND id_comunero = ?
                """, (
                    "Presente" if presente else "Ausente",
                    datetime.now().time() if presente else None,
                    id_reunion,
                    miembro_id
                ))
            else:
                cursor.execute("""
                    INSERT INTO Asistencia (id_reunion, id_comunero, estado_asistencia, hora_entrada)
                    VALUES (?, ?, ?, ?)
                """, (
                    id_reunion,
                    miembro_id,
                    "Presente" if presente else "Ausente",
                    datetime.now().time() if presente else None
                ))
            conexion.commit()
        finally:
            conexion.close()

def guardar_justificacion(id_reunion, miembro_id, descripcion):
    conexion = obtener_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id_asistencia FROM Asistencia 
                WHERE id_reunion = ? AND id_comunero = ?
            """, (id_reunion, miembro_id))
            resultado = cursor.fetchone()
            id_asistencia = None
            if resultado:
                id_asistencia = resultado[0]
                cursor.execute("""
                    UPDATE Asistencia 
                    SET estado_asistencia = 'Justificado',
                        justificacion = ?,
                        fecha_actualizacion = GETDATE()
                    WHERE id_asistencia = ?
                """, (descripcion, id_asistencia))
            else:
                cursor.execute("""
                    INSERT INTO Asistencia (id_reunion, id_comunero, estado_asistencia, justificacion)
                    VALUES (?, ?, 'Justificado', ?)
                """, (id_reunion, miembro_id, descripcion))
                cursor.execute("SELECT SCOPE_IDENTITY()")
                resultado = cursor.fetchone()
                if resultado:
                    id_asistencia = resultado[0]
            if id_asistencia:
                cursor.execute("""
                    INSERT INTO EvidenciasJustificacion 
                    (tipo_registro, id_registro, ruta_archivo, tipo_archivo, descripcion, fecha_subida)
                    VALUES ('REUNION', ?, 'SIN_ARCHIVO', 'TEXTO', ?, GETDATE())
                """, (id_asistencia, descripcion))
            conexion.commit()
        finally:
            conexion.close()

def marcar_tardanza(id_reunion, miembro_id):
    conexion = obtener_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE Asistencia 
                SET estado_asistencia = 'Tardanza',
                    fecha_actualizacion = GETDATE()
                WHERE id_reunion = ? AND id_comunero = ?
            """, (id_reunion, miembro_id))
            conexion.commit()
        finally:
            conexion.close()

def obtener_estadisticas_asistencia(id_reunion):
    conexion = obtener_conexion()
    stats = {
        'total_asignados': 0,
        'presentes': 0,
        'ausentes': 0,
        'tardanzas': 0,
        'justificados': 0,
        'sin_registrar': 0
    }
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_asignados,
                    SUM(CASE WHEN a.estado_asistencia = 'Presente' THEN 1 ELSE 0 END) as presentes,
                    SUM(CASE WHEN a.estado_asistencia = 'Ausente' THEN 1 ELSE 0 END) as ausentes,
                    SUM(CASE WHEN a.estado_asistencia = 'Tardanza' THEN 1 ELSE 0 END) as tardanzas,
                    SUM(CASE WHEN a.estado_asistencia = 'Justificado' THEN 1 ELSE 0 END) as justificados
                FROM Asistencia a
                WHERE a.id_reunion = ?
            """, (id_reunion,))
            resultado = cursor.fetchone()
            if resultado:
                stats['total_asignados'] = resultado[0] or 0
                stats['presentes'] = resultado[1] or 0
                stats['ausentes'] = resultado[2] or 0
                stats['tardanzas'] = resultado[3] or 0
                stats['justificados'] = resultado[4] or 0
                stats['sin_registrar'] = stats['total_asignados'] - (
                    stats['presentes'] + stats['ausentes'] + stats['tardanzas'] + stats['justificados']
                )
        finally:
            conexion.close()
    return stats 