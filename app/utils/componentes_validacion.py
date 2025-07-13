"""
Componentes visuales para validación de datos
Proporciona widgets y funciones para mostrar errores de validación
"""

from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivy.properties import StringProperty, BooleanProperty
from kivy.metrics import dp
from typing import List, Dict, Any

class CampoValidado(MDTextField):
    """
    Campo de texto con validación integrada
    """
    error_text = StringProperty("")
    tiene_error = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(error_text=self._on_error_text)
    
    def _on_error_text(self, instance, value):
        """Actualiza el estado visual cuando hay error"""
        if value:
            self.tiene_error = True
            self.helper_text = value
            self.helper_text_mode = "on_error"
            self.error = True
        else:
            self.tiene_error = False
            self.helper_text = ""
            self.helper_text_mode = "on_focus"
            self.error = False
    
    def mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error"""
        self.error_text = mensaje
    
    def limpiar_error(self):
        """Limpia el mensaje de error"""
        self.error_text = ""

class ValidadorUI:
    """
    Clase utilitaria para mostrar errores de validación en la UI
    """
    
    @staticmethod
    def mostrar_error_snackbar(mensaje: str, duracion: float = 3.0):
        """
        Muestra un error en un snackbar
        
        Args:
            mensaje: Mensaje de error a mostrar
            duracion: Duración en segundos
        """
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
        """
        Muestra un error en un diálogo
        
        Args:
            titulo: Título del diálogo
            mensaje: Mensaje de error
            callback: Función a ejecutar al cerrar el diálogo
        """
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
        """
        Muestra múltiples errores en un diálogo
        
        Args:
            errores: Lista de mensajes de error
            titulo: Título del diálogo
        """
        if not errores:
            return
        
        mensaje = "\n• ".join([""] + errores)
        
        ValidadorUI.mostrar_error_dialogo(titulo, mensaje)
    
    @staticmethod
    def validar_campo_en_tiempo_real(campo, validador_func, *args, **kwargs):
        """
        Valida un campo en tiempo real mientras el usuario escribe
        
        Args:
            campo: Campo a validar (MDTextField o CampoValidado)
            validador_func: Función de validación a usar
            *args, **kwargs: Argumentos para la función de validación
        """
        def on_text_change(instance, value):
            es_valido, mensaje = validador_func(value, *args, **kwargs)
            if not es_valido:
                # Verificar si es CampoValidado o MDTextField normal
                if hasattr(campo, 'mostrar_error'):
                    campo.mostrar_error(mensaje)
                else:
                    # Para MDTextField normal, usar error y helper_text
                    campo.error = True
                    campo.helper_text = mensaje
                    campo.helper_text_mode = "on_error"
            else:
                # Limpiar error
                if hasattr(campo, 'limpiar_error'):
                    campo.limpiar_error()
                else:
                    # Para MDTextField normal
                    campo.error = False
                    campo.helper_text = ""
                    campo.helper_text_mode = "on_focus"
        
        campo.bind(text=on_text_change)

class FormularioValidado:
    """
    Clase base para formularios con validación integrada
    """
    
    def __init__(self):
        self.campos_validados: Dict[str, CampoValidado] = {}
        self.errores: List[str] = []
    
    def agregar_campo_validado(self, nombre: str, campo: CampoValidado):
        """
        Agrega un campo validado al formulario
        
        Args:
            nombre: Nombre identificador del campo
            campo: Instancia de CampoValidado
        """
        self.campos_validados[nombre] = campo
    
    def validar_todos_los_campos(self) -> bool:
        """
        Valida todos los campos del formulario
        
        Returns:
            bool: True si todos los campos son válidos
        """
        self.errores = []
        
        for nombre, campo in self.campos_validados.items():
            if campo.tiene_error:
                self.errores.append(campo.error_text)
        
        return len(self.errores) == 0
    
    def mostrar_errores(self):
        """Muestra todos los errores encontrados"""
        if self.errores:
            ValidadorUI.mostrar_errores_multiples(self.errores)
    
    def limpiar_errores(self):
        """Limpia todos los errores de los campos"""
        for campo in self.campos_validados.values():
            campo.limpiar_error()
        self.errores = [] 