from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import ListProperty, StringProperty, ObjectProperty, BooleanProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.clock import Clock
import threading
from .reuniones_db import obtener_todas_reuniones, eliminar_reunion_completa

class ReunionCard(MDCard):
    reunion_data = ObjectProperty(None)

class ReunionesScreen(MDScreen):
    reuniones_cache = ListProperty(None, allownone=True)
    texto_busqueda = StringProperty("")
    cargando = BooleanProperty(False)

    def on_enter(self, *args):
        # Si la caché no ha sido creada, la poblamos.
        # Usamos on_enter para asegurar que la transición de pantalla sea fluida.
        if self.reuniones_cache is None:
            Clock.schedule_once(lambda dt: self.poblar_cache())
        else:
            # Si ya existe, simplemente refrescamos la vista actual
            self.filtrar_y_actualizar()

    def poblar_cache(self):
        """Carga TODAS las reuniones en una caché en memoria, en segundo plano."""
        if self.cargando:
            return
        self.cargando = True
        self.ids.spinner.active = True
        self.ids.lista_reuniones.data = []
        threading.Thread(target=self._hilo_poblar_cache).start()

    def _hilo_poblar_cache(self):
        try:
            cache = obtener_todas_reuniones()
            Clock.schedule_once(lambda dt: self._callback_poblar_cache(cache))
        except Exception as e:
            print(f"Error en hilo al poblar caché: {e}")
            Clock.schedule_once(lambda dt: self._callback_poblar_cache([]))

    def _callback_poblar_cache(self, cache):
        self.reuniones_cache = cache
        self.cargando = False
        self.ids.spinner.active = False
        self.filtrar_y_actualizar() # Mostramos la lista completa

    def disparar_busqueda(self, texto):
        """Busca en la caché con un pequeño retraso para no buscar en cada pulsación."""
        self.texto_busqueda = texto.strip().lower()
        Clock.unschedule(self.filtrar_y_actualizar)
        Clock.schedule_once(self.filtrar_y_actualizar, 0.2)

    def filtrar_y_actualizar(self, *args):
        """Filtra la caché y actualiza la data del RecycleView."""
        if self.reuniones_cache is None:
            return
            
        if self.texto_busqueda:
            reuniones_filtradas = [
                r for r in self.reuniones_cache 
                if self.texto_busqueda in r['titulo'].lower() or \
                   self.texto_busqueda in r['descripcion'].lower()
            ]
        else:
            reuniones_filtradas = self.reuniones_cache[:]
        
        self.ids.contador_reuniones.text = f"Total: {len(reuniones_filtradas)}"
        
        # Formatear datos para RecycleView y actualizar
        self.ids.lista_reuniones.data = [{'reunion_data': r} for r in reuniones_filtradas]

        if not reuniones_filtradas:
            # Opcional: mostrar un mensaje de "no encontrado"
            # Por ahora, simplemente la lista estará vacía.
            pass

    def on_leave(self, *args):
        # Opcional: Descomentar si quieres que la caché se refresque cada vez que se sale y entra.
        # self.reuniones_cache = None
        pass

    def eliminar_reunion(self, reunion):
        dialog = MDDialog(
            title="Confirmar eliminación",
            text=f"¿Está seguro de que desea eliminar la reunión '{reunion.get('titulo')}'?\n¡Esta acción es irreversible y eliminará todas las asistencias, penalizaciones y datos relacionados con esta reunión!",
            buttons=[
                MDFlatButton(
                    text="CANCELAR", 
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="ELIMINAR", 
                    md_bg_color=self.theme_cls.error_color,
                    on_release=lambda x: (
                        self._hilo_eliminar(reunion),
                        dialog.dismiss()
                    )
                )
            ]
        )
        dialog.open()

    def _hilo_eliminar(self, reunion):
        threading.Thread(target=self._ejecutar_eliminar, args=(reunion,)).start()

    def _ejecutar_eliminar(self, reunion):
        try:
            id_reunion = reunion['id_reunion']
            exito = eliminar_reunion_completa(id_reunion)
            Clock.schedule_once(lambda dt: self._callback_eliminar(reunion, exito))
        except Exception as e:
            print(f"Error en hilo al eliminar reunión: {e}")
            Clock.schedule_once(lambda dt: self._callback_eliminar(reunion, False))
            
    def _callback_eliminar(self, reunion_eliminada, exito):
        if exito:
            snackbar = MDSnackbar(
                MDLabel(
                    text="Reunión eliminada correctamente",
                    theme_text_color="Custom",
                    text_color="white",
                ),
                md_bg_color=(0.2, 0.7, 0.2, 1), # Verde para éxito
                size_hint_x=0.8,
                pos_hint={"center_x": 0.5}
            )
            snackbar.open()
            
            if self.reuniones_cache is not None:
                self.reuniones_cache = [r for r in self.reuniones_cache if r['id_reunion'] != reunion_eliminada['id_reunion']]
            
            # Refrescar la vista
            self.filtrar_y_actualizar()
        else:
            snackbar = MDSnackbar(
                MDLabel(
                    text="Error al eliminar la reunión. Revise las dependencias.",
                    theme_text_color="Custom",
                    text_color="white",
                ),
                md_bg_color=(0.9, 0.2, 0.2, 1), # Rojo para error
                size_hint_x=0.8,
                pos_hint={"center_x": 0.5}
            )
            snackbar.open()

    def ir_a_reunion_form(self):
        # Forzar recarga la próxima vez que se entre
        self.reuniones_cache = None
        reunion_form_screen = self.manager.get_screen('crear_reunion')
        reunion_form_screen.preparar_modo_creacion()
        self.manager.current = "crear_reunion"

    def ir_a_reunion_form_editar(self, reunion):
        # Forzar recarga la próxima vez que se entre
        self.reuniones_cache = None
        reunion_form_screen = self.manager.get_screen('crear_reunion')
        reunion_form_screen.modo_edicion = True
        reunion_form_screen.reunion_actual = reunion
        self.manager.current = "crear_reunion"

    def mostrar_detalles_reunion(self, reunion):
        descripcion = reunion.get('descripcion', 'Sin descripción')
        dialog = MDDialog(
            title="Detalles de la Reunión",
            text=f"Título: {reunion['titulo']}\nFecha: {reunion['fecha']}\nHora: {reunion['hora_inicio']}\nDescripción: {descripcion}",
            buttons=[MDFlatButton(text="Cerrar", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open() 