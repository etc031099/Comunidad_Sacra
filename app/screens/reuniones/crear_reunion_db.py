from app.db.conexion import obtener_conexion
from datetime import datetime

def crear_reunion(fecha, titulo, hora_inicio, descripcion):
    conexion = obtener_conexion()
    id_reunion = None
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO Reunion (fecha, titulo, hora_inicio, descripcion)
                OUTPUT INSERTED.id_reunion
                VALUES (?, ?, ?, ?)
            """, (fecha, titulo, hora_inicio, descripcion))
            result = cursor.fetchone()
            if result:
                id_reunion = result[0]
            conexion.commit()
        finally:
            conexion.close()
    return id_reunion

def actualizar_reunion(id_reunion, fecha, titulo, hora_inicio, descripcion):
    conexion = obtener_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE Reunion 
                SET fecha = ?, titulo = ?, hora_inicio = ?, descripcion = ?
                WHERE id_reunion = ?
            """, (fecha, titulo, hora_inicio, descripcion, id_reunion))
            conexion.commit()
        finally:
            conexion.close()

def registrar_asistencias_inasistencia(id_reunion):
    conexion = obtener_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT ID FROM MiembroComunidad")
            comuneros = cursor.fetchall()
            for comunero in comuneros:
                id_comunero = comunero[0]
                cursor.execute("""
                    INSERT INTO Asistencia (id_reunion, id_comunero, estado_asistencia)
                    VALUES (?, ?, ?)
                """, (id_reunion, id_comunero, 'inasistencia'))
            conexion.commit()
        finally:
            conexion.close() 