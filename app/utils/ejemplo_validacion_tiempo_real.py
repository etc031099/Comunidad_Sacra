"""
Ejemplo de implementación de validación en tiempo real
Este archivo muestra cómo usar los componentes de validación
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from app.utils.componentes_validacion import CampoValidado, ValidadorUI, Validador

class EjemploValidacionTiempoReal(MDScreen):
    """
    Ejemplo de pantalla con validación en tiempo real
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
        self.setup_validaciones()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        layout = MDBoxLayout(orientation="vertical", spacing=10, padding=20)
        
        # Campo de DNI con validación en tiempo real
        self.campo_dni = CampoValidado(
            hint_text="DNI (8 dígitos)",
            helper_text="Ingrese su DNI",
            helper_text_mode="on_focus"
        )
        layout.add_widget(self.campo_dni)
        
        # Campo de email con validación en tiempo real
        self.campo_email = CampoValidado(
            hint_text="Correo electrónico",
            helper_text="Ingrese su correo",
            helper_text_mode="on_focus"
        )
        layout.add_widget(self.campo_email)
        
        # Campo de teléfono con validación en tiempo real
        self.campo_telefono = CampoValidado(
            hint_text="Teléfono",
            helper_text="Ingrese su teléfono",
            helper_text_mode="on_focus"
        )
        layout.add_widget(self.campo_telefono)
        
        # Botón para validar
        boton_validar = MDRaisedButton(
            text="Validar Formulario",
            on_release=self.validar_formulario
        )
        layout.add_widget(boton_validar)
        
        self.add_widget(layout)
    
    def setup_validaciones(self):
        """Configura las validaciones en tiempo real"""
        # Validación de DNI en tiempo real
        ValidadorUI.validar_campo_en_tiempo_real(
            self.campo_dni, 
            Validador.validar_dni
        )
        
        # Validación de email en tiempo real
        ValidadorUI.validar_campo_en_tiempo_real(
            self.campo_email, 
            Validador.validar_email,
            requerido=False
        )
        
        # Validación de teléfono en tiempo real
        ValidadorUI.validar_campo_en_tiempo_real(
            self.campo_telefono, 
            Validador.validar_telefono,
            requerido=False
        )
    
    def validar_formulario(self, instance):
        """Valida todo el formulario al hacer clic en el botón"""
        datos = {
            "DNI": self.campo_dni.text.strip(),
            "Correo": self.campo_email.text.strip(),
            "Teléfono": self.campo_telefono.text.strip()
        }
        
        # Validar DNI (obligatorio)
        es_valido_dni, mensaje_dni = Validador.validar_dni(datos["DNI"])
        if not es_valido_dni:
            ValidadorUI.mostrar_error_snackbar(mensaje_dni)
            return
        
        # Validar email (opcional)
        es_valido_email, mensaje_email = Validador.validar_email(datos["Correo"], requerido=False)
        if not es_valido_email:
            ValidadorUI.mostrar_error_snackbar(mensaje_email)
            return
        
        # Validar teléfono (opcional)
        es_valido_telefono, mensaje_telefono = Validador.validar_telefono(datos["Teléfono"], requerido=False)
        if not es_valido_telefono:
            ValidadorUI.mostrar_error_snackbar(mensaje_telefono)
            return
        
        # Si todo es válido, mostrar éxito
        ValidadorUI.mostrar_error_snackbar("¡Formulario válido! Todos los datos son correctos.")

# Ejemplo de uso en un formulario existente
class EjemploIntegracionFormularioExistente:
    """
    Ejemplo de cómo integrar validaciones en un formulario existente
    """
    
    def __init__(self, screen):
        self.screen = screen
        self.setup_validaciones_existentes()
    
    def setup_validaciones_existentes(self):
        """Configura validaciones para campos existentes"""
        # Ejemplo: validar DNI en tiempo real
        if hasattr(self.screen.ids, 'dni'):
            ValidadorUI.validar_campo_en_tiempo_real(
                self.screen.ids.dni, 
                Validador.validar_dni
            )
        
        # Ejemplo: validar email en tiempo real
        if hasattr(self.screen.ids, 'correo'):
            ValidadorUI.validar_campo_en_tiempo_real(
                self.screen.ids.correo, 
                Validador.validar_email,
                requerido=False
            )
    
    def validar_antes_de_guardar(self, datos):
        """Valida datos antes de guardar"""
        # Validar datos de miembro
        es_valido, mensaje = Validador.validar_datos_miembro(datos)
        if not es_valido:
            ValidadorUI.mostrar_error_snackbar(mensaje)
            return False
        
        return True

# Instrucciones de uso:
"""
Para usar validación en tiempo real en un formulario existente:

1. Importar los módulos necesarios:
   from app.utils.validadores import Validador
   from app.utils.componentes_validacion import ValidadorUI

2. En el método __init__ o on_pre_enter de tu pantalla:
   def setup_validaciones(self):
       # Para campos existentes
       ValidadorUI.validar_campo_en_tiempo_real(
           self.ids.nombre_campo, 
           Validador.validar_dni
       )

3. En el método de guardar:
   def guardar_datos(self):
       datos = {...}  # Recopilar datos
       es_valido, mensaje = Validador.validar_datos_miembro(datos)
       if not es_valido:
           ValidadorUI.mostrar_error_snackbar(mensaje)
           return
       # Continuar con el guardado...
""" 