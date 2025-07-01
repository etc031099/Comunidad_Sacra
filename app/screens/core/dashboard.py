from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.animation import Animation
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from datetime import datetime
from .dashboard_db import calcular_kpis
import threading

class DashboardScreen(MDScreen):
    def on_enter(self):
        """Se ejecuta cuando se entra a la pantalla del dashboard"""
        print("Bienvenido al panel principal.")
        self.mostrar_mensaje_bienvenida()
        self.animar_cards()
        self.poblar_kpis()
        
    def mostrar_mensaje_bienvenida(self):
        """Muestra un mensaje de bienvenida al usuario"""
        try:
            # Obtener la hora actual
            hora_actual = datetime.now().hour
            
            # Determinar el saludo según la hora
            if 5 <= hora_actual < 12:
                saludo = "¡Buenos días!"
            elif 12 <= hora_actual < 18:
                saludo = "¡Buenas tardes!"
            else:
                saludo = "¡Buenas noches!"
                
            mensaje = f"{saludo} Panel de control cargado correctamente"
            
            # Mostrar snackbar con el mensaje (versión corregida)
            snackbar = MDSnackbar(
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.5,
                duration=3
            )
            snackbar.add_widget(
                MDLabel(
                    text=mensaje,
                    theme_text_color="Custom",
                    text_color=[1, 1, 1, 1],
                    halign="center"
                )
            )
            snackbar.open()
            
        except Exception as e:
            print(f"Error al mostrar mensaje de bienvenida: {e}")
    
    def animar_cards(self):
        """Anima las tarjetas del dashboard al cargar"""
        try:
            # Programar animación después de un pequeño delay
            Clock.schedule_once(self._animar_entrada, 0.2)
        except Exception as e:
            print(f"Error en animación: {e}")
    
    def _animar_entrada(self, dt):
        """Ejecuta la animación de entrada de las tarjetas"""
        try:
            # Buscar todas las tarjetas del dashboard
            dashboard_cards = []
            
            def encontrar_cards(widget):
                if hasattr(widget, 'card_title') and widget.card_title:
                    dashboard_cards.append(widget)
                for child in widget.children:
                    encontrar_cards(child)
            
            encontrar_cards(self)
            
            # Animar cada tarjeta con un pequeño delay
            for i, card in enumerate(dashboard_cards):
                # Efecto de escala inicial
                card.scale = 0.8
                card.opacity = 0
                
                # Animación de entrada
                anim = Animation(
                    scale=1.0,
                    opacity=1.0,
                    duration=0.3,
                    transition='out_back'
                )
                
                # Programar la animación con delay
                Clock.schedule_once(
                    lambda dt, c=card, a=anim: a.start(c), 
                    i * 0.1
                )
                
        except Exception as e:
            print(f"Error en animación de entrada: {e}")
    
    def poblar_kpis(self):
        self.ids.dashboard_kpi_section.opacity = 0
        threading.Thread(target=self._hilo_calcular_kpis).start()

    def _hilo_calcular_kpis(self):
        kpis = calcular_kpis()
        Clock.schedule_once(lambda dt: self._callback_poblar_kpis(kpis))

    def _callback_poblar_kpis(self, kpis):
        # Actualizar KPIs en la UI del Dashboard
        self.ids.dashboard_kpi_miembro_mes.text = f"{kpis.get('miembro_del_mes', 'No disponible')}"
        self.ids.dashboard_kpi_asistencia_perfecta.text = f"{kpis.get('asistencia_perfecta', '-')} Miembros"
        self.ids.dashboard_kpi_cero_penalizaciones.text = f"{kpis.get('cero_penalizaciones', '-')} Miembros"

        # Animar la aparición de las tarjetas
        anim = Animation(opacity=1, duration=0.5)
        anim.start(self.ids.dashboard_kpi_section)
    
    def on_leave(self):
        """Se ejecuta cuando se sale de la pantalla del dashboard"""
        print("Saliendo del panel principal...")