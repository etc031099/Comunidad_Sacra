from kivymd.uix.screen import MDScreen
from kivy.properties import ListProperty, ObjectProperty, BooleanProperty
from kivymd.uix.snackbar import Snackbar, MDSnackbar
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.list import TwoLineAvatarIconListItem, IconLeftWidget, IconRightWidget
import pandas as pd
from kivy.utils import platform
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.tooltip import MDTooltip
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.event import EventDispatcher
from app.db.conexion import obtener_conexion
from kivy.factory import Factory
from kivy.clock import Clock
from .miembros_db import obtener_miembros, eliminar_miembro_completo

class HoverBehavior(EventDispatcher):
    """
    Comportamiento de Hover que se puede mezclar con otros widgets.
    """
    hovered = BooleanProperty(False)
    border_point = ObjectProperty(None)

    def __init__(self, **kwargs):
        self.register_event_type('on_enter')
        self.register_event_type('on_leave')
        super(HoverBehavior, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        if self.collide_point(*self.to_widget(*pos)):
            if not self.hovered:
                self.hovered = True
                self.dispatch('on_enter')
        else:
            if self.hovered:
                self.hovered = False
                self.dispatch('on_leave')

    def on_enter(self, *args):
        pass

    def on_leave(self, *args):
        pass

class HoverMDBoxLayout(MDBoxLayout, HoverBehavior):
    normal_color = ListProperty([1, 1, 1, 1])
    hover_color = ListProperty([0.95, 0.95, 1, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = self.normal_color

    def on_enter(self, *args):
        self.md_bg_color = self.hover_color

    def on_leave(self, *args):
        self.md_bg_color = self.normal_color

class TooltipIconButton(MDIconButton, MDTooltip):
    pass

class MiembrosScreen(MDScreen):
    miembros = ListProperty([])
    miembros_filtrados = ListProperty([])
    dialogo_confirmacion = ObjectProperty(allownone=True)

    def get_widget_by_id(self, widget, widget_id):
        if hasattr(widget, 'ids') and widget_id in widget.ids:
            return widget.ids[widget_id]
        for child in getattr(widget, 'children', []):
            result = self.get_widget_by_id(child, widget_id)
            if result:
                return result
        return None

    def on_pre_enter(self):
        self.cargar_miembros()

    def cargar_miembros(self):
        try:
            self.miembros = obtener_miembros()
            self.miembros_filtrados = self.miembros[:]
            self.actualizar_lista_miembros()
        except Exception as e:
            print("Error al cargar miembros:", e)
            self.mostrar_popup("Error", "No se pudieron cargar los miembros")

    def filtrar_miembros(self, texto):
        texto = texto.lower()
        self.miembros_filtrados = [
            m for m in self.miembros
            if texto in f"{m['Nombre']} {m['Apellido_Paterno']} {m['Apellido_Materno']}".lower() or texto in str(m["DNI"]).lower()
        ]
        self.actualizar_lista_miembros()

    def actualizar_lista_miembros(self):
        lista = self.get_widget_by_id(self, 'lista_miembros')
        if not lista:
            return
        lista.clear_widgets()
        for idx, miembro in enumerate(self.miembros_filtrados):
            fila = HoverMDBoxLayout(
                orientation="horizontal",
                spacing=8,
                size_hint_y=None,
                height=56,
                padding=[8, 0, 8, 0],
                hover_color=[0.80, 0.87, 1, 1]  # Color al pasar el mouse
            )

            # Icono a la izquierda
            fila.add_widget(IconLeftWidget(icon="account"))

            # Textos (nombre y datos)
            textos = MDBoxLayout(orientation="vertical", size_hint_x=0.75)
            textos.add_widget(MDLabel(
                text=f"{miembro['Nombre']} {miembro['Apellido_Paterno']} {miembro['Apellido_Materno']}",
                font_style="Subtitle1", 
                font_size="18sp", 
                halign="left",
                valign="middle",
                shorten=True,
                size_hint_y=None,
                height=30
            ))
            textos.add_widget(MDLabel(
                text=f"DNI: {miembro['DNI']} | Correo: {miembro['Correo'] or ''}",
                font_style="Caption",  
                font_size="13sp",        
                halign="left",
                valign="middle",
                shorten=True,
                size_hint_y=None,
                height=20
            ))
            fila.add_widget(textos)

            # Iconos de acción alineados a la derecha
            acciones = MDBoxLayout(orientation="horizontal", spacing=12, size_hint_x=0.25)
            for icon, tooltip, callback in [
                ("information", "Ver detalles", lambda x=miembro: self.ver_detalle_miembro(x)),
                ("pencil", "Editar", lambda x=miembro: self.abrir_panel_editar(x)),
                ("delete", "Eliminar", lambda x=miembro: self.eliminar_miembro(x)),
            ]:
                btn = TooltipIconButton(icon=icon, tooltip_text=tooltip)
                btn.size_hint_x = None
                btn.width = 32
                btn.on_release = callback
                if icon == "delete":
                    btn.theme_text_color = "Custom"
                    btn.text_color = (1, 0, 0, 1)
                acciones.add_widget(btn)
            fila.add_widget(acciones)
            lista.add_widget(fila)
            # Separador visual
            lista.add_widget(Widget(size_hint_y=None, height=2))
        # Actualiza el contador
        self.ids.contador_miembros.text = f"Total miembros: {len(self.miembros_filtrados)}"

    def eliminar_miembro(self, miembro):
        if self.dialogo_confirmacion:
            self.dialogo_confirmacion.dismiss()
            self.dialogo_confirmacion = None

        self.dialogo_confirmacion = MDDialog(
            title="¿Eliminar Miembro?",
            text=f"Está a punto de eliminar a [b]{miembro['Nombre']} {miembro['Apellido_Paterno']}[/b].\n\n"
                 f"Esta acción es irreversible y borrará [b]TODOS[/b] sus registros asociados, incluyendo:\n"
                 f"- Asistencias a reuniones y faenas\n"
                 f"- Penalizaciones y pagos\n"
                 f"- Asignaciones y reconocimientos\n\n"
                 f"¿Desea continuar?",
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    on_release=lambda x: self.dialogo_confirmacion.dismiss()
                ),
                MDRaisedButton(
                    text="SÍ, ELIMINAR",
                    md_bg_color="red",
                    on_release=lambda x, m=miembro: self._proceder_eliminacion(m)
                ),
            ],
        )
        self.dialogo_confirmacion.open()

    def _proceder_eliminacion(self, miembro):
        if self.dialogo_confirmacion:
            self.dialogo_confirmacion.dismiss()
            self.dialogo_confirmacion = None

        miembro_id = miembro["ID"]
        exito, mensaje = eliminar_miembro_completo(miembro_id)
        
        if exito:
            MDSnackbar(MDLabel(text=mensaje)).open()
        else:
            self.mostrar_popup("Error", mensaje)
        
        self.cargar_miembros()

    def ver_detalle_miembro(self, miembro):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.label import MDLabel
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivy.uix.scrollview import ScrollView

        # Crea un layout vertical para los datos
        layout = MDBoxLayout(orientation="vertical", spacing=6, padding=[0, 0, 0, 0], size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # Lista de campos a mostrar
        campos = [
            ("Nombre", miembro['Nombre']),
            ("Apellido Paterno", miembro['Apellido_Paterno']),
            ("Apellido Materno", miembro['Apellido_Materno']),
            ("DNI", miembro['DNI']),
            ("Correo", miembro['Correo'] or '-'),
            ("Dirección", miembro['Dirección'] or '-'),
            ("Teléfono", miembro['Teléfono'] or '-'),
        ]

        for label, valor in campos:
            layout.add_widget(
                MDLabel(
                    text=f"[b]{label}:[/b] {valor}",
                    markup=True,
                    halign="left",
                    theme_text_color="Primary",
                    size_hint_y=None,
                    height=28
                )
            )

        # Agrega scroll si hay muchos datos
        scroll = ScrollView(size_hint=(1, None), size=(500, 220))
        scroll.add_widget(layout)

        try:
            if hasattr(self, 'detalle_dialog') and self.detalle_dialog:
                self.detalle_dialog.dismiss()
        except AttributeError:
            pass
        self.detalle_dialog = MDDialog(
            title="Detalles del Miembro",
            type="custom",
            content_cls=scroll,
            buttons=[
                MDRaisedButton(
                    text="Cerrar",
                    on_release=lambda x: self.detalle_dialog.dismiss()
                )
            ]
        )
        self.detalle_dialog.open()

    def mostrar_popup(self, titulo, mensaje):
        contenido = BoxLayout(orientation="vertical", spacing=10, padding=10)
        contenido.add_widget(Label(text=mensaje))
        cerrar = Button(text="Cerrar", size_hint_y=None, height=40)
        contenido.add_widget(cerrar)
        popup = Popup(title=titulo, content=contenido, size_hint=(0.6, 0.4))
        cerrar.bind(on_release=popup.dismiss) # type: ignore
        popup.open()

    def abrir_panel_agregar(self):
        miembro_form = self.manager.get_screen("miembro_form")
        miembro_form.miembro = {}  # Vacío para agregar
        self.manager.current = "miembro_form"

    def abrir_panel_editar(self, miembro):
        miembro_form = self.manager.get_screen("miembro_form")
        miembro_form.miembro = miembro.copy()  # Pasa los datos para editar
        self.manager.current = "miembro_form"

    def exportar_excel(self):
        if not self.miembros_filtrados:
            MDSnackbar(MDLabel(text="No hay miembros para exportar.")).open()
            return

        # Prepara los datos
        df = pd.DataFrame(self.miembros_filtrados)
        # Opcional: renombra columnas para que sean más legibles
        df = df.rename(columns={
            "ID": "ID",
            "DNI": "DNI",
            "Nombre": "Nombre",
            "Apellido_Paterno": "Apellido Paterno",
            "Apellido_Materno": "Apellido Materno",
            "Correo": "Correo",
            "Dirección": "Dirección",
            "Teléfono": "Teléfono"
        })

        # Define la ruta de guardado
        import os
        if platform == "win":
            ruta = os.path.join(os.path.expanduser("~"), "Downloads", "miembros_exportados.xlsx")
        else:
            ruta = os.path.join(os.path.expanduser("~"), "Downloads", "miembros_exportados.xlsx")

        try:
            df.to_excel(ruta, index=False)
            MDSnackbar(MDLabel(text=f"Exportado a {ruta}")).open()
        except Exception as e:
            print("Error al exportar:", e)
            MDSnackbar(MDLabel(text="Error al exportar a Excel")).open()

class MiembroForm(BoxLayout):
    def __init__(self, miembro=None, **kwargs):
        super().__init__(orientation="vertical", spacing=10, padding=10, **kwargs)
        self.campos = {}
        campos = [
            ("Nombre", "Nombre(s)"),
            ("Apellido_Paterno", "Apellido Paterno"),
            ("Apellido_Materno", "Apellido Materno"),
            ("DNI", "DNI"),
            ("Correo", "Correo electrónico"),
            ("Dirección", "Dirección"),
            ("Teléfono", "Teléfono"),
        ]
        for key, hint in campos:
            tf = MDTextField(hint_text=hint, text=miembro[key] if miembro else "")
            self.campos[key] = tf
            self.add_widget(tf)

    def obtener_datos(self):
        return {k: v.text.strip() for k, v in self.campos.items()}