import customtkinter as ctk
from estilos import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import pandas as pd

from pdf_report import exportar_tabla_pdf, tabla_zebra_pdf
from utils_report import tabla_resumen_general

def exportar_historial_pdf(historial_reportes, logo_path=None):
    from tkinter import filedialog, messagebox
    import os
    from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph, PageBreak
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib import colors

    path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not path:
        return

    doc = SimpleDocTemplate(path, pagesize=letter, leftMargin=32, rightMargin=32, topMargin=32, bottomMargin=32)
    elements = []

    # --- PUBLICACIONES UNA POR UNA ---
    for idx, rep in enumerate(historial_reportes):
        df = rep['df_resultado']
        columnas = [col for col in df.columns if col not in ('nombre_norm', 'post_id', 'post_mensaje', 'post_fecha')]
        areas = list(df['departamento'].dropna().unique())

        # LOGO Y CABECERA
        if logo_path and os.path.exists(logo_path):
            from reportlab.platypus import Image
            img = Image(logo_path, width=80, height=80)
            elements.append(img)
            elements.append(Spacer(1, 10))
        title_style = ParagraphStyle(
            name='TituloGrande',
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=colors.HexColor("#29507A"),
            alignment=1,
        )
        elements.append(Paragraph("REPORTE DE REACCIONES FACEBOOK", title_style))
        elements.append(Spacer(1, 18))
        pub_style = ParagraphStyle(
            name='TituloMedio',
            fontName='Helvetica-Bold',
            fontSize=13,
            textColor=colors.HexColor("#29507A"),
            alignment=0,
        )
        elements.append(Paragraph(f"Título de la publicación: <b>{rep['titulo_publicacion']}</b>", pub_style))
        elements.append(Paragraph(f"Fecha: <b>{rep.get('post_fecha', datetime.today().strftime('%Y-%m-%d'))}</b>", pub_style))
        elements.append(Spacer(1, 12))

        # -- Tablas por área
        from reportlab.platypus import KeepTogether
        for area in areas:
            area_df = df[df['departamento'] == area]
            area_header = []
            area_header.append(Spacer(1, 16))
            area_style = ParagraphStyle(
                name="AreaGrande",
                fontName="Helvetica-Bold",
                fontSize=17,
                textColor=colors.HexColor("#00551E"),
                alignment=1,
                spaceAfter=10,
                spaceBefore=10
            )
            area_header.append(Paragraph(f"Área / Departamento: <b>{area}</b>", area_style))
            tablas = []
            tablas.append(Spacer(1, 8))
            tablas.append(Paragraph("▶ Todos los empleados:", ParagraphStyle('Sub', fontSize=12, fontName="Helvetica-Bold", textColor=colors.HexColor("#29507A"), alignment=0, spaceAfter=3)))
            tablas.append(tabla_zebra_pdf(area_df, columnas))
            solo_si = area_df[area_df['reacciono'] == True]
            tablas.append(Spacer(1, 5))
            tablas.append(Paragraph("🟩 Empleados que SÍ reaccionaron:", ParagraphStyle('Sub', fontSize=11, fontName="Helvetica-Bold", textColor=colors.green, alignment=0, spaceAfter=2)))
            tablas.append(tabla_zebra_pdf(solo_si, columnas))
            solo_no = area_df[area_df['reacciono'] == False]
            tablas.append(Spacer(1, 5))
            tablas.append(Paragraph("🟥 Empleados que NO reaccionaron:", ParagraphStyle('Sub', fontSize=11, fontName="Helvetica-Bold", textColor=colors.red, alignment=0, spaceAfter=2)))
            tablas.append(tabla_zebra_pdf(solo_no, columnas))
            tablas.append(Spacer(1, 12))
            elements.append(KeepTogether(area_header + tablas))

        # Pie de página
        elements.append(Spacer(1, 10))
        footer_style = ParagraphStyle(
            name="Footer",
            fontSize=8,
            textColor=colors.HexColor("#888888"),
            alignment=2,
        )
        elements.append(Paragraph(f"Reporte generado por el sistema | {datetime.today().strftime('%Y-%m-%d %H:%M')}", footer_style))
        if idx < len(historial_reportes) - 1:
            elements.append(PageBreak())

    # ----------- RESUMEN GENERAL -----------
    elements.append(PageBreak())
    resumen_title = ParagraphStyle(
        name='ResumenTitulo',
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor("#29507A"),
        alignment=1,
        spaceAfter=7
    )
    elements.append(Paragraph("Resumen General por Área", resumen_title))
    resumen_subtitle = ParagraphStyle(
        name='ResumenSubtitle',
        fontName='Helvetica',
        fontSize=12,
        textColor=colors.HexColor("#222222"),
        alignment=1,
        spaceAfter=16
    )
    elements.append(Paragraph(
        "La siguiente tabla muestra la participación total por área/departamento, sumando todas las publicaciones incluidas en el presente reporte.",
        resumen_subtitle
    ))

    # TABLA RESUMEN
    resumen_table = tabla_resumen_general(historial_reportes)
    elements.append(resumen_table)

    # Explicación final
    explicacion = """
    <b>¿Qué significa cada columna?</b><br/>
    <b>Reacciones totales esperadas:</b> Es el total de posibles reacciones si todos los empleados de esa área hubieran reaccionado en cada publicación.<br/>
    <b># de reacciones hechas:</b> Suma total de empleados que sí reaccionaron (por área, en todas las publicaciones).<br/>
    <b># de no-reacciones:</b> Suma total de empleados que no reaccionaron (por área, en todas las publicaciones).<br/>
    <b>% de participación:</b> Porcentaje de reacciones hechas sobre el total esperado.<br/><br/>
    <b>Nota:</b> Si algún empleado no aparece en la base o el nombre no coincide exactamente, no se contará en estos resultados.
    """
    explic_style = ParagraphStyle(
        name="NotaPie",
        fontSize=10,
        textColor=colors.HexColor("#333333"),
        alignment=0,
        spaceBefore=7
    )
    elements.append(Paragraph(explicacion, explic_style))

    fecha_style = ParagraphStyle(
        name="FechaPie",
        fontSize=9,
        textColor=colors.HexColor("#888888"),
        alignment=2,
        spaceBefore=9
    )
    elements.append(Paragraph(f"Reporte generado: {datetime.today().strftime('%Y-%m-%d %H:%M')}", fecha_style))

    # --- FIN: guardar PDF ---
    try:
        doc.build(elements)
        messagebox.showinfo("¡Listo!", "Reporte PDF generado exitosamente.")
    except Exception as e:
        messagebox.showerror("Error al exportar PDF", str(e))


