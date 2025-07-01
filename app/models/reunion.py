from app.db.conexion import obtener_conexion
from kivymd.uix.snackbar import MDSnackbar

class Reunion:
    def __init__(self, nombre, fecha, hora, lugar, descripcion, id_reunion=None):
        self.id_reunion = id_reunion
        self.nombre = nombre
        self.fecha = fecha
        self.hora = hora
        self.lugar = lugar
        self.descripcion = descripcion

    def guardar(self):
        conexion = obtener_conexion()
        if not conexion:
            MDSnackbar(text="Error de conexión a la base de datos.").open()
            return None
        try:
            cursor = conexion.cursor()
            if self.id_reunion:
                # Actualizar reunión existente
                sql = """UPDATE Reunion SET nombre = ?, fecha = ?, hora = ?, lugar = ?, descripcion = ?
                         WHERE idReunion = ?"""
                cursor.execute(sql, (self.nombre, self.fecha, self.hora, self.lugar, self.descripcion, self.id_reunion))
            else:
                # Insertar nueva reunión
                sql = """INSERT INTO Reunion (nombre, fecha, hora, lugar, descripcion, estado) 
                         VALUES (?, ?, ?, ?, ?, ?)"""
                cursor.execute(sql, (self.nombre, self.fecha, self.hora, self.lugar, self.descripcion, 'Programada'))
                self.id_reunion = cursor.lastrowid
            conexion.commit()
            return self.id_reunion
        except Exception as e:
            MDSnackbar(text=f"Error al guardar reunión: {e}").open()
            return None
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def obtener_reuniones():
        from app.db.conexion import obtener_conexion
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id_reunion, fecha, titulo, descripcion
                FROM Reunion
                ORDER BY fecha DESC
            """)
            
            reuniones = []
            for row in cursor.fetchall():
                reuniones.append(Reunion(
                    id_reunion=row[0],
                    fecha=row[1],
                    titulo=row[2],
                    descripcion=row[3]
                ))
            return reuniones
        except Exception as e:
            print(f"Error al obtener reuniones: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def crear(fecha, titulo, descripcion=None):
        from app.db.conexion import obtener_conexion
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO Reunion (fecha, titulo, descripcion)
                VALUES (?, ?, ?)
            """, (fecha, titulo, descripcion))
            
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error al crear reunión: {e}")
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def actualizar(id_reunion, fecha, titulo, descripcion=None):
        from app.db.conexion import obtener_conexion
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE Reunion
                SET fecha = ?, titulo = ?, descripcion = ?
                WHERE id_reunion = ?
            """, (fecha, titulo, descripcion, id_reunion))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar reunión: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def eliminar(id_reunion):
        from app.db.conexion import obtener_conexion
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM Reunion WHERE id_reunion = ?", (id_reunion,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar reunión: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close() 