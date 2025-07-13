from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDList
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDIconButton, MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivymd.uix.card import MDCard
from kivymd.uix.widget import Widget
from kivy.metrics import dp
from datetime import datetime
import pyodbc
from app.db.conexion import obtener_conexion
from kivy.factory import Factory
from kivy.clock import Clock
import threading
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.utils import platform
import os
import shutil
from .justificaciones_db import (
    obtener_miembros, obtener_faenas, obtener_reuniones, 
    obtener_fechas_faena, obtener_justificaciones_faena, obtener_justificaciones_reunion,
    obtener_id_registro_faena, obtener_id_registro_reunion,
    guardar_evidencia, guardar_archivo_evidencia,
    obtener_fechas_con_justificaciones_faena
)
from kivy.properties import StringProperty
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner

class JustificacionesScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.directorio_evidencias = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'evidencias')
        if not os.path.exists(self.directorio_evidencias):
            os.makedirs(self.directorio_evidencias)
        # Enlazar el evento del spinner de fecha si existe
        Clock.schedule_once(self._bind_fecha_spinner, 0)

    def _bind_fecha_spinner(self, *args):
        if 'fecha_spinner' in self.ids:
            self.ids.fecha_spinner.unbind(text=self.on_fecha_changed)  # Evitar duplicados
            self.ids.fecha_spinner.bind(text=self.on_fecha_changed)

    def on_tipo_changed(self, instance, value):
        """Se ejecuta cuando se cambia el tipo de justificación"""
        # Limpiar selecciones anteriores
        self.fecha_seleccionada = None
        
        # Limpiar evento seleccionado
        evento_spinner = self.ids.evento_spinner
        evento_spinner.text = 'Seleccionar Evento'
        
        # Cargar eventos según tipo
        if value == 'FAENA':
            eventos = obtener_faenas()
            evento_spinner.values = [f"{e['idFaena']} - {e['nombre']}" for e in eventos]
        elif value == 'REUNION':
            eventos = obtener_reuniones()
            evento_spinner.values = [f"{e['id_reunion']} - {e['titulo']}" for e in eventos]
        else:
            evento_spinner.values = []
        
        # Manejar el spinner de fecha
        self.manejar_spinner_fecha(value)
        
        # Limpiar lista de justificaciones
        self.ids.justificaciones_layout.clear_widgets()

    def manejar_spinner_fecha(self, tipo):
        """Maneja la visibilidad del spinner de fecha según el tipo"""
        fecha_spinner = self.ids.fecha_spinner
        if tipo == 'FAENA':
            fecha_spinner.opacity = 1
            fecha_spinner.disabled = False
            fecha_spinner.text = 'Seleccionar Fecha'
            fecha_spinner.values = []
        else:
            fecha_spinner.opacity = 0
            fecha_spinner.disabled = True
            fecha_spinner.text = 'Seleccionar Fecha'
            fecha_spinner.values = []

    def on_evento_changed(self, instance, value):
        """Se ejecuta cuando se selecciona un evento"""
        if value == 'Seleccionar Evento':
            self.ids.justificaciones_layout.clear_widgets()
            return
            
        # Limpiar fecha seleccionada cuando cambia el evento
        self.fecha_seleccionada = None
        if hasattr(self, 'fecha_spinner'):
            self.fecha_spinner.text = 'Seleccionar Fecha'
        
        # Cargar fechas disponibles si es una faena
        if self.ids.tipo_spinner.text == 'FAENA':
            self.cargar_fechas_disponibles()
        else:
            # Para reuniones, cargar directamente
            self.load_justificaciones()

    def cargar_fechas_disponibles(self):
        """Carga solo las fechas con justificaciones para la faena seleccionada"""
        evento = self.ids.evento_spinner.text
        if evento == 'Seleccionar Evento':
            return
        try:
            id_faena = int(evento.split(' - ')[0])
            fechas = obtener_fechas_con_justificaciones_faena(id_faena)
            fecha_spinner = self.ids.fecha_spinner
            if fechas:
                fechas_str = [f.strftime('%d/%m/%Y') for f in fechas]
                fecha_spinner.values = fechas_str
                fecha_spinner.text = 'Seleccionar Fecha'
                fecha_spinner.opacity = 1
                fecha_spinner.disabled = False
            else:
                fecha_spinner.values = []
                fecha_spinner.text = 'Sin justificaciones'
                fecha_spinner.opacity = 1
                fecha_spinner.disabled = True
                self.ids.justificaciones_layout.clear_widgets()
                # Mostrar mensaje de que no hay justificaciones
                from kivymd.uix.label import MDLabel
                self.ids.justificaciones_layout.add_widget(MDLabel(
                    text="No hay justificaciones en ninguna fecha para esta faena",
                    theme_text_color="Custom",
                    text_color=(0.2,0.2,0.2,1),
                    font_style="Subtitle1",
                    halign="center"
                ))
        except Exception as e:
            print(f"Error al cargar fechas: {e}")
            import traceback
            traceback.print_exc()

    def on_fecha_changed(self, instance, value):
        """Se ejecuta cuando se selecciona una fecha"""
        if value == 'Seleccionar Fecha':
            self.fecha_seleccionada = None
            self.ids.justificaciones_layout.clear_widgets()
            return
            
        # Convertir fecha de formato dd/mm/yyyy a objeto date
        try:
            from datetime import datetime
            self.fecha_seleccionada = datetime.strptime(value, '%d/%m/%Y').date()
            self.load_justificaciones()
        except Exception as e:
            print(f"Error al convertir fecha: {e}")

    def load_justificaciones(self):
        """Carga las justificaciones según el tipo y evento seleccionado"""
        justificaciones_layout = self.ids.justificaciones_layout
        justificaciones_layout.clear_widgets()
        
        tipo = self.ids.tipo_spinner.text
        evento = self.ids.evento_spinner.text
        
        if tipo not in ['FAENA', 'REUNION'] or evento == 'Seleccionar Evento':
            return
            
        try:
            if tipo == 'FAENA':
                id_faena = int(evento.split(' - ')[0])
                registros = obtener_justificaciones_faena(id_faena, getattr(self, 'fecha_seleccionada', None))
            else:
                id_reunion = int(evento.split(' - ')[0])
                registros = obtener_justificaciones_reunion(id_reunion)
            
            for data in registros:
                # Formatear fecha para mostrar
                fecha_display = ""
                if data.get('fecha_asistencia'):
                    if hasattr(data['fecha_asistencia'], 'strftime'):
                        fecha_display = data['fecha_asistencia'].strftime('%d/%m/%Y')
                    else:
                        fecha_display = str(data['fecha_asistencia'])
                
                # Formatear nombre del evento
                nombre_evento = data['nombre_faena'] if tipo == 'FAENA' else data['nombre_reunion']
                if fecha_display:
                    nombre_evento += f" ({fecha_display})"
                
                item = JustificacionItem(
                    nombre_miembro=f"{data['nombre']} {data['Apellido_Paterno']} {data['Apellido_Materno']}",
                    nombre_evento=nombre_evento,
                    fecha_justificacion=str(data['fecha_subida']) if data['fecha_subida'] else '',
                    on_regularizar=lambda d=data: self.regularizar_evidencia(d),
                    on_ver_justificacion=lambda d=data: self.ver_justificacion(d)
                )
                justificaciones_layout.add_widget(item)
                
        except Exception as e:
            print(f"Error al cargar justificaciones: {e}")
            import traceback
            traceback.print_exc()

    def regularizar_evidencia(self, data):
        # Aquí puedes abrir un popup para editar/subir evidencia
        self.show_justificacion_dialog(data)

    def ver_justificacion(self, data):
        """Muestra un popup con los detalles de la justificación de forma organizada"""
        content = MDBoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15)
        )

        # Header con ícono y título
        header = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50),
            md_bg_color=(0.2, 0.6, 0.8, 1)
        )
        header.add_widget(MDIconButton(
            icon="file-document-check",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_size="24sp"
        ))
        header.add_widget(MDLabel(
            text="Detalles de la Justificación",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style="H6"
        ))
        content.add_widget(header)

        # Contenedor scrolleable
        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True
        )
        scroll_content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None,
            height=dp(600)
        )

        # Información del miembro
        miembro_card = MDCard(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(100),
            md_bg_color=(0.95, 0.95, 0.95, 1)
        )
        miembro_card.add_widget(MDLabel(
            text="Miembro",
            theme_text_color="Custom",
            text_color=(0.3, 0.3, 0.3, 1),
            font_style="Caption"
        ))
        miembro_card.add_widget(MDLabel(
            text=f"{data['nombre']} {data['Apellido_Paterno']} {data['Apellido_Materno']}",
            theme_text_color="Custom",
            text_color=(0.1, 0.1, 0.1, 1),
            font_style="Subtitle1"
        ))
        scroll_content.add_widget(miembro_card)

        # Información del evento
        evento_card = MDCard(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(100),
            md_bg_color=(0.95, 0.95, 0.95, 1)
        )
        evento_card.add_widget(MDLabel(
            text="Evento",
            theme_text_color="Custom",
            text_color=(0.3, 0.3, 0.3, 1),
            font_style="Caption"
        ))
        evento_card.add_widget(MDLabel(
            text=data['nombre_faena'] if 'nombre_faena' in data else data['nombre_reunion'],
            theme_text_color="Custom",
            text_color=(0.1, 0.1, 0.1, 1),
            font_style="Subtitle1"
        ))
        scroll_content.add_widget(evento_card)

        # Descripción
        if data.get('descripcion'):
            desc_card = MDCard(
                orientation='vertical',
                padding=dp(15),
                spacing=dp(10),
                size_hint_y=None,
                height=dp(120),
                md_bg_color=(0.95, 0.95, 0.95, 1)
            )
            desc_card.add_widget(MDLabel(
                text="Descripción",
                theme_text_color="Custom",
                text_color=(0.3, 0.3, 0.3, 1),
                font_style="Caption"
            ))
            desc_card.add_widget(MDLabel(
                text=data['descripcion'],
                theme_text_color="Custom",
                text_color=(0.1, 0.1, 0.1, 1),
                font_style="Body1"
            ))
            scroll_content.add_widget(desc_card)

        # Evidencia
        if data.get('ruta_archivo'):
            evidencia_card = MDCard(
                orientation='vertical',
                padding=dp(15),
                spacing=dp(10),
                size_hint_y=None,
                height=dp(200),
                md_bg_color=(0.95, 0.95, 0.95, 1)
            )
            evidencia_card.add_widget(MDLabel(
                text="Evidencia",
                theme_text_color="Custom",
                text_color=(0.3, 0.3, 0.3, 1),
                font_style="Caption"
            ))
            
            # Tipo de archivo
            if data.get('tipo_archivo'):
                evidencia_card.add_widget(MDLabel(
                    text=f"Tipo de archivo: {data['tipo_archivo']}",
                    theme_text_color="Custom",
                    text_color=(0.1, 0.1, 0.1, 1),
                    font_style="Body2"
                ))
            
            ruta = os.path.join(self.directorio_evidencias, data['ruta_archivo'])
            if os.path.exists(ruta):
                if ruta.lower().endswith(('.png', '.jpg', '.jpeg')):
                    evidencia_card.add_widget(Image(
                        source=ruta,
                        size_hint_y=None,
                        height=dp(150)
                    ))
                else:
                    evidencia_card.add_widget(MDLabel(
                        text=f"Archivo: {os.path.basename(ruta)}",
                        theme_text_color="Custom",
                        text_color=(0.1, 0.1, 0.1, 1),
                        font_style="Body1"
                    ))
            scroll_content.add_widget(evidencia_card)

        # Fecha
        if data.get('fecha_subida'):
            fecha_card = MDCard(
                orientation='vertical',
                padding=dp(15),
                spacing=dp(10),
                size_hint_y=None,
                height=dp(80),
                md_bg_color=(0.95, 0.95, 0.95, 1)
            )
            fecha_card.add_widget(MDLabel(
                text="Fecha de Registro",
                theme_text_color="Custom",
                text_color=(0.3, 0.3, 0.3, 1),
                font_style="Caption"
            ))
            fecha_card.add_widget(MDLabel(
                text=str(data['fecha_subida']),
                theme_text_color="Custom",
                text_color=(0.1, 0.1, 0.1, 1),
                font_style="Body1"
            ))
            scroll_content.add_widget(fecha_card)

        scroll.add_widget(scroll_content)
        content.add_widget(scroll)

        # Botón de cerrar
        content.add_widget(MDRaisedButton(
            text="Cerrar",
            pos_hint={'center_x': 0.5},
            on_release=lambda x: popup.dismiss()
        ))

        popup = Popup(
            title='',
            content=content,
            size_hint=(0.9, 0.9),
            background=''
        )
        popup.open()

    def show_justificacion_dialog(self, data):
        """Muestra un popup para regularizar la evidencia"""
        content = MDBoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15)
        )

        # Header con ícono y título
        header = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50),
            md_bg_color=(0.2, 0.6, 0.8, 1)
        )
        header.add_widget(MDIconButton(
            icon="file-document-edit",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_size="24sp"
        ))
        header.add_widget(MDLabel(
            text="Regularizar Evidencia",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style="H6"
        ))
        content.add_widget(header)

        # Contenedor scrolleable
        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True
        )
        scroll_content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None,
            height=dp(600)
        )

        # Información del miembro
        miembro_card = MDCard(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(100),
            md_bg_color=(0.95, 0.95, 0.95, 1)
        )
        miembro_card.add_widget(MDLabel(
            text="Miembro",
            theme_text_color="Custom",
            text_color=(0.3, 0.3, 0.3, 1),
            font_style="Caption"
        ))
        miembro_card.add_widget(MDLabel(
            text=f"{data['nombre']} {data['Apellido_Paterno']} {data['Apellido_Materno']}",
            theme_text_color="Custom",
            text_color=(0.1, 0.1, 0.1, 1),
            font_style="Subtitle1"
        ))
        scroll_content.add_widget(miembro_card)

        # Información del evento
        evento_card = MDCard(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(100),
            md_bg_color=(0.95, 0.95, 0.95, 1)
        )
        evento_card.add_widget(MDLabel(
            text="Evento",
            theme_text_color="Custom",
            text_color=(0.3, 0.3, 0.3, 1),
            font_style="Caption"
        ))
        evento_card.add_widget(MDLabel(
            text=data['nombre_faena'] if 'nombre_faena' in data else data['nombre_reunion'],
            theme_text_color="Custom",
            text_color=(0.1, 0.1, 0.1, 1),
            font_style="Subtitle1"
        ))
        scroll_content.add_widget(evento_card)

        # Descripción
        desc_card = MDCard(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(150),
            md_bg_color=(0.95, 0.95, 0.95, 1)
        )
        desc_card.add_widget(MDLabel(
            text="Descripción",
            theme_text_color="Custom",
            text_color=(0.3, 0.3, 0.3, 1),
            font_style="Caption"
        ))
        desc_input = TextInput(
            multiline=True,
            size_hint_y=None,
            height=dp(100),
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            cursor_color=(0.2, 0.6, 0.8, 1),
            font_size="14sp"
        )
        desc_card.add_widget(desc_input)
        scroll_content.add_widget(desc_card)

        # Selección de archivo
        file_card = MDCard(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(200),
            md_bg_color=(0.95, 0.95, 0.95, 1)
        )
        file_card.add_widget(MDLabel(
            text="Seleccionar Archivo de Evidencia",
            theme_text_color="Custom",
            text_color=(0.3, 0.3, 0.3, 1),
            font_style="Caption"
        ))

        # Botón para abrir el selector de archivos
        selected_file_label = MDLabel(
            text="Ningún archivo seleccionado",
            theme_text_color="Custom",
            text_color=(0.5, 0.5, 0.5, 1),
            font_style="Body2"
        )
        file_card.add_widget(selected_file_label)

        def open_file_chooser(instance):
            content = MDBoxLayout(
                orientation='vertical',
                padding=dp(20),
                spacing=dp(15),
                md_bg_color=(0.13, 0.15, 0.18, 1)  # Fondo oscuro
            )

            # Header del selector de archivos
            header = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(10),
                size_hint_y=None,
                height=dp(50),
                md_bg_color=(0.18, 0.36, 0.56, 1)
            )
            header.add_widget(MDIconButton(
                icon="folder",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                font_size="24sp"
            ))
            header.add_widget(MDLabel(
                text="Seleccionar Archivo",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                font_style="H6"
            ))
            content.add_widget(header)

            # Contenedor para el selector de archivos
            file_chooser_container = MDBoxLayout(
                orientation='vertical',
                spacing=dp(10),
                size_hint_y=None,
                height=dp(400),
                md_bg_color=(0.13, 0.15, 0.18, 1)  # Fondo oscuro
            )

            # Selector de archivos con fondo oscuro
            file_chooser = FileChooserListView(
                path=os.path.expanduser("~"),
                size_hint_y=None,
                height=dp(350),
                dirselect=True,
                file_encodings=['utf-8'],
                filters=[]  # Permitir todos los tipos de archivo
            )
            file_chooser.background_color = (0.13, 0.15, 0.18, 1)  # Fondo oscuro
            file_chooser.foreground_color = (1, 1, 1, 1)  # Texto claro
            file_chooser.font_size = '15sp'

            file_chooser_container.add_widget(file_chooser)
            content.add_widget(file_chooser_container)

            # Etiqueta para mostrar el archivo seleccionado
            selected_file_preview = MDLabel(
                text="Ningún archivo seleccionado",
                theme_text_color="Custom",
                text_color=(0.8, 0.8, 0.8, 1),
                font_style="Body2",
                size_hint_y=None,
                height=dp(30)
            )
            content.add_widget(selected_file_preview)

            # Actualizar la vista previa cuando se selecciona un archivo
            def update_preview(instance, value):
                if file_chooser.selection:
                    selected_file_preview.text = f"Archivo seleccionado: {os.path.basename(file_chooser.selection[0])}"
                    selected_file_preview.text_color = (1, 1, 1, 1)
                else:
                    selected_file_preview.text = "Ningún archivo seleccionado"
                    selected_file_preview.text_color = (0.8, 0.8, 0.8, 1)

            file_chooser.bind(selection=update_preview)

            # Botones de acción
            buttons = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(10),
                size_hint_y=None,
                height=dp(50),
                pos_hint={'center_x': 0.5},
                md_bg_color=(0.13, 0.15, 0.18, 1)
            )
            buttons.add_widget(MDRaisedButton(
                text="Seleccionar",
                md_bg_color=(0.18, 0.36, 0.56, 1),
                text_color=(1, 1, 1, 1),
                on_release=lambda x: self.select_file(file_chooser.selection, selected_file_label, file_popup)
            ))
            buttons.add_widget(MDFlatButton(
                text="Cancelar",
                theme_text_color="Custom",
                text_color=(0.6, 0.8, 1, 1),
                on_release=lambda x: file_popup.dismiss()
            ))
            content.add_widget(buttons)

            file_popup = Popup(
                title='',
                content=content,
                size_hint=(0.9, 0.9),
                background=''
            )
            file_popup.open()

        select_file_btn = MDRaisedButton(
            text="Buscar Archivo",
            md_bg_color=(0.2, 0.6, 0.8, 1),
            on_release=open_file_chooser
        )
        file_card.add_widget(select_file_btn)
        scroll_content.add_widget(file_card)

        scroll.add_widget(scroll_content)
        content.add_widget(scroll)

        # Botones de acción
        buttons = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50),
            pos_hint={'center_x': 0.5}
        )
        buttons.add_widget(MDRaisedButton(
            text="Guardar",
            md_bg_color=(0.2, 0.6, 0.8, 1),
            on_release=lambda x: self.save_justificacion(data, desc_input.text, selected_file_label.text if selected_file_label.text != "Ningún archivo seleccionado" else None)
        ))
        buttons.add_widget(MDFlatButton(
            text="Cancelar",
            theme_text_color="Custom",
            text_color=(0.2, 0.6, 0.8, 1),
            on_release=lambda x: popup.dismiss()
        ))
        content.add_widget(buttons)

        popup = Popup(
            title='',
            content=content,
            size_hint=(0.9, 0.9),
            background=''
        )
        popup.open()

    def select_file(self, selection, label, popup):
        """Actualiza la etiqueta con el archivo seleccionado y cierra el popup"""
        if selection:
            label.text = selection[0]
            label.theme_text_color = "Custom"
            label.text_color = (0.1, 0.1, 0.1, 1)
        popup.dismiss()

    def save_justificacion(self, data, descripcion, archivo):
        """Guarda la justificación con validaciones"""
        try:
            # Validar que los datos necesarios estén presentes
            if not data.get('nombre'):
                from app.utils.validacion_simplificada import UIValidacionSimplificada
                UIValidacionSimplificada.mostrar_error_snackbar("Error: Falta información del miembro")
                return

            # Validar que exista el nombre del evento según el tipo
            if 'nombre_faena' not in data and 'nombre_reunion' not in data:
                from app.utils.validacion_simplificada import UIValidacionSimplificada
                UIValidacionSimplificada.mostrar_error_snackbar("Error: Falta información del evento")
                return

            # Validar descripción si se proporciona
            if descripcion and len(descripcion.strip()) < 10:
                from app.utils.validacion_simplificada import UIValidacionSimplificada
                UIValidacionSimplificada.mostrar_error_snackbar("La descripción debe tener al menos 10 caracteres")
                return

            # Validar archivo si se proporciona
            if archivo:
                from app.utils.validacion_simplificada import ValidacionFormularios, UIValidacionSimplificada
                es_valido, mensaje_error = ValidacionFormularios.validar_archivo_evidencia(archivo, "Archivo de Evidencia")
                if not es_valido:
                    UIValidacionSimplificada.mostrar_error_snackbar(mensaje_error)
                    return

            # Obtener tipo de archivo
            tipo_archivo = None
            if archivo:
                tipo_archivo = os.path.splitext(archivo)[1].replace('.', '').lower()

            # Determinar el tipo de registro y el ID del evento
            tipo_registro = 'FAENA' if 'nombre_faena' in data else 'REUNION'
            id_miembro = data.get('ID')
            
            if tipo_registro == 'FAENA':
                id_evento = data.get('idFaena')
                id_registro = obtener_id_registro_faena(id_miembro, id_evento, getattr(self, 'fecha_seleccionada', None))
            else:
                id_evento = data.get('id_reunion')
                id_registro = obtener_id_registro_reunion(id_miembro, id_evento)
            
            if not id_registro:
                from app.utils.validacion_simplificada import UIValidacionSimplificada
                UIValidacionSimplificada.mostrar_error_snackbar("No existe asistencia para este miembro en el evento seleccionado.")
                return

            # Guardar archivo si se seleccionó uno
            ruta_archivo = None
            if archivo:
                ruta_archivo = guardar_archivo_evidencia(archivo, self.directorio_evidencias)
            
            # Guardar evidencia en la base de datos
            if guardar_evidencia(tipo_registro, id_registro, descripcion, ruta_archivo, tipo_archivo, data.get('idEvidencia')):
                self.load_justificaciones()  # Recargar la lista
                from app.utils.validacion_simplificada import UIValidacionSimplificada
                UIValidacionSimplificada.mostrar_error_snackbar("Evidencia actualizada correctamente")
            else:
                from app.utils.validacion_simplificada import UIValidacionSimplificada
                UIValidacionSimplificada.mostrar_error_snackbar("Error al guardar la evidencia en la base de datos")
                
        except Exception as e:
            print(f"Error al guardar evidencia: {e}")
            import traceback
            traceback.print_exc()
            from app.utils.validacion_simplificada import UIValidacionSimplificada
            UIValidacionSimplificada.mostrar_error_snackbar(f"Error al guardar evidencia: {str(e)}")

