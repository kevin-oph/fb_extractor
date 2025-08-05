import customtkinter as ctk
import bd
from PIL import Image
from estilos import *
from modelo import cargar_base_empleados, comparar_reacciones, agregar_reporte
from tabla import mostrar_tabla
from historial import mostrar_historial_en_tab
from utiles import obtener_lista_nombres
from tkinter import messagebox , filedialog


bd.inicializar_bd()
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")
        self.title("Extractor de Reacciones Facebook - Ayuntamiento")
        self.geometry("1200x760")
        self.configure(bg=COLOR_FONDO)

        self.df_empleados = None
        self.df_tabla_actual = None
        self.no_registrados = []
        self.reporte_posts = []

        # Tabs principales
        self.tabs = ctk.CTkTabview(self, fg_color=COLOR_BLANCO)
        self.tabs.pack(expand=True, fill="both", padx=0, pady=0)
        # ... (después de self.tabs = ctk.CTkTabview(self, fg_color=COLOR_BLANCO))
        self.tab_empleados = self.tabs.add("Empleados")
        self.armar_tab_empleados(self.tab_empleados)


        # 1. Comparador
        self.tab_comparador = self.tabs.add("Comparador")
        self.armar_vista_comparador(self.tab_comparador)

        # 2. Historial
        self.tab_historial = self.tabs.add("Historial")
        mostrar_historial_en_tab(self.tab_historial, self.reporte_posts)
        
        
    def cargar_excel_empleados(self):
        
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if not path:
            return
        try:
            import bd
            bd.importar_empleados_excel(path)
            messagebox.showinfo("¡Listo!", "Empleados importados exitosamente a la base de datos.")
            # Aquí podrías recargar la tabla de empleados si la tienes
        except Exception as e:
            messagebox.showerror("Error al importar", str(e))
        
        #tab empleados
    def armar_tab_empleados(self, parent):
        ctk.CTkLabel(
            parent, 
            text="🧑‍💼 Administración de Empleados",
            font=("Segoe UI Bold", 22),
            text_color=COLOR_PRINCIPAL
        ).pack(pady=(22,8))

        # Botón importar
        ctk.CTkButton(
            parent,
            text="Importar empleados desde Excel",
            fg_color=COLOR_PRINCIPAL,
            text_color=COLOR_BLANCO,
            command=self.cargar_excel_empleados
        ).pack(pady=6)
    
    # Aquí luego puedes poner la tabla de empleados, etc.


    def armar_vista_comparador(self, parent):
        
         # CABECERA
        frame_cabecera = ctk.CTkFrame(parent, fg_color=COLOR_BLANCO)
        frame_cabecera.pack(pady=(10, 0), fill="x")

        # Logo centrado y grande
        logo_img = ctk.CTkImage(light_image=Image.open("images/logo_app1.png"), size=(400, 220))
        lbl_logo = ctk.CTkLabel(frame_cabecera, image=logo_img, text="")
        lbl_logo.pack(pady=(5, 1))  # menos espacio debajo del logo
        
        # TÍTULO Y BOTÓN DE CARGA
        ctk.CTkLabel(
            parent, text="📋 Comparador de Reacciones Facebook",
            font=("Segoe UI Bold", 28), text_color=COLOR_PRINCIPAL
        ).pack(pady=(26,8))

        self.frame_files = ctk.CTkFrame(parent, fg_color=COLOR_PRINCIPAL)
        self.frame_files.pack(pady=12, padx=40, fill="x")
        self.btn_load_empleados = ctk.CTkButton(
            self.frame_files, text="Cargar Base Empleados (.xlsx)",
            fg_color=COLOR_ACENTO, text_color=COLOR_TEXTO, command=self.cargar_empleados
        )
        self.btn_load_empleados.pack(padx=10, pady=10, side="left")
        self.lbl_archivo = ctk.CTkLabel(self.frame_files, text="", font=FUENTE_LABEL, bg_color=COLOR_PRINCIPAL)
        self.lbl_archivo.pack(padx=10, pady=10, side="left")

        # ENTRADA PUBLICACIÓN Y NOMBRES
        self.frame_post = ctk.CTkFrame(parent, fg_color=COLOR_GRIS, corner_radius=8)
        self.frame_post.pack(pady=6, padx=40, fill="x")
        ctk.CTkLabel(
            self.frame_post, text="Identificador de la Publicación (obligatorio)",
            font=FUENTE_LABEL, text_color=COLOR_PRINCIPAL
        ).pack(anchor="w", padx=10, pady=(6,0))
        self.input_postid = ctk.CTkEntry(self.frame_post, font=FUENTE_LABEL)
        self.input_postid.pack(fill="x", padx=10, pady=(0,4))
        ctk.CTkLabel(
            self.frame_post, text="Pega los nombres que reaccionaron aquí:",
            font=FUENTE_LABEL, text_color=COLOR_PRINCIPAL
        ).pack(anchor="w", padx=10)
        self.textarea_nombres = ctk.CTkTextbox(
            self.frame_post, height=90, font=FUENTE_LABEL,
            border_color=COLOR_PRINCIPAL, border_width=2
        )
        self.textarea_nombres.pack(fill="x", padx=10, pady=(0,10))

        self.btn_comparar = ctk.CTkButton(
            parent, text="Comparar y Guardar Reporte",
            fg_color=COLOR_PRINCIPAL, text_color=COLOR_BLANCO,
            command=self.comparar
        )
        self.btn_comparar.pack(pady=10)

        # ----- FILTROS DASHBOARD -----
        self.frame_filtros = ctk.CTkFrame(parent, fg_color=COLOR_BLANCO)
        self.frame_filtros.pack(fill="x", padx=30, pady=(6, 0))

        self.filtro_dashboard = ctk.StringVar(value="Todos")
        self.btn_total = ctk.CTkButton(self.frame_filtros, text="Total: 0",
            command=lambda: self.mostrar_filtro_dashboard("Todos"), fg_color=COLOR_PRINCIPAL)
        self.btn_total.pack(side="left", padx=5, pady=8)
        self.btn_si = ctk.CTkButton(self.frame_filtros, text="Sí reaccionaron: 0",
            command=lambda: self.mostrar_filtro_dashboard("Si"), fg_color=COLOR_VERDE)
        self.btn_si.pack(side="left", padx=5)
        self.btn_no = ctk.CTkButton(self.frame_filtros, text="No reaccionaron: 0",
            command=lambda: self.mostrar_filtro_dashboard("No"), fg_color=COLOR_ROJO)
        self.btn_no.pack(side="left", padx=5)
        self.btn_noreg = ctk.CTkButton(self.frame_filtros, text="No registrados: 0",
            command=lambda: self.mostrar_filtro_dashboard("NoReg"), fg_color=COLOR_ACENTO)
        self.btn_noreg.pack(side="left", padx=5)

        # Frame para la tabla de resultados
        self.frame_tabla = ctk.CTkFrame(parent, fg_color=COLOR_BLANCO, corner_radius=10)
        self.frame_tabla.pack(fill="both", expand=True, padx=40, pady=(2, 10))

        # Frame para tabla de NO REGISTRADOS
        self.frame_noreg = ctk.CTkFrame(parent, fg_color=COLOR_BLANCO, corner_radius=10)
        self.frame_noreg.pack(fill="x", padx=40, pady=(0, 10))
        self.frame_noreg.pack_forget()  # Oculta por defecto

    def cargar_empleados(self):
        path = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xlsx")])
        if path:
            try:
                self.df_empleados = cargar_base_empleados(path)
                self.lbl_archivo.configure(
                    text=f"Archivo cargado: {len(self.df_empleados)} empleados.",
                    text_color=COLOR_BLANCO
                )
            except Exception as e:
                messagebox.showerror("Error al cargar archivo", str(e))

    def comparar(self):
        if self.df_empleados is None:
            messagebox.showerror("Error", "Primero carga la base de empleados.")
            return
        postid = self.input_postid.get().strip()
        if not postid:
            messagebox.showerror("Error", "Debes ingresar el identificador de la publicación.")
            return
        nombres_txt = self.textarea_nombres.get("1.0", "end")
        lista_nombres = obtener_lista_nombres(nombres_txt)
        df_resultado, no_registrados = comparar_reacciones(self.df_empleados, lista_nombres)
        self.df_tabla_actual = df_resultado
        self.no_registrados = no_registrados

        total = len(df_resultado)
        si = df_resultado["reacciono"].sum()
        no = (df_resultado["reacciono"] == False).sum()
        noreg = len(no_registrados)

        self.btn_total.configure(text=f"Total: {total}")
        self.btn_si.configure(text=f"Sí reaccionaron: {si}")
        self.btn_no.configure(text=f"No reaccionaron: {no}")
        self.btn_noreg.configure(text=f"No registrados: {noreg}")

        # Guarda el reporte para historial
        agregar_reporte(
            self.reporte_posts,
            postid, "", "", df_resultado, no_registrados
        )

        # Muestra todos por defecto
        self.mostrar_filtro_dashboard("Todos")
        # Actualiza historial
        mostrar_historial_en_tab(self.tab_historial, self.reporte_posts)

        # Limpiar campos
        self.input_postid.delete(0, "end")
        self.textarea_nombres.delete("1.0", "end")

        messagebox.showinfo("Registro guardado", "¡El registro se guardó exitosamente!")

    def mostrar_filtro_dashboard(self, filtro):
        """Filtra la tabla según el filtro dashboard elegido."""
        if self.df_tabla_actual is None:
            return
        df = self.df_tabla_actual
        self.frame_noreg.pack_forget()  # Oculta por defecto

        if filtro == "Todos":
            mostrar_tabla(self.frame_tabla, df)
        elif filtro == "Si":
            mostrar_tabla(self.frame_tabla, df[df["reacciono"] == True])
        elif filtro == "No":
            mostrar_tabla(self.frame_tabla, df[df["reacciono"] == False])
        elif filtro == "NoReg":
            self.frame_tabla.pack_forget()
            self.frame_noreg.pack(fill="x", padx=40, pady=(0, 10))
            self.mostrar_no_registrados_tabla()
        else:
            mostrar_tabla(self.frame_tabla, df)

        # Muestra/oculta frame principal de tabla según filtro
        if filtro != "NoReg":
            self.frame_tabla.pack(fill="both", expand=True, padx=40, pady=(2, 10))
            self.frame_noreg.pack_forget()

    def mostrar_no_registrados_tabla(self):
        """Muestra la tabla de nombres no registrados en frame_noreg."""
        for widget in self.frame_noreg.winfo_children():
            widget.destroy()
        ctk.CTkLabel(
            self.frame_noreg, text="Nombres no registrados",
            font=("Segoe UI Bold", 18), text_color=COLOR_PRINCIPAL
        ).pack(pady=(8, 0))
        frame_scroll = ctk.CTkScrollableFrame(self.frame_noreg, fg_color=COLOR_BLANCO, height=180)
        frame_scroll.pack(fill="x", padx=6, pady=(3, 8))
        for i, nombre in enumerate(self.no_registrados):
            ctk.CTkLabel(
                frame_scroll, text=nombre, font=FUENTE_TABLA,
                text_color=COLOR_TEXTO, bg_color=COLOR_BLANCO, anchor="w"
            ).grid(row=i, column=0, sticky="w", padx=12, pady=2)

if __name__ == "__main__":
    app = App()
    app.mainloop()
