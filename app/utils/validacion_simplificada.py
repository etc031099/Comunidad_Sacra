"""
Sistema de validación simplificado para formularios existentes
Compatible con MDTextField normales sin necesidad de componentes personalizados
"""

from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from typing import List, Dict, Any, Tuple
import re
from datetime import datetime

class ValidacionSimplificada:
    """
    Clase para validaciones simplificadas que funcionan con MDTextField normales
    """
    
    @staticmethod
    def validar_texto(texto: str, campo: str, requerido: bool = True, 
                     min_longitud: int = 1, max_longitud: int = 255) -> Tuple[bool, str]:
        """Valida texto genérico"""
        texto = texto.strip() if texto else ""
        
        if requerido and not texto:
            return False, f"El campo '{campo}' es obligatorio"
        
        if len(texto) < min_longitud:
            return False, f"El campo '{campo}' debe tener al menos {min_longitud} caracteres"
        
        if len(texto) > max_longitud:
            return False, f"El campo '{campo}' no puede exceder {max_longitud} caracteres"
        
        return True, ""
    
    @staticmethod
    def validar_nombre(nombre: str, campo: str = "Nombre") -> Tuple[bool, str]:
        """Valida nombres y apellidos"""
        es_valido, mensaje = ValidacionSimplificada.validar_texto(
            nombre, campo, requerido=True, min_longitud=2, max_longitud=50
        )
        if not es_valido:
            return es_valido, mensaje
        
        # Validar que solo contenga letras, espacios y algunos caracteres especiales
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            return False, f"El campo '{campo}' solo puede contener letras y espacios"
        
        return True, ""
    
    @staticmethod
    def validar_dni(dni: str) -> Tuple[bool, str]:
        """Valida formato de DNI peruano"""
        dni = dni.strip() if dni else ""
        
        if not dni:
            return False, "El DNI es obligatorio"
        
        # Validar formato: 8 dígitos
        if not re.match(r'^\d{8}$', dni):
            return False, "El DNI debe tener exactamente 8 dígitos numéricos"
        
        return True, ""
    
    @staticmethod
    def validar_email(email: str, requerido: bool = False) -> Tuple[bool, str]:
        """Valida formato de email"""
        email = email.strip() if email else ""
        
        if not requerido and not email:
            return True, ""
        
        if requerido and not email:
            return False, "El correo electrónico es obligatorio"
        
        # Patrón básico de validación de email
        patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(patron_email, email):
            return False, "El formato del correo electrónico no es válido"
        
        return True, ""
    
    @staticmethod
    def validar_fecha(fecha_str: str, campo: str = "Fecha") -> Tuple[bool, str]:
        """Valida formato de fecha"""
        fecha_str = fecha_str.strip() if fecha_str else ""
        
        if not fecha_str:
            return False, f"El campo '{campo}' es obligatorio"
        
        try:
            # Intentar parsear la fecha
            datetime.strptime(fecha_str, "%Y-%m-%d")
        except ValueError:
            return False, f"El formato de fecha debe ser YYYY-MM-DD"
        
        return True, ""
    
    @staticmethod
    def validar_rango_fechas(fecha_inicio: str, fecha_fin: str) -> Tuple[bool, str]:
        """Valida que la fecha de inicio sea anterior a la fecha de fin"""
        # Validar formato de fechas
        es_valido_inicio, mensaje = ValidacionSimplificada.validar_fecha(fecha_inicio, "Fecha de inicio")
        if not es_valido_inicio:
            return False, mensaje
        
        es_valido_fin, mensaje = ValidacionSimplificada.validar_fecha(fecha_fin, "Fecha de fin")
        if not es_valido_fin:
            return False, mensaje
        
        # Comparar fechas
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
            
            if fecha_inicio_obj > fecha_fin_obj:
                return False, "La fecha de inicio no puede ser posterior a la fecha de fin"
            
        except ValueError:
            return False, "Error al procesar las fechas"
        
        return True, ""

