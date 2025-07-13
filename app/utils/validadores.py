"""
Módulo de validaciones centralizado para el sistema Sacra Familia
Contiene funciones de validación para diferentes tipos de datos
"""

import re
from datetime import datetime, date
from typing import Tuple, Dict, Any, Optional

class ValidadorError(Exception):
    """Excepción personalizada para errores de validación"""
    pass

class Validador:
    """Clase principal para validaciones del sistema"""
    
    @staticmethod
    def validar_texto(texto: str, campo: str, requerido: bool = True, 
                     min_longitud: int = 1, max_longitud: int = 255) -> Tuple[bool, str]:
        """
        Valida texto genérico
        
        Args:
            texto: Texto a validar
            campo: Nombre del campo para mensajes de error
            requerido: Si el campo es obligatorio
            min_longitud: Longitud mínima permitida
            max_longitud: Longitud máxima permitida
            
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
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
        """
        Valida nombres y apellidos
        
        Args:
            nombre: Nombre a validar
            campo: Nombre del campo
            
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        es_valido, mensaje = Validador.validar_texto(nombre, campo, requerido=True, min_longitud=2, max_longitud=50)
        if not es_valido:
            return es_valido, mensaje
        
        # Validar que solo contenga letras, espacios y algunos caracteres especiales
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            return False, f"El campo '{campo}' solo puede contener letras y espacios"
        
        return True, ""
    
    @staticmethod
    def validar_dni(dni: str) -> Tuple[bool, str]:
        """
        Valida formato de DNI peruano
        
        Args:
            dni: DNI a validar
            
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        dni = dni.strip() if dni else ""
        
        if not dni:
            return False, "El DNI es obligatorio"
        
        # Validar formato: 8 dígitos
        if not re.match(r'^\d{8}$', dni):
            return False, "El DNI debe tener exactamente 8 dígitos numéricos"
        
        return True, ""
    
    @staticmethod
    def validar_email(email: str, requerido: bool = False) -> Tuple[bool, str]:
        """
        Valida formato de email
        
        Args:
            email: Email a validar
            requerido: Si el campo es obligatorio
            
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
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
    def validar_telefono(telefono: str, requerido: bool = False) -> Tuple[bool, str]:
        """
        Valida formato de teléfono peruano
        
        Args:
            telefono: Teléfono a validar
            requerido: Si el campo es obligatorio
            
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        telefono = telefono.strip() if telefono else ""
        
        if not requerido and not telefono:
            return True, ""
        
        if requerido and not telefono:
            return False, "El teléfono es obligatorio"
        
        # Remover espacios y caracteres especiales
        telefono_limpio = re.sub(r'[\s\-\(\)]', '', telefono)
        
        # Validar formato: 9 dígitos (celular) o 7 dígitos (fijo)
        if not re.match(r'^\d{7,9}$', telefono_limpio):
            return False, "El teléfono debe tener 7 a 9 dígitos numéricos"
        
        return True, ""
    
    @staticmethod
    def validar_fecha(fecha_str: str, campo: str = "Fecha", 
                     fecha_minima: Optional[date] = None,
                     fecha_maxima: Optional[date] = None) -> Tuple[bool, str]:
        """
        Valida formato de fecha
        
        Args:
            fecha_str: Fecha en formato string
            campo: Nombre del campo
            fecha_minima: Fecha mínima permitida
            fecha_maxima: Fecha máxima permitida
            
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        fecha_str = fecha_str.strip() if fecha_str else ""
        
        if not fecha_str:
            return False, f"El campo '{campo}' es obligatorio"
        
        try:
            # Intentar parsear la fecha
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            return False, f"El formato de fecha debe ser YYYY-MM-DD"
        
        # Validar fecha mínima
        if fecha_minima and fecha_obj < fecha_minima:
            return False, f"La fecha no puede ser anterior a {fecha_minima.strftime('%d/%m/%Y')}"
        
        # Validar fecha máxima
        if fecha_maxima and fecha_obj > fecha_maxima:
            return False, f"La fecha no puede ser posterior a {fecha_maxima.strftime('%d/%m/%Y')}"
        
        return True, ""
    
    @staticmethod
    def validar_hora(hora_str: str, campo: str = "Hora") -> Tuple[bool, str]:
        """
        Valida formato de hora
        
        Args:
            hora_str: Hora en formato string
            campo: Nombre del campo
            
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        hora_str = hora_str.strip() if hora_str else ""
        
        if not hora_str:
            return False, f"El campo '{campo}' es obligatorio"
        
        try:
            # Intentar parsear la hora
            datetime.strptime(hora_str, "%H:%M")
        except ValueError:
            return False, f"El formato de hora debe ser HH:MM"
        
        return True, ""
    
    @staticmethod
    def validar_rango_fechas(fecha_inicio: str, fecha_fin: str) -> Tuple[bool, str]:
        """
        Valida que la fecha de inicio sea anterior a la fecha de fin
        
        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        # Validar formato de fechas
        es_valido_inicio, mensaje = Validador.validar_fecha(fecha_inicio, "Fecha de inicio")
        if not es_valido_inicio:
            return False, mensaje
        
        es_valido_fin, mensaje = Validador.validar_fecha(fecha_fin, "Fecha de fin")
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
    
    @staticmethod
    def validar_datos_miembro(datos: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Valida todos los datos de un miembro
        
        Args:
            datos: Diccionario con los datos del miembro
            
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        # Validar nombre
        es_valido, mensaje = Validador.validar_nombre(datos.get("Nombre", ""), "Nombre")
        if not es_valido:
            return False, mensaje
        
        # Validar apellido paterno
        es_valido, mensaje = Validador.validar_nombre(datos.get("Apellido_Paterno", ""), "Apellido Paterno")
        if not es_valido:
            return False, mensaje
        
        # Validar apellido materno
        es_valido, mensaje = Validador.validar_nombre(datos.get("Apellido_Materno", ""), "Apellido Materno")
        if not es_valido:
            return False, mensaje
        
        # Validar DNI
        es_valido, mensaje = Validador.validar_dni(datos.get("DNI", ""))
        if not es_valido:
            return False, mensaje
        
        # Validar email (opcional)
        es_valido, mensaje = Validador.validar_email(datos.get("Correo", ""), requerido=False)
        if not es_valido:
            return False, mensaje
        
        # Validar teléfono (opcional)
        es_valido, mensaje = Validador.validar_telefono(datos.get("Teléfono", ""), requerido=False)
        if not es_valido:
            return False, mensaje
        
        return True, ""
    
    @staticmethod
    def validar_datos_reunion(datos: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Valida todos los datos de una reunión
        
        Args:
            datos: Diccionario con los datos de la reunión
            
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        # Validar título
        es_valido, mensaje = Validador.validar_texto(datos.get("titulo", ""), "Título", requerido=True, min_longitud=3, max_longitud=100)
        if not es_valido:
            return False, mensaje
        
        # Validar fecha
        es_valido, mensaje = Validador.validar_fecha(datos.get("fecha", ""), "Fecha")
        if not es_valido:
            return False, mensaje
        
        # Validar hora
        es_valido, mensaje = Validador.validar_hora(datos.get("hora_inicio", ""), "Hora de inicio")
        if not es_valido:
            return False, mensaje
        
        # Validar descripción (opcional)
        descripcion = datos.get("descripcion", "")
        if descripcion:
            es_valido, mensaje = Validador.validar_texto(descripcion, "Descripción", requerido=False, max_longitud=500)
            if not es_valido:
                return False, mensaje
        
        return True, ""
    
    @staticmethod
    def validar_datos_faena(datos: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Valida todos los datos de una faena
        
        Args:
            datos: Diccionario con los datos de la faena
            
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        # Validar nombre
        es_valido, mensaje = Validador.validar_texto(datos.get("nombre", ""), "Nombre", requerido=True, min_longitud=3, max_longitud=100)
        if not es_valido:
            return False, mensaje
        
        # Validar tipo
        tipo = datos.get("tipo", "")
        if not tipo:
            return False, "Debe seleccionar un tipo de faena"
        
        if tipo.lower() not in ["ordinaria", "extraordinaria"]:
            return False, "El tipo de faena debe ser 'Ordinaria' o 'Extraordinaria'"
        
        # Validar fechas
        fecha_inicio = datos.get("fecha_inicio", "")
        fecha_fin = datos.get("fecha_fin", "")
        
        if fecha_inicio and fecha_fin:
            es_valido, mensaje = Validador.validar_rango_fechas(fecha_inicio, fecha_fin)
            if not es_valido:
                return False, mensaje
        
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