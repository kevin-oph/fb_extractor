import customtkinter as ctk
from ui.tab_empleados import TabEmpleados
from ui.tab_comparador import TabComparador
from ui.tab_historial import TabHistorial
from utiles.estilos import COLOR_FONDO, COLOR_BLANCO
import modelos.bd

# Inicializa la base de datos (asegúrate que este módulo tiene la función)
modelos.bd.inicializar_bd()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")
        self.title("Extractor de Reacciones Facebook - Ayuntamiento")
        self.geometry("1200x760")
        self.configure(bg=COLOR_FONDO)

        # --------- Estado global compartido ----------
        self.historial_reportes = []  # Lista compartida por comparador e historial

        self.tabs = ctk.CTkTabview(self, fg_color=COLOR_BLANCO)
        self.tabs.pack(expand=True, fill="both", padx=0, pady=0)

        # Pasa la referencia de la lista global a los tabs
        self.tab_empleados = TabEmpleados(self.tabs)
        self.tab_historial = TabHistorial(self.tabs, self.historial_reportes)
        self.tab_comparador = TabComparador(self.tabs, self.historial_reportes, self.tab_historial)

if __name__ == "__main__":
    app = App()
    app.mainloop()
