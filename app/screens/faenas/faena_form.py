from kivy.properties import DictProperty, StringProperty, BooleanProperty
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.pickers import MDDatePicker
from datetime import datetime
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.core.clipboard import Clipboard
import webbrowser
from .faena_form_db import crear_faena, actualizar_faena


class FaenaFormScreen(MDScreen):
    estado_faena = StringProperty("")
    faena = DictProperty({})
    titulo = StringProperty("Agregar Faena")
    modo_edicion = BooleanProperty(False)
    mostrar_tipo_jornada = BooleanProperty(False)
    mostrar_motivo_extra = BooleanProperty(False)
    tipo_faena = StringProperty("")

    def on_pre_enter(self):
        # Cambia el título según si es edición o nuevo
        if self.faena and self.faena.get("idFaena"):
            self.titulo = "Editar Faena"
            self.modo_edicion = True
        else:
            self.titulo = "Agregar Faena"
            self.modo_edicion = False
        self.actualizar_campos()
        self.actualizar_visibilidad_campos()

    def actualizar_campos(self):
        # Actualizar campos básicos
        self.ids.input_nombre.text = self.faena.get("nombre", "")
        self.ids.input_descripcion.text = self.faena.get("descripcion", "")
        self.ids.input_ubicacion.text = self.faena.get("ubicacion", "")

        # Formatear fechas con hora si existen
        fecha_inicio = self.faena.get("fecha_inicio", "")
        fecha_fin = self.faena.get("fecha_fin", "")
        
        if fecha_inicio and len(fecha_inicio) > 10:  # Si ya tiene hora
            self.ids.input_fecha_inicio.text = fecha_inicio
        elif fecha_inicio:  # Si solo tiene fecha
            self.ids.input_fecha_inicio.text = fecha_inicio + " 00:00:01"
            
        if fecha_fin and len(fecha_fin) > 10:  # Si ya tiene hora
            self.ids.input_fecha_fin.text = fecha_fin
        elif fecha_fin:  # Si solo tiene fecha
            self.ids.input_fecha_fin.text = fecha_fin + " 23:59:59"
        
        # Actualizar campos específicos
        self.ids.input_tipoJornada.text = self.faena.get("tipoJornada", "")
        self.ids.input_motivoExtra.text = self.faena.get("motivoExtra", "")
        
        # Actualizar tipo de faena y checkboxes
        tipo = self.faena.get("tipo", "")
        if tipo:
            self.tipo_faena = tipo  # Importante: establecer tipo_faena primero
            self.seleccionar_tipo(tipo)
        else:
            self.ids.radio_ordinaria.active = False
            self.ids.radio_extraordinaria.active = False
            self.tipo_faena = ""

        # Actualizar visibilidad y estado
        self.actualizar_visibilidad_campos()
        self.actualizar_estado_faena()

    def actualizar_estado_faena(self):
        """
        Calcula el estado de la faena según las fechas.
        """
        fecha_inicio_str = self.ids.input_fecha_inicio.text.strip()
        fecha_fin_str = self.ids.input_fecha_fin.text.strip()
        ahora = datetime.now()

        if not fecha_inicio_str or not fecha_fin_str:
            self.estado_faena = "Pendiente"
            return

        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d %H:%M:%S")
            fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d %H:%M:%S")
        except Exception:
            self.estado_faena = "Fechas inválidas"
            return

        if ahora < fecha_inicio:
            self.estado_faena = "No iniciada"
        elif fecha_inicio <= ahora <= fecha_fin:
            self.estado_faena = "Activa"
        elif ahora > fecha_fin:
            self.estado_faena = "Finalizada"
        else:
            self.estado_faena = "Desconocido"

    def actualizar_visibilidad_campos(self):
        """
        Actualiza la visibilidad de campos según el tipo de faena
        """
        tipo = self.tipo_faena.lower()
        
        # Actualizar visibilidad
        self.mostrar_tipo_jornada = (tipo == "ordinaria")
        self.mostrar_motivo_extra = (tipo == "extraordinaria")
        
        # Limpiar campos no relevantes
        if not self.mostrar_tipo_jornada:
            self.ids.input_tipoJornada.text = ""
        if not self.mostrar_motivo_extra:
            self.ids.input_motivoExtra.text = ""

    def seleccionar_tipo(self, tipo):
        """
        Maneja la selección del tipo de faena
        """
        self.tipo_faena = tipo
        
        # Forzar estado de los checkboxes
        self.ids.radio_ordinaria.active = (tipo.lower() == "ordinaria")
        self.ids.radio_extraordinaria.active = (tipo.lower() == "extraordinaria")
        
        # Actualizar visibilidad de campos
        self.actualizar_visibilidad_campos()

    def guardar_faena(self):
        if self.ids.radio_ordinaria.active:
            tipo = "Ordinaria"
        elif self.ids.radio_extraordinaria.active:
            tipo = "Extraordinaria"
        else:
            tipo = ""
        fecha_inicio = self.ids.input_fecha_inicio.text.strip()
        fecha_fin = self.ids.input_fecha_fin.text.strip()
        datos = {
            "nombre": self.ids.input_nombre.text.strip(),
            "descripcion": self.ids.input_descripcion.text.strip(),
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "ubicacion": self.ids.input_ubicacion.text.strip(),
            "estado": self.estado_faena,
            "tipo": tipo,
            "tipoJornada": self.ids.input_tipoJornada.text.strip(),
            "motivoExtra": self.ids.input_motivoExtra.text.strip(),
        }
        if not datos["nombre"] or not datos["tipo"]:
            snackbar = MDSnackbar(
                MDLabel(
                    text="Nombre y tipo de faena son obligatorios",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()
            return
        if datos["fecha_inicio"] and datos["fecha_fin"]:
            try:
                fecha_inicio_obj = datetime.strptime(datos["fecha_inicio"], "%Y-%m-%d %H:%M:%S")
                fecha_fin_obj = datetime.strptime(datos["fecha_fin"], "%Y-%m-%d %H:%M:%S")
                if fecha_inicio_obj > fecha_fin_obj:
                    snackbar = MDSnackbar(
                        MDLabel(
                            text="La fecha de inicio no puede ser posterior a la fecha de fin",
                            theme_text_color="Custom",
                            text_color="white",
                        )
                    )
                    snackbar.open()
                    return
            except Exception:
                snackbar = MDSnackbar(
                    MDLabel(
                        text="Formato de fecha inválido",
                        theme_text_color="Custom",
                        text_color="white",
                    )
                )
                snackbar.open()
                return
        if self.modo_edicion and self.faena.get("idFaena"):
            actualizar_faena(self.faena["idFaena"], datos)
            mensaje = "Faena actualizada"
            snackbar = MDSnackbar(
                MDLabel(
                    text=mensaje,
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()
            self.regresar_a_faenas()
        else:
            crear_faena(datos)
            self.mostrar_dialogo_notificacion_faena(datos)

    def mostrar_dialogo_notificacion_faena(self, faena_data):
        nombre = faena_data.get('nombre')
        
        try:
            fecha_inicio = datetime.strptime(faena_data.get('fecha_inicio'), '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y a las %H:%M')
        except (ValueError, TypeError):
            fecha_inicio = "No especificada"

        mensaje_display = (
            f"Se ha programado una nueva FAENA:\n\n"
            f"▶️ [b]Nombre:[/b] {nombre}\n"
            f"🗓️ [b]Fecha y Hora de Inicio:[/b] {fecha_inicio}\n"
            f"📍 [b]Ubicación:[/b] {faena_data.get('ubicacion', 'N/A')}\n\n"
            f"¡Su asistencia es importante!"
        )
        mensaje_whatsapp = (
            f"¡Atención Comunidad!\n\n"
            f"Se ha programado una nueva FAENA:\n\n"
            f"▶️ *Nombre:* {nombre}\n"
            f"🗓️ *Fecha y Hora de Inicio:* {fecha_inicio}\n"
            f"📍 *Ubicación:* {faena_data.get('ubicacion', 'N/A')}\n\n"
            f"¡Contamos con su valiosa participación!"
        )

        scroll_content = ScrollView(size_hint_y=None, height=dp(200))
        label = MDLabel(text=mensaje_display, markup=True, size_hint_y=None, padding=dp(10))
        label.bind(texture_size=label.setter('size'))
        scroll_content.add_widget(label)
        
        dialog = MDDialog(
            title="Faena Creada con Éxito",
            type="custom",
            content_cls=scroll_content,
            buttons=[
                MDFlatButton(text="CERRAR", on_release=lambda x: self.cerrar_dialogo_y_navegar(dialog)),
                MDRaisedButton(text="NOTIFICAR WHATSAPP", on_release=lambda x: self.copiar_y_abrir_whatsapp(mensaje_whatsapp, dialog))
            ]
        )
        dialog.open()
        
    def cerrar_dialogo_y_navegar(self, dialog):
        dialog.dismiss()
        self.regresar_a_faenas()

    def copiar_y_abrir_whatsapp(self, texto, dialog):
        Clipboard.copy(texto)
        webbrowser.open("https://web.whatsapp.com")
        dialog.dismiss()
        MDSnackbar(MDLabel(text="Mensaje copiado. Pégalo en el grupo de WhatsApp.")).open()
        self.regresar_a_faenas()

    def regresar_a_faenas(self):
        # Regresar al panel de faenas
        self.manager.current = "faenas"
        # Opcional: recargar la lista de faenas
        if hasattr(self.manager.get_screen("faenas"), "cargar_faenas"):
            self.manager.get_screen("faenas").cargar_faenas()

    def abrir_calendario_inicio(self):
        date_picker = MDDatePicker(
            min_date=datetime.today().date()
        )
        date_picker.bind(on_save=self.on_fecha_inicio_seleccionada)
        date_picker.open()

    def abrir_calendario_fin(self):
        date_picker = MDDatePicker(
            min_date=datetime.today().date()
        )
        date_picker.bind(on_save=self.on_fecha_fin_seleccionada)
        date_picker.open()

    def on_fecha_inicio_seleccionada(self, instance, value, date_range):
        self.ids.input_fecha_inicio.text = value.strftime('%Y-%m-%d') + ' 00:00:01'
        self.actualizar_estado_faena()

    def on_fecha_fin_seleccionada(self, instance, value, date_range):
        self.ids.input_fecha_fin.text = value.strftime('%Y-%m-%d') + ' 23:59:59'
        self.actualizar_estado_faena()