class UIValidacionSimplificada:
    """
    Utilidades para mostrar errores de validación
    """
    
    @staticmethod
    def mostrar_error_snackbar(mensaje: str, duracion: float = 3.0):
        """Muestra un error en un snackbar"""
        snackbar = MDSnackbar(
            MDLabel(
                text=mensaje,
                theme_text_color="Custom",
                text_color="white",
            ),
            duration=duracion
        )
        snackbar.open()
    
    @staticmethod
    def mostrar_error_dialogo(titulo: str, mensaje: str, callback=None):
        """Muestra un error en un diálogo"""
        def cerrar_dialogo(instance):
            dialog.dismiss()
            if callback:
                callback()
        
        dialog = MDDialog(
            title=titulo,
            text=mensaje,
            buttons=[
                MDFlatButton(
                    text="Aceptar",
                    on_release=cerrar_dialogo
                )
            ]
        )
        dialog.open()
    
    @staticmethod
    def mostrar_errores_multiples(errores: List[str], titulo: str = "Errores de Validación"):
        """Muestra múltiples errores en un diálogo"""
        if not errores:
            return
        
        mensaje = "\n• ".join([""] + errores)
        UIValidacionSimplificada.mostrar_error_dialogo(titulo, mensaje)
    
    @staticmethod
    def mostrar_error_en_campo(campo, mensaje: str):
        """Muestra un error en un campo MDTextField"""
        if hasattr(campo, 'error'):
            campo.error = True
            campo.helper_text = mensaje
            campo.helper_text_mode = "on_error"
    
    @staticmethod
    def limpiar_error_en_campo(campo):
        """Limpia el error de un campo MDTextField"""
        if hasattr(campo, 'error'):
            campo.error = False
            campo.helper_text = ""
            campo.helper_text_mode = "on_focus"
    
    @staticmethod
    def actualizar_campo(campo, es_valido: bool, mensaje_error: str = ""):
        """Actualiza el estado visual de un campo según la validación"""
        if hasattr(campo, 'error'):
            if es_valido:
                campo.error = False
                campo.helper_text = ""
                campo.helper_text_mode = "on_focus"
            else:
                campo.error = True
                campo.helper_text = mensaje_error
                campo.helper_text_mode = "on_error"

