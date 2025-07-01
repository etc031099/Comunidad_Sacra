from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import ListProperty, StringProperty, BooleanProperty, ObjectProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.tooltip import MDTooltip
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.scrollview import MDScrollView
from kivy.animation import Animation
from .faenas_db import obtener_faenas, eliminar_faena_completa
from kivymd.uix.list import MDList
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivymd.uix.widget import Widget
from kivy.metrics import dp

class IconButtonTooltip(MDIconButton, MDTooltip):
    pass

class FaenaCard(MDCard):
    hovered = BooleanProperty(False)
    text = StringProperty("")
    secondary_text = StringProperty("")
    faena_data = ObjectProperty(None)
    
    def on_enter(self, *args):
        """Cuando el mouse entra en la tarjeta"""
        self.hovered = True
        Animation(
            md_bg_color=(0.95, 0.95, 1, 1),  # Color azul muy claro
            duration=0.2
        ).start(self)

    def on_leave(self, *args):
        """Cuando el mouse sale de la tarjeta"""
        self.hovered = False
        Animation(
            md_bg_color=(1, 1, 1, 1),  # Color blanco original
            duration=0.2
        ).start(self)

class FaenasScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None  # Inicializar el atributo dialog
        self.dialog_eliminar = None
        
    faenas = ListProperty([])
    faenas_filtradas = ListProperty([])

    def on_pre_enter(self):
        self.cargar_faenas()

    def cargar_faenas(self):
        self.faenas = obtener_faenas()
        self.faenas_filtradas = self.faenas[:]
        self.actualizar_lista_faenas()

    def filtrar_faenas(self, texto):
        texto = texto.lower()
        self.faenas_filtradas = [
            f for f in self.faenas
            if texto in f["nombre"].lower() or texto in (f["tipo"] or "").lower() or texto in (f["ubicacion"] or "").lower()
        ]
        self.actualizar_lista_faenas()

    def actualizar_lista_faenas(self):
        lista = self.ids.lista_faenas
        lista.clear_widgets()

        if not self.faenas_filtradas:
            # Mostrar mensaje si no hay faenas
            card = FaenaCard(
                orientation="horizontal",
                padding=(16, 8),
                size_hint_y=None,
                height="72dp", # Altura predeterminada para el mensaje
                md_bg_color=(0.95, 0.95, 0.95, 1), # Fondo neutro
                elevation=1,
                radius=[8, 8, 8, 8],
                ripple_behavior=False, # Sin efecto ripple para el mensaje
                text="[b]No hay faenas registradas.[/b]",
                secondary_text="Presiona 'Nueva Faena' para agregar una."
            )
            lista.add_widget(card)
            self.ids.contador_faenas.text = "Total faenas: 0"
            return

        for faena in self.faenas_filtradas:
            card = FaenaCard(
                orientation="horizontal",
                padding=(16, 8),
                size_hint_y=None,
                height="60dp",
                md_bg_color=(1, 1, 1, 1),
                elevation=0,
                radius=[8, 8, 8, 8],
                line_color=(0.7, 0.7, 0.7, 0.2),
                line_width=0.5,
                ripple_behavior=True, # Habilitar efecto ripple al hacer clic
                text=f"[b]{faena['nombre']}[/b] ({faena['tipo']})",
                secondary_text=f"{faena['fecha_inicio']} - {faena['fecha_fin']}",
                faena_data=faena
            )
            lista.add_widget(card)
        # Actualiza el contador
        self.ids.contador_faenas.text = f"Total faenas: {len(self.faenas_filtradas)}"

    def ir_a_faena_form(self):
        faena_form_screen = self.manager.get_screen('faena_form')
        faena_form_screen.faena = {}
        self.manager.current = "faena_form"

    def ir_a_faena_form_editar(self, faena):
        faena_form_screen = self.manager.get_screen('faena_form')
        faena_form_screen.faena = faena
        self.manager.current = "faena_form"

    def asignar_miembros(self, faena):
        print(f"Asignando miembros a faena: {faena['nombre']}")
        # Implementar la lógica de asignación de miembros

    def eliminar_faena(self, faena):
        """Muestra diálogo de confirmación para eliminar faena"""
        self.faena_a_eliminar = faena  # Guardar referencia de la faena
        
        # Se crea el diálogo y se asigna a una variable local para poder referenciarlo
        # de forma segura en la lambda del botón "Cancelar".
        dialog = MDDialog(
            title="Confirmar eliminación",
            text=f"¿Está seguro que desea eliminar la faena '{faena['nombre']}'?\n¡Esta acción es irreversible y eliminará todas las asistencias, penalizaciones, asignaciones y datos relacionados con esta faena!",
            buttons=[
                MDFlatButton(
                    text="Cancelar",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Eliminar",
                    md_bg_color=self.theme_cls.error_color,
                    on_release=lambda x: self.confirmar_eliminacion()
                ),
            ]
        )
        self.dialog_eliminar = dialog
        self.dialog_eliminar.open()

    def confirmar_eliminacion(self):
        """Ejecuta la eliminación de la faena y todos sus datos relacionados en una transacción."""
        if not self.faena_a_eliminar:
            return

        id_faena = self.faena_a_eliminar['idFaena']
        
        if eliminar_faena_completa(id_faena):
            snackbar = MDSnackbar(
                MDLabel(
                    text="Faena eliminada correctamente",
                    theme_text_color="Custom",
                    text_color="white",
                ),
                md_bg_color=(0.2, 0.7, 0.2, 1), # Verde para éxito
                size_hint_x=0.8,
                pos_hint={"center_x": 0.5}
            )
            snackbar.open()
        else:
            snackbar = MDSnackbar(
                MDLabel(
                    text="Error al eliminar la faena. Revise las dependencias.",
                    theme_text_color="Custom",
                    text_color="white",
                ),
                md_bg_color=(0.9, 0.2, 0.2, 1), # Rojo para error
                size_hint_x=0.8,
                pos_hint={"center_x": 0.5}
            )
            snackbar.open()

        if self.dialog_eliminar is not None:
            self.dialog_eliminar.dismiss()
        self.faena_a_eliminar = None # Limpiar referencia
        
        self.cargar_faenas()

    def mostrar_detalles_faena(self, faena):
        if hasattr(self, 'dialog') and self.dialog and self.dialog.is_open:
            self.dialog.dismiss()
            
        # Crear el diálogo
        self.dialog = MDDialog(
            title="Detalles de la Faena",
            type="custom",
            content_cls=ContenidoDialog(faena),
            size_hint=(0.8, 0.8),
            # Agregar estas propiedades para mejorar el aspecto visual
            md_bg_color=[1, 1, 1, 1],  # Fondo blanco
            overlay_color=[0, 0, 0, 0.3],  # Fondo semi-transparente
            radius=[20, 20, 20, 20],  # Bordes redondeados
            elevation=0,  # Quitar sombra predeterminada
            buttons=[
                MDFlatButton(
                    text="Cerrar",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()

    def ir_a_asignar_faena(self, faena):
        asignar_screen = self.manager.get_screen('asignar_faena')
        asignar_screen.cargar_faena(faena)
        self.manager.current = "asignar_faena"

    def on_leave(self):
        """Método que se llama cuando se sale de la pantalla"""
        if hasattr(self, 'dialog') and self.dialog:
            self.dialog.dismiss()
            self.dialog = None

class ContenidoDialog(MDBoxLayout):
    def __init__(self, faena, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = 15
        self.size_hint_y = None
        self.height = 450  # Altura fija para el scroll
        self.padding = [10, 10, 10, 10]  # Padding superior e inferior

        # Contenedor principal con scroll
        scroll = MDScrollView(
            do_scroll_x = False,  # Solo scroll vertical
            size_hint = (1, 1)
        )

        contenido_principal = MDBoxLayout(
            orientation="vertical",
            spacing=15,
            size_hint_y=None,
            padding=[10, 10, 10, 10]
        )
        contenido_principal.bind(
            minimum_height=contenido_principal.setter('height')
        )

        # Colores personalizados
        color_fondo_cards = [0.98, 0.98, 1, 1]  # Azul muy claro
        color_borde = [0.7, 0.7, 0.8, 1]    # Gris azulado para sombras

        card_config = {
            "elevation": 1,
            "radius": [10, 10, 10, 10],
            "md_bg_color": color_fondo_cards,
            "shadow_softness": 2,
            "shadow_offset": (0, 1),
            "line_color": color_borde,
            "line_width": 1.1,  # Ancho del borde aumentado
            "size_hint": (1, None),
            "ripple_behavior": True  # Efecto de ondulación al tocar
        }

        # Información básica
        info_card = MDCard(
            orientation="vertical",
            padding=[15, 15, 15, 15],
            spacing=8,
            height="180dp",
            **card_config
        )

        campos = [
            ("Nombre", faena['nombre']),
            ("Tipo", faena['tipo']),
        ]
        
        # Agregar tipo específico según la faena
        if faena['tipo'].lower() == 'ordinaria':
            campos.append(("Tipo de Jornada", faena['tipoJornada'] or 'No especificado'))
        elif faena['tipo'].lower() == 'extraordinaria':
            campos.append(("Motivo Extra", faena['motivoExtra'] or 'No especificado'))
            
        campos.extend([
            ("Estado", faena['estado']),
            ("Ubicación", faena['ubicacion'] or 'No especificada')
        ])

        for titulo, valor in campos:
            info_card.add_widget(MDLabel(
                text=f"[b]{titulo}:[/b] {valor}",
                markup=True,
                theme_text_color="Secondary",
                size_hint_y=None,
                height="30dp"
            ))

        contenido_principal.add_widget(info_card)

        # Fechas
        fecha_card = MDCard(
            orientation="vertical",
            padding=[15, 15, 15, 15],
            spacing=8,
            height="100dp",
            **card_config
        )

        fecha_card.add_widget(MDLabel(
            text=f"[b]Fecha inicio:[/b] {faena['fecha_inicio']}",
            markup=True,
            theme_text_color="Secondary"
        ))
        fecha_card.add_widget(MDLabel(
            text=f"[b]Fecha fin:[/b] {faena['fecha_fin']}",
            markup=True,
            theme_text_color="Secondary"
        ))
        contenido_principal.add_widget(fecha_card)

        # Descripción
        desc_card = MDCard(
            orientation="vertical",
            padding=[15, 15, 15, 15],
            spacing=8,
            height="120dp",
            **card_config
        )
        desc_card.add_widget(MDLabel(
            text="[b]Descripción:[/b]",
            markup=True,
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp"
        ))
        desc_card.add_widget(MDLabel(
            text=faena['descripcion'] or "Sin descripción",
            theme_text_color="Secondary"
        ))
        contenido_principal.add_widget(desc_card)

        scroll.add_widget(contenido_principal)
        self.add_widget(scroll)
