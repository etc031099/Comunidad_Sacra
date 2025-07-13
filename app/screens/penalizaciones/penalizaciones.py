from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDList
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivymd.uix.card import MDCard
from kivymd.uix.widget import Widget
from kivy.metrics import dp
from datetime import datetime
from kivy.factory import Factory
try:
    from kivymd.uix.pickers import MDDatePicker
    HAS_DATE_PICKER = True
except ImportError:
    HAS_DATE_PICKER = False
from kivy.uix.scrollview import ScrollView
from .penalizaciones_db import (
    obtener_penalizaciones_por_miembro, obtener_multas_miembro,
    obtener_rango_fechas_penalizaciones, obtener_estadisticas_penalizaciones,
    cancelar_multas_acumuladas, exportar_penalizaciones
)

class PenalizacionItem(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected = False
        self.nombre_evento = ""
        self.tipo_penalizacion = ""
        self.estado = ""
        self.valor = 0
        self.valor_realizado = 0
        self.valor_pendiente = 0
        self.fecha_aplicacion = ""
        self.fecha_vencimiento = ""

    def on_registrar_pago(self):
        # Implementar lógica para registrar pago
        pass

    def on_registrar_horas(self):
        # Implementar lógica para registrar horas
        pass

class MiembroPenalizacionItem(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = dp(10)
        self.spacing = dp(10)
        self.md_bg_color = (0.95, 0.95, 0.95, 1)
        self.radius = [dp(8)]

class NuevaPenalizacionDialog(MDDialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.buttons = [
            MDFlatButton(
                text="CANCELAR",
                on_release=lambda x: self.dismiss()
            ),
            MDFlatButton(
                text="GUARDAR",
                on_release=self.guardar_penalizacion
            ),
        ]

    def show_tipo_evento_menu(self):
        menu_items = [
            {
                "text": "FAENA",
                "on_release": lambda x="FAENA": self.set_tipo_evento(x),
            },
            {
                "text": "REUNION",
                "on_release": lambda x="REUNION": self.set_tipo_evento(x),
            },
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.tipo_evento_dropdown,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    def show_tipo_penalizacion_menu(self):
        menu_items = [
            {
                "text": "MULTA",
                "on_release": lambda x="MULTA": self.set_tipo_penalizacion(x),
            },
            {
                "text": "HORAS_REPOSICION",
                "on_release": lambda x="HORAS_REPOSICION": self.set_tipo_penalizacion(x),
            },
            {
                "text": "SUSPENSION",
                "on_release": lambda x="SUSPENSION": self.set_tipo_penalizacion(x),
            },
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.tipo_penalizacion_dropdown,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    def set_tipo_evento(self, tipo):
        self.ids.tipo_evento_dropdown.text = tipo
        self.menu.dismiss()

    def set_tipo_penalizacion(self, tipo):
        self.ids.tipo_penalizacion_dropdown.text = tipo
        self.menu.dismiss()

    def validar_campo(self, campo, valor):
        """Valida un campo específico en tiempo real"""
        from app.utils.validacion_simplificada import ValidacionFormularios, UIValidacionSimplificada
        
        # Crear un diccionario con solo el campo a validar
        datos = {campo: valor.strip()}
        
        # Validar el campo específico
        es_valido, mensaje_error = ValidacionFormularios.validar_campo_penalizacion(campo, valor.strip())
        
        # Actualizar la UI del campo
        UIValidacionSimplificada.actualizar_campo(self.ids[campo], es_valido, mensaje_error)
        
        return es_valido

    def validar_campo_on_focus(self, campo, valor, tiene_foco):
        """Valida un campo cuando pierde el foco"""
        if not tiene_foco:  # Solo validar cuando pierde el foco
            self.validar_campo(campo, valor)

    def guardar_penalizacion(self, *args):
        """Guarda una nueva penalización con validaciones"""
        try:
            # Recopilar datos del formulario
            datos = {
                "id_miembro": self.ids.id_miembro.text.strip(),
                "tipo_evento": self.ids.tipo_evento_dropdown.text,
                "tipo_penalizacion": self.ids.tipo_penalizacion_dropdown.text,
                "valor": self.ids.valor.text.strip(),
                "observaciones": self.ids.observaciones.text.strip()
            }
            
            # Validar todos los datos usando el validador centralizado
            from app.utils.validacion_simplificada import ValidacionFormularios, UIValidacionSimplificada
            
            es_valido, mensaje_error = ValidacionFormularios.validar_datos_penalizacion(datos)
            if not es_valido:
                UIValidacionSimplificada.mostrar_error_snackbar(mensaje_error)
                return
            
            # Si pasó todas las validaciones, proceder a guardar
            # Aquí iría la lógica para guardar en la base de datos
            print(f"Penalización válida: {datos}")
            
            # Mostrar mensaje de éxito
            UIValidacionSimplificada.mostrar_error_snackbar("Penalización guardada correctamente")
            self.dismiss()
            
        except Exception as e:
            UIValidacionSimplificada.mostrar_error_snackbar(f"Error al guardar penalización: {str(e)}")

class RegistrarPagoDialog(MDDialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.buttons = [
            MDFlatButton(
                text="CANCELAR",
                on_release=lambda x: self.dismiss()
            ),
            MDFlatButton(
                text="GUARDAR",
                on_release=self.guardar_pago
            ),
        ]

    def show_metodo_pago_menu(self):
        menu_items = [
            {
                "text": "EFECTIVO",
                "on_release": lambda x="EFECTIVO": self.set_metodo_pago(x),
            },
            {
                "text": "TRANSFERENCIA",
                "on_release": lambda x="TRANSFERENCIA": self.set_metodo_pago(x),
            },
            {
                "text": "DEPOSITO",
                "on_release": lambda x="DEPOSITO": self.set_metodo_pago(x),
            },
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.metodo_pago_dropdown,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    def set_metodo_pago(self, metodo):
        self.ids.metodo_pago_dropdown.text = metodo
        self.menu.dismiss()

    def validar_campo(self, campo, valor):
        """Valida un campo específico en tiempo real"""
        from app.utils.validacion_simplificada import ValidacionFormularios, UIValidacionSimplificada
        
        # Validar el campo específico
        es_valido, mensaje_error = ValidacionFormularios.validar_campo_penalizacion(campo, valor.strip())
        
        # Actualizar la UI del campo
        UIValidacionSimplificada.actualizar_campo(self.ids[campo], es_valido, mensaje_error)
        
        return es_valido

    def validar_campo_on_focus(self, campo, valor, tiene_foco):
        """Valida un campo cuando pierde el foco"""
        if not tiene_foco:  # Solo validar cuando pierde el foco
            self.validar_campo(campo, valor)

    def guardar_pago(self, *args):
        """Guarda un pago con validaciones"""
        try:
            # Recopilar datos del formulario
            datos = {
                "id_penalizacion": self.ids.id_penalizacion.text.strip(),
                "monto_pagado": self.ids.monto_pagado.text.strip(),
                "metodo_pago": self.ids.metodo_pago_dropdown.text,
                "comprobante": self.ids.comprobante.text.strip()
            }
            
            # Validar todos los datos usando el validador centralizado
            from app.utils.validacion_simplificada import ValidacionFormularios, UIValidacionSimplificada
            
            es_valido, mensaje_error = ValidacionFormularios.validar_datos_pago(datos)
            if not es_valido:
                UIValidacionSimplificada.mostrar_error_snackbar(mensaje_error)
                return
            
            # Si pasó todas las validaciones, proceder a guardar
            # Aquí iría la lógica para guardar en la base de datos
            print(f"Pago válido: {datos}")
            
            # Mostrar mensaje de éxito
            UIValidacionSimplificada.mostrar_error_snackbar("Pago registrado correctamente")
            self.dismiss()
            
        except Exception as e:
            UIValidacionSimplificada.mostrar_error_snackbar(f"Error al registrar pago: {str(e)}")

class RegistrarHorasDialog(MDDialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.buttons = [
            MDFlatButton(
                text="CANCELAR",
                on_release=lambda x: self.dismiss()
            ),
            MDFlatButton(
                text="GUARDAR",
                on_release=self.guardar_horas
            ),
        ]

    def validar_campo(self, campo, valor):
        """Valida un campo específico en tiempo real"""
        from app.utils.validacion_simplificada import ValidacionFormularios, UIValidacionSimplificada
        
        # Validar el campo específico
        es_valido, mensaje_error = ValidacionFormularios.validar_campo_penalizacion(campo, valor.strip())
        
        # Actualizar la UI del campo
        UIValidacionSimplificada.actualizar_campo(self.ids[campo], es_valido, mensaje_error)
        
        return es_valido

    def validar_campo_on_focus(self, campo, valor, tiene_foco):
        """Valida un campo cuando pierde el foco"""
        if not tiene_foco:  # Solo validar cuando pierde el foco
            self.validar_campo(campo, valor)

    def guardar_horas(self, *args):
        """Guarda horas de reposición con validaciones"""
        try:
            # Recopilar datos del formulario
            datos = {
                "id_penalizacion": self.ids.id_penalizacion.text.strip(),
                "id_faena": self.ids.id_faena.text.strip(),
                "horas_realizadas": self.ids.horas_realizadas.text.strip(),
                "fecha_realizacion": self.ids.fecha_realizacion.text.strip()
            }
            
            # Validar todos los datos usando el validador centralizado
            from app.utils.validacion_simplificada import ValidacionFormularios, UIValidacionSimplificada
            
            es_valido, mensaje_error = ValidacionFormularios.validar_datos_horas(datos)
            if not es_valido:
                UIValidacionSimplificada.mostrar_error_snackbar(mensaje_error)
                return
            
            # Si pasó todas las validaciones, proceder a guardar
            # Aquí iría la lógica para guardar en la base de datos
            print(f"Horas válidas: {datos}")
            
            # Mostrar mensaje de éxito
            UIValidacionSimplificada.mostrar_error_snackbar("Horas de reposición registradas correctamente")
            self.dismiss()
            
        except Exception as e:
            UIValidacionSimplificada.mostrar_error_snackbar(f"Error al registrar horas: {str(e)}")

class PenalizacionesScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Variables para almacenar los filtros activos
        self.filtro_estado = "Todos"
        self.filtro_fecha_desde = None
        self.filtro_fecha_hasta = None

    def on_enter(self):
        # Restaurar el estado de los filtros si existe
        self.restaurar_estado_filtros()
        self.cargar_penalizaciones_por_miembro()

    def go_back(self):
        # Guardar el estado de los filtros antes de salir
        self.guardar_estado_filtros()
        self.manager.transition.direction = 'right'
        self.manager.current = 'dashboard'

    def cargar_penalizaciones_por_miembro(self):
        try:
            miembros_con_penalizaciones = obtener_penalizaciones_por_miembro(
                self.filtro_estado, self.filtro_fecha_desde, self.filtro_fecha_hasta
            )
            
            self.ids.penalizaciones_list.clear_widgets()

            if not miembros_con_penalizaciones:
                mensaje = MDLabel(
                    text="No se encontraron miembros con el estado y filtros aplicados",
                    theme_text_color="Secondary",
                    font_style="Subtitle1",
                    halign="center",
                    size_hint_y=None,
                    height=dp(60)
                )
                self.ids.penalizaciones_list.add_widget(mensaje)
            else:
                contador = MDLabel(
                    text=f"Mostrando {len(miembros_con_penalizaciones)} miembro(s) con el estado '{self.filtro_estado}'",
                    theme_text_color="Primary",
                    font_style="Caption",
                    halign="center",
                    size_hint_y=None,
                    height=dp(30)
                )
                self.ids.penalizaciones_list.add_widget(contador)
                for miembro in miembros_con_penalizaciones:
                    id_miembro, nombre_completo, total_multas_reuniones, asistencias_validas = miembro
                    
                    asistencias_validas = asistencias_validas if asistencias_validas is not None else 0
                    faltas_faena = max(0, 5 - asistencias_validas)
                    total_multas_faena = faltas_faena * 60
                    total_general = (total_multas_reuniones or 0) + total_multas_faena
                    row_container = MDBoxLayout(
                        orientation='horizontal',
                        adaptive_height=True,
                        spacing=dp(10)
                    )
                    panel_header = MDExpansionPanelOneLine(
                        text=f"{nombre_completo} | Multa reuniones: S/. {total_multas_reuniones:.2f} | Multa faenas: S/. {total_multas_faena:.2f} | Total: S/. {total_general:.2f}"
                    )
                    panel_content = self.crear_contenido_miembro(id_miembro, nombre_completo, total_multas_reuniones, asistencias_validas, total_multas_faena, total_general)
                    expansion_panel = MDExpansionPanel(
                        icon="account",
                        panel_cls=panel_header,
                        content=panel_content
                    )
                    delete_button = Factory.TooltipButton(
                        icon="delete-sweep-outline",
                        on_release=lambda x, mid=id_miembro: self.confirmar_cancelar_multas_acumuladas(mid),
                        tooltip_text="Cancelar todas las multas pendientes del miembro",
                        pos_hint={'center_y': 0.5}
                    )
                    row_container.add_widget(expansion_panel)
                    row_container.add_widget(delete_button)
                    self.ids.penalizaciones_list.add_widget(row_container)

        except Exception as e:
            snackbar = MDSnackbar(
                MDLabel(
                    text=f"Error al cargar penalizaciones: {str(e)}",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()

    def crear_contenido_miembro(self, id_miembro, nombre_completo, total_multas_reuniones, asistencias_validas, total_multas_faena, total_general):
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(15),
            size_hint_y=None,
            height=0
        )
        content.bind(minimum_height=content.setter('height'))
        header = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )
        header.add_widget(MDLabel(
            text="Resumen de Multas por Reuniones y Faenas Faltantes:",
            theme_text_color="Primary",
            font_style="Subtitle1",
            bold=True
        ))
        header.add_widget(Widget())
        content.add_widget(header)
        content.add_widget(MDLabel(
            text=f"Asistencias válidas a faenas: {asistencias_validas}/5 (faltan {max(0,5-asistencias_validas)})",
            theme_text_color="Secondary",
            font_style="Subtitle2",
            bold=True,
            size_hint_y=None,
            height=dp(24)
        ))
        
        # Añadir resumen de multa por faena si aplica
        if total_multas_faena > 0:
            content.add_widget(MDLabel(
                text=f"Multa por Faenas Faltantes: S/. {total_multas_faena:.2f}",
                theme_text_color="Error",
                font_style="Subtitle2",
                bold=True,
                size_hint_y=None,
                height=dp(22)
            ))

        self.cargar_multas_miembro(content, id_miembro, tipo_evento='REUNION')
        return content

    def cargar_multas_miembro(self, content, id_miembro, tipo_evento):
        if tipo_evento != 'REUNION':
            return
            
        try:
            multas = obtener_multas_miembro(
                id_miembro, self.filtro_estado, self.filtro_fecha_desde, self.filtro_fecha_hasta
            )
            
            if multas:
                content.add_widget(MDLabel(
                    text="Multas por Reunión:",
                    theme_text_color="Primary",
                    font_style="Subtitle2",
                    bold=True,
                    size_hint_y=None,
                    height=dp(22)
                ))
                
                for multa in multas:
                    item = self.crear_item_multa(multa)
                    content.add_widget(item)
        except Exception as e:
            content.add_widget(MDLabel(
                text=f"Error al cargar multas: {str(e)}",
                theme_text_color="Error"
            ))

    def crear_item_multa(self, multa):
        item = MDCard(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(70),
            padding=dp(10),
            spacing=dp(10),
            md_bg_color=(1, 1, 1, 0.9),
            radius=[dp(8)]
        )
        
        info_layout = MDBoxLayout(orientation='vertical', size_hint_x=0.7, spacing=dp(2))
        info_layout.add_widget(MDLabel(
            text=multa[5] or "Evento no encontrado",
            theme_text_color="Primary", font_style="Subtitle2", bold=True,
            size_hint_y=None, height=dp(20)
        ))
        
        detalles = f"Valor: S/. {multa[2]:.2f} | Estado: {multa[4]}"
        if multa[6] > 0:
            detalles += f" | Pagado: S/. {multa[6]:.2f}"
        
        info_layout.add_widget(MDLabel(
            text=detalles,
            theme_text_color="Secondary", font_style="Caption",
            size_hint_y=None, height=dp(16)
        ))
        
        fecha_aplicacion_dt = multa[3]
        fecha_aplicacion_str = fecha_aplicacion_dt.strftime("%d/%m/%Y") if fecha_aplicacion_dt else "N/A"
        info_layout.add_widget(MDLabel(
            text=f"Fecha: {fecha_aplicacion_str}",
            theme_text_color="Secondary", font_style="Caption",
            size_hint_y=None, height=dp(16)
        ))
        
        item.add_widget(info_layout)
        
        botones_layout = MDBoxLayout(orientation='vertical', size_hint_x=0.3, spacing=dp(5))
        if multa[4] == 'PENDIENTE':
            botones_layout.add_widget(MDFlatButton(
                text="Pagar",
                theme_text_color="Primary",
                size_hint_y=None, height=dp(30),
                on_release=lambda x, id_pen=multa[0]: self.registrar_pago(id_pen)
            ))
        
        item.add_widget(botones_layout)
        return item

    def registrar_pago(self, id_penalizacion):
        dialog = RegistrarPagoDialog()
        dialog.ids.id_penalizacion.text = str(id_penalizacion)
        dialog.open()

    def show_estado_menu(self):
        menu_items = [
            {"text": "Todos", "on_release": lambda x="Todos": self.filtrar_estado(x)},
            {"text": "PENDIENTE", "on_release": lambda x="PENDIENTE": self.filtrar_estado(x)},
            {"text": "CANCELADO", "on_release": lambda x="CANCELADO": self.filtrar_estado(x)},
        ]
        self.menu = MDDropdownMenu(caller=self.ids.estado_dropdown, items=menu_items, width_mult=4)
        self.menu.open()

    def filtrar_estado(self, estado):
        self.filtro_estado = estado
        self.ids.estado_dropdown.text = estado
        self.menu.dismiss()
        self.aplicar_filtros()

    def aplicar_filtros(self):
        self.cargar_penalizaciones_por_miembro()

    def limpiar_filtros(self):
        self.filtro_estado = "Todos"
        self.filtro_fecha_desde = None
        self.filtro_fecha_hasta = None
        self.ids.estado_dropdown.text = "Estado"
        if hasattr(self.ids, 'fecha_desde'):
            self.ids.fecha_desde.text = ""
        if hasattr(self.ids, 'fecha_hasta'):
            self.ids.fecha_hasta.text = ""
        self.cargar_penalizaciones_por_miembro()
        snackbar = MDSnackbar(MDLabel(text="Filtros limpiados", theme_text_color="Custom", text_color="white"))
        snackbar.open()

    def on_fecha_desde_click(self, *args):
        if HAS_DATE_PICKER:
            min_date, max_date = obtener_rango_fechas_penalizaciones()
            from datetime import datetime, date
            if min_date and max_date:
                if isinstance(min_date, str):
                    min_date = datetime.strptime(min_date, '%Y-%m-%d')
                if isinstance(max_date, str):
                    max_date = datetime.strptime(max_date, '%Y-%m-%d')
                if isinstance(min_date, datetime):
                    min_date = min_date.date()
                if isinstance(max_date, datetime):
                    max_date = max_date.date()
                # Validar rango
                if min_date < max_date:
                    date_dialog = MDDatePicker(title="Selecciona Fecha Desde", min_date=min_date, max_date=max_date)
                    snackbar = MDSnackbar(MDLabel(text=f"Rango disponible: {min_date.strftime('%d/%m/%Y')} - {max_date.strftime('%d/%m/%Y')}", theme_text_color="Custom", text_color="white"))
                    snackbar.open()
                else:
                    date_dialog = MDDatePicker(title="Selecciona Fecha Desde")
                    snackbar = MDSnackbar(MDLabel(text="No hay rango de fechas válido. Selecciona cualquier fecha.", theme_text_color="Custom", text_color="white"))
                    snackbar.open()
            else:
                date_dialog = MDDatePicker(title="Selecciona Fecha Desde")
            date_dialog.bind(on_save=self.set_fecha_desde)
            date_dialog.open()
        else:
            snackbar = MDSnackbar(MDLabel(text="Selector de fecha no disponible. Actualiza KivyMD o ingresa la fecha manualmente.", theme_text_color="Custom", text_color="white"))
            snackbar.open()

    def set_fecha_desde(self, instance, value, date_range):
        fecha_str = value.strftime('%Y-%m-%d')
        fecha_mostrar = value.strftime('%d/%m/%Y')
        self.ids.fecha_desde.text = fecha_mostrar
        self.filtro_fecha_desde = fecha_str
        # Validar rango si ya hay fecha hasta
        if self.ids.fecha_hasta.text:
            try:
                desde = datetime.strptime(fecha_str, '%Y-%m-%d')
                hasta = datetime.strptime(self.filtro_fecha_hasta, '%Y-%m-%d') if self.filtro_fecha_hasta else None
                if hasta and desde > hasta:
                    snackbar = MDSnackbar(MDLabel(text="La fecha desde debe ser menor o igual a la fecha hasta", theme_text_color="Custom", text_color="white"))
                    snackbar.open()
                    self.ids.fecha_desde.text = ""
                    self.filtro_fecha_desde = None
            except Exception:
                pass
        if not self.ids.fecha_desde.text:
            self.filtro_fecha_desde = None

    def on_fecha_hasta_click(self, *args):
        if HAS_DATE_PICKER:
            min_date, max_date = obtener_rango_fechas_penalizaciones()
            from datetime import datetime, date
            if min_date and max_date:
                if isinstance(min_date, str):
                    min_date = datetime.strptime(min_date, '%Y-%m-%d')
                if isinstance(max_date, str):
                    max_date = datetime.strptime(max_date, '%Y-%m-%d')
                if isinstance(min_date, datetime):
                    min_date = min_date.date()
                if isinstance(max_date, datetime):
                    max_date = max_date.date()
                # Validar rango
                if min_date < max_date:
                    date_dialog = MDDatePicker(title="Selecciona Fecha Hasta", min_date=min_date, max_date=max_date)
                    snackbar = MDSnackbar(MDLabel(text=f"Rango disponible: {min_date.strftime('%d/%m/%Y')} - {max_date.strftime('%d/%m/%Y')}", theme_text_color="Custom", text_color="white"))
                    snackbar.open()
                else:
                    date_dialog = MDDatePicker(title="Selecciona Fecha Hasta")
                    snackbar = MDSnackbar(MDLabel(text="No hay rango de fechas válido. Selecciona cualquier fecha.", theme_text_color="Custom", text_color="white"))
                    snackbar.open()
            else:
                date_dialog = MDDatePicker(title="Selecciona Fecha Hasta")
            date_dialog.bind(on_save=self.set_fecha_hasta)
            date_dialog.open()
        else:
            snackbar = MDSnackbar(MDLabel(text="Selector de fecha no disponible. Actualiza KivyMD o ingresa la fecha manualmente.", theme_text_color="Custom", text_color="white"))
            snackbar.open()

    def set_fecha_hasta(self, instance, value, date_range):
        fecha_str = value.strftime('%Y-%m-%d')
        fecha_mostrar = value.strftime('%d/%m/%Y')
        self.ids.fecha_hasta.text = fecha_mostrar
        self.filtro_fecha_hasta = fecha_str
        # Validar rango si ya hay fecha desde
        if self.ids.fecha_desde.text:
            try:
                hasta = datetime.strptime(fecha_str, '%Y-%m-%d')
                desde = datetime.strptime(self.filtro_fecha_desde, '%Y-%m-%d') if self.filtro_fecha_desde else None
                if desde and hasta < desde:
                    snackbar = MDSnackbar(MDLabel(text="La fecha hasta debe ser mayor o igual a la fecha desde", theme_text_color="Custom", text_color="white"))
                    snackbar.open()
                    self.ids.fecha_hasta.text = ""
                    self.filtro_fecha_hasta = None
            except Exception:
                pass
        if not self.ids.fecha_hasta.text:
            self.filtro_fecha_hasta = None

    def aplicar_filtro_fecha(self):
        try:
            from datetime import datetime
            fecha_desde = self.filtro_fecha_desde
            fecha_hasta = self.filtro_fecha_hasta
            if fecha_desde and fecha_hasta:
                if fecha_desde > fecha_hasta:
                    snackbar = MDSnackbar(MDLabel(text="La fecha desde debe ser menor o igual a la fecha hasta", theme_text_color="Custom", text_color="white"))
                    snackbar.open()
                    return
                datetime.strptime(fecha_desde, '%Y-%m-%d')
                datetime.strptime(fecha_hasta, '%Y-%m-%d')
                self.cargar_penalizaciones_por_miembro()
                snackbar = MDSnackbar(MDLabel(text=f"Filtro de fecha aplicado: {fecha_desde} - {fecha_hasta}", theme_text_color="Custom", text_color="white"))
                snackbar.open()
            else:
                snackbar = MDSnackbar(MDLabel(text="Por favor, complete ambas fechas (DD/MM/YYYY)", theme_text_color="Custom", text_color="white"))
                snackbar.open()
        except ValueError:
            snackbar = MDSnackbar(MDLabel(text="Formato de fecha inválido. Use DD/MM/YYYY", theme_text_color="Custom", text_color="white"))
            snackbar.open()
        except Exception as e:
            snackbar = MDSnackbar(MDLabel(text=f"Error al aplicar filtro de fecha: {str(e)}", theme_text_color="Custom", text_color="white"))
            snackbar.open()

    def confirmar_cancelar_multas_acumuladas(self, id_miembro):
        dialog = MDDialog(
            title="Confirmar Cancelación",
            text=f"¿Está seguro de que desea CANCELAR TODAS las multas pendientes de este miembro? Esta acción debe realizarse tras el pago y no se puede deshacer.",
            buttons=[
                MDFlatButton(text="CERRAR", on_release=lambda x: dialog.dismiss()),
                MDFlatButton(text="CANCELAR MULTAS", theme_text_color="Error", on_release=lambda x: self.cancelar_multas_acumuladas(id_miembro, dialog)),
            ],
        )
        dialog.open()

    def cancelar_multas_acumuladas(self, id_miembro, dialog):
        dialog.dismiss()
        try:
            success = cancelar_multas_acumuladas(id_miembro)
            if success:
                snackbar = MDSnackbar(MDLabel(text="Multas de reuniones canceladas y faenas regularizadas."))
                snackbar.open()
            else:
                snackbar = MDSnackbar(MDLabel(text="Error al cancelar multas."))
                snackbar.open()
        except Exception as e:
            snackbar = MDSnackbar(MDLabel(text=f"Error al cancelar multas: {e}"))
            snackbar.open()
        finally:
            # Recargar la lista para reflejar todos los cambios
            self.cargar_penalizaciones_por_miembro()

    def show_nueva_penalizacion_dialog(self):
        dialog = NuevaPenalizacionDialog()
        dialog.open()

    def show_registrar_pago_dialog(self):
        dialog = RegistrarPagoDialog()
        dialog.open()

    def show_registrar_horas_dialog(self):
        dialog = RegistrarHorasDialog()
        dialog.open()

    def exportar_resultados(self):
        try:
            from datetime import datetime
            fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"penalizaciones_filtradas_{fecha_actual}.txt"
            
            contenido = exportar_penalizaciones(
                self.filtro_estado, self.filtro_fecha_desde, self.filtro_fecha_hasta
            )
            
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                f.write('\n'.join(contenido))
            
            snackbar = MDSnackbar(MDLabel(text=f"Reporte exportado como: {nombre_archivo}", theme_text_color="Custom", text_color="white"))
            snackbar.open()
        except Exception as e:
            snackbar = MDSnackbar(MDLabel(text=f"Error al exportar: {str(e)}", theme_text_color="Custom", text_color="white"))
            snackbar.open()

    def guardar_estado_filtros(self):
        try:
            import json
            estado = {
                'filtro_estado': self.filtro_estado,
                'filtro_fecha_desde': self.filtro_fecha_desde,
                'filtro_fecha_hasta': self.filtro_fecha_hasta
            }
            with open('estado_filtros_penalizaciones.json', 'w') as f:
                json.dump(estado, f)
        except Exception as e:
            print(f"Error al guardar estado de filtros: {e}")

    def restaurar_estado_filtros(self):
        try:
            import json
            import os
            if os.path.exists('estado_filtros_penalizaciones.json'):
                with open('estado_filtros_penalizaciones.json', 'r') as f:
                    estado = json.load(f)
                
                self.filtro_estado = estado.get('filtro_estado', 'Todos')
                self.filtro_fecha_desde = estado.get('filtro_fecha_desde')
                self.filtro_fecha_hasta = estado.get('filtro_fecha_hasta')
                
                if self.filtro_estado != "Todos":
                    self.ids.estado_dropdown.text = self.filtro_estado
        except Exception as e:
            print(f"Error al restaurar estado de filtros: {e}")

    def mostrar_estado_filtros(self):
        """Muestra el estado actual de los filtros en un snackbar"""
        try:
            estado_texto = f"Estado: {self.filtro_estado}"
            
            if self.filtro_fecha_desde and self.filtro_fecha_hasta:
                estado_texto += f" | Fechas: {self.filtro_fecha_desde} - {self.filtro_fecha_hasta}"
            elif self.filtro_fecha_desde:
                estado_texto += f" | Desde: {self.filtro_fecha_desde}"
            elif self.filtro_fecha_hasta:
                estado_texto += f" | Hasta: {self.filtro_fecha_hasta}"
            else:
                estado_texto += " | Sin filtros de fecha"
            
            snackbar = MDSnackbar(
                MDLabel(
                    text=estado_texto,
                    theme_text_color="Custom",
                    text_color="white",
                ),
                duration=4.0
            )
            snackbar.open()
        except Exception as e:
            snackbar = MDSnackbar(
                MDLabel(
                    text=f"Error al mostrar estado de filtros: {str(e)}",
                    theme_text_color="Custom",
                    text_color="white",
                )
            )
            snackbar.open()

    def mostrar_estadisticas(self):
        try:
            stats, stats_por_evento = obtener_estadisticas_penalizaciones()
            
            # Contenedor principal del diálogo
            dialog_content = MDBoxLayout(
                orientation='vertical',
                spacing=dp(15),
                padding=dp(20),
                size_hint_y=None,
                adaptive_height=True
            )

            # Función para crear filas de estadísticas con íconos
            def create_stat_row(icon, text, value, is_bold=False):
                row = MDBoxLayout(adaptive_height=True, spacing=dp(15))
                row.add_widget(Factory.MDIcon(icon=icon, pos_hint={'center_y': 0.5}, theme_text_color="Secondary"))
                row.add_widget(MDLabel(text=text, adaptive_height=True, theme_text_color="Primary"))
                row.add_widget(MDLabel(text=str(value), halign='right', bold=is_bold, adaptive_height=True, theme_text_color="Secondary"))
                return row

            # --- Sección de Resumen General ---
            dialog_content.add_widget(MDLabel(
                text="Resumen General",
                font_style="H6",
                adaptive_height=True,
                theme_text_color="Primary",
                padding=(0, dp(10))
            ))
            
            if stats:
                dialog_content.add_widget(create_stat_row(
                    "format-list-numbered", "Total de penalizaciones:", f"{stats[0] or 0}"
                ))
                dialog_content.add_widget(create_stat_row(
                    "clock-alert-outline", "Pendientes:", f"{stats[1] or 0}"
                ))
                dialog_content.add_widget(create_stat_row(
                    "close-circle-outline", "Canceladas:", f"{stats[2] or 0}"
                ))
                dialog_content.add_widget(create_stat_row(
                    "cash-minus", "Total pendiente:", f"S/. {(stats[3] or 0):.2f}", is_bold=True
                ))
            else:
                dialog_content.add_widget(MDLabel(text="No hay datos de resumen disponibles.", theme_text_color="Secondary"))
            
            # Separador manual compatible con versiones antiguas de KivyMD
            dialog_content.add_widget(Widget(size_hint_y=None, height=dp(10)))
            separator = MDCard(
                size_hint_y=None,
                height="1dp",
                md_bg_color=self.theme_cls.divider_color
            )
            dialog_content.add_widget(separator)
            dialog_content.add_widget(Widget(size_hint_y=None, height=dp(10)))
            
            # --- Sección por Tipo de Evento ---
            dialog_content.add_widget(MDLabel(
                text="Desglose por Evento",
                font_style="H6",
                adaptive_height=True,
                theme_text_color="Primary",
                padding=(0, dp(10))
            ))
            
            if stats_por_evento:
                for evento in stats_por_evento:
                    dialog_content.add_widget(create_stat_row(
                        "account-group",
                        f"{evento[0]}:",
                        f"{evento[1]} penalizaciones (S/. {(evento[2] or 0):.2f} pendiente)"
                    ))
            else:
                dialog_content.add_widget(MDLabel(text="No hay datos por tipo de evento.", theme_text_color="Secondary"))

            # Envolver el contenido en un ScrollView
            scroll_view = ScrollView(
                size_hint_y=None,
                height=dp(400)
            )
            scroll_view.add_widget(dialog_content)

            dialog = MDDialog(
                title="Estadísticas de Penalizaciones",
                type="custom",
                content_cls=scroll_view,
                buttons=[MDFlatButton(text="CERRAR", on_release=lambda x: dialog.dismiss())],
            )
            dialog.open()
        except Exception as e:
            snackbar = MDSnackbar(MDLabel(text=f"Error al mostrar estadísticas: {e}", theme_text_color="Custom", text_color="white"))
            snackbar.open() 