import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re
import locale

# Configurar el locale para usar punto como separador decimal y coma como separador de miles
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# Funciones de validación
def validar_solo_letras(cadena):
    return all(caracter.isalpha() or caracter.isspace() for caracter in cadena)

def validar_dos_decimales(cadena):
    return re.match(r'^\d+(\.\d{1,2})?$', cadena) is not None

# Funciones de base de datos
def ejecutar_db(query, params=(), fetchone=False):
    with sqlite3.connect('contabilidad.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        if fetchone:
            return cursor.fetchone()
        return cursor.fetchall()

def crear_tabla():
    ejecutar_db('''
    CREATE TABLE IF NOT EXISTS cuentas_balance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        tipo TEXT NOT NULL,
        monto REAL NOT NULL
    )
    ''')

crear_tabla()  # Crear la tabla al iniciar

def cuenta_existe(nombre):
    return ejecutar_db("SELECT COUNT(*) FROM cuentas_balance WHERE nombre = ?", (nombre,), fetchone=True)[0] > 0

def guardar_cuenta(nombre, tipo, monto):
    if cuenta_existe(nombre):
        messagebox.showerror("Error", "Ya existe una cuenta con ese nombre.")
        return
    try:
        ejecutar_db("INSERT INTO cuentas_balance (nombre, tipo, monto) VALUES (?, ?, ?)", (nombre, tipo, monto))
        messagebox.showinfo("Éxito", "Cuenta guardada correctamente.")
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"No se pudo guardar la cuenta: {e}")

def obtener_cuentas_balancegeneral():
    return ejecutar_db("SELECT nombre, tipo, monto FROM cuentas_balance")

def buscar_cuenta(nombre):
    return ejecutar_db("SELECT nombre, tipo, monto FROM cuentas_balance WHERE nombre = ?", (nombre,), fetchone=True)

def editar_cuenta(nombre_original, nuevo_nombre, tipo, monto):
    if nombre_original != nuevo_nombre and cuenta_existe(nuevo_nombre):
        messagebox.showerror("Error", "Ya existe una cuenta con ese nombre.")
        return False
    ejecutar_db("UPDATE cuentas_balance SET nombre = ?, tipo = ?, monto = ? WHERE nombre = ?", (nuevo_nombre, tipo, monto, nombre_original))
    return True

def eliminar_cuenta(nombre):
    ejecutar_db("DELETE FROM cuentas_balance WHERE nombre = ?", (nombre,))

# Función para formatear números con punto decimal y coma como separador de miles
def formatear_numero(numero):
    return locale.format_string('%.2f', numero, grouping=True)

# Función para desformatear números (quitar comas)
def desformatear_numero(numero_str):
    return numero_str.replace(',', '')

