import unicodedata

def normaliza_nombre(nombre):
    if not nombre:
        return ""
    nombre = nombre.lower().strip()
    nombre = ''.join(
        c for c in unicodedata.normalize('NFD', nombre)
        if unicodedata.category(c) != 'Mn'
    )
    nombre = nombre.replace("  ", " ")
    return nombre

def obtener_lista_nombres(texto):
    return [line.strip() for line in texto.strip().splitlines() if line.strip()]
