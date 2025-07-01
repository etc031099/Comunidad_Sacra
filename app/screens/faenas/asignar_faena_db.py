from app.db.conexion import obtener_conexion

def obtener_miembros_con_estado(id_faena):
    conexion = obtener_conexion()
    miembros = []
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT 
                    m.ID, m.DNI, m.Nombre, m.Apellido_Paterno, 
                    m.Apellido_Materno, m.Dirección,
                    CASE WHEN af.idFaena IS NOT NULL THEN 1 ELSE 0 END as asignado
                FROM MiembroComunidad m
                LEFT JOIN AsignacionFaena af ON m.ID = af.idMiembro 
                    AND af.idFaena = ?
                ORDER BY asignado DESC, m.Nombre
            """, (id_faena,))
            miembros = [{
                "ID": r[0],
                "DNI": r[1],
                "Nombre": f"{r[2]} {r[3]} {r[4]}",
                "Direccion": r[5],
                "asignado": r[6]
            } for r in cursor.fetchall()]
        finally:
            conexion.close()
    return miembros

def asignar_miembro_a_faena(id_faena, miembro_id):
    conexion = obtener_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO AsignacionFaena (idFaena, idMiembro)
                VALUES (?, ?)
            """, (id_faena, miembro_id))
            conexion.commit()
        finally:
            conexion.close()

def desasignar_miembro_de_faena(id_faena, miembro_id):
    conexion = obtener_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                DELETE FROM AsignacionFaena 
                WHERE idFaena = ? AND idMiembro = ?
            """, (id_faena, miembro_id))
            conexion.commit()
        finally:
            conexion.close()

def esta_miembro_asignado(id_faena, miembro_id):
    conexion = obtener_conexion()
    asignado = False
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM AsignacionFaena 
                WHERE idFaena = ? AND idMiembro = ?
            """, (id_faena, miembro_id))
            asignado = cursor.fetchone()[0] > 0
        finally:
            conexion.close()
    return asignado 