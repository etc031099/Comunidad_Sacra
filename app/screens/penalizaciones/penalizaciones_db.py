from app.db.conexion import obtener_conexion
from datetime import datetime, timedelta, date
import pyodbc
import logging

def obtener_penalizaciones_por_miembro(filtro_estado="Todos", filtro_fecha_desde=None, filtro_fecha_hasta=None):
    """Obtiene las penalizaciones agrupadas por miembro con filtros aplicados"""
    conexion = obtener_conexion()
    miembros_con_penalizaciones = []
    
    if conexion:
        try:
            cursor = conexion.cursor()
            penalizaciones_where_list = ["tipo_evento = 'REUNION'"]
            
            if filtro_estado == "PENDIENTE":
                penalizaciones_where_list.append(f"estado = 'PENDIENTE'")
            elif filtro_estado == "CANCELADO":
                penalizaciones_where_list.append(f"estado = 'CANCELADO'")
                
            if filtro_fecha_desde and filtro_fecha_hasta:
                penalizaciones_where_list.append(f"CAST(fecha_aplicacion AS DATE) BETWEEN '{filtro_fecha_desde}' AND '{filtro_fecha_hasta}'")
                
            penalizaciones_where_clause = " AND ".join(penalizaciones_where_list)

            query = f"""
            WITH MiembrosConPenalizacionesFiltradas AS (
                SELECT DISTINCT id_miembro
                FROM Penalizaciones
                WHERE {penalizaciones_where_clause}
            )
            SELECT
                m.ID,
                m.Nombre + ' ' + m.Apellido_Paterno + ' ' + m.Apellido_Materno AS NombreCompleto,
                (
                    SELECT ISNULL(SUM(valor), 0)
                    FROM Penalizaciones
                    WHERE id_miembro = m.ID
                    AND tipo_evento = 'REUNION'
                    AND tipo_penalizacion = 'MULTA'
                    AND estado = 'PENDIENTE'
                ) AS TotalMultasReuniones,
                (
                    SELECT COUNT(DISTINCT fecha_asistencia)
                    FROM AsistenciaFaenaDiaria
                    WHERE idMiembro = m.ID
                    AND estado_asistencia IN ('Presente', 'Justificado')
                ) AS AsistenciasValidas
            FROM MiembroComunidad m
            JOIN MiembrosConPenalizacionesFiltradas f ON m.ID = f.id_miembro
            ORDER BY TotalMultasReuniones DESC, NombreCompleto
            """
            cursor.execute(query)
            miembros_con_penalizaciones = cursor.fetchall()

            # Filtrado adicional para CANCELADO: solo mostrar miembros sin ninguna multa pendiente
            if filtro_estado == "CANCELADO":
                miembros_filtrados = []
                for miembro in miembros_con_penalizaciones:
                    id_miembro, nombre_completo, total_multas_reuniones, asistencias_validas = miembro
                    
                    faltas_faena = max(0, 5 - (asistencias_validas or 0))
                    total_multas_faena = faltas_faena * 60
                    if (total_multas_reuniones or 0) == 0 and total_multas_faena == 0:
                        miembros_filtrados.append((id_miembro, nombre_completo, total_multas_reuniones, asistencias_validas))
                miembros_con_penalizaciones = miembros_filtrados
                
        except Exception as e:
            logging.error(f"Error al obtener penalizaciones por miembro: {e}")
        finally:
            conexion.close()
            
    return miembros_con_penalizaciones

def obtener_multas_miembro(id_miembro, filtro_estado="Todos", filtro_fecha_desde=None, filtro_fecha_hasta=None):
    """Obtiene las multas específicas de un miembro"""
    conexion = obtener_conexion()
    multas = []
    
    if conexion:
        try:
            cursor = conexion.cursor()
            
            query_base = """
                SELECT 
                    p.id_penalizacion, p.tipo_evento, p.valor, p.fecha_aplicacion, p.estado,
                    r.titulo as nombre_evento,
                    ISNULL(SUM(pp.monto_pagado), 0) as valor_pagado,
                    p.valor - ISNULL(SUM(pp.monto_pagado), 0) as valor_pendiente
                FROM Penalizaciones p
                LEFT JOIN PagosPenalizaciones pp ON p.id_penalizacion = pp.id_penalizacion
                LEFT JOIN Reunion r ON p.id_evento = r.id_reunion
                WHERE p.id_miembro = ? AND p.tipo_evento = 'REUNION'
            """
            
            where_conditions = []
            params = [id_miembro]
            
            if filtro_estado != "Todos":
                where_conditions.append("p.estado = ?")
                params.append(filtro_estado)
            
            if filtro_fecha_desde and filtro_fecha_hasta:
                where_conditions.append("CAST(p.fecha_aplicacion AS DATE) BETWEEN ? AND ?")
                params.append(filtro_fecha_desde)
                params.append(filtro_fecha_hasta)
            
            if where_conditions:
                query_base += " AND " + " AND ".join(where_conditions)
            
            query_base += """
                GROUP BY 
                    p.id_penalizacion, p.tipo_evento, p.valor, p.fecha_aplicacion, p.estado, r.titulo
                ORDER BY p.fecha_aplicacion DESC
            """
            
            cursor.execute(query_base, params)
            multas = cursor.fetchall()
            
        except Exception as e:
            logging.error(f"Error al obtener multas del miembro: {e}")
        finally:
            conexion.close()
            
    return multas

