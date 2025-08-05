# utils_report.py
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from datetime import datetime
from collections import defaultdict

def tabla_resumen_general(historial_reportes):
    resumen_colwidths = [150, 100, 105, 115, 100]
    resumen_data = [
        [
            Paragraph("<b>Área /<br/>Departamento</b>", ParagraphStyle('cab', fontSize=11, textColor=colors.white, fontName="Helvetica-Bold", alignment=1)),
            Paragraph("<b>Reacciones<br/>totales esperadas</b>", ParagraphStyle('cab', fontSize=11, textColor=colors.white, fontName="Helvetica-Bold", alignment=1)),
            Paragraph("<b># de<br/>reacciones hechas</b>", ParagraphStyle('cab', fontSize=11, textColor=colors.white, fontName="Helvetica-Bold", alignment=1)),
            Paragraph("<b># de<br/>no-reacciones</b>", ParagraphStyle('cab', fontSize=11, textColor=colors.white, fontName="Helvetica-Bold", alignment=1)),
            Paragraph("<b>% de<br/>participación</b>", ParagraphStyle('cab', fontSize=11, textColor=colors.white, fontName="Helvetica-Bold", alignment=1)),
        ]
    ]
    resumen_acum = defaultdict(lambda: {"totales": 0, "hechas": 0, "no_hechas": 0})
    for rep in historial_reportes:
        df = rep['df_resultado']
        for area in df['departamento'].dropna().unique():
            df_area = df[df['departamento'] == area]
            resumen_acum[area]["totales"] += len(df_area)
            resumen_acum[area]["hechas"] += df_area['reacciono'].sum()
            resumen_acum[area]["no_hechas"] += (df_area['reacciono'] == False).sum()
    for area, vals in resumen_acum.items():
        tot = vals["totales"]
        hechas = vals["hechas"]
        no_hechas = vals["no_hechas"]
        pct = f"{(hechas / tot * 100):.1f}%" if tot else "0%"
        resumen_data.append([
            Paragraph(str(area), ParagraphStyle('cuerpo', fontSize=10, alignment=0, textColor=colors.HexColor("#00203A"))),
            Paragraph(str(tot), ParagraphStyle('cuerpo', fontSize=10, alignment=1)),
            Paragraph(str(hechas), ParagraphStyle('cuerpo', fontSize=10, alignment=1)),
            Paragraph(str(no_hechas), ParagraphStyle('cuerpo', fontSize=10, alignment=1)),
            Paragraph(pct, ParagraphStyle('cuerpo', fontSize=10, alignment=1, textColor=colors.HexColor("#1FB772" if float(pct[:-1]) >= 60 else "#D35400"))),
        ])
    resumen_table = Table(
        resumen_data, 
        repeatRows=1, 
        hAlign="CENTER", 
        colWidths=resumen_colwidths
    )
    resumen_style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#29507A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('FONTSIZE', (0,1), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 11),
        ('TOPPADDING', (0,0), (-1,0), 9),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.7, colors.HexColor("#cccccc")),
    ]
    for i in range(1, len(resumen_data)):
        bg = colors.HexColor("#F3F4F7") if i%2==0 else colors.white
        resumen_style.append(('BACKGROUND', (0,i), (-1,i), bg))
    resumen_table.setStyle(TableStyle(resumen_style))
    return resumen_table
