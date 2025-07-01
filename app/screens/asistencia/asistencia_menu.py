from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivy.metrics import dp

class AsistenciaMenuScreen(MDScreen):
    def go_to_asistencia_reuniones(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'asistencia'

    def go_to_asistencia_faenas(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'asistencia_faena'

    def go_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'dashboard' 