def obtener_rango_fechas_penalizaciones():
    """Obtiene la fecha mínima y máxima de penalizaciones para usar como rango en el calendario"""
    conexion = obtener_conexion()
    min_date = None
    max_date = None
    
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT MIN(fecha_aplicacion), MAX(fecha_aplicacion) FROM Penalizaciones WHERE tipo_evento = 'REUNION'")
            resultado = cursor.fetchone()
            if resultado and resultado[0] and resultado[1]:
                min_date = resultado[0]
                max_date = resultado[1]
        except Exception as e:
            logging.error(f"Error al obtener rango de fechas: {e}")
        finally:
            conexion.close()
            
    return min_date, max_date

def obtener_estadisticas_penalizaciones():
    """Obtiene estadísticas generales de penalizaciones"""
    conexion = obtener_conexion()
    stats = None
    stats_por_evento = []
    
    if conexion:
        try:
            cursor = conexion.cursor()
            
            # Estadísticas generales
            cursor.execute("""
                SELECT 
                    COUNT(*),
                    COUNT(CASE WHEN estado = 'PENDIENTE' THEN 1 END),
                    COUNT(CASE WHEN estado = 'CANCELADO' THEN 1 END),
                    SUM(CASE WHEN tipo_penalizacion = 'MULTA' AND estado = 'PENDIENTE' THEN valor ELSE 0 END)
                FROM Penalizaciones WHERE tipo_evento = 'REUNION'
            """)
            stats = cursor.fetchone()
            
            # Estadísticas por tipo de evento
            cursor.execute("""
                SELECT tipo_evento, COUNT(*), SUM(CASE WHEN estado = 'PENDIENTE' THEN valor ELSE 0 END)
                FROM Penalizaciones WHERE tipo_penalizacion = 'MULTA' AND tipo_evento = 'REUNION'
                GROUP BY tipo_evento
            """)
            stats_por_evento = cursor.fetchall()
            
        except Exception as e:
            logging.error(f"Error al obtener estadísticas: {e}")
        finally:
            conexion.close()
            
    return stats, stats_por_evento

def cancelar_multas_acumuladas(id_miembro):
    """Cancela todas las multas pendientes de un miembro y regulariza sus faenas"""
    conexion = obtener_conexion()
    success = False
    
    if conexion:
        try:
            cursor = conexion.cursor()
            
            # Anular multas por reuniones
            cursor.execute(
                "UPDATE Penalizaciones SET estado = 'CANCELADO', observaciones = 'Cancelado por regularización de pago anual.' WHERE id_miembro = ? AND tipo_evento = 'REUNION' AND estado = 'PENDIENTE'",
                (id_miembro,)
            )

            # Regularizar asistencias a faenas
            # 1. Asegurarse de que todas las ausencias injustificadas se conviertan en justificadas
            cursor.execute("""
                UPDATE AsistenciaFaenaDiaria
                SET estado_asistencia = 'Justificado', justificacion = 'Regularización anual automática'
                WHERE idMiembro = ? AND estado_asistencia = 'Ausente'
            """, (id_miembro,))

            # 2. Recalcular cuántas asistencias válidas tiene el miembro AHORA
            cursor.execute("""
                SELECT COUNT(DISTINCT fecha_asistencia)
                FROM AsistenciaFaenaDiaria
                WHERE idMiembro = ? AND estado_asistencia IN ('Presente', 'Justificado')
            """, (id_miembro,))
            resultado = cursor.fetchone()
            asistencias_validas = resultado[0] if resultado and resultado[0] is not None else 0

            # 3. Si aún faltan para llegar a 5, agregar nuevas asistencias justificadas
            if asistencias_validas < 5:
                # Buscar TODAS las faenas asignadas al miembro para encontrar 'días libres'
                cursor.execute("""
                    SELECT f.idFaena, f.fecha_inicio, f.fecha_fin
                    FROM AsignacionFaena af
                    JOIN Faena f ON af.idFaena = f.idFaena
                    WHERE af.idMiembro = ?
                    ORDER BY f.fecha_fin DESC, f.idFaena DESC
                """, (id_miembro,))
                faenas_asignadas = cursor.fetchall()

                if faenas_asignadas:
                    dias_a_agregar = 5 - asistencias_validas
                    
                    # Iterar sobre todas las faenas asignadas para rellenar los huecos
                    for id_faena, fecha_inicio, fecha_fin in faenas_asignadas:
                        if dias_a_agregar <= 0:
                            break  # Ya hemos agregado suficientes

                        if not fecha_inicio or not fecha_fin:
                            continue  # Saltar faenas sin rango de fechas válido

                        # Iterar día por día dentro del rango de la faena
                        dias_en_rango = (fecha_fin - fecha_inicio).days
                        for i in range(dias_en_rango + 1):
                            if dias_a_agregar <= 0:
                                break
                            
                            fecha_a_revisar = fecha_inicio + timedelta(days=i)
                            
                            try:
                                # Intentar insertar. Si ya existe un registro para ese día,
                                # el UNIQUE constraint lo impedirá y saltará al except.
                                cursor.execute("""
                                    INSERT INTO AsistenciaFaenaDiaria (idFaena, idMiembro, fecha_asistencia, estado_asistencia, justificacion)
                                    VALUES (?, ?, ?, 'Justificado', 'Regularización anual automática')
                                """, (id_faena, id_miembro, fecha_a_revisar))
                                dias_a_agregar -= 1
                            except pyodbc.IntegrityError:
                                # Este día ya tiene un registro de asistencia (presente, ausente, etc.),
                                # lo cual es correcto. Simplemente lo ignoramos y pasamos al siguiente día libre.
                                pass

            conexion.commit()
            success = True
            
        except Exception as e:
            if conexion:
                conexion.rollback()
            logging.error(f"Error al cancelar multas acumuladas: {e}")
        finally:
            conexion.close()
            
    return success

