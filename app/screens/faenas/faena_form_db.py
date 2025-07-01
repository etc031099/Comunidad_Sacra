from app.db.conexion import obtener_conexion

def crear_faena(datos):
    conexion = obtener_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO Faena (nombre, descripcion, fecha_inicio, fecha_fin, ubicacion, estado, tipo, tipoJornada, motivoExtra)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datos["nombre"], datos["descripcion"], datos["fecha_inicio"], datos["fecha_fin"],
                datos["ubicacion"], datos["estado"], datos["tipo"], datos["tipoJornada"], datos["motivoExtra"]
            ))
            conexion.commit()
        finally:
            conexion.close()

def actualizar_faena(id_faena, datos):
    conexion = obtener_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE Faena SET nombre=?, descripcion=?, fecha_inicio=?, fecha_fin=?, ubicacion=?, estado=?, tipo=?, tipoJornada=?, motivoExtra=?
                WHERE idFaena=?
            """, (
                datos["nombre"], datos["descripcion"], datos["fecha_inicio"], datos["fecha_fin"],
                datos["ubicacion"], datos["estado"], datos["tipo"], datos["tipoJornada"], datos["motivoExtra"],
                id_faena
            ))
            conexion.commit()
        finally:
            conexion.close() 