class JustificacionItem(BoxLayout):
    nombre_miembro = StringProperty("")
    nombre_evento = StringProperty("")
    fecha_justificacion = StringProperty("")

    def __init__(self, nombre_miembro, nombre_evento, fecha_justificacion, on_regularizar, on_ver_justificacion, **kwargs):
        super().__init__(**kwargs)
        self.nombre_miembro = nombre_miembro
        self.nombre_evento = nombre_evento
        self.fecha_justificacion = fecha_justificacion
        self.on_regularizar = on_regularizar
        self.on_ver_justificacion = on_ver_justificacion

class JustificacionDialog(BoxLayout):
    def __init__(self, tipo, justificacion=None, on_save=None, **kwargs):
        super().__init__(**kwargs)
        self.tipo = tipo
        self.justificacion = justificacion
        self.on_save = on_save
        
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # Campos del formulario
        self.miembro_spinner = Spinner(
            text='Seleccionar Miembro',
            values=self.get_miembros(),
            size_hint_y=None,
            height=40
        )
        self.add_widget(self.miembro_spinner)
        
        # Selector de evento (faena o reunión)
        self.evento_spinner = Spinner(
            text='Seleccionar Evento',
            values=self.get_eventos(),
            size_hint_y=None,
            height=40
        )
        self.add_widget(self.evento_spinner)
        
        self.descripcion_input = TextInput(
            hint_text='Descripción de la justificación',
            multiline=True,
            size_hint_y=None,
            height=100
        )
        self.add_widget(self.descripcion_input)
        
        # Selector de archivo
        self.file_chooser = FileChooserListView(
            path=os.path.expanduser('~'),
            filters=['*.jpg', '*.jpeg', '*.png', '*.pdf']
        )
        self.add_widget(self.file_chooser)
        
        # Botones
        buttons_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=50
        )
        
        save_btn = Button(
            text='Guardar',
            on_press=self.save_justificacion
        )
        cancel_btn = Button(
            text='Cancelar',
            on_press=self.dismiss
        )
        
        buttons_layout.add_widget(save_btn)
        buttons_layout.add_widget(cancel_btn)
        
        self.add_widget(buttons_layout)
        
        if justificacion:
            self.load_justificacion_data()
    
    def validar_campo(self, campo, valor):
        """Valida un campo específico en tiempo real"""
        from app.utils.validacion_simplificada import ValidacionFormularios, UIValidacionSimplificada
        
        # Validar el campo específico
        es_valido, mensaje_error = ValidacionFormularios.validar_campo_justificacion(campo, valor.strip())
        
        # Actualizar la UI del campo
        if campo == "descripcion":
            UIValidacionSimplificada.actualizar_campo(self.descripcion_input, es_valido, mensaje_error)
        elif campo == "miembro":
            # Para spinners, solo mostrar error en snackbar
            if not es_valido:
                UIValidacionSimplificada.mostrar_error_snackbar(mensaje_error)
        elif campo == "evento":
            # Para spinners, solo mostrar error en snackbar
            if not es_valido:
                UIValidacionSimplificada.mostrar_error_snackbar(mensaje_error)
        
        return es_valido

    def validar_campo_on_focus(self, campo, valor, tiene_foco):
        """Valida un campo cuando pierde el foco"""
        if not tiene_foco:  # Solo validar cuando pierde el foco
            self.validar_campo(campo, valor)
            
    def get_miembros(self):
        try:
            miembros = obtener_miembros()
            return [f"{m['ID']} - {m['nombre']} {m['Apellido_Paterno']} {m['Apellido_Materno']}" for m in miembros]
        except Exception as e:
            print(f"Error al obtener miembros: {e}")
            return []
        
    def get_eventos(self):
        try:
            if self.tipo == 'FAENA':
                eventos = obtener_faenas()
                return [f"{e['idFaena']} - {e['nombre']}" for e in eventos]
            else:
                eventos = obtener_reuniones()
                return [f"{e['id_reunion']} - {e['titulo']}" for e in eventos]
        except Exception as e:
            print(f"Error al obtener eventos: {e}")
            return []
        
    def load_justificacion_data(self):
        """Carga los datos de la justificación en el formulario"""
        if not self.justificacion:
            return

        try:
            # Cargar datos del miembro
            if 'ID' in self.justificacion:
                self.miembro_spinner.text = f"{self.justificacion['ID']} - {self.justificacion.get('nombre', '')} {self.justificacion.get('Apellido_Paterno', '')} {self.justificacion.get('Apellido_Materno', '')}"

            # Cargar datos del evento
            if 'idFaena' in self.justificacion:
                self.evento_spinner.text = f"{self.justificacion['idFaena']} - {self.justificacion.get('nombre', '')}"
            elif 'id_reunion' in self.justificacion:
                self.evento_spinner.text = f"{self.justificacion['id_reunion']} - {self.justificacion.get('titulo', '')}"

            # Cargar descripción
            if 'descripcion' in self.justificacion and self.justificacion['descripcion']:
                self.descripcion_input.text = self.justificacion['descripcion']
            else:
                self.descripcion_input.text = ""

        except Exception as e:
            print(f"Error al cargar datos de justificación: {e}")
            self.descripcion_input.text = ""

    def save_justificacion(self, instance):
        """Guarda la justificación con validaciones"""
        try:
            # Recopilar datos del formulario
            datos = {
                "tipo": self.tipo,
                "miembro": self.miembro_spinner.text,
                "evento": self.evento_spinner.text,
                "descripcion": self.descripcion_input.text.strip(),
                "archivo": self.file_chooser.selection[0] if self.file_chooser.selection else ""
            }
            
            # Validar todos los datos usando el validador centralizado
            from app.utils.validacion_simplificada import ValidacionFormularios, UIValidacionSimplificada
            
            es_valido, mensaje_error = ValidacionFormularios.validar_datos_justificacion(datos)
            if not es_valido:
                UIValidacionSimplificada.mostrar_error_snackbar(mensaje_error)
                return
            
            # Si pasó todas las validaciones, proceder a guardar
            justificacion_data = {
                'tipo': self.tipo,
                'id_miembro': int(self.miembro_spinner.text.split(' - ')[0]),
                'id_evento': int(self.evento_spinner.text.split(' - ')[0]),
                'descripcion': self.descripcion_input.text.strip() or None,
                'archivo': datos["archivo"]
            }
            
            if self.justificacion and 'idEvidencia' in self.justificacion:
                justificacion_data['id'] = self.justificacion['idEvidencia']
            
            # Mostrar mensaje de éxito
            UIValidacionSimplificada.mostrar_error_snackbar("Justificación guardada correctamente")
            
            if self.on_save:
                self.on_save(justificacion_data)
            self.dismiss()
            
        except Exception as e:
            from app.utils.validacion_simplificada import UIValidacionSimplificada
            UIValidacionSimplificada.mostrar_error_snackbar(f"Error al guardar justificación: {str(e)}")

    def dismiss(self, instance=None):
        """Cierra el diálogo"""
        if hasattr(self, 'parent') and isinstance(self.parent, Popup):
            self.parent.dismiss() 