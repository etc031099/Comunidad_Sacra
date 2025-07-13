from kivy.properties import DictProperty, StringProperty
from kivymd.uix.snackbar import Snackbar, MDSnackbar
from app.db.conexion import obtener_conexion
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from app.utils.validacion_simplificada import ValidacionFormularios, UIValidacionSimplificada

class MiembroFormScreen(MDScreen):
    miembro = DictProperty({})
    titulo = StringProperty("Agregar Miembro")

    def on_pre_enter(self):
        # Cambia el título según si es edición o nuevo
        if self.miembro and self.miembro.get("ID"):
            self.titulo = "Editar Miembro"
        else:
            self.titulo = "Agregar Miembro"
        
        # Actualiza los campos visuales con los datos del miembro
        self.ids.nombre.text = self.miembro.get("Nombre", "")
        self.ids.apellido_paterno.text = self.miembro.get("Apellido_Paterno", "")
        self.ids.apellido_materno.text = self.miembro.get("Apellido_Materno", "")
        self.ids.dni.text = self.miembro.get("DNI", "")
        self.ids.correo.text = self.miembro.get("Correo", "")
        self.ids.direccion.text = self.miembro.get("Dirección", "")
        self.ids.telefono.text = self.miembro.get("Teléfono", "")

    def guardar_miembro(self):
        datos = {
            "Nombre": self.ids.nombre.text.strip(),
            "Apellido_Paterno": self.ids.apellido_paterno.text.strip(),
            "Apellido_Materno": self.ids.apellido_materno.text.strip(),
            "DNI": self.ids.dni.text.strip(),
            "Correo": self.ids.correo.text.strip(),
            "Dirección": self.ids.direccion.text.strip(),
            "Teléfono": self.ids.telefono.text.strip(),
        }
        
        # Validar todos los datos usando el validador centralizado
        es_valido, mensaje_error = ValidacionFormularios.validar_datos_miembro(datos)
        if not es_valido:
            UIValidacionSimplificada.mostrar_error_snackbar(mensaje_error)
            return

        conexion = obtener_conexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                # Verifica si el DNI ya existe (solo al agregar, no al editar)
                if not (self.miembro and self.miembro.get("ID")):
                    cursor.execute("SELECT 1 FROM MiembroComunidad WHERE DNI = ?", (datos["DNI"],))
                    if cursor.fetchone():
                        MDSnackbar(MDLabel(text="Ya existe un miembro con ese DNI.")).open()
                        return

                if self.miembro and self.miembro.get("ID"):
                    # Editar
                    cursor.execute("""
                        UPDATE MiembroComunidad
                        SET Nombre=?, Apellido_Paterno=?, Apellido_Materno=?, DNI=?, Correo=?, Dirección=?, Teléfono=?
                        WHERE ID=?
                    """, (
                        datos["Nombre"], datos["Apellido_Paterno"], datos["Apellido_Materno"], datos["DNI"],
                        datos["Correo"], datos["Dirección"], datos["Teléfono"], self.miembro["ID"]
                    ))
                    mensaje = "Miembro actualizado"
                else:
                    # Agregar
                    cursor.execute("""
                        INSERT INTO MiembroComunidad (Nombre, Apellido_Paterno, Apellido_Materno, DNI, Correo, Dirección, Teléfono)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        datos["Nombre"], datos["Apellido_Paterno"], datos["Apellido_Materno"], datos["DNI"],
                        datos["Correo"], datos["Dirección"], datos["Teléfono"]
                    ))
                    mensaje = "Miembro agregado"
                conexion.commit()
                MDSnackbar(MDLabel(text=mensaje)).open()
                # Regresar al panel de miembros
                self.manager.current = "miembros"
                # Opcional: recargar la lista de miembros
                if hasattr(self.manager.get_screen("miembros"), "cargar_miembros"):
                    self.manager.get_screen("miembros").cargar_miembros()
            except Exception as e:
                print("Error al guardar miembro:", e)
                MDSnackbar(MDLabel(text="Error: Verifica que el DNI y correo no estén repetidos.")).open()
            finally:
                conexion.close()