def exportar_penalizaciones(filtro_estado="Todos", filtro_fecha_desde=None, filtro_fecha_hasta=None):
    """Exporta las penalizaciones filtradas a un formato de texto"""
    conexion = obtener_conexion()
    contenido = []
    
    if conexion:
        try:
            cursor = conexion.cursor()
            penalizaciones_where_list = ["p.tipo_evento = 'REUNION'"]
            
            if filtro_estado != "Todos":
                penalizaciones_where_list.append(f"p.estado = '{filtro_estado}'")
                
            if filtro_fecha_desde and filtro_fecha_hasta:
                penalizaciones_where_list.append(f"CAST(p.fecha_aplicacion AS DATE) BETWEEN '{filtro_fecha_desde}' AND '{filtro_fecha_hasta}'")
                
            penalizaciones_where_clause = " AND ".join(penalizaciones_where_list)

            query = f"""
            WITH MiembrosConPenalizacionesFiltradas AS (
                SELECT DISTINCT id_miembro FROM Penalizaciones p WHERE {penalizaciones_where_clause}
            )
            SELECT m.Nombre + ' ' + m.Apellido_Paterno + ' ' + m.Apellido_Materno AS NombreCompleto,
                (SELECT ISNULL(SUM(valor), 0) FROM Penalizaciones WHERE id_miembro = m.ID AND tipo_evento = 'REUNION' AND tipo_penalizacion = 'MULTA' AND estado = 'PENDIENTE') AS TotalMultasPendientes,
                (SELECT COUNT(DISTINCT fecha_asistencia) FROM AsistenciaFaenaDiaria WHERE idMiembro = m.ID AND estado_asistencia IN ('Presente', 'Justificado')) AS AsistenciasValidas
            FROM MiembroComunidad m
            JOIN MiembrosConPenalizacionesFiltradas f ON m.ID = f.id_miembro
            ORDER BY TotalMultasPendientes DESC, NombreCompleto
            """
            cursor.execute(query)
            miembros = cursor.fetchall()
            
            contenido = [
                "REPORTE DE PENALIZACIONES",
                "="*50,
                f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                ""
            ]
            
            filtros_activos = []
            if filtro_estado != "Todos":
                filtros_activos.append(f"Estado: {filtro_estado}")
            if filtro_fecha_desde and filtro_fecha_hasta:
                filtros_activos.append(f"Fecha: {filtro_fecha_desde} - {filtro_fecha_hasta}")
            
            if filtros_activos:
                contenido.append("Filtros aplicados:")
                contenido.extend(f"  • {filtro}" for filtro in filtros_activos)
            else:
                contenido.append("Sin filtros aplicados")
            contenido.append("")
            
            contenido.append(f"Total de miembros con penalizaciones: {len(miembros)}")
            contenido.append("")
            
            for miembro in miembros:
                contenido.append(f"Miembro: {miembro[0]}")
                contenido.append(f"  • Total pendiente: S/. {miembro[1]:.2f}")
                contenido.append(f"  • Asistencias válidas: {miembro[2]}/5")
                contenido.append("")
                
        except Exception as e:
            logging.error(f"Error al exportar penalizaciones: {e}")
        finally:
            conexion.close()
            
    return contenido 