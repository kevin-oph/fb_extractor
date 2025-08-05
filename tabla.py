# tabla.py
import customtkinter as ctk
from estilos import *

def mostrar_tabla(frame_tabla, df):
    for widget in frame_tabla.winfo_children():
        widget.destroy()
    # Encabezado centrado
    frame_scroll = ctk.CTkScrollableFrame(frame_tabla, fg_color=COLOR_BLANCO, bg_color=COLOR_BLANCO, height=300)
    frame_scroll.pack(fill="both", expand=True)

    columnas_mostrar = [col for col in df.columns if col not in ['nombre_norm']]
    # Encabezados
    for j, col in enumerate(columnas_mostrar):
        lbl = ctk.CTkLabel(
            frame_scroll, text=col, font=FUENTE_LABEL,
            text_color=COLOR_BLANCO, bg_color=COLOR_PRINCIPAL,
            width=150, anchor="center"
        )
        lbl.grid(row=0, column=j, padx=3, pady=5, sticky="nsew")
        frame_scroll.grid_columnconfigure(j, weight=1)  # Hace columnas elásticas

    # Filas
    for i, row in df.iterrows():
        for j, col in enumerate(columnas_mostrar):
            val = row[col]
            # Estilo profesional de celdas
            if str(col).lower() == 'reacciono':
                color = COLOR_VERDE if val else COLOR_ROJO
                txtcolor = COLOR_BLANCO
                val = "Sí" if val else "No"
            else:
                color = "#F3F4F7" if i % 2 == 0 else "#FFFFFF"  # alterna filas
                txtcolor = COLOR_TEXTO
            ctk.CTkLabel(
                frame_scroll, text=str(val), font=FUENTE_TABLA, width=150,
                text_color=txtcolor, bg_color=color, anchor="center"
            ).grid(row=i+1, column=j, padx=2, pady=2, sticky="nsew")
