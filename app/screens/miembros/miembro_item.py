from kivymd.uix.card import MDCard
from kivy.properties import ObjectProperty, BooleanProperty

class MiembroItem(MDCard):
    text = ObjectProperty("")
    secondary_text = ObjectProperty("")
    asignado = BooleanProperty(False)
    miembro_id = ObjectProperty(0)
    on_release = ObjectProperty(None)

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