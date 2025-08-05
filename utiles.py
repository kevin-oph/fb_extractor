import unicodedata
import re


def normaliza_nombre(nombre):
    if nombre is None:
        return ""
    # Elimina espacios extra, pasa a minúsculas
    nombre = str(nombre).strip().lower()
    # Reemplaza dobles o múltiples espacios por uno solo
    nombre = re.sub(r'\s+', ' ', nombre)
    # Quita acentos/diacríticos
    nombre = ''.join(
        c for c in unicodedata.normalize('NFD', nombre)
        if unicodedata.category(c) != 'Mn'
    )
    return nombre

def obtener_lista_nombres(texto_multilinea):
    return [normaliza_nombre(n) for n in texto_multilinea.splitlines() if n.strip()]