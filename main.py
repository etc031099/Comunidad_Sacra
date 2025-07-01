from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.core.window import Window

# Imports actualizados para la nueva estructura modular
from app.screens.core.login import LoginScreen
from app.screens.core.dashboard import DashboardScreen
from app.screens.asistencia.asistencia import AsistenciaScreen
from app.screens.reuniones.crear_reunion import CrearReunionScreen
from app.screens.miembros.miembros import MiembrosScreen
from app.screens.miembros.miembro_form import MiembroFormScreen
from app.screens.faenas.faenas import FaenasScreen
from app.screens.faenas.faena_form import FaenaFormScreen
from app.screens.faenas.asignar_faena import AsignarFaenaScreen
from app.screens.asistencia.asistencia_faena import AsistenciaFaenaScreen
from app.screens.justificaciones.justificaciones import JustificacionesScreen
from app.screens.penalizaciones.penalizaciones import PenalizacionesScreen
from app.screens.miembros.historial_miembro import HistorialMiembroScreen
from app.screens.asistencia.asistencia_menu import AsistenciaMenuScreen
from app.screens.reuniones.reuniones import ReunionesScreen
from app.screens.notificaciones.notificaciones import NotificacionesScreen
from app.screens.reportes.reportes import ReportesScreen


Builder.load_file('app/kv/login.kv')
Builder.load_file('app/kv/dashboard.kv')
Builder.load_file('app/kv/asistencia.kv')
Builder.load_file('app/kv/crear_reunion.kv')
Builder.load_file('app/kv/miembros.kv')
Builder.load_file('app/kv/miembro_form.kv')
Builder.load_file('app/kv/faenas.kv')
Builder.load_file('app/kv/faena_form.kv')
Builder.load_file('app/kv/asignar_faena.kv')
Builder.load_file('app/kv/asistencia_faena.kv')
Builder.load_file('app/kv/justificaciones.kv')
Builder.load_file('app/kv/penalizaciones.kv')
Builder.load_file('app/kv/historial_miembro.kv')
Builder.load_file('app/kv/asistencia_menu.kv')
Builder.load_file('app/kv/reuniones.kv')
Builder.load_file('app/kv/notificaciones.kv')
Builder.load_file('app/kv/reportes.kv')

class MainApp(MDApp):
    title = "Sistema de Asistencia - Sacra Familia"
    icon = "assets/images/aiease_1749954653564.jpg"
    def build(self):
        Window.maximize()
        sm = MDScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(AsistenciaScreen(name="asistencia"))
        sm.add_widget(CrearReunionScreen(name="crear_reunion"))
        sm.add_widget(MiembrosScreen(name="miembros"))
        sm.add_widget(MiembroFormScreen(name="miembro_form"))
        sm.add_widget(FaenasScreen(name="faenas"))
        sm.add_widget(FaenaFormScreen(name="faena_form"))
        sm.add_widget(AsignarFaenaScreen(name="asignar_faena"))
        sm.add_widget(AsistenciaFaenaScreen(name="asistencia_faena"))
        sm.add_widget(JustificacionesScreen(name="justificaciones"))
        sm.add_widget(PenalizacionesScreen(name="penalizaciones"))
        sm.add_widget(HistorialMiembroScreen(name="historial_miembro"))
        sm.add_widget(AsistenciaMenuScreen(name="asistencia_menu"))
        sm.add_widget(ReunionesScreen(name="reuniones"))
        sm.add_widget(NotificacionesScreen(name="notificaciones"))
        sm.add_widget(ReportesScreen(name="reportes"))
        return sm

if __name__ == '__main__':
    MainApp().run()
