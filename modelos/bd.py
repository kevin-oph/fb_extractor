import sqlite3
import os
import pandas as pd

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

def importar_empleados_excel(path):
    df = pd.read_excel(path)
    df.columns = [c.strip().lower() for c in df.columns]
    required_cols = ["nombre del trabajador", "departamento", "puesto"]
    if not all(col in df.columns for col in required_cols):
        raise ValueError("El archivo debe tener columnas: nombre del trabajador, departamento, puesto")

    conn = get_connection()
    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute(
            "INSERT INTO empleados (nombre, departamento, puesto, nombre_fb) VALUES (?, ?, ?, ?)",
            (row["nombre del trabajador"], row["departamento"], row["puesto"], "")
        )
    conn.commit()
    conn.close()
