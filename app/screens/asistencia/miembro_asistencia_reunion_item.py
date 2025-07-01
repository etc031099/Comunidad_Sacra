from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ObjectProperty

class MiembroAsistenciaReunionItem(MDCard):
    text = StringProperty("")
    secondary_text = StringProperty("")
    presente = BooleanProperty(False)
    miembro_id = NumericProperty(0)
    on_check_change = ObjectProperty(None)
    estado_asistencia = StringProperty("Sin registrar")

    def __init__(self, **kwargs):
        super().__init__(**kwargs) 