from app.db.conexion import obtener_conexion
import logging

def obtener_miembros():
    """Obtiene la lista de todos los miembros de la comunidad"""
    conexion = obtener_conexion()
    miembros = []
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT ID, DNI, Nombre, Apellido_Paterno, Apellido_Materno, Correo, Dirección, Teléfono
                FROM MiembroComunidad ORDER BY Nombre
            """)
            miembros = [{
                "ID": r[0],
                "DNI": r[1],
                "Nombre": r[2],
                "Apellido_Paterno": r[3],
                "Apellido_Materno": r[4],
                "Correo": r[5],
                "Dirección": r[6],
                "Teléfono": r[7]
            } for r in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error al obtener miembros: {e}")
        finally:
            conexion.close()
    return miembros

def eliminar_miembro_completo(miembro_id):
    """Elimina un miembro y todos sus datos relacionados en una transacción"""
    conexion = obtener_conexion()
    if not conexion:
        return False, "No se pudo conectar a la base de datos."
    
    try:
        cursor = conexion.cursor()
        
        # 1. Obtener y eliminar Pagos de Penalizaciones
        cursor.execute("SELECT id_penalizacion FROM Penalizaciones WHERE id_miembro = ?", (miembro_id,))
        penalizaciones_ids = [row[0] for row in cursor.fetchall()]
        if penalizaciones_ids:
            # El placeholder '?' se debe repetir por cada id
            placeholders = ','.join('?' for _ in penalizaciones_ids)
            cursor.execute(f"DELETE FROM PagosPenalizaciones WHERE id_penalizacion IN ({placeholders})", penalizaciones_ids)

        # 2. Eliminar Penalizaciones
        cursor.execute("DELETE FROM Penalizaciones WHERE id_miembro = ?", (miembro_id,))
        
        # 3. Eliminar Evidencias (obteniendo IDs de asistencia primero)
        cursor.execute("SELECT id_asistencia FROM Asistencia WHERE id_comunero = ?", (miembro_id,))
        asistencia_reunion_ids = [row[0] for row in cursor.fetchall()]
        if asistencia_reunion_ids:
            placeholders = ','.join('?' for _ in asistencia_reunion_ids)
            cursor.execute(f"DELETE FROM EvidenciasJustificacion WHERE tipo_registro = 'REUNION' AND id_registro IN ({placeholders})", asistencia_reunion_ids)

        cursor.execute("SELECT idAsistenciaDiaria FROM AsistenciaFaenaDiaria WHERE idMiembro = ?", (miembro_id,))
        asistencia_faena_ids = [row[0] for row in cursor.fetchall()]
        if asistencia_faena_ids:
            placeholders = ','.join('?' for _ in asistencia_faena_ids)
            cursor.execute(f"DELETE FROM EvidenciasJustificacion WHERE tipo_registro = 'FAENA' AND id_registro IN ({placeholders})", asistencia_faena_ids)

        # 4. Eliminar Asistencias
        cursor.execute("DELETE FROM Asistencia WHERE id_comunero = ?", (miembro_id,))
        cursor.execute("DELETE FROM AsistenciaFaenaDiaria WHERE idMiembro = ?", (miembro_id,))
        cursor.execute("DELETE FROM AsistenciaFaena WHERE idMiembro = ?", (miembro_id,)) # Por si aún existe la tabla antigua

        # 5. Eliminar Asignaciones y Reconocimientos
        cursor.execute("DELETE FROM AsignacionFaena WHERE idMiembro = ?", (miembro_id,))
        cursor.execute("DELETE FROM Reconocimiento WHERE id_miembro = ?", (miembro_id,))

        # 6. Finalmente, eliminar al miembro
        cursor.execute("DELETE FROM MiembroComunidad WHERE ID = ?", (miembro_id,))
        
        conexion.commit()
        return True, "Miembro eliminado con éxito."
        
    except Exception as e:
        conexion.rollback()
        logging.error(f"Error al eliminar miembro y sus dependencias: {e}")
        return False, "No se pudo completar la eliminación. Se revirtieron los cambios."
    finally:
        if conexion:
            conexion.close() 