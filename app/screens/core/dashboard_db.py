from datetime import datetime
from app.db.conexion import obtener_conexion, cerrar_conexion

def calcular_kpis():
    now = datetime.now()
    kpis = {
        "miembro_del_mes": "-",
        "asistencia_perfecta": 0,
        "cero_penalizaciones": 0
    }
    conexion = obtener_conexion()
    if not conexion:
        return kpis
    try:
        cursor = conexion.cursor()
        
        # Consulta optimizada para miembro del mes
        cursor.execute("""
            SELECT TOP 1
                (m.Nombre + ' ' + m.Apellido_Paterno + ' ' + m.Apellido_Materno) as NombreCompleto,
                ISNULL(pr.Puntos, 0) + ISNULL(pf.Puntos, 0) as PuntosTotales
            FROM MiembroComunidad m
            LEFT JOIN (
                SELECT id_comunero, COUNT(*) as Puntos 
                FROM Asistencia 
                WHERE MONTH(fecha_registro) = ? AND YEAR(fecha_registro) = ?
                GROUP BY id_comunero
            ) pr ON m.ID = pr.id_comunero
            LEFT JOIN (
                SELECT idMiembro, COUNT(*) * 2 as Puntos 
                FROM AsistenciaFaena 
                WHERE MONTH(fecha_registro) = ? AND YEAR(fecha_registro) = ?
                GROUP BY idMiembro
            ) pf ON m.ID = pf.idMiembro
            ORDER BY PuntosTotales DESC
        """, (now.month, now.year, now.month, now.year))
        
        miembro_mes_row = cursor.fetchone()
        if miembro_mes_row:
            kpis["miembro_del_mes"] = miembro_mes_row[0]
        
        # Consulta optimizada para asistencia perfecta
        cursor.execute("""
            SELECT COUNT(*) 
            FROM (
                SELECT idMiembro
                FROM AsistenciaFaena
                WHERE MONTH(fecha_registro) = ? AND YEAR(fecha_registro) = ?
                GROUP BY idMiembro
                HAVING COUNT(DISTINCT idFaena) = (
                    SELECT COUNT(*) 
                    FROM Faena 
                    WHERE MONTH(fecha_inicio) = ? AND YEAR(fecha_inicio) = ?
                )
            ) as MiembrosPerfectos
        """, (now.month, now.year, now.month, now.year))
        
        asistencia_perfecta_row = cursor.fetchone()
        if asistencia_perfecta_row:
            kpis["asistencia_perfecta"] = asistencia_perfecta_row[0]
        
        # Consulta optimizada para cero penalizaciones
        cursor.execute("""
            SELECT COUNT(ID) 
            FROM MiembroComunidad 
            WHERE ID NOT IN (
                SELECT DISTINCT id_miembro 
                FROM Penalizaciones 
                WHERE MONTH(fecha_aplicacion) = ? AND YEAR(fecha_aplicacion) = ?
            )
        """, (now.month, now.year))
        
        cero_penalizaciones_row = cursor.fetchone()
        if cero_penalizaciones_row:
            kpis["cero_penalizaciones"] = cero_penalizaciones_row[0]
            
    except Exception as e:
        print(f"Error calculando KPIs: {e}")
    finally:
        cerrar_conexion(conexion)
    return kpis 