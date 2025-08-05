import sqlite3
import os
import pandas as pd
from tkinter import filedialog

DB_NAME = "empleados.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def inicializar_bd():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS empleados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            departamento TEXT,
            puesto TEXT,
            nombre_fb TEXT
        )
    ''')
    conn.commit()
    conn.close()

def existe_bd():
    return os.path.exists(DB_NAME)

def importar_empleados_excel(ruta_excel):
    """Lee empleados desde un Excel y los inserta a la BD."""
    ruta = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xlsx")])
    if ruta:
        df = pd.read_excel(ruta, header=10)
    # Normaliza los nombres de columnas
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Checa que existan las columnas que necesitas
    if not all(c in df.columns for c in ["nombre del trabajador", "departamento", "puesto"]):
        raise ValueError("El archivo debe tener columnas: nombre del trabajador, departamento, puesto")
    
    # Conecta a la BD
    conn = get_connection()
    cursor = conn.cursor()
    
    
    # Inserta nuevos
    for _, row in df.iterrows():
        cursor.execute('''
            INSERT INTO empleados (nombre, departamento, puesto, nombre_fb)
            VALUES (?, ?, ?, ?)
        ''', (
            row["nombre del trabajador"], row["departamento"], row["puesto"], ""
        ))
    conn.commit()
    conn.close()