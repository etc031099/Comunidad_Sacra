import pyodbc
from threading import Lock
import queue
import time

class ConnectionPool:
    def __init__(self, max_connections=5):
        self.max_connections = max_connections
        self.connections = queue.Queue(maxsize=max_connections)
        self.lock = Lock()
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Inicializa el pool con conexiones"""
        for _ in range(self.max_connections):
            try:
                conn = self._create_connection()
                if conn:
                    self.connections.put(conn)
            except Exception as e:
                print(f"Error creando conexión del pool: {e}")
    
    def _create_connection(self):
        """Crea una nueva conexión"""
        try:
            return pyodbc.connect(
                'DRIVER={ODBC Driver 17 for SQL Server};'
                'SERVER=L_PC\\SSAS2022;'
                'DATABASE=COMUNIDADSACRA1;'
                'UID=sa;'
                'PWD=SSAS2022;'
                'Connection Timeout=10;'
            )
        except Exception as e:
            print(f"Error al crear conexión: {e}")
            return None
    
    def get_connection(self):
        """Obtiene una conexión del pool"""
        try:
            # Intentar obtener conexión existente
            conn = self.connections.get_nowait()
            
            # Verificar si la conexión sigue válida
            try:
                conn.execute("SELECT 1")
                return conn
            except:
                # Si no es válida, crear una nueva
                conn.close()
                return self._create_connection()
                
        except queue.Empty:
            # Si no hay conexiones disponibles, crear una nueva
            return self._create_connection()
    
    def return_connection(self, connection):
        """Devuelve una conexión al pool"""
        if connection:
            try:
                # Verificar si la conexión sigue válida
                connection.execute("SELECT 1")
                self.connections.put_nowait(connection)
            except:
                # Si no es válida, cerrarla
                try:
                    connection.close()
                except:
                    pass

# Instancia global del pool
_pool = None
_pool_lock = Lock()

def get_pool():
    """Obtiene la instancia global del pool"""
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                _pool = ConnectionPool()
    return _pool

def obtener_conexion():
    """Obtiene una conexión del pool"""
    pool = get_pool()
    return pool.get_connection()

def cerrar_conexion(conexion):
    """Devuelve una conexión al pool"""
    if conexion:
        pool = get_pool()
        pool.return_connection(conexion)

# Función de compatibilidad para código existente
def obtener_conexion_legacy():
    """Función original para compatibilidad"""
    try:
        conexion = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=L_PC\\SSAS2022;'
            'DATABASE=COMUNIDADSACRA1;'
            'UID=sa;'
            'PWD=SSAS2022;'
            'Connection Timeout=10;'
        )
        return conexion
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return None
