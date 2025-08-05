# pdf_report.py
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer, Paragraph, PageBreak, KeepTogether
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

def tabla_zebra_pdf(df, columnas):
    data = [columnas]
    for _, row in df.iterrows():
        fila = []
        for col in columnas:
            val = row[col]
            if str(col).lower() == "reacciono":
                val = "Sí" if val in (True, "SI", "VERDADERO", "True", "si", "verdadero", 1) else "No"
            fila.append(val)
        data.append(fila)
    t = Table(data, repeatRows=1, hAlign="LEFT")
    style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#29507A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]
    for i in range(1, len(data)):
        bg = colors.HexColor("#F3F4F7") if i%2==0 else colors.white
        style.append(('BACKGROUND', (0,i), (-1,i), bg))
    style.append(('GRID', (0,0), (-1,-1), 0.5, colors.grey))
    # Columna "reacciono"
    try:
        col_reacc = [c.lower() for c in columnas].index("reacciono")
        for i, fila in enumerate(data[1:], start=1):
            val = str(fila[col_reacc]).upper()
            if val == "SÍ":
                style.append(('BACKGROUND', (col_reacc, i), (col_reacc, i), colors.HexColor("#1FB772")))
                style.append(('TEXTCOLOR', (col_reacc, i), (col_reacc, i), colors.white))
                style.append(('FONTNAME', (col_reacc, i), (col_reacc, i), 'Helvetica-Bold'))
            elif val == "NO":
                style.append(('BACKGROUND', (col_reacc, i), (col_reacc, i), colors.HexColor("#D35400")))
                style.append(('TEXTCOLOR', (col_reacc, i), (col_reacc, i), colors.white))
                style.append(('FONTNAME', (col_reacc, i), (col_reacc, i), 'Helvetica-Bold'))
    except Exception:
        pass
    t.setStyle(TableStyle(style))
    return t

def exportar_tabla_pdf(titulo, departamento, df, logo_path=None):
    from tkinter import filedialog, messagebox
    import os
    if df.empty:
        messagebox.showwarning("Tabla vacía", "No hay datos para exportar en este departamento.")
        return
    path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile=f"Reporte_{titulo[:15]}_{departamento[:10]}.pdf"
    )
    if not path:
        return
    doc = SimpleDocTemplate(path, pagesize=letter, leftMargin=32, rightMargin=32, topMargin=32, bottomMargin=32)
    elements = []
    # Logo y cabecera
    if logo_path and os.path.exists(logo_path):
        img = Image(logo_path, width=70, height=70)
        elements.append(img)
        elements.append(Spacer(1, 8))
    style_title = ParagraphStyle(
        name="TituloGrande",
        fontName="Helvetica-Bold",
        fontSize=17,
        textColor=colors.HexColor("#29507A"),
        alignment=1,
    )
    elements.append(Paragraph("REPORTE DE REACCIONES FACEBOOK", style_title))
    elements.append(Spacer(1, 8))
    style_sub = ParagraphStyle(
        name="TituloMedio",
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=colors.HexColor("#29507A"),
        alignment=1,
    )
    elements.append(Paragraph(f"Título de la publicación: <b>{titulo}</b>", style_sub))
    elements.append(Paragraph(f"Departamento: <b>{departamento}</b>", style_sub))
    elements.append(Spacer(1, 6))
    # Tabla
    columnas = [col for col in df.columns if col not in ('nombre_norm', 'post_id', 'post_mensaje', 'post_fecha')]
    elements.append(tabla_zebra_pdf(df, columnas))
    # Pie y fecha
    elements.append(Spacer(1, 8))
    style_footer = ParagraphStyle(
        name="Footer",
        fontSize=8,
        textColor=colors.HexColor("#888888"),
        alignment=2,
    )
    elements.append(Paragraph(f"Reporte generado por el sistema | {datetime.today().strftime('%Y-%m-%d %H:%M')}", style_footer))
    try:
        doc.build(elements)
        messagebox.showinfo("¡Listo!", f"PDF generado correctamente en:\n{path}")
    except Exception as e:
        messagebox.showerror("Error al exportar PDF", str(e))
