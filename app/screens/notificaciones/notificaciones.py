from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.snackbar import MDSnackbar
from kivy.metrics import dp
from datetime import datetime, timedelta
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivymd.uix.list import TwoLineAvatarIconListItem, ILeftBodyTouch, IconLeftWidget
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivy.animation import Animation
from kivy.clock import Clock
from kivymd.uix.spinner import MDSpinner
from .notificaciones_db import (
    obtener_eventos_proximos, obtener_penalizaciones_pendientes,
    obtener_miembros_con_inasistencias, obtener_detalles_inasistencias_miembro
)

class ContenidoInasistencias(MDBoxLayout):
    def __init__(self, id_miembro, fecha_limite, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(6)
        self.padding = dp(10)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        self.id_miembro = id_miembro
        self.fecha_limite = fecha_limite
        self.cargar_detalles()

    def cargar_detalles(self):
        try:
            faltas_detalle = obtener_detalles_inasistencias_miembro(self.id_miembro, self.fecha_limite)

            if not faltas_detalle:
                self.add_widget(MDLabel(text="Sin detalles de inasistencias.", theme_text_color="Secondary"))
            else:
                for titulo, fecha in faltas_detalle:
                    fecha_str = fecha.strftime('%d/%m/%Y') if fecha else 'N/A'
                    item = TwoLineAvatarIconListItem(
                        text=f"Reunión: {titulo}",
                        secondary_text=f"Fecha: {fecha_str}",
                        theme_text_color="Primary",
                        secondary_theme_text_color="Secondary",
                        _no_ripple_effect=True
                    )
                    item.add_widget(IconLeftWidget(
                        icon="calendar-remove"
                    ))
                    self.add_widget(item)

                ver_historial_btn = MDRaisedButton(
                    text="Ver Ficha del Miembro",
                    on_release=self.ver_historial_miembro,
                    pos_hint={"center_x": 0.5},
                    size_hint_x=0.8,
                    md_bg_color= (0.1, 0.4, 0.7, 1)
                )
                self.add_widget(ver_historial_btn)

        except Exception as e:
            self.add_widget(MDLabel(text=f"Error al cargar detalles: {e}", theme_text_color="Error"))

    def ver_historial_miembro(self, *args):
        app = MDApp.get_running_app()
        if app and app.root and app.root.has_screen('historial_miembro'):
            historial_screen = app.root.get_screen('historial_miembro')
            historial_screen.previous_screen = 'notificaciones'
            historial_screen.id_miembro_seleccionado = self.id_miembro
            app.root.current = 'historial_miembro'
        else:
            print("La pantalla 'historial_miembro' no existe.")

class NotificacionesScreen(MDScreen):
    def add_widget_with_animation(self, box, widget, index):
        """Añade un widget a un layout con una animación de fundido y un retraso."""
        widget.opacity = 0
        box.add_widget(widget)
        
        delay = index * 0.05  # Crea un efecto escalonado
        anim = Animation(opacity=1, duration=0.3, t='out_quad')
        
        Clock.schedule_once(lambda dt: anim.start(widget), delay)

    def on_enter(self):
        self.cargar_todas_las_notificaciones()

    def create_card_container(self, title):
        """Crea una tarjeta contenedora para un tipo de notificación."""
        card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            adaptive_height=True,
            padding=dp(15),
            spacing=dp(10),
            md_bg_color=(1, 1, 1, 1),
            radius=[15, 15, 15, 15]
        )
        title_label = MDLabel(
            text=title,
            font_style="H6",
            size_hint_y=None,
            adaptive_height=True,
            bold=True
        )
        content_box = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            adaptive_height=True
        )
        card.add_widget(title_label)
        card.add_widget(content_box)
        return card, content_box

    def cargar_todas_las_notificaciones(self):
        main_box = self.ids.main_content_box
        main_box.clear_widgets()

        # --- Eventos ---
        eventos_card, eventos_box = self.create_card_container("Eventos Próximos (Siguientes 7 días)")
        eventos_box.add_widget(MDSpinner(size_hint=(None, None), size=(dp(46), dp(46)), pos_hint={'center_x': 0.5}))
        main_box.add_widget(eventos_card)
        Clock.schedule_once(lambda dt: self._fetch_eventos_proximos(eventos_box), 0.1)

        # --- Penalizaciones ---
        penalizaciones_card, penalizaciones_box = self.create_card_container("Nuevas Penalizaciones Pendientes")
        penalizaciones_box.add_widget(MDSpinner(size_hint=(None, None), size=(dp(46), dp(46)), pos_hint={'center_x': 0.5}))
        main_box.add_widget(penalizaciones_card)
        Clock.schedule_once(lambda dt: self._fetch_nuevas_penalizaciones(penalizaciones_box), 0.1)
        
        # --- Inasistencias ---
        inasistencias_card, inasistencias_box = self.create_card_container("Miembros con Inasistencias Recientes")
        inasistencias_box.add_widget(MDSpinner(size_hint=(None, None), size=(dp(46), dp(46)), pos_hint={'center_x': 0.5}))
        main_box.add_widget(inasistencias_card)
        Clock.schedule_once(lambda dt: self._fetch_muchas_inasistencias(inasistencias_box), 0.1)

    def _fetch_eventos_proximos(self, box):
        box.clear_widgets()
        try:
            eventos = obtener_eventos_proximos()

            if not eventos:
                label = MDLabel(text="No hay eventos próximos.", halign="center", theme_text_color="Secondary")
                self.add_widget_with_animation(box, label, 0)
            else:
                for i, evento in enumerate(eventos):
                    icono = "calendar-clock" if evento['tipo'] == 'Reunión' else "shovel"
                    item = TwoLineAvatarIconListItem(
                        text=f"{evento['tipo']}: {evento['nombre']}",
                        secondary_text=f"Fecha: {evento['fecha'].strftime('%d/%m/%Y')}",
                    )
                    item.add_widget(IconLeftWidget(icon=icono))
                    self.add_widget_with_animation(box, item, i)
                    
        except Exception as e:
            label = MDLabel(text=f"Error al cargar eventos: {e}", theme_text_color="Error")
            self.add_widget_with_animation(box, label, 0)

    def _fetch_nuevas_penalizaciones(self, box):
        box.clear_widgets()
        try:
            penalizaciones = obtener_penalizaciones_pendientes()
            
            if not penalizaciones:
                label = MDLabel(text="No hay penalizaciones pendientes.", halign="center", theme_text_color="Secondary")
                self.add_widget_with_animation(box, label, 0)
            else:
                for i, p in enumerate(penalizaciones):
                    nombre, tipo, valor, fecha = p
                    item = TwoLineAvatarIconListItem(
                        text=f"{nombre}",
                        secondary_text=f"Tipo: {tipo} | Valor: {valor} | Fecha: {fecha.strftime('%d/%m/%Y')}",
                    )
                    item.add_widget(IconLeftWidget(icon="cash-remove"))
                    self.add_widget_with_animation(box, item, i)

        except Exception as e:
            label = MDLabel(text=f"Error al cargar penalizaciones: {e}", theme_text_color="Error")
            self.add_widget_with_animation(box, label, 0)

    def _fetch_muchas_inasistencias(self, box):
        box.clear_widgets()
        try:
            resultados = obtener_miembros_con_inasistencias()
            
            if not resultados:
                label = MDLabel(
                    text="No hay miembros con más de 3 inasistencias.",
                    halign="center",
                    theme_text_color="Secondary"
                )
                self.add_widget_with_animation(box, label, 0)
            else:
                fecha_limite = (datetime.now() - timedelta(days=30)).date()
                for i, miembro in enumerate(resultados):
                    id_miembro, nombre, faltas, ultima_falta = miembro
                    header_text = f"{nombre} | Inasistencias: {faltas} | Última: {ultima_falta.strftime('%d/%m/%Y') if ultima_falta else 'N/A'}"
                    content = ContenidoInasistencias(id_miembro=id_miembro, fecha_limite=fecha_limite)
                    panel = MDExpansionPanel(
                        icon="account-alert",
                        panel_cls=MDExpansionPanelOneLine(text=header_text),
                        content=content
                    )
                    self.add_widget_with_animation(box, panel, i)
                    
        except Exception as e:
            label = MDLabel(
                text=f"Error al cargar inasistencias: {e}",
                theme_text_color="Error",
                halign="center"
            )
            self.add_widget_with_animation(box, label, 0) 