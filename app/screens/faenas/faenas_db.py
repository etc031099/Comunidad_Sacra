from app.db.conexion import obtener_conexion

def obtener_faenas():
    conexion = obtener_conexion()
    faenas = []
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT idFaena, nombre, descripcion, fecha_inicio, fecha_fin, 
                   ubicacion, estado, tipo, tipoJornada, motivoExtra
                FROM Faena ORDER BY fecha_inicio DESC
            """)
            faenas = [{
                "idFaena": r[0],
                "nombre": r[1],
                "descripcion": r[2],
                "fecha_inicio": str(r[3]) if r[3] else "",
                "fecha_fin": str(r[4]) if r[4] else "",
                "ubicacion": r[5],
                "estado": r[6],
                "tipo": r[7],
                "tipoJornada": r[8],
                "motivoExtra": r[9]
            } for r in cursor.fetchall()]
        finally:
            conexion.close()
    return faenas

def eliminar_faena_completa(id_faena):
    conexion = obtener_conexion()
    if not conexion:
        return False
    try:
        cursor = conexion.cursor()
        # 1. Eliminar Pagos de Penalizaciones relacionadas
        cursor.execute("""
            DELETE FROM PagosPenalizaciones
            WHERE id_penalizacion IN (
                SELECT id_penalizacion FROM Penalizaciones 
                WHERE tipo_evento = 'FAENA' AND id_evento = ?
            )
        """, (id_faena,))
        # 2. Eliminar Penalizaciones relacionadas
        cursor.execute("""
            DELETE FROM Penalizaciones 
            WHERE tipo_evento = 'FAENA' AND id_evento = ?
        """, (id_faena,))
        # 3. Eliminar Evidencias de justificaciones
        cursor.execute("""
            DELETE FROM EvidenciasJustificacion
            WHERE tipo_registro = 'FAENA' AND id_registro IN (
                SELECT idAsistencia FROM AsistenciaFaena WHERE idFaena = ?
            )
        """, (id_faena,))
        # 4. Eliminar Asistencias a la faena (tabla general)
        cursor.execute("DELETE FROM AsistenciaFaena WHERE idFaena = ?", (id_faena,))
        # 5. Eliminar Asistencias diarias a la faena
        cursor.execute("DELETE FROM AsistenciaFaenaDiaria WHERE idFaena = ?", (id_faena,))
        # 6. Eliminar Asignaciones de la faena
        cursor.execute("DELETE FROM AsignacionFaena WHERE idFaena = ?", (id_faena,))
        # 7. Finalmente, eliminar la faena
        cursor.execute("DELETE FROM Faena WHERE idFaena = ?", (id_faena,))
        conexion.commit()
        return True
    except Exception as e:
        if conexion:
            conexion.rollback()
        print(f"Error al eliminar faena: {e}")
        return False
    finally:
        if conexion:
            conexion.close() 