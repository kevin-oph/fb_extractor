# ui/tab_comparador.py
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

        # Estado
        self.df_tabla_actual = None
        self.no_registrados = []
        self.historial_reportes = historial_reportes
        self.tab_historial = tab_historial

        # Paginación propia de la tabla renderizada por mostrar_tabla()
        self.pagina_actual = 0

        # Filtro activo del dashboard (Todos / Si / No / NoReg)
        self.filtro_dashboard = ctk.StringVar(value="Todos")

        # Filtro por dpto (combobox con scroll)
        self.departamentos = []
        self.depto_filtro_var = ctk.StringVar(value="Todos")

        # Contenedor con scroll (como en Historial)
        self.container = ctk.CTkScrollableFrame(self.tab, fg_color=COLOR_BLANCO, height=880)
        self.container.pack(fill="both", expand=True, padx=0, pady=0)

        self.armar_vista_comparador(self.container)

    # ----------------- UI -----------------
    def armar_vista_comparador(self, parent):
        # Cabecera + logo
        frame_cabecera = ctk.CTkFrame(parent, fg_color=COLOR_BLANCO)
        frame_cabecera.pack(pady=(10, 0), fill="x")
        try:
            logo_img = ctk.CTkImage(light_image=Image.open("images/logo_app1.png"), size=(400, 220))
            ctk.CTkLabel(frame_cabecera, image=logo_img, text="").pack(pady=(5, 1))
        except Exception:
            pass

        ctk.CTkLabel(
            parent, text="📋 Comparador de Reacciones Facebook",
            font=("Segoe UI Bold", 28), text_color=COLOR_PRINCIPAL
        ).pack(pady=(26, 8))

        # Entrada publicación y nombres
        self.frame_post = ctk.CTkFrame(parent, fg_color=COLOR_GRIS, corner_radius=8)
        self.frame_post.pack(pady=6, padx=40, fill="x")

        ctk.CTkLabel(
            self.frame_post, text="Identificador de la Publicación (obligatorio)",
            font=FUENTE_LABEL, text_color=COLOR_PRINCIPAL
        ).pack(anchor="w", padx=10, pady=(10, 0))

        self.input_postid = ctk.CTkEntry(self.frame_post, font=FUENTE_LABEL)
        self.input_postid.pack(fill="x", padx=10, pady=(0, 8))

        ctk.CTkLabel(
            self.frame_post, text="Pega los nombres que reaccionaron aquí:",
            font=FUENTE_LABEL, text_color=COLOR_PRINCIPAL
        ).pack(anchor="w", padx=10)

        self.textarea_nombres = ctk.CTkTextbox(
            self.frame_post, height=90, font=FUENTE_LABEL,
            border_color=COLOR_PRINCIPAL, border_width=2
        )
        self.textarea_nombres.pack(fill="x", padx=10, pady=(0, 10))

        self.btn_comparar = ctk.CTkButton(
            parent, text="Comparar y Guardar Reporte",
            fg_color=COLOR_PRINCIPAL, text_color=COLOR_BLANCO,
            command=self.comparar
        )
        self.btn_comparar.pack(pady=10)

        # --- Filtro por Departamento (encima de la tabla) ---
        filtro_frame = ctk.CTkFrame(parent, fg_color=COLOR_BLANCO)
        filtro_frame.pack(fill="x", padx=40, pady=(8, 0))

        ctk.CTkLabel(
            filtro_frame, text="Filtrar empleados por departamento:",
            font=FUENTE_LABEL, text_color=COLOR_PRINCIPAL
        ).pack(side="left", padx=(4, 6))

        self.actualizar_departamentos()  # llena self.departamentos = ["Todos", ...]
        # CTkComboBox con dropdown scrolleable
        self.combo_depto = ctk.CTkComboBox(
            filtro_frame,
            values=self.departamentos,
            variable=self.depto_filtro_var,
            width=240,
            justify="left",
            fg_color="#ffffff",
            border_color=COLOR_PRINCIPAL,
            button_color=COLOR_PRINCIPAL,
            button_hover_color=COLOR_ACENTO,
            dropdown_fg_color="#ffffff",
            dropdown_hover_color="#ededed",
            command=lambda *_: self.on_cambio_departamento()
        )
        self.combo_depto.pack(side="left", padx=(0, 8), pady=6)

        # Filtros dashboard (Total / Sí / No / NoReg)
        self.frame_filtros = ctk.CTkFrame(parent, fg_color=COLOR_BLANCO)
        self.frame_filtros.pack(fill="x", padx=40, pady=(6, 0))

        self.btn_total = ctk.CTkButton(
            self.frame_filtros, text="Total: 0", fg_color=COLOR_PRINCIPAL,
            command=lambda: self.mostrar_filtro_dashboard("Todos", reset_pagina=True)
        )
        self.btn_total.pack(side="left", padx=5, pady=8)

        self.btn_si = ctk.CTkButton(
            self.frame_filtros, text="Sí reaccionaron: 0", fg_color=COLOR_VERDE,
            command=lambda: self.mostrar_filtro_dashboard("Si", reset_pagina=True)
        )
        self.btn_si.pack(side="left", padx=5)

        self.btn_no = ctk.CTkButton(
            self.frame_filtros, text="No reaccionaron: 0", fg_color=COLOR_ROJO,
            command=lambda: self.mostrar_filtro_dashboard("No", reset_pagina=True)
        )
        self.btn_no.pack(side="left", padx=5)

        self.btn_noreg = ctk.CTkButton(
            self.frame_filtros, text="No registrados: 0", fg_color=COLOR_ACENTO,
            command=lambda: self.mostrar_filtro_dashboard("NoReg", reset_pagina=True)
        )
        self.btn_noreg.pack(side="left", padx=5)

        # Tabla de resultados
        self.frame_tabla = ctk.CTkFrame(parent, fg_color=COLOR_BLANCO, corner_radius=10)
        self.frame_tabla.pack(fill="both", expand=True, padx=40, pady=(6, 10))

        # Tabla de NO REGISTRADOS (oculta al inicio)
        self.frame_noreg = ctk.CTkFrame(parent, fg_color=COLOR_BLANCO, corner_radius=10)
        self.frame_noreg.pack(fill="x", padx=40, pady=(0, 10))
        self.frame_noreg.pack_forget()

        # Footer/espaciado para “respirar” visualmente
        ctk.CTkFrame(parent, fg_color=COLOR_BLANCO, height=70).pack(fill="x", pady=(10, 0))

    # ----------------- LÓGICA -----------------
    def actualizar_departamentos(self):
        empleados = obtener_todos_empleados()
        # Soporta DataFrame o lista de dicts
        if hasattr(empleados, "columns"):  # DataFrame
            try:
                departamentos = sorted(list(set(empleados["departamento"].dropna())))
            except Exception:
                departamentos = []
        else:  # Lista de dicts
            departamentos = sorted(list(set(e.get("departamento") for e in empleados if e.get("departamento"))))
        self.departamentos = ["Todos"] + departamentos
        # Refresca combobox si ya existe
        if hasattr(self, "combo_depto"):
            self.combo_depto.configure(values=self.departamentos)
            if self.depto_filtro_var.get() not in self.departamentos:
                self.depto_filtro_var.set("Todos")

    def on_cambio_departamento(self):
        """Cuando cambie el departamento, recomparamos con el nuevo universo de empleados filtrado."""
        # resetear paginación SIEMPRE que cambie el dpto
        self.pagina_actual = 0
        # Si ya hay algo comparado, recomparar con filtrar=True (no guarda historial)
        if self.df_tabla_actual is not None:
            self.comparar(filtrar=True)
        # Si aún no hay comparación, no hacemos nada hasta que el usuario compare

    def comparar(self, filtrar=False):
        empleados = obtener_todos_empleados()

        # Aplica filtro por dpto si corresponde
        depto = self.depto_filtro_var.get()
        if depto and depto != "Todos":
            if hasattr(empleados, "columns"):
                empleados = empleados[empleados["departamento"] == depto]
            else:
                empleados = [e for e in empleados if e.get("departamento") == depto]

        # Validación base
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

        # Compara
        df_resultado, no_registrados = comparar_reacciones(empleados, lista_nombres)
        self.df_tabla_actual = df_resultado
        self.no_registrados = no_registrados

        # SIEMPRE reset pagina al comparar (evita quedar fuera de rango)
        self.pagina_actual = 0

        # KPIs
        total = len(df_resultado)
        si = int(df_resultado["reacciono"].sum()) if total else 0
        no = int((df_resultado["reacciono"] == False).sum()) if total else 0
        noreg = len(no_registrados)

        self.btn_total.configure(text=f"Total: {total}")
        self.btn_si.configure(text=f"Sí reaccionaron: {si}")
        self.btn_no.configure(text=f"No reaccionaron: {no}")
        self.btn_noreg.configure(text=f"No registrados: {noreg}")

        # Guarda en historial sólo si NO es filtrado
        if not filtrar:
            agregar_reporte(self.historial_reportes, postid, "", "", df_resultado, no_registrados)
            if self.tab_historial:
                self.tab_historial.refrescar_historial()

        # Muestra datos (mantén el filtro activo o por defecto "Todos")
        filtro_activo = self.filtro_dashboard.get() or "Todos"
        self.mostrar_filtro_dashboard(filtro_activo, reset_pagina=False)

        # Limpia campos y confirma si fue comparación normal
        if not filtrar:
            self.input_postid.delete(0, "end")
            self.textarea_nombres.delete("1.0", "end")
            messagebox.showinfo("Registro guardado", "¡El registro se guardó exitosamente!")

    def mostrar_filtro_dashboard(self, filtro, reset_pagina=True):
        """Renderiza la tabla con el filtro del dashboard. Resetea paginación si se solicita."""
        if self.df_tabla_actual is None:
            for w in self.frame_tabla.winfo_children():
                w.destroy()
            return

        # Guarda filtro activo y resetea paginación si cambiamos de filtro
        self.filtro_dashboard.set(filtro)
        if reset_pagina:
            self.pagina_actual = 0

        # Prepara subset según filtro
        df = self.df_tabla_actual
        self.frame_noreg.pack_forget()

        if filtro == "Todos":
            df_subset = df
            self.frame_tabla.pack(fill="both", expand=True, padx=40, pady=(6, 10))

        elif filtro == "Si":
            df_subset = df[df["reacciono"] == True]
            self.frame_tabla.pack(fill="both", expand=True, padx=40, pady=(6, 10))

        elif filtro == "No":
            df_subset = df[df["reacciono"] == False]
            self.frame_tabla.pack(fill="both", expand=True, padx=40, pady=(6, 10))

        elif filtro == "NoReg":
            df_subset = None
            self.frame_tabla.pack_forget()
            self.frame_noreg.pack(fill="x", padx=40, pady=(0, 10))
            self.mostrar_no_registrados_tabla()

        else:
            df_subset = df
            self.frame_tabla.pack(fill="both", expand=True, padx=40, pady=(6, 10))

        # Render de tabla si aplica
        if df_subset is not None:
            # Si el número de páginas para este subset es menor y estabas en una página alta, rehúsa quedarte vacío
            self._render_tabla_pag(df_subset)

    def _render_tabla_pag(self, df_subset):
        """Pintar tabla + paginación única desde mostrar_tabla, robusto a cambios de cantidad de filas."""
        # Calcular total de páginas con el tamaño por defecto (30) que usa mostrar_tabla
        filas_por_pagina = 30
        total_filas = len(df_subset)
        total_paginas = (total_filas + filas_por_pagina - 1) // filas_por_pagina
        if total_paginas == 0:
            total_paginas = 1

        # Si estás en una página fuera de rango para este subset, vuelve a 0
        if self.pagina_actual > total_paginas - 1:
            self.pagina_actual = 0

        # Si no hay filas, muestra un mensaje claro
        if total_filas == 0:
            for w in self.frame_tabla.winfo_children():
                w.destroy()
            ctk.CTkLabel(
                self.frame_tabla,
                text="No hay empleados que cumplan el filtro seleccionado.",
                font=FUENTE_LABEL, text_color=COLOR_PRINCIPAL
            ).pack(pady=30)
            return

        # Render de tabla con callback de paginado
        mostrar_tabla(
            self.frame_tabla,
            df_subset,
            modo="comparador",
            pagina=self.pagina_actual,
            filas_por_pagina=filas_por_pagina,
            on_pagina=self.cambiar_pagina
        )

    def cambiar_pagina(self, nueva_pagina):
        """Callback que se invoca desde mostrar_tabla al navegar páginas."""
        self.pagina_actual = max(0, int(nueva_pagina))
        # Re-render con el filtro activo
        filtro = self.filtro_dashboard.get() or "Todos"
        self.mostrar_filtro_dashboard(filtro, reset_pagina=False)

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
