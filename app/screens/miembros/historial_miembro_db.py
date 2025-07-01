from app.db.conexion import obtener_conexion
from datetime import datetime, timedelta
import logging
import traceback

def obtener_miembros():
    """Obtiene la lista de todos los miembros de la comunidad"""
    conexion = obtener_conexion()
    miembros = []
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT ID, Nombre, Apellido_Paterno, Apellido_Materno, DNI FROM MiembroComunidad ORDER BY Nombre")
            miembros = cursor.fetchall()
        except Exception as e:
            logging.error("Error al cargar miembros:", exc_info=True)
        finally:
            conexion.close()
    return miembros

def obtener_nombre_miembro(id_miembro):
    """Obtiene el nombre completo de un miembro por su ID"""
    conexion = obtener_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT Nombre, Apellido_Paterno, Apellido_Materno FROM MiembroComunidad WHERE ID = ?", (id_miembro,))
            miembro_data = cursor.fetchone()
            if miembro_data:
                return f"{miembro_data[0]} {miembro_data[1]} {miembro_data[2]}"
            return "Miembro no encontrado"
        except Exception as e:
            logging.error(f"Error al obtener nombre de miembro {id_miembro}:", exc_info=True)
            return "Error al cargar nombre"
        finally:
            conexion.close()
    return "Error de conexión"

def obtener_fecha_inicio(periodo):
    """Calcula la fecha de inicio según el período seleccionado"""
    hoy = datetime.now()
    if periodo == "Última Semana":
        return hoy - timedelta(days=7)
    elif periodo == "Último Mes":
        return hoy - timedelta(days=30)
    elif periodo == "Último Año":
        return hoy - timedelta(days=365)
    elif periodo == "Últimos 3 Meses":
        return hoy - timedelta(days=90)
    elif periodo == "Últimos 6 Meses":
        return hoy - timedelta(days=180)
    else:  # Todo el historial
        return datetime(2000, 1, 1)  # Fecha muy antigua para obtener todo

def obtener_historial_miembro(id_miembro, periodo, tipo_evento_filtro, estado_filtro):
    """Obtiene el historial completo de un miembro con filtros aplicados"""
    conexion = obtener_conexion()
    if not conexion:
        return []
    
    try:
        cursor = conexion.cursor()
        fecha_inicio = obtener_fecha_inicio(periodo)

        query_parts = []
        params = []

        # Asistencia Faena Diaria
        query_parts.append("""
        SELECT 
            'FAENA' as tipo_evento,
            f.nombre as nombre_evento,
            afd.fecha_asistencia as fecha,
            afd.estado_asistencia as estado,
            afd.observaciones as detalles
        FROM AsistenciaFaenaDiaria afd
        JOIN Faena f ON afd.idFaena = f.idFaena
        WHERE afd.idMiembro = ? AND afd.fecha_asistencia >= ?
        """)
        params.extend([id_miembro, fecha_inicio])

        # Asistencia Reunión
        query_parts.append("""
        SELECT 
            'REUNION' as tipo_evento,
            r.titulo as nombre_evento,
            a.fecha_registro as fecha,
            a.estado_asistencia as estado,
            NULL as detalles
        FROM Asistencia a
        JOIN Reunion r ON a.id_reunion = r.id_reunion
        WHERE a.id_comunero = ? AND a.fecha_registro >= ?
        """)
        params.extend([id_miembro, fecha_inicio])

        # Penalizaciones
        query_parts.append("""
        SELECT 
            'PENALIZACION' as tipo_evento,
            CASE 
                WHEN p.tipo_evento = 'FAENA' THEN f.nombre
                WHEN p.tipo_evento = 'REUNION' THEN r.titulo
            END as nombre_evento,
            p.fecha_aplicacion as fecha,
            p.estado as estado,
            p.observaciones as detalles
        FROM Penalizaciones p
        LEFT JOIN Faena f ON p.id_evento = f.idFaena AND p.tipo_evento = 'FAENA'
        LEFT JOIN Reunion r ON p.id_evento = r.id_reunion AND p.tipo_evento = 'REUNION'
        WHERE p.id_miembro = ? AND p.fecha_aplicacion >= ?
        """)
        params.extend([id_miembro, fecha_inicio])

        # Construcción de la consulta para evitar ORDER BY en subqueries
        full_query = " UNION ALL ".join(query_parts)

        # Aplica los filtros primero
        where_clauses = []
        filtered_params = list(params)  # Copia de params para no modificar el original
        if tipo_evento_filtro != "Todos":
            where_clauses.append("tipo_evento = ?")
            filtered_params.append(tipo_evento_filtro)
        if estado_filtro != "Todos":
            where_clauses.append("estado = ?")
            filtered_params.append(estado_filtro)

        if where_clauses:
            full_query = f"SELECT * FROM ({full_query}) as subquery WHERE {' AND '.join(where_clauses)}"

        # El ORDER BY va solo al final
        full_query += " ORDER BY tipo_evento, nombre_evento, fecha DESC"

        cursor.execute(full_query, filtered_params)
        return cursor.fetchall()
        
    except Exception as e:
        logging.error("Error al cargar historial del miembro:", exc_info=True)
        return []
    finally:
        conexion.close() 