# Funciones de la interfaz gráfica
def crear_cuenta_balance_general():
    ventana_datos = tk.Toplevel()
    ventana_datos.title("Crear Cuenta - Balance General")
    ventana_datos.geometry("620x650")
    ventana_datos.configure(bg="#6399b1")
    ventana_datos.resizable(False, False)

    campos = [
        ("Nombre de la Cuenta:", "entry_nombre", None),
        ("Tipo de Cuenta:", "tipo_var", ["Activos circulantes", "Activos no circulantes", "Pasivos circulantes", "Pasivos no circulantes", "Capital"]),
        ("Monto:", "entry_monto", None)
    ]

    widgets = {}
    for i, (label_text, widget_name, options) in enumerate(campos):
        tk.Label(ventana_datos, bg="#6399b1", font=("Arial", 10, "bold"), width=18, anchor="w", text=label_text).grid(row=i, column=0, padx=10, pady=10)
        if options:
            var = tk.StringVar(value=options[0])
            widget = tk.OptionMenu(ventana_datos, var, *options)
            widget.config(width=23)
            widgets[widget_name] = var
        else:
            widget = tk.Entry(ventana_datos, width=30)
            widgets[widget_name] = widget
        widget.grid(row=i, column=1, padx=10, pady=10)

    tabla = ttk.Treeview(ventana_datos, columns=("Nombre", "Tipo", "Monto"), show='headings')
    for col in tabla['columns']:
        tabla.heading(col, text=col)
    tabla.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    tk.label_buscarCuenta = tk.Label(ventana_datos, bg="#6399b1", font=("Arial", 10, "bold"), width=20, anchor="w", text="Ingrese cuenta a buscar:")
    tk.label_buscarCuenta.grid(row=5, column=0, padx=0, pady=0)
    entry_buscarCuenta = tk.Entry(ventana_datos, width=25)
    entry_buscarCuenta.grid(row=6, column=0, padx=0, pady=0)

    def actualizar_tabla_cuentas():
        for fila in tabla.get_children():
            tabla.delete(fila)
        for cuenta in obtener_cuentas_balancegeneral():
            nombre, tipo, monto = cuenta
            monto_formateado = formatear_numero(monto)
            tabla.insert("", tk.END, values=(nombre, tipo, monto_formateado))

    def limpiar_campos():
        widgets['entry_nombre'].delete(0, tk.END)
        widgets['tipo_var'].set("Activos circulantes")
        widgets['entry_monto'].delete(0, tk.END)
        entry_buscarCuenta.delete(0, tk.END)

    def validar_campos():
        nombre = widgets['entry_nombre'].get().strip()
        monto_texto = widgets['entry_monto'].get().strip()
        if not nombre or not monto_texto:
            messagebox.showerror("Error", "No puede dejar campos vacíos.")
            return False
        if not validar_solo_letras(nombre):
            messagebox.showerror("Error", "El nombre de la cuenta solo puede contener letras.")
            return False
        if not validar_dos_decimales(monto_texto):
            messagebox.showerror("Error", "El monto debe ser un número con máximo dos decimales.")
            return False
        return True

    nombre_original = tk.StringVar()

    def buscar_cuenta_gui():
        nombre = entry_buscarCuenta.get().strip()
        if not nombre:
            messagebox.showerror("Error", "Ingrese un nombre de cuenta para buscar.")
            return
        cuenta = buscar_cuenta(nombre)
        if cuenta:
            widgets['entry_nombre'].delete(0, tk.END)
            widgets['entry_nombre'].insert(0, cuenta[0])
            widgets['tipo_var'].set(cuenta[1])
            widgets['entry_monto'].delete(0, tk.END)
            widgets['entry_monto'].insert(0, str(cuenta[2]))
            nombre_original.set(cuenta[0])
            messagebox.showinfo("Éxito", "Cuenta encontrada.")
        else:
            messagebox.showerror("Error", "La cuenta no existe.")

    def eliminar_cuenta_gui():
        nombre = widgets['entry_nombre'].get().strip()
        if not nombre:
            messagebox.showerror("Error", "Seleccione una cuenta para eliminar.")
            return
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar la cuenta '{nombre}'?"):
            eliminar_cuenta(nombre)
            messagebox.showinfo("Éxito", "Cuenta eliminada correctamente.")
            limpiar_campos()
            actualizar_tabla_cuentas()

    def editar_cuenta_gui():
        if not validar_campos():
            return
        nuevo_nombre = widgets['entry_nombre'].get().strip()
        tipo = widgets['tipo_var'].get()
        monto = float(widgets['entry_monto'].get().strip())
        if editar_cuenta(nombre_original.get(), nuevo_nombre, tipo, monto):
            messagebox.showinfo("Éxito", "Cuenta actualizada correctamente.")
            actualizar_tabla_cuentas()
            limpiar_campos()
            nombre_original.set('')
        else:
            messagebox.showerror("Error", "No se pudo actualizar la cuenta.")

    def submit_datos():
        if not validar_campos():
            return
        nombre = widgets['entry_nombre'].get().strip()
        tipo = widgets['tipo_var'].get()
        monto = float(widgets['entry_monto'].get().strip())
        guardar_cuenta(nombre, tipo, monto)
        actualizar_tabla_cuentas()
        limpiar_campos()

    botones = [
        ("Guardar", submit_datos, 3, 0),
        ("Buscar Cuenta", buscar_cuenta_gui, 5, 1),
        ("Eliminar Cuenta", eliminar_cuenta_gui, 6, 1),
        ("Editar Cuenta", editar_cuenta_gui, 7, 1)
    ]

    for texto, comando, fila, columna in botones:
        tk.Button(ventana_datos, text=texto, command=comando, bg="#1c3847", fg="white", width=30, height=2, font=("Arial", 10, "bold")).grid(row=fila, column=columna, columnspan=2, padx=10, pady=10)

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
            ejecutar_db("DELETE FROM cuentas_balance")
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

    botones = [
        ("Borrar Contenido", borrar_contenido, 0, 2),
        ("Cerrar", cerrar_ventana, 2, 2)
    ]

    for texto, comando, fila, columna in botones:
        tk.Button(ventana_tabla, text=texto, command=comando, bg="#a83232", fg="white", width=30, height=2, font=("Arial", 10, "bold")).grid(row=fila, column=columna, padx=10, pady=10)

    trees = {
        "Activos circulantes": (1, 0),
        "Activos no circulantes": (3, 0),
        "Pasivos circulantes": (1, 1),
        "Pasivos no circulantes": (3, 1),
        "Capital": (5, 1)
    }

    for tipo, (fila, columna) in trees.items():
        tree = ttk.Treeview(ventana_tabla, columns=("Nombre", "Monto"), show='headings')
        for col in tree['columns']:
            tree.heading(col, text=col)
        tree.grid(row=fila, column=columna, padx=10, pady=10)
        tree.tag_configure("total", background="#3a596b", foreground="white")
        trees[tipo] = tree

    filas = obtener_cuentas_balancegeneral()

    totales = {tipo: 0 for tipo in trees.keys()}
    for nombre, tipo, monto in filas:
        monto_formateado = formatear_numero(monto)
        trees[tipo].insert("", tk.END, values=(nombre, monto_formateado))
        totales[tipo] += monto

    for tipo, tree in trees.items():
        total_formateado = formatear_numero(totales[tipo])
        tree.insert("", tk.END, values=(f"Total de {tipo.lower()}", total_formateado), tags=("total",))

    total_activos = totales["Activos circulantes"] + totales["Activos no circulantes"]
    total_pasivos_patrimonio = sum(totales[tipo] for tipo in ["Pasivos circulantes", "Pasivos no circulantes", "Capital"])

    tk.Label(ventana_tabla, bg="#6399b1", fg="#a83232", text=f"Total de activos = ${formatear_numero(total_activos)}", font=("Arial", 14, "bold")).grid(row=6, column=0, columnspan=1, padx=10, pady=10)
    tk.Label(ventana_tabla, bg="#6399b1", fg="#a83232", text=f"Total de pasivos + patrimonio = ${formatear_numero(total_pasivos_patrimonio)}", font=("Arial", 14, "bold")).grid(row=6, column=1, columnspan=1, padx=10, pady=10)

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