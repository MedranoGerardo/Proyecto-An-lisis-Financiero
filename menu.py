import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re
from tkinter import simpledialog

# Funciones de validación
def validar_solo_letras(cadena):
    return all(caracter.isalpha() or caracter.isspace() for caracter in cadena)

def validar_dos_decimales(cadena):
    patron = r'^\d+(\.\d{1,2})?$'
    return re.match(patron, cadena) is not None

# Funciones de base de datos
def crear_conexion():
    return sqlite3.connect('contabilidad.db')

def crear_tabla():
    with crear_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cuentas_balance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL,
            monto REAL NOT NULL
        )
        ''')
        conn.commit()

crear_tabla()  # Crear la tabla al iniciar

def cuenta_existe(nombre):
    with crear_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cuentas_balance WHERE nombre = ?", (nombre,))
        return cursor.fetchone()[0] > 0

def guardar_cuenta(nombre, tipo, monto):
    if cuenta_existe(nombre):
        messagebox.showerror("Error", "Ya existe una cuenta con ese nombre.")
        return
    try:
        with crear_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO cuentas_balance (nombre, tipo, monto) VALUES (?, ?, ?)", (nombre, tipo, monto))
            conn.commit()
        messagebox.showinfo("Éxito", "Cuenta guardada correctamente.")
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"No se pudo guardar la cuenta: {e}")

def obtener_cuentas_balancegeneral():
    with crear_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, tipo, monto FROM cuentas_balance")
        return cursor.fetchall()

# Funciones de la interfaz gráfica
def crear_cuenta_balance_general():
    ventana_datos = tk.Toplevel()
    ventana_datos.title("Crear Cuenta - Balance General")
    ventana_datos.geometry("620x650")
    ventana_datos.configure(bg="#6399b1")
    ventana_datos.resizable(False, False)

    tk.Label(ventana_datos, bg="#6399b1", font=("Arial", 10, "bold"), width=18, anchor="w", text="Nombre de la Cuenta:").grid(row=0, column=0, padx=10, pady=10)
    entry_nombre = tk.Entry(ventana_datos, width=30)
    entry_nombre.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(ventana_datos, bg="#6399b1", font=("Arial", 10, "bold"), width=18, anchor="w", text="Tipo de Cuenta:").grid(row=1, column=0, padx=10, pady=10)
    tipo_var = tk.StringVar(value="Activos circulantes")
    option_tipo = tk.OptionMenu(ventana_datos, tipo_var, "Activos circulantes", "Activos no circulantes", "Pasivos circulantes", "Pasivos no circulantes", "Capital")
    option_tipo.grid(row=1, column=1, padx=10, pady=10)
    option_tipo.config(width=23)

    tk.Label(ventana_datos, bg="#6399b1", font=("Arial", 10, "bold"), width=18, anchor="w", text="Monto:").grid(row=2, column=0, padx=10, pady=10)
    entry_monto = tk.Entry(ventana_datos, width=30)
    entry_monto.grid(row=2, column=1, padx=10, pady=10)

    tabla = ttk.Treeview(ventana_datos, columns=("Nombre", "Tipo", "Monto"), show='headings')
    tabla.heading("Nombre", text="Nombre")
    tabla.heading("Tipo", text="Tipo")
    tabla.heading("Monto", text="Monto")
    tabla.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    entry_buscarCuenta = tk.Entry(ventana_datos, width=30)
    entry_buscarCuenta.grid(row=5, column=0, padx=10, pady=10)

    btn_buscarCuenta = tk.Button(ventana_datos, text="Buscar Cuenta", bg="#1c3847", fg="white", width=30, height=2)
    btn_buscarCuenta.grid(row=5, column=1, padx=10, pady=10)

    btn_eliminarCuenta = tk.Button(ventana_datos, text="Eliminar Cuenta", bg="#1c3847", fg="white", width=30, height=2)
    btn_eliminarCuenta.grid(row=6, column=1, columnspan=2, padx=10, pady=10)

    btn_editarCuenta = tk.Button(ventana_datos, text="Editar Cuenta", bg="#1c3847", fg="white", width=30, height=2)
    btn_editarCuenta.grid(row=7, column=1, columnspan=2, padx=10, pady=10)

    def actualizar_tabla_cuentas():
        for fila in tabla.get_children():
            tabla.delete(fila)
        cuentas = obtener_cuentas_balancegeneral()
        for cuenta in cuentas:
            tabla.insert("", tk.END, values=cuenta)

    def submit_datos():
        nombre = entry_nombre.get().strip()
        tipo = tipo_var.get()
        monto_texto = entry_monto.get().strip()

        if not nombre or not monto_texto:
            messagebox.showerror("Error", "No puede dejar campos vacíos.")
            return
        if not validar_solo_letras(nombre):
            messagebox.showerror("Error", "El nombre de la cuenta solo puede contener letras.")
            return
        if not validar_dos_decimales(monto_texto):
            messagebox.showerror("Error", "El monto debe ser un número con máximo dos decimales.")
            return

        try:
            monto = float(monto_texto)
            guardar_cuenta(nombre, tipo, monto)
            actualizar_tabla_cuentas()
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número válido.")

    btn_guardar = tk.Button(ventana_datos, text="Guardar", command=submit_datos, bg="#1c3847", fg="white", width=30, height=2)
    btn_guardar.grid(row=3, column=0, columnspan=2, pady=10)

    actualizar_tabla_cuentas()

def mostrar_balance_general():
    ventana_tabla = tk.Toplevel()
    ventana_tabla.title("Balance General")
    ventana_tabla.configure(bg="#6399b1")
    ventana_tabla.resizable(False, False)

    def cerrar_ventana():
        ventana_tabla.destroy()

    def borrar_contenido():
        try:
            with crear_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cuentas_balance")
                conn.commit()
            messagebox.showinfo("Éxito", "Se han borrado todos los registros correctamente.")
            ventana_tabla.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo borrar los registros: {e}")

    etiquetas = [
        ("ACTIVOS CIRCULANTES", 0, 0),
        ("ACTIVOS NO CIRCULANTES", 2, 0),
        ("PASIVOS CIRCULANTES", 0, 1),
        ("PASIVOS NO CIRCULANTES", 2, 1),
        ("PATRIMONIO", 4, 1)
    ]

    for texto, fila, columna in etiquetas:
        tk.Label(ventana_tabla, text=texto, bg="#6399b1", font=("Arial", 14, "bold")).grid(row=fila, column=columna, padx=10, pady=10)

    btn_borrar_contenido = tk.Button(ventana_tabla, text="Borrar Contenido", command=borrar_contenido, bg="#a83232", fg="white", width=30, height=2, font=("Arial", 10, "bold"))
    btn_borrar_contenido.grid(row=0, column=2, padx=10, pady=10)

    btn_cerrar = tk.Button(ventana_tabla, text="Cerrar", command=cerrar_ventana, bg="#a83232", fg="white", width=30, height=2, font=("Arial", 10, "bold"))
    btn_cerrar.grid(row=2, column=2, padx=10, pady=10)

    trees = {
        "Activos circulantes": (1, 0),
        "Activos no circulantes": (3, 0),
        "Pasivos circulantes": (1, 1),
        "Pasivos no circulantes": (3, 1),
        "Capital": (5, 1)
    }

    for tipo, (fila, columna) in trees.items():
        tree = ttk.Treeview(ventana_tabla, columns=("Nombre", "Monto"), show='headings')
        tree.heading("Nombre", text="Nombre de la Cuenta")
        tree.heading("Monto", text="Monto")
        tree.grid(row=fila, column=columna, padx=10, pady=10)
        tree.tag_configure("total", background="#3a596b", foreground="white")
        trees[tipo] = tree

    filas = obtener_cuentas_balancegeneral()

    totales = {tipo: 0 for tipo in trees.keys()}
    for nombre, tipo, monto in filas:
        monto_formateado = f"{monto:,.2f}"
        trees[tipo].insert("", tk.END, values=(nombre, monto_formateado))
        totales[tipo] += monto

    for tipo, tree in trees.items():
        total_formateado = f"{totales[tipo]:,.2f}"
        tree.insert("", tk.END, values=(f"Total de {tipo.lower()}", total_formateado), tags=("total",))

    total_activos = totales["Activos circulantes"] + totales["Activos no circulantes"]
    total_pasivos_patrimonio = (totales["Pasivos circulantes"] +
                                totales["Pasivos no circulantes"] +
                                totales["Capital"])

    tk.Label(ventana_tabla, bg="#6399b1", fg="#a83232", text=f"Total de activos = ${total_activos:,.2f}", font=("Arial", 14, "bold")).grid(row=6, column=0, columnspan=1, padx=10, pady=10)
    tk.Label(ventana_tabla, bg="#6399b1", fg="#a83232", text=f"Total de pasivos + patrimonio = ${total_pasivos_patrimonio:,.2f}", font=("Arial", 14, "bold")).grid(row=6, column=1, columnspan=1, padx=10, pady=10)

def menu_principal():
    ventana_principal = tk.Tk()
    ventana_principal.title("Sistema de Contabilidad")
    ventana_principal.geometry("400x360")
    ventana_principal.configure(bg="#6399b1")
    ventana_principal.resizable(False, False)

    botones = [
        ("Crear Cuenta - Estado de Resultado", None),
        ("Crear Cuenta - Balance General", crear_cuenta_balance_general),
        ("Mostrar Estado de Resultado", None),
        ("Mostrar Balance General", mostrar_balance_general),
        ("Salir", ventana_principal.quit)
    ]

    for texto, comando in botones:
        color = "#a83232" if texto == "Salir" else "#1c3847"
        tk.Button(ventana_principal, text=texto, command=comando, bg=color, fg="white", width=30, height=2, font=("Arial", 12, "bold")).pack(pady=10)

    ventana_principal.mainloop()