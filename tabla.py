import customtkinter as ctk
from utiles.estilos import *

def mostrar_tabla(frame_tabla, df, modo="comparador", pagina=0, filas_por_pagina=30, on_pagina=None):
    for widget in frame_tabla.winfo_children():
        widget.destroy()
    if df.empty:
        ctk.CTkLabel(frame_tabla, text="Sin datos para mostrar", font=FUENTE_LABEL, text_color=COLOR_PRINCIPAL).pack(pady=40)
        return

    if modo == "comparador":
        columnas_mostrar = ["nombre", "departamento", "nombre_fb", "reacciono"]
    elif modo == "empleados":
        columnas_mostrar = ["nombre", "departamento", "puesto", "nombre_fb"]
    else:
        columnas_mostrar = df.columns.tolist()

    total_filas = len(df)
    inicio = pagina * filas_por_pagina
    fin = min(inicio + filas_por_pagina, total_filas)
    df_vista = df.iloc[inicio:fin]

    frame_scroll = ctk.CTkScrollableFrame(frame_tabla, fg_color=COLOR_BLANCO, height=400)
    frame_scroll.pack(fill="both", expand=True)

    for j, col in enumerate(columnas_mostrar):
        lbl = ctk.CTkLabel(
            frame_scroll, text=col.upper(), font=FUENTE_LABEL,
            text_color=COLOR_BLANCO, bg_color=COLOR_PRINCIPAL,
            width=160, anchor="center", pady=6
        )
        lbl.grid(row=0, column=j, padx=2, pady=3, sticky="nsew")
        frame_scroll.grid_columnconfigure(j, weight=1)

    for i, row in df_vista.iterrows():
        for j, col in enumerate(columnas_mostrar):
            val = row.get(col, "---")
            color = "#F3F4F7" if (i % 2 == 0) else "#FFFFFF"
            txtcolor = COLOR_TEXTO
            if col == "reacciono":
                if val:
                    val = "Sí"
                    color = "#FF9800"
                    txtcolor = COLOR_BLANCO
                else:
                    val = "No"
                    color = "#4CAF50"
                    txtcolor = COLOR_BLANCO
            ctk.CTkLabel(
                frame_scroll, text=str(val), font=FUENTE_TABLA, width=160,
                text_color=txtcolor, bg_color=color, anchor="center", pady=4
            ).grid(row=i+1, column=j, padx=2, pady=2, sticky="nsew")

    # SOLO muestra paginación si te mandan el callback
    if on_pagina:
        frame_paginacion = ctk.CTkFrame(frame_tabla, fg_color=COLOR_BLANCO)
        frame_paginacion.pack(fill="x", pady=(5, 0))
        paginas_totales = (total_filas + filas_por_pagina - 1) // filas_por_pagina

        btn_prev = ctk.CTkButton(
            frame_paginacion, text="⟨ Anterior", fg_color=COLOR_PRINCIPAL, text_color=COLOR_BLANCO,
            state=("normal" if pagina > 0 else "disabled"),
            command=lambda: on_pagina(pagina - 1)
        )
        btn_prev.pack(side="left", padx=(10, 5), pady=6)

        lbl_pagina = ctk.CTkLabel(
            frame_paginacion,
            text=f"Página {pagina+1} de {paginas_totales}",
            font=FUENTE_LABEL, text_color=COLOR_PRINCIPAL
        )
        lbl_pagina.pack(side="left", padx=10)

        btn_next = ctk.CTkButton(
            frame_paginacion, text="Siguiente ⟩", fg_color=COLOR_PRINCIPAL, text_color=COLOR_BLANCO,
            state=("normal" if pagina < paginas_totales - 1 else "disabled"),
            command=lambda: on_pagina(pagina + 1)
        )
        btn_next.pack(side="left", padx=(5, 10), pady=6)



