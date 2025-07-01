from app.db.conexion import obtener_conexion, cerrar_conexion

def validar_credenciales_admin(dni, contrasena):
    """Valida las credenciales del administrador"""
    conexion = obtener_conexion()
    if not conexion:
        return False, "Error de conexión con la base de datos"
    
    try:
        cursor = conexion.cursor()
        # Consulta optimizada con índices específicos
        query = """
        SELECT TOP 1 ID, DNI, Nombre 
        FROM Administrador 
        WHERE DNI = ? AND Contraseña = ?
        """
        cursor.execute(query, (dni, contrasena))
        resultado = cursor.fetchone()
        
        if resultado:
            return True, ""
        else:
            return False, "DNI o contraseña incorrectos"
            
    except Exception as e:
        return False, f"Error al validar credenciales: {str(e)}"
    finally:
        cerrar_conexion(conexion) 