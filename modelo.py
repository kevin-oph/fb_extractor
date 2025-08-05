# modelo.py
import pandas as pd
from utiles import normaliza_nombre

def cargar_base_empleados(path):
    df_raw = pd.read_excel(path, header=None, nrows=20)
    encabezado_idx = None
    for i, row in df_raw.iterrows():
        columnas = [str(col).strip().lower() for col in row]
        if "nombre" in columnas and "departamento" in columnas:
            encabezado_idx = i
            break
    if encabezado_idx is None:
        raise Exception("No se encontró encabezado válido (debe tener 'nombre' y 'departamento')")
    df = pd.read_excel(path, header=encabezado_idx)
    df = df.dropna(how='all')
    return df

def comparar_reacciones(df_empleados, lista_nombres):
    df = df_empleados.copy()
    col_nombre = 'nombre_fb' if 'nombre_fb' in df.columns else 'nombre'
    df['nombre_norm'] = df[col_nombre].apply(normaliza_nombre)

    # ¡Normalizamos los nombres pegados para comparar, pero guardamos el original!
    nombres_norm = [normaliza_nombre(n) for n in lista_nombres if n]
    df['reacciono'] = df['nombre_norm'].isin(nombres_norm)

    # --- Mejora: Para mostrar "no registrados" tal cual se pegaron ---
    nombres_encontrados = set(df['nombre_norm'])
    # Creamos una lista de TUPLAS (nombre original, nombre normalizado)
    nombres_con_norm = [(n, normaliza_nombre(n)) for n in lista_nombres if n]
    nombres_no_registrados = [n_orig for (n_orig, n_norm) in nombres_con_norm if n_norm not in nombres_encontrados]

    return df, nombres_no_registrados


def agregar_reporte(historial, titulo_publicacion, post_msg, post_date, df_resultado, nombres_no_encontrados):
    resumen = {
        "titulo_publicacion": titulo_publicacion,
        "post_mensaje": post_msg,
        "post_fecha": post_date,
        "df_resultado": df_resultado,
        "no_encontrados": nombres_no_encontrados,
        "totales": {
            "total_pegados": len(nombres_no_encontrados) + df_resultado['reacciono'].sum(),
            "total_empleados": len(df_resultado),
            "total_reacciono": df_resultado['reacciono'].sum(),
            "total_no_reacciono": len(df_resultado) - df_resultado['reacciono'].sum(),
            "total_no_encontrados": len(nombres_no_encontrados)
        }
    }
    historial.append(resumen)
