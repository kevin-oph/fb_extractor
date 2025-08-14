# utiles/normalizacion.py
import re
import unicodedata
import pandas as pd

# 🔁 Mapa de alias -> nombre canónico
ALIAS_DEPARTAMENTOS = {
    # ---- SISTEMAS Y DESARROLLO TECNOLÓGICO ----
    "SIST Y DES TECNOLOGICO": "SISTEMAS Y DESARROLLO TECNOLOGICO",
    "SIST Y DES. TECNOLOGICO": "SISTEMAS Y DESARROLLO TECNOLOGICO",
    "SISTEMAS Y DES. TECNOLOGICO": "SISTEMAS Y DESARROLLO TECNOLOGICO",
    "SISTEMAS Y DESARROLLO TEC": "SISTEMAS Y DESARROLLO TECNOLOGICO",
    "SISTEMAS Y DES TECNOLOGICO": "SISTEMAS Y DESARROLLO TECNOLOGICO",
    "SISTEMAS Y DESARROLLO TECNOLOGICO": "SISTEMAS Y DESARROLLO TECNOLOGICO",

    # 👇 Agrega aquí más alias si detectas otros casos en tu base
    # "TES. MUN.": "TESORERIA MUNICIPAL",
    # "DIR. TRANSITO": "DIRECCION DE TRANSITO",
}

def _quitar_acentos_y_limpiar(s: str) -> str:
    s = s.upper().strip()
    s = "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )
    s = re.sub(r"[^\w\s]", " ", s)  # quita puntuación
    s = re.sub(r"\s+", " ", s)      # espacios múltiples -> uno
    return s.strip()

def normalizar_departamento(nombre: str) -> str:
    if not nombre:
        return ""
    s_norm = _quitar_acentos_y_limpiar(nombre)

    # 1) Coincidencia exacta en alias
    if s_norm in ALIAS_DEPARTAMENTOS:
        return ALIAS_DEPARTAMENTOS[s_norm]

    # 2) Heurística para SISTEMAS Y DESARROLLO TECNOLÓGICO
    #    (si contiene tokens clave en cualquier orden)
    tokens = s_norm.split()
    tiene = lambda t: any(tok.startswith(t) for tok in tokens)
    if tiene("SIST") and tiene("DES") and (tiene("TEC") or "TECNOLOGICO" in tokens):
        return "SISTEMAS Y DESARROLLO TECNOLOGICO"

    # 3) Dejar el original si no hay regla
    return nombre.strip()

def normalizar_df_departamentos(df: pd.DataFrame, col: str = "departamento") -> pd.DataFrame:
    if df is None or df.empty:
        return df
    if col not in df.columns:
        return df
    df2 = df.copy()
    df2[col] = df2[col].astype(str).map(normalizar_departamento)
    return df2
