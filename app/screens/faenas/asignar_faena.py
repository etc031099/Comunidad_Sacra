from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDList
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from app.screens.miembros.miembro_item import MiembroItem
from kivy.properties import ObjectProperty, ListProperty, BooleanProperty, NumericProperty
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from .asignar_faena_db import (
    obtener_miembros_con_estado,
    asignar_miembro_a_faena,
    desasignar_miembro_de_faena,
    esta_miembro_asignado
)

class AsignarFaenaScreen(MDScreen):
    faena = ObjectProperty(None)
    miembros = ListProperty([])
    miembros_filtrados = ListProperty([])
    chip_activo = BooleanProperty(False)

    FILTRO_ASIGNADOS = 0    # Mostrar solo asignados
    FILTRO_NO_ASIGNADOS = 1 # Mostrar solo no asignados
    FILTRO_TODOS = 2        # Mostrar todos
    
    estado_filtro = NumericProperty(FILTRO_TODOS)  # Estado inicial: mostrar todos

    def cargar_faena(self, faena):
        self.faena = faena
        self.cargar_miembros()

    def cargar_miembros(self):
        if self.faena:
            self.miembros = obtener_miembros_con_estado(self.faena['idFaena'])
            self.miembros_filtrados = self.miembros[:]
            self.actualizar_lista_miembros()

    def filtrar_miembros(self, texto="", ubicacion="", estado_asignacion=None):
        texto = texto.lower()
        self.miembros_filtrados = [
            m for m in self.miembros
            if (texto in m["Nombre"].lower() or texto in m["DNI"].lower()) and
               (not ubicacion or ubicacion.lower() in m["Direccion"].lower()) and
               (estado_asignacion is None or m["asignado"] == estado_asignacion)
        ]
        self.actualizar_lista_miembros()

    def actualizar_lista_miembros(self):
        self.ids.rv_miembros.data = [
            {
                'text': miembro['Nombre'],
                'secondary_text': f"DNI: {miembro['DNI']} - {miembro['Direccion']}",
                'asignado': bool(miembro['asignado']),
                'miembro_id': miembro['ID'],
                'on_release': lambda mid=miembro['ID']: self.toggle_asignacion(mid)
            } for miembro in self.miembros_filtrados
        ]

    def toggle_asignacion(self, miembro_id):
        if self.faena:
            if esta_miembro_asignado(self.faena['idFaena'], miembro_id):
                desasignar_miembro_de_faena(self.faena['idFaena'], miembro_id)
            else:
                asignar_miembro_a_faena(self.faena['idFaena'], miembro_id)
            self.cargar_miembros()
        self.actualizar_contador_seleccionados()

    def actualizar_contador_seleccionados(self):
        total_asignados = sum(1 for m in self.miembros_filtrados if m['asignado'])
        self.ids.contador_seleccionados.text = f"{total_asignados} miembros asignados"

    def confirmar_asignaciones(self):
        miembros_asignados = [m for m in self.miembros_filtrados if m['asignado']]
        if not miembros_asignados:
            snackbar = MDSnackbar(
                MDLabel(
                    text="No hay miembros asignados a la faena",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()
            return
        contenido = "\n".join([
            f"• {m['Nombre']}" for m in miembros_asignados
        ])
        self.dialog_confirmacion = MDDialog(
            title="Confirmar Asignaciones",
            text=f"Se han asignado {len(miembros_asignados)} miembros a la faena '{self.faena['nombre']}':\n\n{contenido}",
            buttons=[
                MDFlatButton(
                    text="Cancelar",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.dialog_confirmacion.dismiss()
                ),
                MDRaisedButton(
                    text="Confirmar",
                    theme_text_color="Custom",
                    text_color="white",
                    on_release=lambda x: self.finalizar_asignaciones()
                )
            ]
        )
        self.dialog_confirmacion.open()

    def finalizar_asignaciones(self):
        self.dialog_confirmacion.dismiss()
        snackbar = MDSnackbar(
            MDLabel(
                text="Asignaciones guardadas correctamente",
                theme_text_color="Custom",
                text_color="white",
            )
        )
        snackbar.open()
        self.manager.current = 'faenas'

    def on_enter(self):
        self.actualizar_contador_seleccionados()

    def toggle_filtro_asignados(self):
        self.estado_filtro = (self.estado_filtro + 1) % 3
        estado_asignacion = None
        if self.estado_filtro == self.FILTRO_ASIGNADOS:
            estado_asignacion = True
        elif self.estado_filtro == self.FILTRO_NO_ASIGNADOS:
            estado_asignacion = False
        self.filtrar_miembros(
            self.ids.busqueda.text,
            self.ids.ubicacion.text,
            estado_asignacion
        )

    def get_estado_filtro_texto(self):
        if self.estado_filtro == self.FILTRO_ASIGNADOS:
            return "Ver Asignados"
        elif self.estado_filtro == self.FILTRO_NO_ASIGNADOS:
            return "Ver No Asignados"
        else:
            return "Ver Todos"

