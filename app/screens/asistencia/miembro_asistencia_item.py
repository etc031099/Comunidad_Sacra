from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ObjectProperty

class MiembroAsistenciaItem(MDCard):
    text = StringProperty("")
    secondary_text = StringProperty("")
    presente = BooleanProperty(False)
    miembro_id = NumericProperty(0)
    on_check_change = ObjectProperty(None)
    estado_asistencia = StringProperty("Sin registrar")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.padding = (16, 8)
        self.spacing = 10
        self.elevation = 1
        self.ripple_behavior = True
        self.size_hint_y = None
        self.height = "72dp"
        self.radius = [8, 8, 8, 8]
        self.bind(estado_asistencia=self.actualizar_color)

    def actualizar_color(self, *args):
        if self.estado_asistencia == "Presente":
            self.md_bg_color = (0.2, 0.8, 0.2, 0.2)
        elif self.estado_asistencia == "Ausente":
            self.md_bg_color = (0.8, 0.2, 0.2, 0.2)
        elif self.estado_asistencia == "Tardanza":
            self.md_bg_color = (0.8, 0.6, 0.0, 0.2)
        elif self.estado_asistencia == "Justificado":
            self.md_bg_color = (0.2, 0.6, 0.8, 0.2)
        else:
            self.md_bg_color = (0.95, 0.95, 0.95, 1) 