class ValidacionFormularios:
    """
    Validaciones específicas para formularios completos
    """
    
    @staticmethod
    def validar_datos_miembro(datos: Dict[str, Any]) -> Tuple[bool, str]:
        """Valida todos los datos de un miembro"""
        # Validar nombre
        es_valido, mensaje = ValidacionSimplificada.validar_nombre(datos.get("Nombre", ""), "Nombre")
        if not es_valido:
            return False, mensaje
        
        # Validar apellido paterno
        es_valido, mensaje = ValidacionSimplificada.validar_nombre(datos.get("Apellido_Paterno", ""), "Apellido Paterno")
        if not es_valido:
            return False, mensaje
        
        # Validar apellido materno
        es_valido, mensaje = ValidacionSimplificada.validar_nombre(datos.get("Apellido_Materno", ""), "Apellido Materno")
        if not es_valido:
            return False, mensaje
        
        # Validar DNI
        es_valido, mensaje = ValidacionSimplificada.validar_dni(datos.get("DNI", ""))
        if not es_valido:
            return False, mensaje
        
        # Validar email (opcional)
        es_valido, mensaje = ValidacionSimplificada.validar_email(datos.get("Correo", ""), requerido=False)
        if not es_valido:
            return False, mensaje
        
        return True, ""
    
    @staticmethod
    def validar_datos_reunion(datos: Dict[str, Any]) -> Tuple[bool, str]:
        """Valida todos los datos de una reunión"""
        # Validar título
        es_valido, mensaje = ValidacionSimplificada.validar_texto(
            datos.get("titulo", ""), "Título", requerido=True, min_longitud=3, max_longitud=100
        )
        if not es_valido:
            return False, mensaje
        
        # Validar fecha
        es_valido, mensaje = ValidacionSimplificada.validar_fecha(datos.get("fecha", ""), "Fecha")
        if not es_valido:
            return False, mensaje
        
        # Validar hora (formato básico)
        hora = datos.get("hora_inicio", "")
        if not hora:
            return False, "La hora de inicio es obligatoria"
        
        try:
            datetime.strptime(hora, "%H:%M")
        except ValueError:
            return False, "El formato de hora debe ser HH:MM"
        
        return True, ""
    
    @staticmethod
    def validar_datos_faena(datos: Dict[str, Any]) -> Tuple[bool, str]:
        """Valida todos los datos de una faena"""
        # Validar nombre
        es_valido, mensaje = ValidacionSimplificada.validar_texto(
            datos.get("nombre", ""), "Nombre", requerido=True, min_longitud=3, max_longitud=100
        )
        if not es_valido:
            return False, mensaje
        
        # Validar tipo
        tipo = datos.get("tipo", "")
        if not tipo:
            return False, "Debe seleccionar un tipo de faena"
        
        if tipo.lower() not in ["ordinaria", "extraordinaria"]:
            return False, "El tipo de faena debe ser 'Ordinaria' o 'Extraordinaria'"
        
        # Validar fechas si están presentes (las fechas son opcionales)
        fecha_inicio = datos.get("fecha_inicio", "").strip()
        fecha_fin = datos.get("fecha_fin", "").strip()
        
        # Solo validar fechas si ambas están presentes
        if fecha_inicio and fecha_fin:
            try:
                # Extraer solo la fecha (sin hora) para validación
                fecha_inicio_solo = fecha_inicio.split(" ")[0]
                fecha_fin_solo = fecha_fin.split(" ")[0]
                
                # Validar formato de fecha
                fecha_inicio_obj = datetime.strptime(fecha_inicio_solo, "%Y-%m-%d").date()
                fecha_fin_obj = datetime.strptime(fecha_fin_solo, "%Y-%m-%d").date()
                
                # Validar que la fecha de inicio no sea posterior a la fecha de fin
                if fecha_inicio_obj > fecha_fin_obj:
                    return False, "La fecha de inicio no puede ser posterior a la fecha de fin"
                
                # Validar que las fechas no sean en el pasado (opcional)
                fecha_actual = datetime.now().date()
                if fecha_inicio_obj < fecha_actual:
                    return False, "La fecha de inicio no puede ser en el pasado"
                    
            except (ValueError, IndexError):
                return False, "Formato de fecha inválido. Use YYYY-MM-DD"
        
        # Validar campos específicos según tipo
        if tipo.lower() == "ordinaria":
            tipo_jornada = datos.get("tipoJornada", "")
            if not tipo_jornada:
                return False, "Para faenas ordinarias debe especificar el tipo de jornada"
        
        elif tipo.lower() == "extraordinaria":
            motivo_extra = datos.get("motivoExtra", "")
            if not motivo_extra:
                return False, "Para faenas extraordinarias debe especificar el motivo"
        
        return True, ""

    @staticmethod
    def validar_numero_positivo(valor: str, campo: str = "Valor") -> Tuple[bool, str]:
        """Valida que un valor sea un número positivo"""
        valor = valor.strip() if valor else ""
        
        if not valor:
            return False, f"El campo '{campo}' es obligatorio"
        
        try:
            numero = float(valor)
            if numero <= 0:
                return False, f"El campo '{campo}' debe ser mayor a 0"
        except ValueError:
            return False, f"El campo '{campo}' debe ser un número válido"
        
        return True, ""
    
    @staticmethod
    def validar_id_numerico(id_str: str, campo: str = "ID") -> Tuple[bool, str]:
        """Valida que un ID sea un número entero positivo"""
        id_str = id_str.strip() if id_str else ""
        
        if not id_str:
            return False, f"El campo '{campo}' es obligatorio"
        
        try:
            id_num = int(id_str)
            if id_num <= 0:
                return False, f"El campo '{campo}' debe ser un número mayor a 0"
        except ValueError:
            return False, f"El campo '{campo}' debe ser un número entero válido"
        
        return True, ""
    
    @staticmethod
    def validar_seleccion_dropdown(valor: str, campo: str = "Campo") -> Tuple[bool, str]:
        """Valida que se haya seleccionado un valor en un dropdown"""
        if not valor or valor in ["Seleccionar", "Tipo de Evento", "Tipo de Penalización", "Método de Pago"]:
            return False, f"Debe seleccionar un '{campo}'"
        
        return True, ""
    
    @staticmethod
    def validar_horas(horas_str: str, campo: str = "Horas") -> Tuple[bool, str]:
        """Valida formato de horas (HH:MM)"""
        horas_str = horas_str.strip() if horas_str else ""
        
        if not horas_str:
            return False, f"El campo '{campo}' es obligatorio"
        
        try:
            # Validar formato HH:MM
            if not re.match(r'^\d{1,2}:\d{2}$', horas_str):
                return False, f"El campo '{campo}' debe tener formato HH:MM"
            
            horas, minutos = map(int, horas_str.split(':'))
            if horas < 0 or horas > 23 or minutos < 0 or minutos > 59:
                return False, f"El campo '{campo}' tiene valores inválidos"
                
        except ValueError:
            return False, f"El campo '{campo}' tiene formato inválido"
        
        return True, ""
    
    @staticmethod
    def validar_archivo_evidencia(archivo: str, campo: str = "Archivo") -> Tuple[bool, str]:
        """Valida archivo de evidencia"""
        if not archivo:
            return True, ""  # El archivo es opcional
        
        # Validar extensión de archivo
        extensiones_permitidas = ['.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx']
        archivo_lower = archivo.lower()
        
        if not any(archivo_lower.endswith(ext) for ext in extensiones_permitidas):
            return False, f"El {campo} debe ser un archivo válido (JPG, PNG, PDF, DOC, DOCX)"
        
        # Validar tamaño del archivo (máximo 10MB)
        try:
            import os
            if os.path.exists(archivo):
                tamaño = os.path.getsize(archivo)
                if tamaño > 10 * 1024 * 1024:  # 10MB
                    return False, f"El {campo} no puede exceder 10MB"
        except Exception:
            pass  # Si no se puede verificar el tamaño, continuar
        
        return True, ""
    
    @staticmethod
    def validar_tipo_justificacion(tipo: str, campo: str = "Tipo") -> Tuple[bool, str]:
        """Valida tipo de justificación"""
        if not tipo or tipo in ["Seleccionar Tipo", "Seleccionar"]:
            return False, f"Debe seleccionar un '{campo}'"
        
        tipos_validos = ["FAENA", "REUNION"]
        if tipo not in tipos_validos:
            return False, f"El {campo} debe ser 'FAENA' o 'REUNION'"
        
        return True, ""
    
    @staticmethod
    def validar_datos_justificacion(datos: Dict[str, Any]) -> Tuple[bool, str]:
        """Valida todos los datos de una justificación"""
        # Validar tipo de justificación
        es_valido, mensaje = ValidacionFormularios.validar_tipo_justificacion(
            datos.get("tipo", ""), "Tipo de Justificación"
        )
        if not es_valido:
            return False, mensaje
        
        # Validar selección de miembro
        es_valido, mensaje = ValidacionFormularios.validar_seleccion_dropdown(
            datos.get("miembro", ""), "Miembro"
        )
        if not es_valido:
            return False, mensaje
        
        # Validar selección de evento
        es_valido, mensaje = ValidacionFormularios.validar_seleccion_dropdown(
            datos.get("evento", ""), "Evento"
        )
        if not es_valido:
            return False, mensaje
        
        # Validar descripción (opcional pero si se proporciona debe tener mínimo 10 caracteres)
        descripcion = datos.get("descripcion", "").strip()
        if descripcion and len(descripcion) < 10:
            return False, "La descripción debe tener al menos 10 caracteres"
        
        if descripcion and len(descripcion) > 500:
            return False, "La descripción no puede exceder 500 caracteres"
        
        # Validar archivo de evidencia (opcional)
        archivo = datos.get("archivo", "")
        if archivo:
            es_valido, mensaje = ValidacionFormularios.validar_archivo_evidencia(archivo, "Archivo de Evidencia")
            if not es_valido:
                return False, mensaje
        
        return True, ""
    
    @staticmethod
    def validar_datos_penalizacion(datos: Dict[str, Any]) -> Tuple[bool, str]:
        """Valida todos los datos de una penalización"""
        es_valido, mensaje = ValidacionFormularios.validar_id_numerico(
            datos.get("id_miembro", ""), "ID del Miembro"
        )
        if not es_valido:
            return False, mensaje
        es_valido, mensaje = ValidacionFormularios.validar_seleccion_dropdown(
            datos.get("tipo_evento", ""), "Tipo de Evento"
        )
        if not es_valido:
            return False, mensaje
        es_valido, mensaje = ValidacionFormularios.validar_seleccion_dropdown(
            datos.get("tipo_penalizacion", ""), "Tipo de Penalización"
        )
        if not es_valido:
            return False, mensaje
        es_valido, mensaje = ValidacionFormularios.validar_numero_positivo(
            datos.get("valor", ""), "Valor"
        )
        if not es_valido:
            return False, mensaje
        observaciones = datos.get("observaciones", "").strip()
        if observaciones and len(observaciones) > 500:
            return False, "Las observaciones no pueden exceder 500 caracteres"
        return True, ""

    @staticmethod
    def validar_datos_pago(datos: Dict[str, Any]) -> Tuple[bool, str]:
        """Valida todos los datos de un pago"""
        es_valido, mensaje = ValidacionFormularios.validar_id_numerico(
            datos.get("id_penalizacion", ""), "ID de la Penalización"
        )
        if not es_valido:
            return False, mensaje
        es_valido, mensaje = ValidacionFormularios.validar_numero_positivo(
            datos.get("monto_pagado", ""), "Monto Pagado"
        )
        if not es_valido:
            return False, mensaje
        es_valido, mensaje = ValidacionFormularios.validar_seleccion_dropdown(
            datos.get("metodo_pago", ""), "Método de Pago"
        )
        if not es_valido:
            return False, mensaje
        comprobante = datos.get("comprobante", "").strip()
        if comprobante and len(comprobante) > 200:
            return False, "La ruta del comprobante no puede exceder 200 caracteres"
        return True, ""

    @staticmethod
    def validar_datos_horas(datos: Dict[str, Any]) -> Tuple[bool, str]:
        """Valida todos los datos de horas de reposición"""
        es_valido, mensaje = ValidacionFormularios.validar_id_numerico(
            datos.get("id_penalizacion", ""), "ID de la Penalización"
        )
        if not es_valido:
            return False, mensaje
        es_valido, mensaje = ValidacionFormularios.validar_id_numerico(
            datos.get("id_faena", ""), "ID de la Faena"
        )
        if not es_valido:
            return False, mensaje
        es_valido, mensaje = ValidacionFormularios.validar_numero_positivo(
            datos.get("horas_realizadas", ""), "Horas Realizadas"
        )
        if not es_valido:
            return False, mensaje
        es_valido, mensaje = ValidacionSimplificada.validar_fecha(
            datos.get("fecha_realizacion", ""), "Fecha de Realización"
        )
        if not es_valido:
            return False, mensaje
        return True, ""
    
    @staticmethod
    def validar_campo_penalizacion(campo: str, valor: str) -> Tuple[bool, str]:
        """Valida un campo específico de penalización"""
        valor = valor.strip() if valor else ""
        
        if campo == "id_miembro":
            return ValidacionFormularios.validar_id_numerico(valor, "ID del Miembro")
        elif campo == "valor":
            return ValidacionFormularios.validar_numero_positivo(valor, "Valor")
        elif campo == "id_penalizacion":
            return ValidacionFormularios.validar_id_numerico(valor, "ID de Penalización")
        elif campo == "monto_pagado":
            return ValidacionFormularios.validar_numero_positivo(valor, "Monto Pagado")
        elif campo == "id_faena":
            return ValidacionFormularios.validar_id_numerico(valor, "ID de Faena")
        elif campo == "horas_realizadas":
            return ValidacionFormularios.validar_horas(valor, "Horas Realizadas")
        elif campo == "fecha_realizacion":
            return ValidacionSimplificada.validar_fecha(valor, "Fecha de Realización")
        else:
            return True, ""  # Campo no reconocido, no validar
    
    @staticmethod
    def validar_campo_justificacion(campo: str, valor: str) -> Tuple[bool, str]:
        """Valida un campo específico de justificación"""
        valor = valor.strip() if valor else ""
        
        if campo == "descripcion":
            return ValidacionSimplificada.validar_texto(valor, "Descripción", requerido=False, min_longitud=10, max_longitud=500)
        elif campo == "archivo":
            return ValidacionFormularios.validar_archivo_evidencia(valor, "Archivo de Evidencia")
        elif campo == "miembro":
            return ValidacionFormularios.validar_seleccion_dropdown(valor, "Miembro")
        elif campo == "evento":
            return ValidacionFormularios.validar_seleccion_dropdown(valor, "Evento")
        elif campo == "tipo":
            return ValidacionFormularios.validar_tipo_justificacion(valor, "Tipo de Justificación")
        else:
            return True, ""  # Campo no reconocido, no validar 