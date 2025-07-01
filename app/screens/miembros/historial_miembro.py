from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivymd.uix.label import MDIcon
from kivy.metrics import dp
from datetime import datetime, timedelta
import pyodbc
import logging
import os
import traceback
from kivy.properties import StringProperty, NumericProperty
from .historial_miembro_db import obtener_miembros, obtener_nombre_miembro, obtener_historial_miembro

# Configurar el logger
log_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'error_historial.log')
logging.basicConfig(filename=log_file_path, level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class HistorialItem(MDBoxLayout):
    tipo_evento = StringProperty("")
    nombre_evento = StringProperty("")
    fecha = StringProperty("")
    estado = StringProperty("")
    detalles = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class MiembroListItem(TwoLineAvatarIconListItem):
    id_miembro = NumericProperty(0)
    nombre_completo = StringProperty("")
    dni = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = self.nombre_completo
        self.secondary_text = f"DNI: {self.dni}"

class HistorialMiembroScreen(MDScreen):
    previous_screen = StringProperty('dashboard')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id_miembro_seleccionado = None

    def on_enter(self):
        try:
            self.cargar_miembros()
            if self.ids.periodo_dropdown.text == "Período":
                self.ids.periodo_dropdown.text = "Todo el Historial"
            if self.ids.tipo_evento_dropdown.text == "Tipo de Evento":
                self.ids.tipo_evento_dropdown.text = "Todos"
            if self.ids.estado_dropdown.text == "Estado":
                self.ids.estado_dropdown.text = "Todos"

            # Si hay un miembro seleccionado previamente, recargar su historial
            if self.id_miembro_seleccionado:
                self.seleccionar_miembro(self.id_miembro_seleccionado)

        except Exception as e:
            error_details = traceback.format_exc()
            logging.error("Error al conectar con la base de datos en on_enter:", exc_info=True)
            snackbar = MDSnackbar(
                MDLabel(
                    text=f"Error al conectar con la base de datos. Detalles en error_historial.log",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()

    def on_leave(self):
        self.previous_screen = 'dashboard'
        self.id_miembro_seleccionado = None

    def go_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = self.previous_screen

    def cargar_miembros(self):
        try:
            miembros = obtener_miembros()
            
            self.ids.miembros_list.clear_widgets()
            for m in miembros:
                item = MiembroListItem(
                    id_miembro=m[0],
                    nombre_completo=f"{m[1]} {m[2]} {m[3]}",
                    dni=m[4]
                )
                item.bind(on_release=lambda x, id=m[0]: self.seleccionar_miembro(id))
                self.ids.miembros_list.add_widget(item)

        except Exception as e:
            error_details = traceback.format_exc()
            logging.error("Error al cargar miembros:", exc_info=True)
            snackbar = MDSnackbar(
                MDLabel(
                    text=f"Error al cargar miembros. Detalles en error_historial.log",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()

    def seleccionar_miembro(self, id_miembro):
        self.id_miembro_seleccionado = id_miembro

        # Actualizar el label del miembro seleccionado
        try:
            nombre_miembro = obtener_nombre_miembro(id_miembro)
            self.ids.miembro_seleccionado_label.text = f"Historial de {nombre_miembro}"
        except Exception as e:
            logging.error(f"Error al obtener nombre de miembro {id_miembro}:", exc_info=True)
            self.ids.miembro_seleccionado_label.text = "Error al cargar nombre"

        self.cargar_historial_miembro_seleccionado()

    def cargar_historial_miembro_seleccionado(self):
        if not self.id_miembro_seleccionado:
            self.ids.historial_actividades_list.clear_widgets()
            return

        try:
            periodo = self.ids.periodo_dropdown.text
            tipo_evento_filtro = self.ids.tipo_evento_dropdown.text
            estado_filtro = self.ids.estado_dropdown.text

            registros = obtener_historial_miembro(
                self.id_miembro_seleccionado, 
                periodo, 
                tipo_evento_filtro, 
                estado_filtro
            )
            
            # Limpiar completamente la lista antes de agregar nuevos elementos
            self.ids.historial_actividades_list.clear_widgets()

            # Agrupar faenas por nombre_evento
            faenas = {}
            reuniones = {}
            penalizaciones = []
            for r in registros:
                tipo = r[0]
                nombre = r[1]
                fecha = r[2]
                estado = r[3]
                detalles = r[4] if r[4] else ""
                if tipo == 'FAENA':
                    if nombre not in faenas:
                        faenas[nombre] = []
                    faenas[nombre].append({
                        'fecha': fecha,
                        'estado': estado,
                        'detalles': detalles
                    })
                elif tipo == 'REUNION':
                    if nombre not in reuniones:
                        reuniones[nombre] = []
                    reuniones[nombre].append({
                        'fecha': fecha,
                        'estado': estado,
                        'detalles': detalles
                    })
                else:
                    penalizaciones.append((tipo, nombre, fecha, estado, detalles))

            # Mostrar faenas como acordeón (restaurado)
            for nombre_faena, asistencias in faenas.items():
                asistencias_ordenadas = sorted(asistencias, key=lambda x: x['fecha'], reverse=True)
                # Contenido del panel: lista de días
                content_box = MDBoxLayout(
                    orientation='vertical',
                    spacing=dp(5),
                    padding=dp(10),
                    size_hint_y=None,
                    adaptive_height=True
                )
                for a in asistencias_ordenadas:
                    day_label = MDLabel(
                        text=f"{a['fecha'].strftime('%d/%m/%Y')}: {a['estado']}" + (f" | {a['detalles']}" if a['detalles'] else ""),
                        theme_text_color="Primary",
                        font_style="Body2",
                        size_hint_y=None,
                        height=dp(20)
                    )
                    content_box.add_widget(day_label)
                # Panel con fondo amarillo claro en el título
                panel = MDExpansionPanel(
                    icon="shovel",
                    content=content_box,
                    panel_cls=MDExpansionPanelOneLine(
                        text=nombre_faena,
                        size_hint_y=None,
                        height=dp(48)
                    )
                )
                # Unificar tipografía y color del título (faena y reunión)
                panel.panel_cls.text = nombre_faena
                panel.panel_cls.font_style = "Subtitle1"
                panel.panel_cls.bold = True
                panel.panel_cls.theme_text_color = "Primary"
                # Fondo amarillo claro en el título del acordeón
                panel.panel_cls.md_bg_color = (1, 0.98, 0.77, 1)
                panel.content.md_bg_color = (1, 0.98, 0.77, 1)  # Amarillo claro
                self.ids.historial_actividades_list.add_widget(panel)

            # Mostrar reuniones como tarjetas/fila con MDIcon (sin flecha)
            for nombre_reunion, asistencias in reuniones.items():
                asistencias_ordenadas = sorted(asistencias, key=lambda x: x['fecha'], reverse=True)
                for a in asistencias_ordenadas:
                    card = MDBoxLayout(
                        orientation='horizontal',
                        spacing=dp(10),
                        padding=dp(10),
                        size_hint_y=None,
                        height=dp(56),
                        md_bg_color=(0.91, 0.96, 0.99, 1),  # Azul claro
                        radius=[8, 8, 8, 8]
                    )
                    # Ícono de reunión
                    card.add_widget(MDIcon(
                        icon="calendar",
                        theme_text_color="Custom",
                        text_color=(0.2, 0.6, 0.8, 1),
                        size_hint_x=None,
                        size=(dp(32), dp(32))
                    ))
                    # Nombre y fecha (título)
                    info_box = MDBoxLayout(orientation='vertical', spacing=0)
                    info_box.add_widget(MDLabel(
                        text=f"{nombre_reunion} - {a['fecha'].strftime('%d/%m/%Y')}",
                        theme_text_color="Primary",
                        font_style="Subtitle1",
                        bold=True,
                        size_hint_y=None,
                        height=dp(24)
                    ))
                    # Estado debajo
                    info_box.add_widget(MDLabel(
                        text=f"Estado: {a['estado']}" + (f" | {a['detalles']}" if a['detalles'] else ""),
                        theme_text_color="Secondary",
                        font_style="Caption",
                        size_hint_y=None,
                        height=dp(18)
                    ))
                    card.add_widget(info_box)
                    # Quitar la flecha a la derecha
                    self.ids.historial_actividades_list.add_widget(card)

            # Mostrar penalizaciones como antes
            for tipo, nombre, fecha, estado, detalles in penalizaciones:
                item = HistorialItem()
                item.tipo_evento = tipo
                item.nombre_evento = nombre
                item.fecha = fecha.strftime("%d/%m/%Y")
                item.estado = estado
                item.detalles = detalles
                self.ids.historial_actividades_list.add_widget(item)

        except Exception as e:
            error_details = traceback.format_exc()
            logging.error("Error al cargar historial del miembro:", exc_info=True)
            snackbar = MDSnackbar(
                MDLabel(
                    text=f"Error al cargar historial del miembro. Detalles en error_historial.log",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()

    def show_periodo_menu(self):
        menu_items = [
            {
                "text": "Todo el Historial",
                "on_release": lambda x="Todo el Historial": self.filtrar_periodo(x),
            },
            {
                "text": "Última Semana",
                "on_release": lambda x="Última Semana": self.filtrar_periodo(x),
            },
            {
                "text": "Último Mes",
                "on_release": lambda x="Último Mes": self.filtrar_periodo(x),
            },
            {
                "text": "Últimos 3 Meses",
                "on_release": lambda x="Últimos 3 Meses": self.filtrar_periodo(x),
            },
            {
                "text": "Últimos 6 Meses",
                "on_release": lambda x="Últimos 6 Meses": self.filtrar_periodo(x),
            },
            {
                "text": "Último Año",
                "on_release": lambda x="Último Año": self.filtrar_periodo(x),
            },
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.periodo_dropdown,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    def show_tipo_evento_menu(self):
        menu_items = [
            {
                "text": "Todos",
                "on_release": lambda x="Todos": self.filtrar_tipo_evento(x),
            },
            {
                "text": "FAENA",
                "on_release": lambda x="FAENA": self.filtrar_tipo_evento(x),
            },
            {
                "text": "REUNION",
                "on_release": lambda x="REUNION": self.filtrar_tipo_evento(x),
            },
            {
                "text": "PENALIZACION",
                "on_release": lambda x="PENALIZACION": self.filtrar_tipo_evento(x),
            },
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.tipo_evento_dropdown,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    def show_estado_menu(self):
        tipo_evento = self.ids.tipo_evento_dropdown.text
        if tipo_evento == "PENALIZACION":
            menu_items = [
                {"text": "Todos", "on_release": lambda x="Todos": self.filtrar_estado(x)},
                {"text": "PENDIENTE", "on_release": lambda x="PENDIENTE": self.filtrar_estado(x)},
                {"text": "PAGADO", "on_release": lambda x="PAGADO": self.filtrar_estado(x)},
            ]
        else:
            menu_items = [
                {"text": "Todos", "on_release": lambda x="Todos": self.filtrar_estado(x)},
                {"text": "Presente", "on_release": lambda x="Presente": self.filtrar_estado(x)},
                {"text": "Ausente", "on_release": lambda x="Ausente": self.filtrar_estado(x)},
                {"text": "Tardanza", "on_release": lambda x="Tardanza": self.filtrar_estado(x)},
                {"text": "Justificado", "on_release": lambda x="Justificado": self.filtrar_estado(x)},
            ]
        self.menu = MDDropdownMenu(
            caller=self.ids.estado_dropdown,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    def filtrar_periodo(self, periodo):
        self.ids.periodo_dropdown.text = periodo
        self.menu.dismiss()
        self.cargar_historial_miembro_seleccionado()

    def filtrar_tipo_evento(self, tipo):
        self.ids.tipo_evento_dropdown.text = tipo
        self.menu.dismiss()
        self.cargar_historial_miembro_seleccionado()

    def filtrar_estado(self, estado):
        self.ids.estado_dropdown.text = estado
        self.menu.dismiss()
        self.cargar_historial_miembro_seleccionado() 