def mostrar_tabla_empleados(frame_tabla, df, pagina=0, filas_por_pagina=30, on_pagina=None, on_nuevo=None, on_editar=None, on_eliminar=None):
    for widget in frame_tabla.winfo_children():
        widget.destroy()
    if df.empty:
        ctk.CTkLabel(frame_tabla, text="Sin empleados para mostrar", font=FUENTE_LABEL, text_color=COLOR_PRINCIPAL).pack(pady=40)
        return

    columnas_mostrar = ["#", "nombre", "departamento", "puesto", "nombre_fb"]
    total_filas = len(df)
    inicio = pagina * filas_por_pagina
    fin = min(inicio + filas_por_pagina, total_filas)
    df_vista = df.iloc[inicio:fin]

    frame_top = ctk.CTkFrame(frame_tabla, fg_color=COLOR_BLANCO)
    frame_top.pack(fill="x")
    if on_nuevo:
        ctk.CTkButton(
            frame_top, text="➕ Nuevo empleado", fg_color=COLOR_VERDE, text_color=COLOR_BLANCO,
            command=on_nuevo
        ).pack(side="left", padx=10, pady=6)

    # Encabezados
    frame_scroll = ctk.CTkScrollableFrame(frame_tabla, fg_color=COLOR_BLANCO, height=400)
    frame_scroll.pack(fill="both", expand=True)

    for j, col in enumerate(columnas_mostrar):
        lbl = ctk.CTkLabel(
            frame_scroll, text=col.upper(), font=FUENTE_LABEL,
            text_color=COLOR_BLANCO, bg_color=COLOR_PRINCIPAL,
            width=90 if col == "#" else 160, anchor="center", pady=6
        )
        lbl.grid(row=0, column=j, padx=2, pady=3, sticky="nsew")
        frame_scroll.grid_columnconfigure(j, weight=1)

    for idx, (i, row) in enumerate(df_vista.iterrows()):
        # Numeración
        ctk.CTkLabel(
            frame_scroll, text=str(inicio + idx + 1), font=FUENTE_TABLA,
            width=60, text_color=COLOR_TEXTO, bg_color="#F3F4F7" if (idx % 2 == 0) else "#FFFFFF",
            anchor="center", pady=4
        ).grid(row=idx+1, column=0, padx=2, pady=2, sticky="nsew")
        # Campos
        for j, col in enumerate(columnas_mostrar[1:]):
            val = row.get(col, "---")
            ctk.CTkLabel(
                frame_scroll, text=str(val), font=FUENTE_TABLA, width=160,
                text_color=COLOR_TEXTO, bg_color="#F3F4F7" if (idx % 2 == 0) else "#FFFFFF",
                anchor="center", pady=4
            ).grid(row=idx+1, column=j+1, padx=2, pady=2, sticky="nsew")
        # Botones Editar/Eliminar (última columna)
        if on_editar or on_eliminar:
            btn_editar = ctk.CTkButton(
                frame_scroll, text="Editar", fg_color="#d5a100", text_color=COLOR_BLANCO,
                width=60, command=lambda r=row: on_editar(r) if on_editar else None
            )
            btn_editar.grid(row=idx+1, column=len(columnas_mostrar), padx=2, pady=2)
            btn_eliminar = ctk.CTkButton(
                frame_scroll, text="Eliminar", fg_color=COLOR_ROJO, text_color=COLOR_BLANCO,
                width=80, command=lambda r=row: on_eliminar(r) if on_eliminar else None
            )
            btn_eliminar.grid(row=idx+1, column=len(columnas_mostrar)+1, padx=2, pady=2)

    # Paginación
    frame_paginacion = ctk.CTkFrame(frame_tabla, fg_color=COLOR_BLANCO)
    frame_paginacion.pack(fill="x", pady=(5, 0))
    paginas_totales = (total_filas + filas_por_pagina - 1) // filas_por_pagina

    btn_prev = ctk.CTkButton(
        frame_paginacion, text="⟨ Anterior", fg_color=COLOR_PRINCIPAL, text_color=COLOR_BLANCO,
        state=("normal" if pagina > 0 else "disabled"),
        command=lambda: on_pagina(pagina - 1) if on_pagina else None
    )
    btn_prev.pack(side="left", padx=(10, 5), pady=6)
    lbl_pagina = ctk.CTkLabel(
        frame_paginacion, text=f"Página {pagina+1} de {paginas_totales}",
        font=FUENTE_LABEL, text_color=COLOR_PRINCIPAL
    )
    lbl_pagina.pack(side="left", padx=10)
    btn_next = ctk.CTkButton(
        frame_paginacion, text="Siguiente ⟩", fg_color=COLOR_PRINCIPAL, text_color=COLOR_BLANCO,
        state=("normal" if pagina < paginas_totales - 1 else "disabled"),
        command=lambda: on_pagina(pagina + 1) if on_pagina else None
    )
    btn_next.pack(side="left", padx=(5, 10), pady=6)