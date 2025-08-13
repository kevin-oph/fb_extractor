import sqlite3
import pandas as pd

def get_connection():
    return sqlite3.connect("empleados.db")

def obtener_empleados():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, departamento, puesto, nombre_fb FROM empleados")
    empleados = cursor.fetchall()
    conn.close()
    df = pd.DataFrame(empleados, columns=["id", "nombre", "departamento", "puesto", "nombre_fb"])
    return df

def insertar_empleado(nombre, departamento, puesto, nombre_fb=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO empleados (nombre, departamento, puesto, nombre_fb) VALUES (?, ?, ?, ?)",
        (nombre, departamento, puesto, nombre_fb)
    )
    conn.commit()
    conn.close()

def editar_empleado(id_empleado, nombre=None, departamento=None, puesto=None, nombre_fb=None):
    conn = get_connection()
    cursor = conn.cursor()
    campos = []
    valores = []
    if nombre is not None:
        campos.append("nombre = ?")
        valores.append(nombre)
    if departamento is not None:
        campos.append("departamento = ?")
        valores.append(departamento)
    if puesto is not None:
        campos.append("puesto = ?")
        valores.append(puesto)
    if nombre_fb is not None:
        campos.append("nombre_fb = ?")
        valores.append(nombre_fb)
    valores.append(id_empleado)
    sql = f"UPDATE empleados SET {', '.join(campos)} WHERE id = ?"
    cursor.execute(sql, valores)
    conn.commit()
    conn.close()

def eliminar_empleado(id_empleado):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM empleados WHERE id = ?", (id_empleado,))
    conn.commit()
    conn.close()
