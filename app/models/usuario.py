class Usuario:
    def __init__(self, id_usuario, nombre, apellido, email, rol):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.rol = rol

    @staticmethod
    def autenticar(email, password):
        from app.db.conexion import obtener_conexion
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id_usuario, nombre, apellido, email, rol
                FROM Usuario
                WHERE email = ? AND password = ?
            """, (email, password))
            
            usuario = cursor.fetchone()
            if usuario:
                return Usuario(
                    id_usuario=usuario[0],
                    nombre=usuario[1],
                    apellido=usuario[2],
                    email=usuario[3],
                    rol=usuario[4]
                )
            return None
        except Exception as e:
            print(f"Error al autenticar usuario: {e}")
            return None
        finally:
            cursor.close()
            conn.close()