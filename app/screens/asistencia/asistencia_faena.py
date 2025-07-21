from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty, ListProperty, BooleanProperty, NumericProperty, StringProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.list import OneLineAvatarIconListItem, OneLineListItem
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDIcon
from kivy.metrics import dp
from datetime import datetime, time, timedelta, date
import traceback
from .miembro_asistencia_item import MiembroAsistenciaItem
from .asistencia_faena_db import (
    obtener_faenas,
    obtener_miembros_asignados,
    obtener_asistencias_fecha,
    guardar_justificacion,
    marcar_tardanza,
    marcar_estado_asistencia
)

def format_date_safely(d, fmt='%d/%m/%Y'):
    if isinstance(d, datetime) or isinstance(d, date):
        return d.strftime(fmt)
    return str(d) if d else ''

class AsistenciaFaenaScreen(MDScreen):
    faenas_data = ListProperty([])
    miembros_asignados = ListProperty([])
    selected_faena_id = NumericProperty(None, allownone=True)
    selected_faena = ObjectProperty(None, allownone=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.dropdown_menu = None
        self.miembros_seleccionados = {}  # Inicialización para evitar AttributeError
        
    def on_enter(self):
        """Se ejecuta cuando se entra a la pantalla"""
        self.faenas_data = obtener_faenas()
        self.crear_dropdown_menu()
    
    def cargar_faenas(self):
        """Carga las faenas activas en el dropdown"""
        self.faenas_data = obtener_faenas()
        self.crear_dropdown_menu()
    
    def crear_dropdown_menu(self):
        """Crea el menú dropdown con las faenas"""
        if not self.faenas_data:
            print("No hay faenas disponibles")
            snackbar = MDSnackbar(
                MDLabel(
                    text="No hay faenas disponibles",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()
            return
            
        menu_items = []
        for faena in self.faenas_data:
            menu_items.append({
                "text": f"{faena['nombre']} - {faena['tipo']}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=faena['idFaena']: self.seleccionar_faena(x),
            })
        
        self.dropdown_menu = MDDropdownMenu(
            caller=self.ids.dropdown_faena,
            items=menu_items,
            width_mult=4,
        )
    
    def abrir_dropdown(self):
        """Abre el dropdown menu"""
        if self.dropdown_menu:
            self.dropdown_menu.open()
        else:
            print("Dropdown menu no creado, recargando faenas...")
            self.cargar_faenas()
    
    def abrir_calendario_asistencia(self):
        """Abre el calendario para seleccionar fecha de asistencia"""
        if not self.selected_faena:
            snackbar = MDSnackbar(
                MDLabel(
                    text="Seleccione una faena primero",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()
            return
            
        # Obtener fechas de la faena
        fecha_inicio = self.selected_faena['fecha_inicio']
        fecha_fin = self.selected_faena['fecha_fin']
        
        if not fecha_inicio or not fecha_fin:
            snackbar = MDSnackbar(
                MDLabel(
                    text="La faena no tiene fechas válidas",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()
            return
        
        # Verificar que las fechas sean válidas
        try:
            # Convertir a objetos date si son strings
            if isinstance(fecha_inicio, str):
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            if isinstance(fecha_fin, str):
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            
            # Verificar que fecha_inicio <= fecha_fin
            if fecha_inicio > fecha_fin:
                snackbar = MDSnackbar(
                    MDLabel(
                        text="Error: La fecha de inicio es posterior a la fecha de fin",
                        theme_text_color="Custom",
                        text_color="white",
                    )
                )
                snackbar.open()
                return
                
        except Exception as e:
            print(f"Error al procesar fechas: {e}")
            snackbar = MDSnackbar(
                MDLabel(
                    text="Error al procesar las fechas de la faena",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()
            return
        
        # Crear calendario con rango de fechas de la faena
        from kivymd.uix.pickers import MDDatePicker
        
        date_picker = MDDatePicker(
            min_date=fecha_inicio,
            max_date=fecha_fin,
            title="Seleccionar fecha de asistencia"
        )
        date_picker.bind(on_save=self.on_fecha_asistencia_seleccionada)
        date_picker.open()
        
        # Mostrar información del rango disponible
        fecha_inicio_str = format_date_safely(fecha_inicio)
        fecha_fin_str = format_date_safely(fecha_fin)
        
        snackbar = MDSnackbar(
            MDLabel(
                text=f"Rango disponible: {fecha_inicio_str} - {fecha_fin_str}",
                theme_text_color="Custom",
                text_color="white",
            )
        )
        snackbar.open()

    def on_fecha_asistencia_seleccionada(self, instance, value, date_range):
        """Se ejecuta cuando se selecciona una fecha de asistencia"""
        if not self.selected_faena:
            return
            
        # Obtener fechas de la faena para validación
        fecha_inicio = self.selected_faena['fecha_inicio']
        fecha_fin = self.selected_faena['fecha_fin']
        
        # Convertir fechas si son strings
        try:
            if isinstance(fecha_inicio, str):
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            if isinstance(fecha_fin, str):
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except:
            pass
        
        # Validar que la fecha seleccionada esté dentro del rango
        if fecha_inicio and fecha_fin:
            if value < fecha_inicio or value > fecha_fin:
                fecha_inicio_str = format_date_safely(fecha_inicio)
                fecha_fin_str = format_date_safely(fecha_fin)
                
                snackbar = MDSnackbar(
                    MDLabel(
                        text=f"La fecha seleccionada debe estar entre {fecha_inicio_str} y {fecha_fin_str}",
                        theme_text_color="Custom",
                        text_color="white",
                    )
                )
                snackbar.open()
                return
        
        self.fecha_seleccionada = value
        self.ids.input_fecha_asistencia.text = value.strftime('%d/%m/%Y')
        
        # Cargar asistencias para la fecha seleccionada
        self.cargar_asistencias_fecha(value)
        
        # Mostrar mensaje de confirmación
        snackbar = MDSnackbar(
            MDLabel(
                text=f"Asistencias cargadas para {format_date_safely(value)}",
                theme_text_color="Custom",
                text_color="white",
            )
        )
        snackbar.open()

    def seleccionar_faena(self, faena_id):
        """Selecciona una faena y carga los miembros asignados"""
        print(f"Seleccionando faena ID: {faena_id}")
        self.selected_faena_id = faena_id
        
        # Cerrar el dropdown
        if self.dropdown_menu:
            self.dropdown_menu.dismiss()
        
        # Encontrar la faena seleccionada
        self.selected_faena = None
        for faena in self.faenas_data:
            if faena['idFaena'] == faena_id:
                self.selected_faena = faena
                break
        
        if self.selected_faena:
            # Actualizar la información de la faena
            self.ids.dropdown_faena.text = f"{self.selected_faena['nombre']} - {self.selected_faena['tipo']}"
            self.ids.info_faena.text = f"Descripción: {self.selected_faena['descripcion'] or 'Sin descripción'}"
            self.ids.info_ubicacion.text = f"Ubicación: {self.selected_faena['ubicacion'] or 'No especificada'}"
            
            # Formatear fechas de forma segura
            fecha_inicio_str = format_date_safely(self.selected_faena.get('fecha_inicio')) or 'Sin fecha'
            fecha_fin_str = format_date_safely(self.selected_faena.get('fecha_fin')) or 'Sin fecha fin'
                
            self.ids.info_fechas.text = f"Fecha: {fecha_inicio_str} - {fecha_fin_str}"
            
            # Limpiar fecha de asistencia y buscador
            self.ids.input_fecha_asistencia.text = ""
            self.fecha_seleccionada = None
            if 'search_field' in self.ids:
                self.ids.search_field.text = ""
            
            # Cargar miembros asignados
            self.cargar_miembros_asignados()
    
    def cargar_miembros_asignados(self):
        """Carga los miembros asignados a la faena seleccionada"""
        if not self.selected_faena_id:
            print("No hay faena seleccionada")
            return
            
        self.miembros_asignados = obtener_miembros_asignados(self.selected_faena_id)
        self.actualizar_lista_miembros()
        
        if not self.miembros_asignados:
            snackbar = MDSnackbar(
                MDLabel(
                    text="No hay miembros asignados a esta faena",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()
    
    def cargar_asistencias_fecha(self, fecha):
        """Carga las asistencias para una fecha específica"""
        if not self.selected_faena_id:
            return
            
        self.miembros_asignados = obtener_asistencias_fecha(self.selected_faena_id, fecha)
        self.actualizar_lista_miembros()
    
    def actualizar_lista_miembros(self, miembros_a_mostrar=None):
        """Actualiza la lista visual de miembros"""
        if miembros_a_mostrar is None:
            miembros_a_mostrar = self.miembros_asignados

        self.ids.rv_miembros.data = [
            {
                'text': miembro['Nombre'],
                'secondary_text': f"Estado: {miembro['estado_asistencia'] or 'Sin registrar'}",
                'presente': miembro['estado_asistencia'] == 'Presente',
                'miembro_id': miembro['ID'],
                'on_check_change': self.cambiar_estado_miembro,
                'estado_asistencia': miembro['estado_asistencia'] or 'Sin registrar'
            } for miembro in miembros_a_mostrar
        ]
        self.ids.rv_miembros.refresh_from_data()

    def buscar_miembro(self, texto_busqueda=""):
        texto_busqueda = texto_busqueda.lower().strip()
        if not texto_busqueda:
            self.actualizar_lista_miembros()
            return

        miembros_filtrados = [
            miembro for miembro in self.miembros_asignados
            if texto_busqueda in miembro['Nombre'].lower()
        ]
        self.actualizar_lista_miembros(miembros_filtrados)
    
    def cambiar_estado_miembro(self, miembro_id):
        """Cambia el estado de asistencia de un miembro alternando entre 'Presente' y 'Ausente'"""
        if not self.selected_faena_id:
            snackbar = MDSnackbar(MDLabel(text="Primero debe seleccionar una faena."))
            snackbar.open()
            return

        if not hasattr(self, 'fecha_seleccionada') or not self.fecha_seleccionada:
            snackbar = MDSnackbar(MDLabel(text="Por favor, seleccione una fecha de asistencia para continuar."))
            snackbar.open()
            return
            
        print(f"Cambiando estado del miembro ID: {miembro_id}")
        
        miembro_actual = next((m for m in self.miembros_asignados if m['ID'] == miembro_id), None)
        if not miembro_actual:
            return
        
        estado_actual = miembro_actual['estado_asistencia'] or 'Sin registrar'
        
        # Alternar entre 'Presente' y 'Ausente'
        if estado_actual == 'Presente':
            nuevo_estado = 'Ausente'
        else:
            nuevo_estado = 'Presente'
        
        fecha_asistencia = self.fecha_seleccionada
        marcar_estado_asistencia(self.selected_faena_id, miembro_id, fecha_asistencia, nuevo_estado)
        
        # Recargar la lista para actualizar la UI
        self.cargar_asistencias_fecha(fecha_asistencia)

    def mostrar_dialog_justificacion(self):
        """Muestra dialog para justificar ausencias individualmente"""
        if not self.selected_faena_id:
            snackbar = MDSnackbar(
                MDLabel(
                    text="Seleccione una faena primero",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()
            return
            
        # Obtener miembros ausentes
        miembros_ausentes = [m for m in self.miembros_asignados if m['estado_asistencia'] == 'Ausente']
        
        if not miembros_ausentes:
            snackbar = MDSnackbar(
                MDLabel(
                    text="No hay miembros ausentes para justificar",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()
            return
        
        # Guardar los miembros ausentes para usarlos en guardar_justificacion
        self.miembros_ausentes_seleccionados = []
        
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(400)
        )
        
        # Título
        content.add_widget(MDLabel(
            text="Seleccione miembros para justificar:",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(30)
        ))
        
        # Scroll para la lista de miembros
        scroll = MDScrollView(
            size_hint=(1, None),
            height=dp(200)
        )
        
        # Contenedor para las tarjetas de miembros
        miembros_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(5),
            size_hint_y=None,
            adaptive_height=True
        )
        
        # Crear una tarjeta para cada miembro ausente
        self.miembros_seleccionados = {}
        for miembro in miembros_ausentes:
            # Crear una tarjeta para cada miembro
            card = MDCard(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(50),
                padding=dp(10),
                spacing=dp(10),
                ripple_behavior=True,
                md_bg_color=(0.95, 0.95, 0.95, 1),  # Color por defecto
                radius=dp(5)
            )
            
            # Agregar un icono
            card.add_widget(MDIcon(
                icon="account",
                theme_text_color="Custom",
                text_color=(0.8, 0.2, 0.2, 1),  # Rojo para ausentes
                size_hint=(None, None),
                size=(dp(24), dp(24))
            ))
            
            # Agregar el nombre del miembro
            card.add_widget(MDLabel(
                text=miembro['Nombre'],
                theme_text_color="Primary"
            ))
            
            # Guardar referencia al miembro y su estado de selección
            self.miembros_seleccionados[miembro['ID']] = {
                'card': card,
                'selected': False,
                'nombre': miembro['Nombre']
            }
            
            # Función para manejar la selección de la tarjeta
            def toggle_selection(card_instance, miembro_id=miembro['ID']):
                if self.miembros_seleccionados[miembro_id]['selected']:
                    # Deseleccionar
                    self.miembros_seleccionados[miembro_id]['selected'] = False
                    card_instance.md_bg_color = (0.95, 0.95, 0.95, 1)  # Gris claro
                else:
                    # Seleccionar
                    self.miembros_seleccionados[miembro_id]['selected'] = True
                    card_instance.md_bg_color = (0.2, 0.6, 0.8, 0.2)  # Azul claro
            
            # Asignar la función al evento on_release de la tarjeta
            card.bind(on_release=lambda x, mid=miembro['ID']: toggle_selection(x, mid))
            
            # Agregar la tarjeta al contenedor
            miembros_box.add_widget(card)
        
        scroll.add_widget(miembros_box)
        content.add_widget(scroll)
        
        # Campo de texto para justificación
        content.add_widget(MDLabel(
            text="Justificación:",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(30)
        ))
        
        self.justificacion_field = MDTextField(
            hint_text="Ingrese la justificación",
            multiline=True,
            size_hint_y=None,
            height=dp(100)
        )
        content.add_widget(self.justificacion_field)
        
        self.dialog = MDDialog(
            title="Justificar Ausencias",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    on_release=self.cerrar_dialog
                ),
                MDRaisedButton(
                    text="GUARDAR",
                    on_release=self.guardar_justificacion_multiple
                ),
            ],
        )
        self.dialog.open()
    
    def cerrar_dialog(self, *args):
        """Cierra el dialog"""
        if self.dialog:
            self.dialog.dismiss()
    
    def guardar_justificacion(self, miembro_id, fecha, descripcion):
        """Guarda la justificación y crea un registro en EvidenciasJustificacion"""
        if not self.selected_faena_id:
            return

        # Obtener los miembros seleccionados del diccionario self.miembros_seleccionados
        miembros_seleccionados = [m for m in self.miembros_asignados if self.miembros_seleccionados.get(m['ID'], {}).get('selected', False)]
        if not miembros_seleccionados:
            snackbar = MDSnackbar(
                MDLabel(
                    text="Seleccione al menos un miembro",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()
            return

        descripcion = self.justificacion_field.text.strip()
        if not descripcion:
            snackbar = MDSnackbar(
                MDLabel(
                    text="Ingrese un motivo de justificación",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()
            return

        # Obtener la fecha seleccionada
        fecha_asistencia = getattr(self, 'fecha_seleccionada', datetime.now().date())

        guardar_justificacion(self.selected_faena_id, miembro_id, fecha_asistencia, descripcion)
        self.cargar_asistencias_fecha(fecha_asistencia)
        self.cerrar_dialog()
        snackbar = MDSnackbar(
            MDLabel(
                text="Justificación registrada correctamente",
                theme_text_color="Custom",
                text_color="white",
            )
        )
        snackbar.open()
    
    def generar_reporte(self):
        """Genera reporte de asistencia"""
        if not self.selected_faena_id:
            snackbar = MDSnackbar(
                MDLabel(
                    text="Seleccione una faena primero",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()
            return
            
        stats = {
            'total_asignados': len(self.miembros_asignados),
            'presentes': sum(1 for m in self.miembros_asignados if m['estado_asistencia'] == 'Presente'),
            'ausentes': sum(1 for m in self.miembros_asignados if m['estado_asistencia'] == 'Ausente'),
            'tardanzas': sum(1 for m in self.miembros_asignados if m['estado_asistencia'] == 'Tardanza'),
            'justificados': sum(1 for m in self.miembros_asignados if m['estado_asistencia'] == 'Justificado'),
            'sin_registrar': len(self.miembros_asignados) - (
                sum(1 for m in self.miembros_asignados if m['estado_asistencia'] in ['Presente', 'Ausente', 'Tardanza', 'Justificado'])
            )
        }
        
        self.mostrar_reporte_dialog(stats)
    
    def mostrar_reporte_dialog(self, stats):
        """Muestra el reporte en un dialog con mejor visualización, íconos claros y orden correcto"""
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(420)
        )
        if self.selected_faena:
            content.add_widget(MDLabel(
                text=f"Faena: {self.selected_faena['nombre']}",
                theme_text_color="Primary",
                font_style="H6",
                size_hint_y=None,
                height=dp(30)
            ))
        # Scroll para la tarjeta de estadísticas
        stats_card = MDCard(
            orientation="vertical",
            padding=dp(15),
            elevation=2,
            radius=dp(10),
            size_hint_y=None,
            height=dp(340),
            md_bg_color=(0.98, 0.98, 0.98, 1)
        )
        stats_card.add_widget(MDLabel(
            text="Estadísticas de Asistencia",
            theme_text_color="Primary",
            font_style="Subtitle1",
            bold=True,
            size_hint_y=None,
            height=dp(30)
        ))
        stats_grid = MDGridLayout(
            cols=2,
            spacing=dp(12),
            padding=dp(10),
            size_hint_y=None,
            height=dp(240)
        )
        def stat_row(icon, color, label, value):
            row = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(32))
            row.add_widget(MDIcon(icon=icon, theme_text_color="Custom", text_color=color, size_hint=(None, None), size=(dp(24), dp(24))))
            row.add_widget(MDLabel(text=label, theme_text_color="Secondary", font_style="Body1"))
            return row, MDLabel(text=str(value), theme_text_color="Custom", text_color=color, font_style="Body1", bold=True)
        # ORDEN CORRECTO:
        # 1. Total asignados
        stats_grid.add_widget(MDLabel(text="Total de miembros asignados:", theme_text_color="Secondary", bold=True, halign="right"))
        stats_grid.add_widget(MDLabel(text=f"{stats['total_asignados']}", theme_text_color="Primary", bold=True))
        # 2. Presentes
        row, val = stat_row("checkbox-marked-circle", (0.2, 0.7, 0.2, 1), "Presentes", stats['presentes'])
        stats_grid.add_widget(row)
        stats_grid.add_widget(val)
        # 3. Ausentes
        row, val = stat_row("close-circle", (0.8, 0.2, 0.2, 1), "Ausentes", stats['ausentes'])
        stats_grid.add_widget(row)
        stats_grid.add_widget(val)
        # 4. Tardanzas
        row, val = stat_row("clock-alert", (0.9, 0.6, 0.1, 1), "Tardanzas", stats['tardanzas'])
        stats_grid.add_widget(row)
        stats_grid.add_widget(val)
        # 5. Justificados
        row, val = stat_row("file-document", (0.1, 0.6, 0.8, 1), "Justificados", stats['justificados'])
        stats_grid.add_widget(row)
        stats_grid.add_widget(val)
        # 6. Sin registrar
        row, val = stat_row("help-circle", (0.5, 0.5, 0.5, 1), "Sin registrar", stats['sin_registrar'])
        stats_grid.add_widget(row)
        stats_grid.add_widget(val)
        # 7. Porcentaje de asistencia
        stats_grid.add_widget(MDLabel(text="Porcentaje de asistencia:", theme_text_color="Secondary", bold=True, halign="right"))
        porcentaje = (stats['presentes'] / stats['total_asignados'] * 100) if stats['total_asignados'] else 0
        stats_grid.add_widget(MDLabel(text=f"{porcentaje:.1f}%", theme_text_color="Primary", bold=True))
        stats_card.add_widget(stats_grid)
        scroll = MDScrollView(size_hint=(1, None), height=dp(340))
        scroll.add_widget(stats_card)
        content.add_widget(scroll)
        self.dialog = MDDialog(
            title="Reporte de Asistencia",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CERRAR",
                    on_release=self.cerrar_dialog
                ),
            ],
        )
        self.dialog.open()
    
    def marcar_tardanza(self, miembro_id=None, fecha=None):
        """Marca como tardanza a los miembros que están como 'Ausente' en la fecha seleccionada o a un miembro específico si se pasan argumentos."""
        if not self.selected_faena_id:
            return
        # Si se pasan los argumentos, marcar solo ese miembro
        if miembro_id is not None and fecha is not None:
            marcar_tardanza(self.selected_faena_id, miembro_id, fecha)
            self.cargar_asistencias_fecha(fecha)
            return
        # Si no, marcar a todos los ausentes en la fecha seleccionada
        fecha_asistencia = getattr(self, 'fecha_seleccionada', None)
        if not fecha_asistencia:
            snackbar = MDSnackbar(MDLabel(text="Seleccione una fecha de asistencia para continuar."))
            snackbar.open()
            return
        miembros_ausentes = [m for m in self.miembros_asignados if m['estado_asistencia'] == 'Ausente']
        if not miembros_ausentes:
            snackbar = MDSnackbar(MDLabel(text="No hay miembros ausentes para marcar como tardanza."))
            snackbar.open()
            return
        for miembro in miembros_ausentes:
            marcar_tardanza(self.selected_faena_id, miembro['ID'], fecha_asistencia)
        self.cargar_asistencias_fecha(fecha_asistencia)
        snackbar = MDSnackbar(MDLabel(text="Tardanza marcada para todos los ausentes."))
        snackbar.open()
    
    def resetear_estado_miembro(self, miembro_id):
        """Resetea el estado de un miembro a 'Sin registrar'"""
        if not self.selected_faena_id:
            return
            
        print(f"Reseteando estado del miembro ID: {miembro_id}")
        
        # Obtener la fecha seleccionada
        fecha_asistencia = getattr(self, 'fecha_seleccionada', datetime.now().date())
        
        # Encontrar el miembro actual
        miembro_actual = next((m for m in self.miembros_asignados if m['ID'] == miembro_id), None)
        if not miembro_actual:
            return
        
        self.guardar_justificacion(miembro_id, fecha_asistencia, "")

    def mostrar_leyenda_colores(self):
        """Muestra un diálogo con la leyenda de colores para los estados de asistencia"""
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(300)
        )
        
        # Título
        content.add_widget(MDLabel(
            text="Leyenda de Colores",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height=dp(30)
        ))
        
        # Crear tarjetas para cada estado
        estados = [
            {"estado": "Presente", "color": (0.2, 0.8, 0.2, 0.2), "icon": "check-circle", "icon_color": (0.2, 0.8, 0.2, 1)},
            {"estado": "Ausente", "color": (0.8, 0.2, 0.2, 0.2), "icon": "close-circle", "icon_color": (0.8, 0.2, 0.2, 1)},
            {"estado": "Tardanza", "color": (0.8, 0.6, 0.0, 0.2), "icon": "clock-alert", "icon_color": (0.8, 0.6, 0.0, 1)},
            {"estado": "Justificado", "color": (0.2, 0.6, 0.8, 0.2), "icon": "file-document", "icon_color": (0.2, 0.6, 0.8, 1)},
            {"estado": "Sin registrar", "color": (0.95, 0.95, 0.95, 1), "icon": "help-circle", "icon_color": (0.5, 0.5, 0.5, 1)}
        ]
        
        for estado_info in estados:
            # Crear una tarjeta para cada estado
            card = MDCard(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(50),
                padding=dp(10),
                spacing=dp(10),
                md_bg_color=estado_info["color"],
                radius=dp(5)
            )
            
            # Agregar un icono
            card.add_widget(MDIcon(
                icon=estado_info["icon"],
                theme_text_color="Custom",
                text_color=estado_info["icon_color"],
                size_hint=(None, None),
                size=(dp(24), dp(24))
            ))
            
            # Agregar el nombre del estado
            card.add_widget(MDLabel(
                text=estado_info["estado"],
                theme_text_color="Primary"
            ))
            
            content.add_widget(card)
        
        self.dialog = MDDialog(
            title="Estados de Asistencia",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CERRAR",
                    on_release=self.cerrar_dialog
                ),
            ],
        )
        self.dialog.open()

    def volver_asistencia_menu(self):
        self.manager.transition.direction = 'right'
        self.manager.current = "dashboard"

    def go_to_registrar_asistencia(self):
        if not self.selected_faena:
            snackbar = MDSnackbar(
                MDLabel(
                    text="Seleccione una faena primero",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()
            return

    def guardar_justificacion_multiple(self, *args):
        """Guarda la justificación para todos los miembros seleccionados"""
        if not self.selected_faena_id:
            return

        miembros_seleccionados = [m for m in self.miembros_asignados if self.miembros_seleccionados.get(m['ID'], {}).get('selected', False)]
        if not miembros_seleccionados:
            snackbar = MDSnackbar(
                MDLabel(
                    text="Seleccione al menos un miembro",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()
            return

        descripcion = self.justificacion_field.text.strip()
        if not descripcion:
            snackbar = MDSnackbar(
                MDLabel(
                    text="Ingrese un motivo de justificación",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()
            return

        fecha_asistencia = getattr(self, 'fecha_seleccionada', datetime.now().date())

        for miembro in miembros_seleccionados:
            self.guardar_justificacion(miembro['ID'], fecha_asistencia, descripcion)
        self.cargar_asistencias_fecha(fecha_asistencia)
        self.cerrar_dialog()
        snackbar = MDSnackbar(
            MDLabel(
                text=f"Justificación registrada para {len(miembros_seleccionados)} miembro(s)",
                theme_text_color="Custom",
                text_color="white",
            )
        )
        snackbar.open()