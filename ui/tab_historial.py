# ui/tab_historial.py
import customtkinter as ctk
from utiles.estilos import *
import pandas as pd
from tabla import mostrar_tabla
from tkinter import messagebox, filedialog
from pdf_report import exportar_tabla_pdf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Normalización de departamentos
from utiles.normalizacion import normalizar_df_departamentos, normalizar_departamento

# Reportlab para PDFs
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle


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

        # Estado de tabla
        self.tabla_pagina_actual = 1
        self.tabla_rows_per_page = 20
        self._df_actual_para_vista = pd.DataFrame()

        self.armar_vista_historial()

    def armar_vista_historial(self):
        parent = self.tab
        for widget in parent.winfo_children():
            widget.destroy()

        # --------- SCROLL GENERAL ---------
        self.main_scroll = ctk.CTkScrollableFrame(parent, fg_color=COLOR_BLANCO, height=880)
        self.main_scroll.pack(fill="both", expand=True, padx=0, pady=(0, 0))

        # ---------- HEADER: título + buscar + reporte general ----------
        frame_header = ctk.CTkFrame(self.main_scroll, fg_color=COLOR_BLANCO)
        frame_header.pack(fill="x", padx=28, pady=(10, 6))

        ctk.CTkLabel(
            frame_header,
            text="📊 Historial de Publicaciones Comparadas",
            font=("Segoe UI Bold", 24),
            text_color=COLOR_PRINCIPAL,
            bg_color=COLOR_BLANCO
        ).pack(side="left", padx=(10, 14), pady=(8,4))

        # Botón: Reporte General (todas las publicaciones, resumen por depto)
        btn_reporte_gral = ctk.CTkButton(
            frame_header,
            text="📄 Reporte General (PDF)",
            fg_color=COLOR_PRINCIPAL,
            text_color=COLOR_BLANCO,
            command=self.exportar_reporte_general_pdf
        )
        btn_reporte_gral.pack(side="right", padx=(8, 2), pady=6)

        # Buscador de publicación por título
        self.input_buscar = ctk.CTkEntry(frame_header, font=FUENTE_LABEL, width=320)
        self.input_buscar.pack(side="left", padx=10)
        self.input_buscar.bind("<KeyRelease>", self.on_filtrar)

        # ------------- LISTA DE PUBLICACIONES -------------
        self.frame_lista = ctk.CTkScrollableFrame(self.main_scroll, fg_color=COLOR_GRIS, height=80)
        self.frame_lista.pack(fill="x", padx=28, pady=(0, 14))

        # ------------- CONTENEDOR REPORTE (tabla + filtro + gráfica) -------------
        self.frame_reporte = ctk.CTkFrame(self.main_scroll, fg_color=COLOR_BLANCO)
        self.frame_reporte.pack(fill="both", expand=True, padx=16, pady=12)

        self.actualizar_lista_publicaciones()
        if self.publicaciones:
            self.mostrar_tabla_reporte(self.publicaciones[0][1])

        # Footer visual
        ctk.CTkFrame(self.main_scroll, fg_color=COLOR_BLANCO, height=80).pack(fill="x", pady=4)

    def refrescar_historial(self):
        self.armar_vista_historial()

    # -------------------------- LISTA Y BÚSQUEDA --------------------------

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

    # -------------------------- VISTA DE UN REPORTE --------------------------

    def mostrar_tabla_reporte(self, idx):
        for widget in self.frame_reporte.winfo_children():
            widget.destroy()
        self.reporte_actual_idx = idx

        rep = self.historial_reportes[idx]
        df = rep.get('df_resultado', pd.DataFrame())
        df = normalizar_df_departamentos(df)  # normaliza nombres de depto
        self._df_actual_para_vista = df.copy()

        titulo = rep.get('titulo_publicacion', '(Sin título)')
        mensaje = rep.get('post_mensaje', '')

        # Reset de paginación
        self.tabla_pagina_actual = 1

        # Título
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

        # Filtro por departamento + PDF (individual y por deptos)
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

        # Botones PDF
        btn_pdf_deptos = ctk.CTkButton(
            frame_filtro,
            text="Reporte por departamento (PDF)",
            fg_color=COLOR_PRINCIPAL,
            text_color=COLOR_BLANCO,
            font=FUENTE_LABEL,
            command=self.exportar_detalle_por_departamento_pdf
        )
        btn_pdf_deptos.pack(side="right", padx=12)

        btn_pdf = ctk.CTkButton(
            frame_filtro,
            text="Exportar PDF tabla filtrada",
            fg_color=COLOR_PRINCIPAL,
            text_color=COLOR_BLANCO,
            font=FUENTE_LABEL,
            command=self.exportar_pdf_tabla_filtrada
        )
        btn_pdf.pack(side="right", padx=12)

        # Divider
        ctk.CTkFrame(self.frame_reporte, fg_color="#cccccc", height=2).pack(fill="x", padx=8, pady=(6,16))

        # Tabla (sin paginación interna para evitar doble paginación)
        self.frame_tabla = ctk.CTkFrame(self.frame_reporte, fg_color=COLOR_BLANCO)
        self.frame_tabla.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        # Paginación (nuestra)
        self.frame_tabla_paginacion = ctk.CTkFrame(self.frame_reporte, fg_color=COLOR_BLANCO)
        self.frame_tabla_paginacion.pack(fill="x", padx=10, pady=(0, 16))

        # Pintamos tabla 1ra vez
        self.actualizar_tabla_filtrada()

        # Divider grande + gráfica
        ctk.CTkFrame(self.frame_reporte, fg_color="#e7e7e7", height=7, corner_radius=3).pack(fill="x", padx=4, pady=(30,20))
        self.frame_grafica = ctk.CTkFrame(self.frame_reporte, fg_color=COLOR_BLANCO, height=420)
        self.frame_grafica.pack(fill="both", expand=True, padx=16, pady=(0, 30))
        self.mostrar_grafica_reporte()

        # Reaccionar al cambio de filtro
        self.var_depto.trace_add('write', lambda *_: self.actualizar_tabla_filtrada())

    # -------------------------- TABLA + PAGINACIÓN --------------------------

    def actualizar_tabla_filtrada(self):
        for widget in self.frame_tabla.winfo_children():
            widget.destroy()
        for widget in self.frame_tabla_paginacion.winfo_children():
            widget.destroy()

        df = self._df_actual_para_vista.copy()
        depto = self.var_depto.get() if self.var_depto else "Todos"
        if depto != "Todos":
            df = df[df['departamento'] == depto]

        rows_per_page = self.tabla_rows_per_page
        total_registros = len(df)
        total_pages = max(1, (total_registros + rows_per_page - 1) // rows_per_page)
        if self.tabla_pagina_actual > total_pages:
            self.tabla_pagina_actual = 1

        start = (self.tabla_pagina_actual - 1) * rows_per_page
        end = start + rows_per_page
        df_pagina = df.iloc[start:end]

        if df_pagina.empty:
            ctk.CTkLabel(
                self.frame_tabla, text="Sin datos para mostrar",
                font=FUENTE_LABEL, text_color=COLOR_PRINCIPAL
            ).pack(pady=40)
        else:
            # Muy importante: sin paginación interna para NO duplicar
            try:
                mostrar_tabla(self.frame_tabla, df_pagina, show_paginacion=False)
            except TypeError:
                # Si tu versión de mostrar_tabla no acepta show_paginacion, la mostramos normal
                mostrar_tabla(self.frame_tabla, df_pagina)

        # Nuestra paginación
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

        # Actualiza también la gráfica
        self.mostrar_grafica_reporte()

    def pagina_anterior_tabla(self):
        if self.tabla_pagina_actual > 1:
            self.tabla_pagina_actual -= 1
            self.actualizar_tabla_filtrada()

    def pagina_siguiente_tabla(self):
        df = self._df_actual_para_vista.copy()
        depto = self.var_depto.get() if self.var_depto else "Todos"
        if depto != "Todos":
            df = df[df['departamento'] == depto]
        total_registros = len(df)
        total_pages = max(1, (total_registros + self.tabla_rows_per_page - 1) // self.tabla_rows_per_page)
        if self.tabla_pagina_actual < total_pages:
            self.tabla_pagina_actual += 1
            self.actualizar_tabla_filtrada()

    # -------------------------- GRÁFICA --------------------------

    def mostrar_grafica_reporte(self):
        for widget in self.frame_grafica.winfo_children():
            widget.destroy()

        df = self._df_actual_para_vista.copy()
        depto = self.var_depto.get() if self.var_depto else "Todos"
        if depto != "Todos":
            df = df[df['departamento'] == depto]
        if df.empty:
            return

        plt.style.use('seaborn-v0_8-whitegrid')
        fig, ax = plt.subplots(figsize=(13, 4.7), dpi=120)

        si = int(df['reacciono'].sum())
        no = int(len(df) - si)
        labels = ['Sí reaccionó', 'No reaccionó']
        valores = [si, no]
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

    # -------------------------- EXPORTAR PDF (tabla filtrada de la vista) --------------------------

    def exportar_pdf_tabla_filtrada(self):
        idx = self.reporte_actual_idx
        rep = self.historial_reportes[idx]
        df = rep.get('df_resultado', pd.DataFrame())
        df = normalizar_df_departamentos(df)

        depto = self.var_depto.get() if self.var_depto else "Todos"
        df_filtrado = df if depto == "Todos" else df[df['departamento'] == depto]

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

    # -------------------------- EXPORTAR PDF (detalle por depto – secciones) --------------------------

    def exportar_detalle_por_departamento_pdf(self):
        """Genera un PDF (para la publicación seleccionada) con secciones por departamento."""
        df = getattr(self, "_df_actual_para_vista", None)
        if df is None or df.empty:
            messagebox.showwarning("Sin datos", "No hay datos para exportar en esta publicación.")
            return

        # Respetar filtro UI si está activo
        depto_ui = self.var_depto.get() if self.var_depto else "Todos"
        if depto_ui and depto_ui != "Todos":
            df = df[df["departamento"] == depto_ui]

        # Dialogo guardar
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Guardar Reporte por Departamento"
        )
        if not path:
            return

        # Documento
        doc = SimpleDocTemplate(path, pagesize=letter, leftMargin=32, rightMargin=32, topMargin=32, bottomMargin=32)
        elements = []

        # Encabezado general
        title_style = ParagraphStyle(
            name='TituloGrande',
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=colors.HexColor("#29507A"),
            alignment=1,
        )
        elements.append(Paragraph("DETALLE DE REACCIONES POR DEPARTAMENTO", title_style))
        elements.append(Spacer(1, 12))

        # Subtítulo: publicación
        idx = getattr(self, "reporte_actual_idx", 0)
        rep = self.historial_reportes[idx] if 0 <= idx < len(self.historial_reportes) else {}
        titulo_pub = rep.get('titulo_publicacion', '(Sin título)')
        sub_style = ParagraphStyle(
            name='Sub',
            fontName='Helvetica',
            fontSize=11,
            textColor=colors.HexColor("#333333"),
            alignment=1,
        )
        elements.append(Paragraph(f"Publicación: {titulo_pub}", sub_style))
        elements.append(Spacer(1, 10))

        if df.empty:
            elements.append(Paragraph("No hay datos para el filtro actual.", sub_style))
            try:
                doc.build(elements)
                messagebox.showinfo("PDF generado", "Se generó el PDF (sin filas para el filtro actual).")
            except Exception as e:
                messagebox.showerror("Error al exportar PDF", str(e))
            return

        # Agrupar por departamento
        df_sorted = df.sort_values(["departamento", "nombre"], na_position="last")
        departamentos = list(df_sorted["departamento"].dropna().unique())

        depto_title_style = ParagraphStyle(
            name="DeptoTitle",
            fontName="Helvetica-Bold",
            fontSize=14,
            textColor=colors.HexColor("#00551E"),
            alignment=0,
            spaceBefore=10,
            spaceAfter=6,
        )
        nota_style = ParagraphStyle(
            name='Nota',
            fontName='Helvetica',
            fontSize=9,
            textColor=colors.HexColor("#666666"),
            alignment=0,
            leading=12
        )

        for d_idx, depto in enumerate(departamentos):
            area_df = df_sorted[df_sorted["departamento"] == depto].copy()
            area_df["REACCIONÓ"] = area_df["reacciono"].apply(lambda x: "Sí" if bool(x) else "No")

            header = ["NOMBRE", "PUESTO", "NOMBRE_FB", "REACCIONÓ"]
            data = [header]
            for _, r in area_df.iterrows():
                data.append([
                    str(r.get("nombre", "")),
                    str(r.get("puesto", "")),
                    str(r.get("nombre_fb", "")),
                    str(r.get("REACCIONÓ", "")),
                ])

            elements.append(Paragraph(f"Departamento: <b>{depto}</b>  |  Empleados: <b>{len(area_df)}</b>", depto_title_style))
            elements.append(Spacer(1, 3))

            table = Table(data, colWidths=[200, 160, 130, 80])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#29507A")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 10),
                ('ALIGN', (1,1), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('INNERGRID', (0,0), (-1,-1), 0.4, colors.HexColor("#DDDDDD")),
                ('BOX', (0,0), (-1,-1), 0.6, colors.HexColor("#BBBBBB")),
            ]))
            # Zebra
            for i in range(1, len(data)):
                if i % 2 == 0:
                    table.setStyle(TableStyle([('BACKGROUND', (0,i), (-1,i), colors.HexColor("#F7F9FC"))]))

            elements.append(table)
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(
                "Nota: El campo “REACCIONÓ” se refiere a la participación del empleado en esta publicación.",
                nota_style
            ))

            if d_idx < len(departamentos) - 1:
                elements.append(PageBreak())

        try:
            doc.build(elements)
            messagebox.showinfo("¡Listo!", "Reporte por departamento (PDF) generado exitosamente.")
        except Exception as e:
            messagebox.showerror("Error al exportar PDF", str(e))

    # -------------------------- EXPORTAR PDF (resumen general) --------------------------

    def exportar_reporte_general_pdf(self):
        """Genera un PDF resumen por departamento (todas las publicaciones del historial)."""
        dfs = []
        for rep in self.historial_reportes:
            df = rep.get('df_resultado', None)
            if df is not None and not df.empty:
                df = normalizar_df_departamentos(df)
                dfs.append(df)

        if not dfs:
            messagebox.showwarning("Sin datos", "No hay publicaciones con datos para generar el reporte general.")
            return

        df_all = pd.concat(dfs, ignore_index=True)

        # Resumen por departamento
        resumen = (
            df_all
            .groupby('departamento', dropna=True)
            .agg(total=('reacciono', 'size'), si=('reacciono', 'sum'))
            .reset_index()
        )
        resumen['no'] = resumen['total'] - resumen['si']
        resumen['%_participacion'] = (resumen['si'] / resumen['total'] * 100).round(2)
        resumen = resumen.sort_values(['%_participacion', 'si'], ascending=[False, False])

        # Guardar
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Guardar Reporte General"
        )
        if not path:
            return

        doc = SimpleDocTemplate(path, pagesize=letter, leftMargin=32, rightMargin=32, topMargin=32, bottomMargin=32)
        elements = []

        # Título
        title_style = ParagraphStyle(
            name='TituloGrande',
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=colors.HexColor("#29507A"),
            alignment=1,
        )
        elements.append(Paragraph("REPORTE GENERAL DE REACCIONES POR DEPARTAMENTO", title_style))
        elements.append(Spacer(1, 16))

        # Descripción
        desc_style = ParagraphStyle(
            name='Desc',
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.HexColor("#333333"),
            alignment=0,
            leading=14,
        )
        elements.append(Paragraph(
            "El siguiente resumen agrega todas las publicaciones comparadas y muestra, "
            "por departamento, el total de registros considerados, cuántos reaccionaron, "
            "cuántos no reaccionaron y el porcentaje de participación.",
            desc_style
        ))
        elements.append(Spacer(1, 12))

        # Tabla
        data = [["DEPARTAMENTO", "TOTAL", "SÍ", "NO", "% PARTICIPACIÓN"]]
        for _, row in resumen.iterrows():
            data.append([
                str(row['departamento']),
                int(row['total']),
                int(row['si']),
                int(row['no']),
                f"{row['%_participacion']}%"
            ])

        table = Table(data, colWidths=[220, 60, 50, 50, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#29507A")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 11),
            ('ALIGN', (1,1), (-1,-1), 'CENTER'),
            ('ALIGN', (0,0), (0,-1), 'LEFT'),
            ('INNERGRID', (0,0), (-1,-1), 0.4, colors.HexColor("#DDDDDD")),
            ('BOX', (0,0), (-1,-1), 0.6, colors.HexColor("#BBBBBB")),
        ]))
        # Zebra
        for i in range(1, len(data)):
            if i % 2 == 0:
                table.setStyle(TableStyle([('BACKGROUND', (0,i), (-1,i), colors.HexColor("#F7F9FC"))]))

        elements.append(table)
        elements.append(Spacer(1, 16))

        # Nota
        nota_style = ParagraphStyle(
            name='Nota',
            fontName='Helvetica-Oblique',
            fontSize=9,
            textColor=colors.HexColor("#666666"),
            alignment=0,
        )
        elements.append(Paragraph(
            "Notas: Los nombres de departamentos han sido normalizados para unificar abreviaturas y variantes. "
            "Si detectas nuevas abreviaturas, podemos agregarlas al mapeo para mejorar la agrupación.",
            nota_style
        ))

        try:
            doc.build(elements)
            messagebox.showinfo("¡Listo!", "Reporte general PDF generado exitosamente.")
        except Exception as e:
            messagebox.showerror("Error al exportar PDF", str(e))
