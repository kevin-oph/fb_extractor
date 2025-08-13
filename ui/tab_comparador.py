import customtkinter as ctk
from PIL import Image
from utiles.estilos import *
from modelos.modelo import obtener_todos_empleados, comparar_reacciones, agregar_reporte
from tabla import mostrar_tabla
from utiles.utiles import obtener_lista_nombres
from tkinter import messagebox

class TabComparador:
    def __init__(self, parent_tabs, historial_reportes, tab_historial):
        self.tab = parent_tabs.add("Comparador")
        self.df_tabla_actual = None
        self.no_registrados = []
        self.historial_reportes = historial_reportes
        self.tab_historial = tab_historial
        self.pagina_actual = 1
        self.filtro_dashboard = ctk.StringVar(value="Todos")
        self.departamentos = []
        self.depto_filtro_var = ctk.StringVar(value="Todos")
        self.armar_vista_comparador(self.tab)

    def armar_vista_comparador(self, parent):
        # --- SCROLLABLE GENERAL ---
        self.main_scroll = ctk.CTkScrollableFrame(parent, fg_color=COLOR_BLANCO, height=880)
        self.main_scroll.pack(fill="both", expand=True, padx=0, pady=(0, 0))

        # Cabecera y logo
        frame_cabecera = ctk.CTkFrame(self.main_scroll, fg_color=COLOR_BLANCO)
        frame_cabecera.pack(pady=(10, 0), fill="x")
        try:
            logo_img = ctk.CTkImage(light_image=Image.open("images/logo_app1.png"), size=(400, 220))
            lbl_logo = ctk.CTkLabel(frame_cabecera, image=logo_img, text="")
            lbl_logo.pack(pady=(5, 1))
        except Exception:
            pass

        ctk.CTkLabel(
            self.main_scroll, text="📋 Comparador de Reacciones Facebook",
            font=("Segoe UI Bold", 28), text_color=COLOR_PRINCIPAL
        ).pack(pady=(26,8))

        # Inputs publicación
        self.frame_post = ctk.CTkFrame(self.main_scroll, fg_color=COLOR_GRIS, corner_radius=8)
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
            self.main_scroll, text="Comparar y Guardar Reporte",
            fg_color=COLOR_PRINCIPAL, text_color=COLOR_BLANCO,
            command=self.comparar
        )
        self.btn_comparar.pack(pady=10)

        # --- Filtro de departamento sobre la tabla ---
        frame_tabla_filtros = ctk.CTkFrame(self.main_scroll, fg_color=COLOR_BLANCO)
        frame_tabla_filtros.pack(fill="x", padx=44, pady=(12, 4))
        ctk.CTkLabel(
            frame_tabla_filtros,
            text="Filtrar empleados por departamento:",
            font=FUENTE_LABEL, text_color=COLOR_PRINCIPAL
        ).pack(side="left", padx=(4,4))

        self.actualizar_departamentos()

        # --- Opción 1: OptionMenu más pequeño (estilo compacto) ---
        self.filtro_menu = ctk.CTkOptionMenu(
            frame_tabla_filtros,
            variable=self.depto_filtro_var,
            values=self.departamentos,
            width=130,   # más pequeño
            fg_color="#fff",
            button_color=COLOR_PRINCIPAL,
            button_hover_color=COLOR_ACENTO,
            text_color=COLOR_PRINCIPAL
        )
        self.filtro_menu.pack(side="left", padx=4)

        # --- Opción 2: Lista de departamentos con scroll (si tienes muchos) ---
        # Descomenta esto si tienes demasiados departamentos y quieres que se vea un "dropdown" con scroll.
        # from tkinter import Listbox
        # if len(self.departamentos) > 10:
        #     listbox_frame = ctk.CTkFrame(frame_tabla_filtros, fg_color=COLOR_BLANCO)
        #     listbox_frame.pack(side="left", padx=4)
        #     self.listbox_deptos = Listbox(listbox_frame, height=6)
        #     for depto in self.departamentos:
        #         self.listbox_deptos.insert("end", depto)
        #     self.listbox_deptos.pack(side="left")
        #     # Aquí le agregas funcionalidad: cuando seleccionen un depto, actualizas self.depto_filtro_var.set(...)

        self.depto_filtro_var.trace_add('write', lambda *_: self.filtrar_por_departamento())

        # --- Filtros dashboard ---
        self.frame_filtros = ctk.CTkFrame(self.main_scroll, fg_color=COLOR_BLANCO)
        self.frame_filtros.pack(fill="x", padx=30, pady=(6, 0))
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

        self.frame_tabla = ctk.CTkFrame(self.main_scroll, fg_color=COLOR_BLANCO, corner_radius=10)
        self.frame_tabla.pack(fill="both", expand=True, padx=40, pady=(2, 10))

        self.frame_noreg = ctk.CTkFrame(self.main_scroll, fg_color=COLOR_BLANCO, corner_radius=10)
        self.frame_noreg.pack(fill="x", padx=40, pady=(0, 10))
        self.frame_noreg.pack_forget()


    def actualizar_departamentos(self):
        empleados = obtener_todos_empleados()
        if hasattr(empleados, "columns"):  # Es DataFrame
            departamentos = sorted(list(set(empleados["departamento"].dropna())))
        else:  # Lista de dict
            departamentos = sorted(list(set(e["departamento"] for e in empleados if e.get("departamento"))))
        self.departamentos = ["Todos"] + departamentos

    def filtrar_por_departamento(self):
        if self.df_tabla_actual is not None:
            self.comparar(filtrar=True)

    def comparar(self, filtrar=False):
        empleados = obtener_todos_empleados()
        depto = self.depto_filtro_var.get()
        if depto and depto != "Todos":
            if hasattr(empleados, "columns"):
                empleados = empleados[empleados["departamento"] == depto]
            else:
                empleados = [e for e in empleados if e["departamento"] == depto]

        if hasattr(empleados, "empty"):
            if empleados.empty:
                messagebox.showerror("Error", "La base de empleados está vacía. Agrega empleados en la pestaña correspondiente.")
                return
        elif not empleados:
            messagebox.showerror("Error", "La base de empleados está vacía. Agrega empleados en la pestaña correspondiente.")
            return

        postid = self.input_postid.get().strip()
        if not postid and not filtrar:
            messagebox.showerror("Error", "Debes ingresar el identificador de la publicación.")
            return
        nombres_txt = self.textarea_nombres.get("1.0", "end")
        lista_nombres = obtener_lista_nombres(nombres_txt)
        df_resultado, no_registrados = comparar_reacciones(empleados, lista_nombres)
        self.df_tabla_actual = df_resultado
        self.no_registrados = no_registrados
        self.pagina_actual = 1

        total = len(df_resultado)
        si = df_resultado["reacciono"].sum()
        no = (df_resultado["reacciono"] == False).sum()
        noreg = len(no_registrados)

        self.btn_total.configure(text=f"Total: {total}")
        self.btn_si.configure(text=f"Sí reaccionaron: {si}")
        self.btn_no.configure(text=f"No reaccionaron: {no}")
        self.btn_noreg.configure(text=f"No registrados: {noreg}")

        if not filtrar:
            agregar_reporte(
                self.historial_reportes,
                postid, "", "", df_resultado, no_registrados
            )
            if self.tab_historial:
                self.tab_historial.refrescar_historial()

        self.mostrar_filtro_dashboard("Todos")

        if not filtrar:
            self.input_postid.delete(0, "end")
            self.textarea_nombres.delete("1.0", "end")
            messagebox.showinfo("Registro guardado", "¡El registro se guardó exitosamente!")

    def mostrar_filtro_dashboard(self, filtro):
        if self.df_tabla_actual is None:
            for widget in self.frame_tabla.winfo_children():
                widget.destroy()
            return
        df = self.df_tabla_actual
        self.frame_noreg.pack_forget()
        if filtro == "Todos":
            self.frame_tabla.pack(fill="both", expand=True, padx=40, pady=(2, 10))
            self.frame_noreg.pack_forget()
            mostrar_tabla(self.frame_tabla, df, modo="comparador", pagina=self.pagina_actual, on_pagina=self.cambiar_pagina)
        elif filtro == "Si":
            self.frame_tabla.pack(fill="both", expand=True, padx=40, pady=(2, 10))
            self.frame_noreg.pack_forget()
            mostrar_tabla(self.frame_tabla, df[df["reacciono"] == True], modo="comparador", pagina=self.pagina_actual, on_pagina=self.cambiar_pagina)
        elif filtro == "No":
            self.frame_tabla.pack(fill="both", expand=True, padx=40, pady=(2, 10))
            self.frame_noreg.pack_forget()
            mostrar_tabla(self.frame_tabla, df[df["reacciono"] == False], modo="comparador", pagina=self.pagina_actual, on_pagina=self.cambiar_pagina)
        elif filtro == "NoReg":
            self.frame_tabla.pack_forget()
            self.frame_noreg.pack(fill="x", padx=40, pady=(0, 10))
            self.mostrar_no_registrados_tabla()
        else:
            self.frame_tabla.pack(fill="both", expand=True, padx=40, pady=(2, 10))
            self.frame_noreg.pack_forget()
            mostrar_tabla(self.frame_tabla, df, modo="comparador", pagina=self.pagina_actual, on_pagina=self.cambiar_pagina)

    def cambiar_pagina(self, nueva_pagina):
        self.pagina_actual = nueva_pagina
        self.mostrar_filtro_dashboard(self.filtro_dashboard.get())

    def mostrar_no_registrados_tabla(self):
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
