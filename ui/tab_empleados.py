import customtkinter as ctk
from modelos.modelo import insertar_empleado, actualizar_empleado_por_id, eliminar_empleado_por_id, obtener_todos_empleados
from utiles.estilos import *
from tkinter import StringVar
from tkinter import messagebox

class TabEmpleados:
    def __init__(self, parent_tabs):
        self.tab = parent_tabs.add("Empleados")
        self.current_page = 1
        self.rows_per_page = 20
        self.departamento_filtrado = "Todos"
        self.empleados_all = []
        self.departamentos = []
        self.filtro_var = StringVar(value="Todos")
        self.frame_tabla = None
        self.frame_paginacion = None
        self.filtro_menu = None
        self.armar_vista_empleados()

    def armar_vista_empleados(self):
        parent = self.tab
        for widget in parent.winfo_children():
            widget.destroy()

        # --- Filtros y botón arriba ---
        frame_filtros = ctk.CTkFrame(parent, fg_color=COLOR_BLANCO)
        frame_filtros.pack(fill="x", padx=18, pady=(10, 2))

        ctk.CTkLabel(
            frame_filtros, text="Filtrar por departamento:", font=FUENTE_LABEL, text_color=COLOR_PRINCIPAL
        ).pack(side="left")

        # --- Obtén departamentos y empleados seguros (convierte a lista de dicts) ---
        empleados_lista = obtener_todos_empleados()
        if hasattr(empleados_lista, "to_dict"):
            empleados_lista = empleados_lista.to_dict(orient="records")
        if not empleados_lista or not isinstance(empleados_lista, list) or not isinstance(empleados_lista[0], dict):
            empleados_lista = []

        self.departamentos = ["Todos"] + sorted({e["departamento"] for e in empleados_lista if e["departamento"]})
        self.filtro_var = StringVar(value="Todos")
        self.filtro_menu = ctk.CTkOptionMenu(
            frame_filtros, variable=self.filtro_var, values=self.departamentos, width=180, fg_color=COLOR_PRINCIPAL
        )
        self.filtro_menu.pack(side="left", padx=6)
        self.filtro_var.trace_add('write', lambda *_: self.refrescar_tabla_empleados())

        # --- Botón de nuevo empleado (arriba a la derecha) ---
        ctk.CTkButton(
            frame_filtros, text="+ Nuevo empleado", fg_color="#297a12", command=self.ventana_nuevo_empleado
        ).pack(side="right", padx=6)

        # --- Título ---
        ctk.CTkLabel(
            parent, text="🧑‍💼 Administración de Empleados", font=("Segoe UI Bold", 22), text_color=COLOR_PRINCIPAL
        ).pack(pady=(10,8))

        # --- Tabla (marco) ---
        self.frame_tabla = ctk.CTkFrame(parent, fg_color=COLOR_BLANCO)
        self.frame_tabla.pack(fill="both", expand=True, padx=18, pady=(5, 2))

        # --- Paginación ---
        self.frame_paginacion = ctk.CTkFrame(parent, fg_color=COLOR_BLANCO)
        self.frame_paginacion.pack(fill="x", padx=18, pady=(0, 10))

        self.refrescar_tabla_empleados()

    def refrescar_tabla_empleados(self):
        empleados_db = obtener_todos_empleados()
        if hasattr(empleados_db, "to_dict"):
            empleados_db = empleados_db.to_dict(orient="records")
        if not empleados_db or not isinstance(empleados_db, list) or not isinstance(empleados_db[0], dict):
            empleados_db = []

        self.empleados_all = empleados_db
        depto = self.filtro_var.get()
        if depto and depto != "Todos":
            empleados = [e for e in empleados_db if e["departamento"] == depto]
        else:
            empleados = empleados_db

        total_empleados = len(empleados)
        total_pages = max(1, (total_empleados + self.rows_per_page - 1) // self.rows_per_page)
        self.current_page = min(self.current_page, total_pages)

        start = (self.current_page - 1) * self.rows_per_page
        end = start + self.rows_per_page
        empleados_pagina = empleados[start:end]

        self.mostrar_tabla_empleados(empleados_pagina, start)
        self.mostrar_paginacion(total_pages)

    def mostrar_tabla_empleados(self, empleados_pagina, start_idx):
        for widget in self.frame_tabla.winfo_children():
            widget.destroy()

        headers = ["#", "NOMBRE", "DEPARTAMENTO", "PUESTO", "NOMBRE_FB", "EDITAR", "ELIMINAR"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(
                self.frame_tabla, text=header, font=FUENTE_LABEL, text_color=COLOR_BLANCO,
                bg_color=COLOR_PRINCIPAL, anchor="center", width=140
            ).grid(row=0, column=col, padx=1, pady=3, sticky="nsew")

        for i, row in enumerate(empleados_pagina):
            idx_global = start_idx + i + 1
            ctk.CTkLabel(
                self.frame_tabla, text=f"{idx_global}", font=FUENTE_TABLA, text_color=COLOR_TEXTO, width=40,
                bg_color="#F3F4F7" if i%2==0 else "#FFFFFF", anchor="center"
            ).grid(row=i+1, column=0, padx=1, pady=2, sticky="nsew")
            ctk.CTkLabel(
                self.frame_tabla, text=row["nombre"], font=FUENTE_TABLA, text_color=COLOR_TEXTO, width=190,
                bg_color="#F3F4F7" if i%2==0 else "#FFFFFF", anchor="w"
            ).grid(row=i+1, column=1, padx=1, pady=2, sticky="nsew")
            ctk.CTkLabel(
                self.frame_tabla, text=row["departamento"], font=FUENTE_TABLA, text_color=COLOR_TEXTO, width=180,
                bg_color="#F3F4F7" if i%2==0 else "#FFFFFF", anchor="w"
            ).grid(row=i+1, column=2, padx=1, pady=2, sticky="nsew")
            ctk.CTkLabel(
                self.frame_tabla, text=row["puesto"], font=FUENTE_TABLA, text_color=COLOR_TEXTO, width=170,
                bg_color="#F3F4F7" if i%2==0 else "#FFFFFF", anchor="w"
            ).grid(row=i+1, column=3, padx=1, pady=2, sticky="nsew")
            ctk.CTkLabel(
                self.frame_tabla, text=row["nombre_fb"] or "---", font=FUENTE_TABLA, text_color=COLOR_TEXTO, width=170,
                bg_color="#F3F4F7" if i%2==0 else "#FFFFFF", anchor="w"
            ).grid(row=i+1, column=4, padx=1, pady=2, sticky="nsew")

            btn_editar = ctk.CTkButton(
                self.frame_tabla, text="Editar", fg_color="#e2b007",
                command=lambda row=row: self.ventana_editar_empleado(row)
            )
            btn_editar.grid(row=i+1, column=5, padx=2, pady=2, sticky="nsew")

            btn_eliminar = ctk.CTkButton(
                self.frame_tabla, text="Eliminar", fg_color="#c0392b",
                command=lambda row=row: self.eliminar_empleado(row)
            )
            btn_eliminar.grid(row=i+1, column=6, padx=2, pady=2, sticky="nsew")

    def mostrar_paginacion(self, total_pages):
        for widget in self.frame_paginacion.winfo_children():
            widget.destroy()

        ctk.CTkButton(
            self.frame_paginacion, text="〈 Anterior", fg_color=COLOR_PRINCIPAL,
            state="normal" if self.current_page > 1 else "disabled",
            command=self.pag_anterior
        ).pack(side="left", padx=4)

        ctk.CTkLabel(
            self.frame_paginacion, text=f"Página {self.current_page} de {total_pages}", font=FUENTE_TABLA
        ).pack(side="left", padx=7)

        ctk.CTkButton(
            self.frame_paginacion, text="Siguiente 〉", fg_color=COLOR_PRINCIPAL,
            state="normal" if self.current_page < total_pages else "disabled",
            command=self.pag_siguiente
        ).pack(side="left", padx=4)

    def pag_anterior(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.refrescar_tabla_empleados()

    def pag_siguiente(self):
        empleados_db = self.empleados_all
        depto = self.filtro_var.get()
        if depto and depto != "Todos":
            empleados = [e for e in empleados_db if e["departamento"] == depto]
        else:
            empleados = empleados_db
        total_empleados = len(empleados)
        total_pages = max(1, (total_empleados + self.rows_per_page - 1) // self.rows_per_page)

        if self.current_page < total_pages:
            self.current_page += 1
            self.refrescar_tabla_empleados()

    # --- Altas, edición y bajas ---
    def ventana_nuevo_empleado(self):
        def guardar_nuevo(data):
            try:
                insertar_empleado(data["nombre"], data["departamento"], data["puesto"], data["nombre_fb"])
                messagebox.showinfo("¡Listo!", "Empleado registrado correctamente.")
                self.refrescar_tabla_empleados()
                return True
            except Exception as e:
                messagebox.showerror("Error al registrar", str(e))
                return False
        VentanaEmpleado(self.tab, modo="nuevo", on_save=guardar_nuevo)

    def ventana_editar_empleado(self, row):
        def guardar_editado(data):
            try:
                actualizar_empleado_por_id(data["id"], data["nombre"], data["departamento"], data["puesto"], data["nombre_fb"])
                messagebox.showinfo("¡Listo!", "Empleado actualizado correctamente.")
                self.refrescar_tabla_empleados()
                return True
            except Exception as e:
                messagebox.showerror("Error al actualizar", str(e))
                return False
        VentanaEmpleado(self.tab, modo="editar", datos=row, on_save=guardar_editado)

    def eliminar_empleado(self, row):
        if messagebox.askyesno("Confirmar", f"¿Eliminar a {row['nombre']}?"):
            eliminar_empleado_por_id(row["id"])
            self.refrescar_tabla_empleados()


class VentanaEmpleado(ctk.CTkToplevel):
    def __init__(self, master, modo="nuevo", datos=None, on_save=None):
        super().__init__(master)
        self.title("Nuevo empleado" if modo=="nuevo" else "Editar empleado")
        self.geometry("440x370")
        self.modo = modo
        self.datos = datos or {}
        self.on_save = on_save

        self.resizable(False, False)
        self.grab_set()  # Ventana modal

        # --- Entradas ---
        ctk.CTkLabel(self, text="Nombre", anchor="w").pack(padx=18, pady=(18, 3), fill="x")
        self.input_nombre = ctk.CTkEntry(self)
        self.input_nombre.pack(padx=18, fill="x")
        self.input_nombre.insert(0, self.datos.get("nombre", ""))

        ctk.CTkLabel(self, text="Departamento", anchor="w").pack(padx=18, pady=(10, 3), fill="x")
        self.input_depto = ctk.CTkEntry(self)
        self.input_depto.pack(padx=18, fill="x")
        self.input_depto.insert(0, self.datos.get("departamento", ""))

        ctk.CTkLabel(self, text="Puesto", anchor="w").pack(padx=18, pady=(10, 3), fill="x")
        self.input_puesto = ctk.CTkEntry(self)
        self.input_puesto.pack(padx=18, fill="x")
        self.input_puesto.insert(0, self.datos.get("puesto", ""))

        ctk.CTkLabel(self, text="Nombre Facebook (opcional)", anchor="w").pack(padx=18, pady=(10, 3), fill="x")
        self.input_nombrefb = ctk.CTkEntry(self)
        self.input_nombrefb.pack(padx=18, fill="x")
        self.input_nombrefb.insert(0, self.datos.get("nombre_fb", ""))

        frame_btn = ctk.CTkFrame(self, fg_color="transparent")
        frame_btn.pack(pady=18)
        ctk.CTkButton(
            frame_btn, text="Guardar", fg_color="#218838", command=self.guardar
        ).pack(side="left", padx=(0, 12))
        ctk.CTkButton(
            frame_btn, text="Cancelar", fg_color="#b7b7b7", text_color="#333", command=self.destroy
        ).pack(side="left")

    def guardar(self):
        nombre = self.input_nombre.get().strip()
        depto = self.input_depto.get().strip()
        puesto = self.input_puesto.get().strip()
        nombre_fb = self.input_nombrefb.get().strip()

        if not nombre or not depto or not puesto:
            messagebox.showerror("Campos obligatorios", "Debes llenar nombre, departamento y puesto.")
            return

        if self.on_save:
            datos_guardar = {
                "nombre": nombre,
                "departamento": depto,
                "puesto": puesto,
                "nombre_fb": nombre_fb,
            }
            if self.modo == "editar":
                datos_guardar["id"] = self.datos.get("id")
            exito = self.on_save(datos_guardar)
            if exito:
                self.destroy()
