import customtkinter as ctk
from utiles.estilos import *
import pandas as pd
from tabla import mostrar_tabla
from tkinter import messagebox
from pdf_report import exportar_tabla_pdf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TabHistorial:
    def __init__(self, parent_tabs, historial_reportes):
        self.tab = parent_tabs.add("Historial")
        self.historial_reportes = historial_reportes
        self.publicaciones = []
        self.publicaciones_full = []
        self.reporte_actual_idx = 0
        self.departamentos_all = []
        self.var_depto = None
        self.input_buscar = None
        self.tabla_pagina_actual = 1
        self.tabla_rows_per_page = 20
        self.armar_vista_historial()

    def exportar_pdf_tabla_filtrada(self):
        idx = self.reporte_actual_idx
        rep = self.historial_reportes[idx]
        df = rep.get('df_resultado', pd.DataFrame())
        depto = self.var_depto.get() if self.var_depto else "Todos"
        if depto == "Todos":
            df_filtrado = df
        else:
            df_filtrado = df[df['departamento'] == depto]
        try:
            exportar_tabla_pdf(
                titulo=rep.get('titulo_publicacion', "Reporte"),
                departamento=depto,
                df=df_filtrado,
                logo_path="images/logo_app1.png"
            )
            messagebox.showinfo("¡Listo!", "Reporte PDF generado exitosamente.")
        except Exception as e:
            messagebox.showerror("Error al exportar PDF", str(e))

    def armar_vista_historial(self):
        parent = self.tab
        for widget in parent.winfo_children():
            widget.destroy()
        self.main_scroll = ctk.CTkScrollableFrame(parent, fg_color=COLOR_BLANCO, height=880)
        self.main_scroll.pack(fill="both", expand=True, padx=0, pady=(0, 0))

        # HEADER
        frame_header = ctk.CTkFrame(self.main_scroll, fg_color=COLOR_BLANCO)
        frame_header.pack(fill="x", padx=28, pady=(10, 6))
        ctk.CTkLabel(
            frame_header,
            text="📊 Historial de Publicaciones Comparadas",
            font=("Segoe UI Bold", 24),
            text_color=COLOR_PRINCIPAL,
            bg_color=COLOR_BLANCO
        ).pack(side="left", padx=(10, 14), pady=(8,4))
        self.input_buscar = ctk.CTkEntry(frame_header, font=FUENTE_LABEL, width=320)
        self.input_buscar.pack(side="left", padx=10)
        self.input_buscar.bind("<KeyRelease>", self.on_filtrar)

        # LISTA PUBLICACIONES
        self.frame_lista = ctk.CTkScrollableFrame(self.main_scroll, fg_color=COLOR_GRIS, height=80)
        self.frame_lista.pack(fill="x", padx=28, pady=(0, 14))

        # REPORTE PRINCIPAL (solo una vez)
        self.frame_reporte = ctk.CTkFrame(self.main_scroll, fg_color=COLOR_BLANCO)
        self.frame_reporte.pack(fill="both", expand=True, padx=16, pady=12)

        self.actualizar_lista_publicaciones()
        if self.publicaciones:
            self.mostrar_tabla_reporte(self.publicaciones[0][1])

        ctk.CTkFrame(self.main_scroll, fg_color=COLOR_BLANCO, height=80).pack(fill="x", pady=4)

    def refrescar_historial(self):
        self.armar_vista_historial()

    def on_filtrar(self, event=None):
        q = self.input_buscar.get().strip().lower()
        if not q:
            self.actualizar_lista_publicaciones()
        else:
            pubs_filtradas = [(txt, idx) for (txt, idx) in self.publicaciones_full if q in txt.lower()]
            self.publicaciones = pubs_filtradas
            self.mostrar_lista_publicaciones()

    def actualizar_lista_publicaciones(self):
        self.publicaciones = []
        for idx, rep in enumerate(self.historial_reportes):
            titulo = rep.get('titulo_publicacion', '(Sin título)')
            mensaje = rep.get('post_mensaje', '')
            txt = f"{idx+1}. {titulo}"
            if mensaje:
                txt += f"  |  {mensaje[:70]}"
            self.publicaciones.append((txt, idx))
        self.publicaciones_full = self.publicaciones.copy()
        self.mostrar_lista_publicaciones()

    def mostrar_lista_publicaciones(self):
        for widget in self.frame_lista.winfo_children():
            widget.destroy()
        for txt, idx in self.publicaciones:
            btn = ctk.CTkButton(
                self.frame_lista,
                text=txt,
                fg_color=COLOR_PRINCIPAL,
                text_color=COLOR_BLANCO,
                anchor="w",
                font=FUENTE_LABEL,
                command=lambda i=idx: self.mostrar_tabla_reporte(i)
            )
            btn.pack(pady=2, padx=4, anchor="w")

    def mostrar_tabla_reporte(self, idx):
        for widget in self.frame_reporte.winfo_children():
            widget.destroy()
        self.reporte_actual_idx = idx
        rep = self.historial_reportes[idx]
        df = rep.get('df_resultado', pd.DataFrame())
        titulo = rep.get('titulo_publicacion', '(Sin título)')
        mensaje = rep.get('post_mensaje', '')
        self.tabla_pagina_actual = 1

        # TITULO
        frame_titulo = ctk.CTkFrame(self.frame_reporte, fg_color=COLOR_BLANCO)
        frame_titulo.pack(fill="x", padx=0, pady=(8, 0))
        ctk.CTkLabel(
            frame_titulo,
            text=f"📰  Título de la publicación: {titulo}",
            font=("Segoe UI Bold", 22),
            text_color=COLOR_PRINCIPAL,
            bg_color=COLOR_BLANCO,
            anchor="w"
        ).pack(pady=(10,4), padx=16, anchor="w")
        if mensaje:
            ctk.CTkLabel(
                frame_titulo,
                text=mensaje,
                font=("Segoe UI", 16),
                text_color="#226f43",
                bg_color=COLOR_BLANCO,
                anchor="w"
            ).pack(pady=(0,4), padx=18, anchor="w")

        # FILTRO DEPARTAMENTO y PDF
        self.departamentos_all = sorted(list(df['departamento'].dropna().unique()))
        self.departamentos_all.insert(0, "Todos")
        self.var_depto = ctk.StringVar(value="Todos")

        frame_filtro = ctk.CTkFrame(self.frame_reporte, fg_color=COLOR_BLANCO)
        frame_filtro.pack(fill="x", padx=20, pady=(0,7))
        ctk.CTkLabel(
            frame_filtro,
            text="Filtrar por departamento:",
            font=FUENTE_LABEL,
            text_color=COLOR_PRINCIPAL
        ).pack(side="left", padx=(8,4))
        filtro_menu = ctk.CTkOptionMenu(
            frame_filtro,
            variable=self.var_depto,
            values=self.departamentos_all,
            width=210,
            fg_color="#f0f0f0",
            button_color=COLOR_PRINCIPAL,
            button_hover_color=COLOR_ACENTO,
            text_color=COLOR_PRINCIPAL
        )
        filtro_menu.pack(side="left", padx=8)

        btn_pdf = ctk.CTkButton(
            frame_filtro,
            text="Exportar PDF tabla filtrada",
            fg_color=COLOR_PRINCIPAL,
            text_color=COLOR_BLANCO,
            font=FUENTE_LABEL,
            command=self.exportar_pdf_tabla_filtrada
        )
        btn_pdf.pack(side="right", padx=12)

        ctk.CTkFrame(self.frame_reporte, fg_color="#cccccc", height=2).pack(fill="x", padx=8, pady=(6,16))

        # TABLA
        self.frame_tabla = ctk.CTkFrame(self.frame_reporte, fg_color=COLOR_BLANCO)
        self.frame_tabla.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        self.frame_tabla_paginacion = ctk.CTkFrame(self.frame_reporte, fg_color=COLOR_BLANCO)
        self.frame_tabla_paginacion.pack(fill="x", padx=10, pady=(0, 16))

        self.actualizar_tabla_filtrada()

        ctk.CTkFrame(self.frame_reporte, fg_color="#e7e7e7", height=7, corner_radius=3).pack(fill="x", padx=4, pady=(30,20))

        # GRÁFICA
        self.frame_grafica = ctk.CTkFrame(self.frame_reporte, fg_color=COLOR_BLANCO, height=420)
        self.frame_grafica.pack(fill="both", expand=True, padx=16, pady=(0, 30))

        self.mostrar_grafica_reporte()

        self.var_depto.trace_add('write', lambda *_: self.actualizar_tabla_filtrada())

    def actualizar_tabla_filtrada(self):
        for widget in self.frame_tabla.winfo_children():
            widget.destroy()
        for widget in self.frame_tabla_paginacion.winfo_children():
            widget.destroy()
        idx = self.reporte_actual_idx
        rep = self.historial_reportes[idx]
        df = rep.get('df_resultado', pd.DataFrame())
        depto = self.var_depto.get() if self.var_depto else "Todos"

        if depto == "Todos":
            df_filtrado = df
        else:
            df_filtrado = df[df['departamento'] == depto]

        rows_per_page = self.tabla_rows_per_page
        total_registros = len(df_filtrado)
        total_pages = max(1, (total_registros + rows_per_page - 1) // rows_per_page)
        if self.tabla_pagina_actual > total_pages:
            self.tabla_pagina_actual = 1
        start = (self.tabla_pagina_actual - 1) * rows_per_page
        end = start + rows_per_page
        df_pagina = df_filtrado.iloc[start:end]

        if df_pagina.empty:
            ctk.CTkLabel(
                self.frame_tabla, text="Sin datos para mostrar",
                font=FUENTE_LABEL, text_color=COLOR_PRINCIPAL
            ).pack(pady=40)
        else:
            mostrar_tabla(self.frame_tabla, df_pagina)

        ctk.CTkButton(
            self.frame_tabla_paginacion, text="〈 Anterior", fg_color=COLOR_PRINCIPAL,
            state="normal" if self.tabla_pagina_actual > 1 else "disabled",
            command=self.pagina_anterior_tabla
        ).pack(side="left", padx=4)
        ctk.CTkLabel(
            self.frame_tabla_paginacion,
            text=f"Página {self.tabla_pagina_actual} de {total_pages}",
            font=FUENTE_TABLA
        ).pack(side="left", padx=7)
        ctk.CTkButton(
            self.frame_tabla_paginacion, text="Siguiente 〉", fg_color=COLOR_PRINCIPAL,
            state="normal" if self.tabla_pagina_actual < total_pages else "disabled",
            command=self.pagina_siguiente_tabla
        ).pack(side="left", padx=4)

    def pagina_anterior_tabla(self):
        if self.tabla_pagina_actual > 1:
            self.tabla_pagina_actual -= 1
            self.actualizar_tabla_filtrada()

    def pagina_siguiente_tabla(self):
        idx = self.reporte_actual_idx
        rep = self.historial_reportes[idx]
        df = rep.get('df_resultado', pd.DataFrame())
        depto = self.var_depto.get() if self.var_depto else "Todos"
        if depto == "Todos":
            df_filtrado = df
        else:
            df_filtrado = df[df['departamento'] == depto]
        total_registros = len(df_filtrado)
        total_pages = max(1, (total_registros + self.tabla_rows_per_page - 1) // self.tabla_rows_per_page)
        if self.tabla_pagina_actual < total_pages:
            self.tabla_pagina_actual += 1
            self.actualizar_tabla_filtrada()

    def mostrar_grafica_reporte(self):
        for widget in self.frame_grafica.winfo_children():
            widget.destroy()
        idx = self.reporte_actual_idx
        rep = self.historial_reportes[idx]
        df = rep.get('df_resultado', pd.DataFrame())
        depto = self.var_depto.get() if self.var_depto else "Todos"
        if depto == "Todos":
            df_filtrado = df
        else:
            df_filtrado = df[df['departamento'] == depto]
        if df_filtrado.empty:
            return
        plt.style.use('seaborn-v0_8-whitegrid')
        fig, ax = plt.subplots(figsize=(13, 4.7), dpi=120)
        labels = ['Sí reaccionó', 'No reaccionó']
        valores = [int(df_filtrado['reacciono'].sum()), int(len(df_filtrado) - df_filtrado['reacciono'].sum())]
        colores = ['#28b267', '#d35400']
        bars = ax.bar(labels, valores, color=colores, width=0.45, edgecolor='#eeeeee', linewidth=2, zorder=3)
        ax.set_ylim(0, max(valores) + 4)
        ax.set_title('Participación en publicación', fontsize=17, weight='bold', color="#233140", pad=12)
        for bar in bars:
            ax.annotate(f'{int(bar.get_height())}',
                        xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                        xytext=(0, 6),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=15, weight="bold")
        ax.spines[['top','right','left']].set_visible(False)
        ax.spines['bottom'].set_color("#aaaaaa")
        ax.yaxis.set_visible(False)
        ax.tick_params(left=False, bottom=False, labelsize=14, colors="#233140")
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)