# ======================== VISTA HISTORIAL ==========================
def mostrar_historial_en_tab(parent, historial_reportes):
    from tkinter import filedialog, messagebox

    for widget in parent.winfo_children():
        widget.destroy()

    # Header + botón exportar
    frame_header = ctk.CTkFrame(parent, fg_color=COLOR_BLANCO)
    frame_header.pack(fill="x", padx=18, pady=(0, 3))
    ctk.CTkLabel(
        frame_header,
        text="📊 Historial de Publicaciones Comparadas",
        font=("Segoe UI Bold", 26),
        text_color=COLOR_PRINCIPAL,
        bg_color=COLOR_BLANCO
    ).pack(side="left", padx=(10,4), pady=(8,4))

    btn_exportar_global = ctk.CTkButton(
        frame_header,
        text="📄 Generar Reporte PDF",
        fg_color=COLOR_PRINCIPAL,
        text_color=COLOR_BLANCO,
        font=("Segoe UI Bold", 16),
        hover_color=COLOR_ACENTO,
        command=lambda: exportar_historial_pdf(historial_reportes, logo_path="logo.png")
    )
    btn_exportar_global.pack(side="right", padx=8, pady=8)

    # Filtros de búsqueda
    frame_filtros = ctk.CTkFrame(parent, fg_color=COLOR_BLANCO)
    frame_filtros.pack(fill="x", padx=18, pady=(0, 6))
    ctk.CTkLabel(
        frame_filtros,
        text="Buscar por Título:",
        font=FUENTE_LABEL,
        text_color=COLOR_PRINCIPAL
    ).pack(side="left", padx=4)
    input_buscar = ctk.CTkEntry(frame_filtros, font=FUENTE_LABEL, width=260)
    input_buscar.pack(side="left", padx=6)
    btn_recargar = ctk.CTkButton(
        frame_filtros,
        text="Recargar",
        fg_color=COLOR_PRINCIPAL,
        text_color=COLOR_BLANCO,
        command=lambda: mostrar_historial_en_tab(parent, historial_reportes)
    )
    btn_recargar.pack(side="right", padx=10)

    # Lista de publicaciones
    frame_lista = ctk.CTkScrollableFrame(parent, fg_color=COLOR_GRIS, height=100)
    frame_lista.pack(fill="x", padx=12, pady=(0, 8))

    # Frame para mostrar tabla del reporte seleccionado
    frame_reporte = ctk.CTkFrame(parent, fg_color=COLOR_BLANCO, corner_radius=10)
    frame_reporte.pack(fill="both", expand=True, padx=12, pady=6)

    # Frame para gráfica
    frame_grafica = ctk.CTkFrame(parent, fg_color=COLOR_BLANCO, corner_radius=10)
    frame_grafica.pack(fill="x", padx=12, pady=(0, 12))

    publicaciones = []
    for idx, rep in enumerate(historial_reportes):
        txt = f"{idx+1}. {rep['titulo_publicacion']} - {rep['post_mensaje']}"
        publicaciones.append((txt, idx))
    publicaciones_full = publicaciones.copy()

    def actualizar_lista():
        for widget in frame_lista.winfo_children():
            widget.destroy()
        for txt, idx in publicaciones:
            btn = ctk.CTkButton(
                frame_lista,
                text=txt,
                fg_color=COLOR_PRINCIPAL,
                text_color=COLOR_BLANCO,
                anchor="w",
                font=FUENTE_LABEL,
                command=lambda i=idx: mostrar_tabla_reporte(i)
            )
            btn.pack(pady=2, padx=4, anchor="w")

    def on_filtrar(event=None):
        q = input_buscar.get().strip().lower()
        nonlocal publicaciones
        if not q:
            publicaciones = publicaciones_full.copy()
        else:
            publicaciones = [(txt, idx) for (txt, idx) in publicaciones_full if q in txt.lower()]
        actualizar_lista()

    input_buscar.bind("<KeyRelease>", on_filtrar)
    actualizar_lista()

    def mostrar_tabla_reporte(idx):
        # Limpia frames para tabla y gráfico
        for widget in frame_reporte.winfo_children():
            widget.destroy()
        for widget in frame_grafica.winfo_children():
            widget.destroy()

        rep = historial_reportes[idx]
        df = rep['df_resultado']

        # Título grande
        ctk.CTkLabel(
            frame_reporte,
            text=f"📰  Título de la publicación: {rep['titulo_publicacion']}",
            font=("Segoe UI Bold", 22),
            text_color=COLOR_PRINCIPAL,
            bg_color=COLOR_BLANCO,
            anchor="w"
        ).pack(pady=(12,6), padx=30, anchor="w")

        # FILTRO POR DEPARTAMENTO + BOTÓN PDF
        try:
            from modelo import cargar_base_empleados
            df_empleados = cargar_base_empleados('base_empleados.xlsx')
            departamentos_all = sorted(list(set(df_empleados['departamento'].dropna())))
        except Exception:
            departamentos_all = sorted(list(set(rep['df_resultado']['departamento'].dropna())))
        departamentos_all.insert(0, "Todos")
        var_depto = ctk.StringVar(value="Todos")

        frame_filtro = ctk.CTkFrame(frame_reporte, fg_color=COLOR_BLANCO)
        frame_filtro.pack(fill="x", padx=20, pady=(0,7))

        ctk.CTkLabel(
            frame_filtro,
            text="Filtrar por departamento:",
            font=FUENTE_LABEL,
            text_color=COLOR_PRINCIPAL
        ).pack(side="left", padx=(8,4))

        filtro_menu = ctk.CTkOptionMenu(
            frame_filtro,
            variable=var_depto,
            values=departamentos_all,
            width=200,
            fg_color="#f0f0f0",
            button_color=COLOR_PRINCIPAL,
            button_hover_color=COLOR_ACENTO,
            text_color=COLOR_PRINCIPAL
        )
        filtro_menu.pack(side="left", padx=8)

        def exportar_pdf_tabla_filtrada():
            depto = var_depto.get()
            if depto == "Todos":
                df_filtrado = rep['df_resultado']
            else:
                df_filtrado = rep['df_resultado'][rep['df_resultado']['departamento'] == depto]
            exportar_tabla_pdf(
                titulo=rep['titulo_publicacion'],
                departamento=depto,
                df=df_filtrado,
                logo_path="logo.png"
            )

        btn_pdf = ctk.CTkButton(
            frame_filtro,
            text="Exportar PDF tabla filtrada",
            fg_color=COLOR_PRINCIPAL,
            text_color=COLOR_BLANCO,
            font=FUENTE_LABEL,
            command=exportar_pdf_tabla_filtrada
        )
        btn_pdf.pack(side="right", padx=12)

        # Divider visual tipo línea
        ctk.CTkFrame(frame_reporte, fg_color="#cccccc", height=2, corner_radius=1).pack(fill="x", padx=10, pady=(2,8))

        # TABLA Y GRÁFICO FILTRABLES
        frame_scroll = ctk.CTkScrollableFrame(frame_reporte, fg_color=COLOR_BLANCO, height=350)
        frame_scroll.pack(fill="both", expand=True)

        def actualizar_tabla_y_grafico(*args):
            for widget in frame_scroll.winfo_children():
                widget.destroy()
            for widget in frame_grafica.winfo_children():
                widget.destroy()
            depto = var_depto.get()
            if depto == "Todos":
                df_mostrar = rep['df_resultado']
            else:
                df_mostrar = rep['df_resultado'][rep['df_resultado']['departamento'] == depto]

            columnas = [col for col in df_mostrar.columns if col not in ('nombre_norm', 'post_id', 'post_mensaje', 'post_fecha')]
            for j, col in enumerate(columnas):
                lbl = ctk.CTkLabel(
                    frame_scroll,
                    text=col,
                    font=FUENTE_LABEL,
                    text_color=COLOR_BLANCO,
                    bg_color=COLOR_PRINCIPAL,
                    width=150,
                    anchor="center"
                )
                lbl.grid(row=0, column=j, padx=3, pady=5, sticky="nsew")
                frame_scroll.grid_columnconfigure(j, weight=1)
            for i, row in df_mostrar.iterrows():
                for j, col in enumerate(columnas):
                    val = row[col]
                    if str(col).lower() == 'reacciono':
                        color = COLOR_VERDE if val else COLOR_ROJO
                        txtcolor = COLOR_BLANCO
                        val = "Sí" if val else "No"
                    else:
                        color = "#F3F4F7" if i % 2 == 0 else "#FFFFFF"
                        txtcolor = COLOR_TEXTO
                    ctk.CTkLabel(
                        frame_scroll,
                        text=str(val),
                        font=FUENTE_TABLA,
                        width=150,
                        text_color=txtcolor,
                        bg_color=color,
                        anchor="center"
                    ).grid(row=i+1, column=j, padx=2, pady=2, sticky="nsew")

            # Gráfico elegante y largo
            if not df_mostrar.empty:
                plt.style.use('seaborn-v0_8-whitegrid')
                fig, ax = plt.subplots(figsize=(5.5, 2.2), dpi=120)
                labels = ['Sí reaccionó', 'No reaccionó']
                valores = [df_mostrar['reacciono'].sum(), len(df_mostrar) - df_mostrar['reacciono'].sum()]
                colores = ['#28b267', '#d35400']
                bars = ax.bar(labels, valores, color=colores, width=0.4, edgecolor='#eeeeee', linewidth=2, zorder=3)
                ax.set_ylim(0, max(valores) + 1)
                ax.set_title('Participación en publicación', fontsize=15, weight='bold', color="#233140", pad=10)
                for bar in bars:
                    ax.annotate(f'{int(bar.get_height())}',
                                xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                                xytext=(0, 5),
                                textcoords="offset points",
                                ha='center', va='bottom',
                                fontsize=13, weight="bold")
                ax.spines[['top','right','left']].set_visible(False)
                ax.spines['bottom'].set_color("#aaaaaa")
                ax.yaxis.set_visible(False)
                ax.tick_params(left=False, bottom=False, labelsize=12, colors="#233140")
                plt.tight_layout()
                canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="x")
                plt.close(fig)

        # LLAMA A LA FUNCIÓN INICIALMENTE PARA QUE SIEMPRE MUESTRE LOS DATOS
        actualizar_tabla_y_grafico()

        # ASEGURA QUE AL CAMBIAR EL SELECT SE ACTUALICE LA TABLA Y GRÁFICO
        var_depto.trace_add('write', lambda *_: actualizar_tabla_y_grafico())
