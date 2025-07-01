from app.db.conexion import obtener_conexion
import logging

def obtener_todas_reuniones():
    """Obtiene todas las reuniones ordenadas por fecha descendente"""
    conexion = obtener_conexion()
    reuniones = []
    
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_reunion, fecha, titulo, hora_inicio, descripcion FROM Reunion ORDER BY fecha DESC")
            reuniones = [
                {
                    "id_reunion": r[0], 
                    "fecha": str(r[1]), 
                    "titulo": r[2], 
                    "hora_inicio": str(r[3]) if r[3] else "", 
                    "descripcion": r[4] if r[4] else ""
                } 
                for r in cursor.fetchall()
            ]
        except Exception as e:
            logging.error(f"Error al obtener reuniones: {e}")
        finally:
            conexion.close()
            
    return reuniones

def eliminar_reunion_completa(id_reunion):
    """Elimina una reunión y todos sus datos relacionados en una transacción"""
    conexion = obtener_conexion()
    exito = False
    
    if conexion:
        try:
            cursor = conexion.cursor()

            # 1. Eliminar Pagos de Penalizaciones relacionadas
            cursor.execute("""
                DELETE FROM PagosPenalizaciones
                WHERE id_penalizacion IN (
                    SELECT id_penalizacion FROM Penalizaciones 
                    WHERE tipo_evento = 'REUNION' AND id_evento = ?
                )
            """, (id_reunion,))

            # 2. Eliminar Penalizaciones relacionadas
            cursor.execute("""
                DELETE FROM Penalizaciones 
                WHERE tipo_evento = 'REUNION' AND id_evento = ?
            """, (id_reunion,))

            # 3. Eliminar Evidencias de justificaciones
            cursor.execute("""
                DELETE FROM EvidenciasJustificacion
                WHERE tipo_registro = 'REUNION' AND id_registro IN (
                    SELECT id_asistencia FROM Asistencia WHERE id_reunion = ?
                )
            """, (id_reunion,))

            # 4. Eliminar Asistencias a la reunión
            cursor.execute("DELETE FROM Asistencia WHERE id_reunion = ?", (id_reunion,))

            # 5. Finalmente, eliminar la reunión
            cursor.execute("DELETE FROM Reunion WHERE id_reunion = ?", (id_reunion,))

            conexion.commit()
            exito = True
            
        except Exception as e:
            if conexion:
                conexion.rollback()
            logging.error(f"Error al eliminar reunión: {e}")
        finally:
            conexion.close()
            
    return exito 