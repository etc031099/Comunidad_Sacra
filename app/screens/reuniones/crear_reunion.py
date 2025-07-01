from kivymd.app import MDApp
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from datetime import datetime
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar, MDSnackbar
from kivymd.uix.label import MDLabel
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.core.clipboard import Clipboard
import webbrowser
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from .crear_reunion_db import crear_reunion, actualizar_reunion, registrar_asistencias_inasistencia

class CrearReunionScreen(MDScreen):

    modo_edicion = BooleanProperty(False)
    reunion_actual = ObjectProperty(None, allownone=True)

    def abrir_reloj_inicio(self):
        time_picker = MDTimePicker()
        time_picker.bind(time=self.on_hora_inicio_seleccionada)
        time_picker.open()

    def on_hora_inicio_seleccionada(self, instance, time):
        self.ids.input_hora_inicio.text = time.strftime('%H:%M')

    def crear_reunion(self, fecha, titulo):
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            self.mostrar_popup("Fecha inválida", "Usa el formato YYYY-MM-DD.")
            return

        if not titulo.strip():
            self.mostrar_popup("Título requerido", "Debes ingresar un título.")
            return
        
        # ⏰ Obtener hora de inicio
        hora_inicio = self.ids.input_hora_inicio.text

        # Validación básica de hora
        if not hora_inicio:
            self.mostrar_popup("Hora requerida", "Debes seleccionar hora de inicio.")
            return

        try:
            datetime.strptime(hora_inicio, "%H:%M")
        except ValueError:
            self.mostrar_popup("Formato de hora inválido", "Usa el formato HH:MM.")
            return

        descripcion = self.ids.input_descripcion.text
        id_reunion = crear_reunion(fecha, titulo, hora_inicio, descripcion)
        if id_reunion:
            registrar_asistencias_inasistencia(id_reunion)
            self.mostrar_popup("Reunión guardada", "Se registró correctamente.")
        else:
            self.mostrar_popup("Error", "No se pudo guardar la reunión.")

    def mostrar_popup(self, titulo, mensaje):
        contenido = BoxLayout(orientation="vertical", spacing=10, padding=10)
        contenido.add_widget(Label(text=mensaje))
        cerrar = Button(text="Cerrar", size_hint_y=None, height=40)
        contenido.add_widget(cerrar)

        popup = Popup(title=titulo, content=contenido, size_hint=(0.6, 0.4))
        cerrar.bind(on_release=popup.dismiss)
        popup.open()
    
    def abrir_calendario(self):
        date_picker = MDDatePicker(
            min_date=datetime.today().date()
        )
        date_picker.bind(on_save=self.on_fecha_seleccionada)
        date_picker.open()

    def on_fecha_seleccionada(self, instance, value, date_range):
        self.ids.input_fecha.text = value.strftime('%Y-%m-%d')

    def cargar_datos_reunion(self, reunion):
        """Carga datos asegurando formato correcto"""
        try:
            self.ids.input_fecha.text = reunion.get('fecha', '')
            self.ids.input_titulo.text = reunion.get('titulo', '')
            
            # Manejo especial para hora
            hora_inicio = reunion.get('hora_inicio', '')
            
            # Si la hora viene como datetime.time, la convertimos a string
            if hasattr(hora_inicio, 'strftime'):
                hora_inicio = hora_inicio.strftime('%H:%M')
                
            self.ids.input_hora_inicio.text = hora_inicio or '00:00'
            self.ids.input_descripcion.text = reunion.get('descripcion', '')
            
            print(f"Datos cargados - Hora inicio: {hora_inicio}, Descripción: {reunion.get('descripcion', '')}")  # Debug
        except Exception as e:
            print(f"Error cargando datos: {e}")
            self.mostrar_popup("Error", "No se pudieron cargar los datos completos de la reunión")

    def guardar_cambios(self):
        """Guarda los cambios según sea creación o edición"""
        # Validar campos obligatorios
        if not all([self.ids.input_fecha.text, self.ids.input_titulo.text]):
            self.mostrar_popup("Error", "Debes completar todos los campos obligatorios")
            return
        
        # Validar hora
        hora_inicio = self.ids.input_hora_inicio.text
        
        if not hora_inicio:
            self.mostrar_popup("Error", "Debes especificar hora de inicio")
            return
        
        try:
            # Convertir a objeto datetime para validación
            datetime.strptime(hora_inicio, "%H:%M")
                
        except ValueError:
            self.mostrar_popup("Error", "Formato de hora inválido. Usa HH:MM")
            return
        
        # Si pasó todas las validaciones, proceder a guardar
        if self.modo_edicion and self.reunion_actual:
            self.actualizar_reunion()
        else:
            self.crear_nueva_reunion()

    def actualizar_reunion(self):
        if self.reunion_actual:
            actualizar_reunion(
                self.reunion_actual['id_reunion'],
                self.ids.input_fecha.text,
                self.ids.input_titulo.text,
                self.ids.input_hora_inicio.text,
                self.ids.input_descripcion.text
            )
            MDSnackbar(MDLabel(text="Reunión actualizada correctamente")).open()
            self.manager.current = "reuniones"

    def crear_nueva_reunion(self):
        """Guarda una nueva reunión en la base de datos y muestra diálogo de notificación."""
        reunion_data = {
            'fecha': self.ids.input_fecha.text,
            'titulo': self.ids.input_titulo.text,
            'hora_inicio': self.ids.input_hora_inicio.text,
            'descripcion': self.ids.input_descripcion.text
        }
        id_reunion = crear_reunion(
            reunion_data['fecha'],
            reunion_data['titulo'],
            reunion_data['hora_inicio'],
            reunion_data['descripcion']
        )
        if id_reunion:
            registrar_asistencias_inasistencia(id_reunion)
            self.mostrar_dialogo_notificacion(reunion_data)
        else:
            self.mostrar_popup("Error", "No se pudo crear la reunión")

    def mostrar_dialogo_notificacion(self, reunion):
        nombre = reunion.get('titulo')
        fecha = reunion.get('fecha', '').split(' ')[0]
        hora = reunion.get('hora_inicio')

        try:
            fecha_formateada = datetime.strptime(fecha, '%Y-%m-%d').strftime('%d/%m/%Y')
        except ValueError:
            fecha_formateada = fecha
            
        mensaje_whatsapp = (
            f"¡Atención Comunidad!\n\n"
            f"Se ha convocado a una nueva REUNIÓN:\n\n"
            f"▶️ *Título:* {nombre}\n"
            f"🗓️ *Fecha:* {fecha_formateada}\n"
            f"🕒 *Hora:* {hora}\n\n"
            f"¡Su participación es crucial para la toma de decisiones! No falten."
        )

        # Contenido del diálogo con Layouts para asegurar que los iconos se vean bien
        dialog_content = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(15),
            padding=(dp(10), dp(20), dp(10), dp(20))
        )
        dialog_content.add_widget(MDLabel(
            text="Se ha convocado a una nueva REUNIÓN:",
            adaptive_height=True,
            halign="center"
        ))
        
        details_box = MDBoxLayout(orientation='vertical', adaptive_height=True, spacing=dp(10), padding=(dp(20), 0))
        
        # Fila de Título
        title_layout = MDBoxLayout(adaptive_height=True, spacing=dp(15))
        title_layout.add_widget(MDIconButton(icon="format-title", theme_text_color="Primary"))
        title_layout.add_widget(MDLabel(text=f"[b]Título:[/b] {nombre}", markup=True, adaptive_height=True))
        details_box.add_widget(title_layout)

        # Fila de Fecha
        date_layout = MDBoxLayout(adaptive_height=True, spacing=dp(15))
        date_layout.add_widget(MDIconButton(icon="calendar-month", theme_text_color="Primary"))
        date_layout.add_widget(MDLabel(text=f"[b]Fecha:[/b] {fecha_formateada}", markup=True, adaptive_height=True))
        details_box.add_widget(date_layout)

        # Fila de Hora
        time_layout = MDBoxLayout(adaptive_height=True, spacing=dp(15))
        time_layout.add_widget(MDIconButton(icon="clock-outline", theme_text_color="Primary"))
        time_layout.add_widget(MDLabel(text=f"[b]Hora:[/b] {hora}", markup=True, adaptive_height=True))
        details_box.add_widget(time_layout)

        dialog_content.add_widget(details_box)
        
        dialog_content.add_widget(MDLabel(
            text="¡Su participación es crucial!",
            adaptive_height=True,
            halign="center",
            padding=(0, dp(10))
        ))
        
        scroll_content = ScrollView(size_hint_y=None, height=dp(250))
        scroll_content.add_widget(dialog_content)

        def cerrar_dialogo_y_navegar(inst):
            dialog.dismiss()
            self.manager.current = "reuniones"
            if hasattr(self.manager.get_screen("reuniones"), "cargar_reuniones"):
                self.manager.get_screen("reuniones").cargar_reuniones()


        dialog = MDDialog(
            title="Reunión Creada con Éxito",
            type="custom",
            content_cls=scroll_content,
            buttons=[
                MDFlatButton(text="CERRAR", on_release=cerrar_dialogo_y_navegar),
                MDRaisedButton(text="NOTIFICAR WHATSAPP", on_release=lambda x: self.copiar_y_abrir_whatsapp(mensaje_whatsapp, dialog))
            ]
        )
        dialog.open()

    def copiar_y_abrir_whatsapp(self, texto, dialog):
        Clipboard.copy(texto)
        webbrowser.open("https://web.whatsapp.com")
        dialog.dismiss()
        MDSnackbar(MDLabel(text="Mensaje copiado. Pégalo en el grupo de WhatsApp.")).open()
        self.manager.current = "reuniones"
        if hasattr(self.manager.get_screen("reuniones"), "cargar_reuniones"):
            self.manager.get_screen("reuniones").cargar_reuniones()

    def on_pre_enter(self):
        """Siempre limpia campos al entrar, excepto en edición"""
        if not self.modo_edicion:  # Solo limpia si no estamos editando
            self.limpiar_campos()
            self.reunion_actual = None
        
    def on_enter(self):
        """Si estamos en modo edición, carga los datos"""
        if self.modo_edicion and self.reunion_actual:
            print(f"Cargando datos para edición: {self.reunion_actual}")
            self.cargar_datos_reunion(self.reunion_actual)

    def limpiar_campos(self):
        """Limpia todos los campos del formulario"""
        self.ids.input_fecha.text = ""
        self.ids.input_titulo.text = ""
        self.ids.input_hora_inicio.text = ""
        self.ids.input_descripcion.text = ""

    def preparar_modo_creacion(self):
        """Forza el modo creación y limpia campos"""
        self.modo_edicion = False
        self.reunion_actual = None
        self.limpiar_campos()

    def on_leave(self):
        """Reinicia el estado al salir"""
        self.modo_edicion = False
        self.reunion_actual = None
