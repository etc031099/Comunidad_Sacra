from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty, ListProperty, BooleanProperty, NumericProperty, StringProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDIcon
from kivy.metrics import dp
from datetime import datetime, time
import traceback
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from .miembro_asistencia_reunion_item import MiembroAsistenciaReunionItem
from .asistencia_reunion_db import (
    obtener_reuniones,
    obtener_miembros_asignados,
    cambiar_estado_miembro,
    guardar_justificacion,
    marcar_tardanza,
    obtener_estadisticas_asistencia
)

class AsistenciaScreen(MDScreen):
    reuniones_data = ListProperty([])
    miembros_asignados = ListProperty([])
    selected_reunion_id = NumericProperty(None, allownone=True)
    selected_reunion = ObjectProperty(None, allownone=True)
    dropdown_menu = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.dropdown_menu = None

    def on_enter(self):
        self.reuniones_data = obtener_reuniones()
        self.crear_dropdown_menu()

    def cargar_reuniones(self):
        self.reuniones_data = obtener_reuniones()
        self.crear_dropdown_menu()

    def crear_dropdown_menu(self):
        if not self.reuniones_data:
            snackbar = MDSnackbar(
                MDLabel(
                    text="No hay reuniones disponibles",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()
            return
        menu_items = []
        for reunion in self.reuniones_data:
            menu_items.append({
                "text": f"{reunion['fecha']} - {reunion['titulo']}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=reunion['id_reunion']: self.seleccionar_reunion(x),
            })
        self.dropdown_menu = MDDropdownMenu(
            caller=self.ids.dropdown_reunion,
            items=menu_items,
            width_mult=4,
        )

    def abrir_dropdown(self):
        if self.dropdown_menu:
            self.dropdown_menu.open()
        else:
            self.cargar_reuniones()

    def seleccionar_reunion(self, reunion_id):
        self.selected_reunion_id = reunion_id
        if self.dropdown_menu:
            self.dropdown_menu.dismiss()
        self.selected_reunion = None
        for reunion in self.reuniones_data:
            if reunion['id_reunion'] == reunion_id:
                self.selected_reunion = reunion
                break
        if self.selected_reunion:
            self.ids.dropdown_reunion.text = f"{self.selected_reunion['fecha']} - {self.selected_reunion['titulo']}"
            self.ids.info_reunion.text = f"Hora inicio: {self.selected_reunion['hora_inicio'] or 'Sin hora'} - {self.selected_reunion['descripcion'] or ''}"
            if 'search_field' in self.ids:
                self.ids.search_field.text = ""
            self.cargar_miembros_asignados()

    def cargar_miembros_asignados(self):
        if not self.selected_reunion_id:
            print("No hay reunión seleccionada")
            return
        self.miembros_asignados = obtener_miembros_asignados(self.selected_reunion_id)
        self.actualizar_lista_miembros()

    def actualizar_lista_miembros(self, miembros_a_mostrar=None):
        if miembros_a_mostrar is None:
            miembros_a_mostrar = self.miembros_asignados

        self.ids.rv_miembros.data = [
            {
                'text': miembro['Nombre'],
                'secondary_text': f"Estado: {miembro['estado_asistencia'] or 'Sin registrar'}",
                'presente': miembro['estado_asistencia'] == 'Presente',
                'miembro_id': miembro['ID'],
                'on_check_change': self.cambiar_estado_miembro,
                'estado_asistencia': miembro['estado_asistencia'] or 'Sin registrar'
            } for miembro in miembros_a_mostrar
        ]
        self.ids.rv_miembros.refresh_from_data()

    def buscar_miembro(self, texto_busqueda=""):
        texto_busqueda = texto_busqueda.lower().strip()
        if not texto_busqueda:
            self.actualizar_lista_miembros()
            return

        miembros_filtrados = [
            miembro for miembro in self.miembros_asignados
            if texto_busqueda in miembro['Nombre'].lower()
        ]
        self.actualizar_lista_miembros(miembros_filtrados)

    def cambiar_estado_miembro(self, miembro_id):
        if not self.selected_reunion_id:
            return
        print(f"Cambiando estado del miembro ID: {miembro_id}")
        miembro_actual = next((m for m in self.miembros_asignados if m['ID'] == miembro_id), None)
        if not miembro_actual:
            return
        estado_actual = miembro_actual['estado_asistencia'] or 'Sin registrar'
        if estado_actual in ['Tardanza', 'Justificado']:
            menu_items = [
                {
                    "text": "Resetear estado",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda: self.resetear_estado_miembro(miembro_id),
                }
            ]
            # Buscar el widget correspondiente en la lista
            for item in self.ids.rv_miembros.layout_manager.children:
                if hasattr(item, 'miembro_id') and item.miembro_id == miembro_id:
                    self.dropdown_menu_miembro = MDDropdownMenu(
                        caller=item,
                        items=menu_items,
                        width_mult=3,
                    )
                    self.dropdown_menu_miembro.open()
                    return
            # Si no se encontró el widget, muestra el mensaje
            snackbar = MDSnackbar(
                MDLabel(
                    text=f"No se puede cambiar directamente un estado {estado_actual}. Use el botón 'Resetear' para cambiar el estado.",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()
            return
        presente = estado_actual != 'Presente'
        cambiar_estado_miembro(self.selected_reunion_id, miembro_id, presente)
        self.cargar_miembros_asignados()

    def guardar_justificacion(self, miembro_id, descripcion):
        if not self.selected_reunion_id:
            return
        guardar_justificacion(self.selected_reunion_id, miembro_id, descripcion)
        self.cargar_miembros_asignados()

    def guardar_justificacion_multiple(self, *args):
        """Guarda justificaciones para múltiples miembros seleccionados"""
        if not self.selected_reunion_id:
            return
        
        # Obtener miembros seleccionados
        miembros_seleccionados = [m for m in self.miembros_seleccionados.values() if m['selected']]
        if not miembros_seleccionados:
            snackbar = MDSnackbar(
                MDLabel(
                    text="Seleccione al menos un miembro",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()
            return
        
        # Obtener descripción
        descripcion = self.justificacion_field.text.strip()
        if not descripcion:
            snackbar = MDSnackbar(
                MDLabel(
                    text="Ingrese un motivo de justificación",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()
            return
        
        # Guardar justificación para cada miembro seleccionado
        for miembro_info in miembros_seleccionados:
            miembro_id = next(k for k, v in self.miembros_seleccionados.items() if v == miembro_info)
            guardar_justificacion(self.selected_reunion_id, miembro_id, descripcion)
        
        # Cerrar diálogo y actualizar lista
        self.cerrar_dialog()
        self.cargar_miembros_asignados()
        
        snackbar = MDSnackbar(
            MDLabel(
                text=f"Justificaciones registradas para {len(miembros_seleccionados)} miembro(s)",
                theme_text_color="Custom",
                text_color="white",
            )
        )
        snackbar.open()

    def marcar_tardanza(self, miembro_id):
        if not self.selected_reunion_id:
            return
        marcar_tardanza(self.selected_reunion_id, miembro_id)
        self.cargar_miembros_asignados()

    def volver_asistencia_menu(self):
        self.manager.transition.direction = 'right'
        self.manager.current = "dashboard"

    def mostrar_dialog_justificacion(self):
        if not self.selected_reunion_id:
            snackbar = MDSnackbar(
                MDLabel(
                    text="Seleccione una reunión primero",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()
            return
        miembros_ausentes = [m for m in self.miembros_asignados if m['estado_asistencia'] == 'Ausente']
        if not miembros_ausentes:
            snackbar = MDSnackbar(
                MDLabel(
                    text="No hay miembros ausentes para justificar",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()
            return
        self.miembros_ausentes_seleccionados = []
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(400)
        )
        content.add_widget(MDLabel(
            text="Seleccione miembros para justificar:",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(30)
        ))
        scroll = MDScrollView(
            size_hint=(1, None),
            height=dp(200)
        )
        miembros_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(5),
            size_hint_y=None,
            adaptive_height=True
        )
        self.miembros_seleccionados = {}
        for miembro in miembros_ausentes:
            card = MDCard(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(50),
                padding=dp(10),
                spacing=dp(10),
                ripple_behavior=True,
                md_bg_color=(0.95, 0.95, 0.95, 1),
                radius=dp(5)
            )
            card.add_widget(MDIcon(
                icon="account",
                theme_text_color="Custom",
                text_color=(0.8, 0.2, 0.2, 1),
                size_hint=(None, None),
                size=(dp(24), dp(24))
            ))
            card.add_widget(MDLabel(
                text=miembro['Nombre'],
                theme_text_color="Primary"
            ))
            self.miembros_seleccionados[miembro['ID']] = {
                'card': card,
                'selected': False,
                'nombre': miembro['Nombre']
            }
            def toggle_selection(card_instance, miembro_id=miembro['ID']):
                if self.miembros_seleccionados[miembro_id]['selected']:
                    self.miembros_seleccionados[miembro_id]['selected'] = False
                    card_instance.md_bg_color = (0.95, 0.95, 0.95, 1)
                else:
                    self.miembros_seleccionados[miembro_id]['selected'] = True
                    card_instance.md_bg_color = (0.2, 0.6, 0.8, 0.2)
            card.bind(on_release=lambda x, mid=miembro['ID']: toggle_selection(x, mid))
            miembros_box.add_widget(card)
        scroll.add_widget(miembros_box)
        content.add_widget(scroll)
        content.add_widget(MDLabel(
            text="Justificación:",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(30)
        ))
        self.justificacion_field = MDTextField(
            hint_text="Ingrese la justificación",
            multiline=True,
            size_hint_y=None,
            height=dp(100)
        )
        content.add_widget(self.justificacion_field)
        self.dialog = MDDialog(
            title="Justificar Ausencias",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    on_release=self.cerrar_dialog
                ),
                MDRaisedButton(
                    text="GUARDAR",
                    on_release=self.guardar_justificacion_multiple
                ),
            ],
        )
        self.dialog.open()

    def cerrar_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()

    def generar_reporte(self):
        if not self.selected_reunion_id:
            snackbar = MDSnackbar(
                MDLabel(
                    text="Seleccione una reunión primero",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()
            return
        stats = obtener_estadisticas_asistencia(self.selected_reunion_id)
        self.mostrar_reporte_dialog(stats)

    def mostrar_reporte_dialog(self, stats):
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(420)
        )
        if self.selected_reunion:
            content.add_widget(MDLabel(
                text=f"Reunión: {self.selected_reunion['titulo']}",
                theme_text_color="Primary",
                font_style="H6",
                size_hint_y=None,
                height=dp(30)
            ))
        stats_card = MDCard(
            orientation="vertical",
            padding=dp(15),
            elevation=2,
            radius=dp(10),
            size_hint_y=None,
            height=dp(340),
            md_bg_color=(0.98, 0.98, 0.98, 1)
        )
        stats_card.add_widget(MDLabel(
            text="Estadísticas de Asistencia",
            theme_text_color="Primary",
            font_style="Subtitle1",
            bold=True,
            size_hint_y=None,
            height=dp(30)
        ))
        stats_grid = MDGridLayout(
            cols=2,
            spacing=dp(12),
            padding=dp(10),
            size_hint_y=None,
            height=dp(240)
        )
        def stat_row(icon, color, label, value):
            row = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(32))
            row.add_widget(MDIcon(icon=icon, theme_text_color="Custom", text_color=color, size_hint=(None, None), size=(dp(24), dp(24))))
            row.add_widget(MDLabel(text=label, theme_text_color="Secondary", font_style="Body1"))
            return row, MDLabel(text=str(value), theme_text_color="Custom", text_color=color, font_style="Body1", bold=True)
        stats_grid.add_widget(MDLabel(text="Total de miembros asignados:", theme_text_color="Secondary", bold=True, halign="right"))
        stats_grid.add_widget(MDLabel(text=f"{stats['total_asignados']}", theme_text_color="Primary", bold=True))
        row, val = stat_row("checkbox-marked-circle", (0.2, 0.7, 0.2, 1), "Presentes", stats['presentes'])
        stats_grid.add_widget(row)
        stats_grid.add_widget(val)
        row, val = stat_row("close-circle", (0.8, 0.2, 0.2, 1), "Ausentes", stats['ausentes'])
        stats_grid.add_widget(row)
        stats_grid.add_widget(val)
        row, val = stat_row("clock-alert", (0.9, 0.6, 0.1, 1), "Tardanzas", stats['tardanzas'])
        stats_grid.add_widget(row)
        stats_grid.add_widget(val)
        row, val = stat_row("file-document", (0.1, 0.6, 0.8, 1), "Justificados", stats['justificados'])
        stats_grid.add_widget(row)
        stats_grid.add_widget(val)
        row, val = stat_row("help-circle", (0.5, 0.5, 0.5, 1), "Sin registrar", stats['sin_registrar'])
        stats_grid.add_widget(row)
        stats_grid.add_widget(val)
        stats_grid.add_widget(MDLabel(text="Porcentaje de asistencia:", theme_text_color="Secondary", bold=True, halign="right"))
        porcentaje = (stats['presentes'] / stats['total_asignados'] * 100) if stats['total_asignados'] else 0
        stats_grid.add_widget(MDLabel(text=f"{porcentaje:.1f}%", theme_text_color="Primary", bold=True))
        stats_card.add_widget(stats_grid)
        scroll = MDScrollView(size_hint=(1, None), height=dp(340))
        scroll.add_widget(stats_card)
        content.add_widget(scroll)
        self.dialog = MDDialog(
            title="Reporte de Asistencia",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CERRAR",
                    on_release=self.cerrar_dialog
                ),
            ],
        )
        self.dialog.open()

    def resetear_estado_miembro(self, miembro_id):
        if not self.selected_reunion_id:
            return
        print(f"Reseteando estado del miembro ID: {miembro_id}")
        miembro_actual = next((m for m in self.miembros_asignados if m['ID'] == miembro_id), None)
        if not miembro_actual:
            return
        cambiar_estado_miembro(self.selected_reunion_id, miembro_id, 'Sin registrar')
        self.cargar_miembros_asignados()

    def mostrar_leyenda_colores(self):
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(300)
        )
        content.add_widget(MDLabel(
            text="Leyenda de Colores",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height=dp(30)
        ))
        estados = [
            {"estado": "Presente", "color": (0.2, 0.8, 0.2, 0.2), "icon": "check-circle", "icon_color": (0.2, 0.8, 0.2, 1)},
            {"estado": "Ausente", "color": (0.8, 0.2, 0.2, 0.2), "icon": "close-circle", "icon_color": (0.8, 0.2, 0.2, 1)},
            {"estado": "Tardanza", "color": (0.8, 0.6, 0.0, 0.2), "icon": "clock-alert", "icon_color": (0.8, 0.6, 0.0, 1)},
            {"estado": "Justificado", "color": (0.2, 0.6, 0.8, 0.2), "icon": "file-document", "icon_color": (0.2, 0.6, 0.8, 1)},
            {"estado": "Sin registrar", "color": (0.95, 0.95, 0.95, 1), "icon": "help-circle", "icon_color": (0.5, 0.5, 0.5, 1)}
        ]
        for estado_info in estados:
            card = MDCard(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(50),
                padding=dp(10),
                spacing=dp(10),
                md_bg_color=estado_info["color"],
                radius=dp(5)
            )
            card.add_widget(MDIcon(
                icon=estado_info["icon"],
                theme_text_color="Custom",
                text_color=estado_info["icon_color"],
                size_hint=(None, None),
                size=(dp(24), dp(24))
            ))
            card.add_widget(MDLabel(
                text=estado_info["estado"],
                theme_text_color="Primary"
            ))
            content.add_widget(card)
        self.dialog = MDDialog(
            title="Estados de Asistencia",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CERRAR",
                    on_release=self.cerrar_dialog
                ),
            ],
        )
        self.dialog.open()
