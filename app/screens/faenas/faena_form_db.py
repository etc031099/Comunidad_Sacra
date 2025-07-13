from app.db.conexion import obtener_conexion

def crear_faena(datos):
    conexion = obtener_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            
            # Manejar fechas vacías - convertir a None para que la BD las maneje como NULL
            fecha_inicio = datos["fecha_inicio"].strip() if datos["fecha_inicio"] else None
            fecha_fin = datos["fecha_fin"].strip() if datos["fecha_fin"] else None
            
            # Solo convertir a datetime si las fechas no están vacías
            if fecha_inicio:
                try:
                    # Si solo tiene fecha sin hora, agregar hora por defecto
                    if len(fecha_inicio) == 10:  # Solo fecha YYYY-MM-DD
                        fecha_inicio = fecha_inicio + " 00:00:01"
                except:
                    fecha_inicio = None
            
            if fecha_fin:
                try:
                    # Si solo tiene fecha sin hora, agregar hora por defecto
                    if len(fecha_fin) == 10:  # Solo fecha YYYY-MM-DD
                        fecha_fin = fecha_fin + " 23:59:59"
                except:
                    fecha_fin = None
            
            cursor.execute("""
                INSERT INTO Faena (nombre, descripcion, fecha_inicio, fecha_fin, ubicacion, estado, tipo, tipoJornada, motivoExtra)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datos["nombre"], datos["descripcion"], fecha_inicio, fecha_fin,
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
            
            # Manejar fechas vacías - convertir a None para que la BD las maneje como NULL
            fecha_inicio = datos["fecha_inicio"].strip() if datos["fecha_inicio"] else None
            fecha_fin = datos["fecha_fin"].strip() if datos["fecha_fin"] else None
            
            # Solo convertir a datetime si las fechas no están vacías
            if fecha_inicio:
                try:
                    # Si solo tiene fecha sin hora, agregar hora por defecto
                    if len(fecha_inicio) == 10:  # Solo fecha YYYY-MM-DD
                        fecha_inicio = fecha_inicio + " 00:00:01"
                except:
                    fecha_inicio = None
            
            if fecha_fin:
                try:
                    # Si solo tiene fecha sin hora, agregar hora por defecto
                    if len(fecha_fin) == 10:  # Solo fecha YYYY-MM-DD
                        fecha_fin = fecha_fin + " 23:59:59"
                except:
                    fecha_fin = None
            
            cursor.execute("""
                UPDATE Faena SET nombre=?, descripcion=?, fecha_inicio=?, fecha_fin=?, ubicacion=?, estado=?, tipo=?, tipoJornada=?, motivoExtra=?
                WHERE idFaena=?
            """, (
                datos["nombre"], datos["descripcion"], fecha_inicio, fecha_fin,
                datos["ubicacion"], datos["estado"], datos["tipo"], datos["tipoJornada"], datos["motivoExtra"],
                id_faena
            ))
            conexion.commit()
        finally:
            conexion.close() 