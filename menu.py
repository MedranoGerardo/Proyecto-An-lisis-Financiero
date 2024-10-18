import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import locale

# Configurar el locale para formateo de números
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# Funciones de base de datos
def ejecutar_db(query, params=(), fetchone=False):
    with sqlite3.connect('contabilidad.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.fetchone() if fetchone else cursor.fetchall()

# Crear la tabla de cuentas al iniciar
def crear_tabla():
    ejecutar_db('''
        CREATE TABLE IF NOT EXISTS cuentas_balance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL,
            monto REAL NOT NULL
        )
    ''')

crear_tabla()

# Función para formatear números
def formatear_numero(numero):
    return locale.format_string('%.2f', numero, grouping=True)

# Función para guardar cuenta
def guardar_cuenta(nombre, tipo, monto):
    if ejecutar_db("SELECT COUNT(*) FROM cuentas_balance WHERE nombre = ?", (nombre,), fetchone=True)[0] > 0:
        messagebox.showerror("Error", "Ya existe una cuenta con ese nombre.")
        return
    ejecutar_db("INSERT INTO cuentas_balance (nombre, tipo, monto) VALUES (?, ?, ?)", (nombre, tipo, monto))
    messagebox.showinfo("Éxito", "Cuenta guardada correctamente.")

# Obtener todas las cuentas
def obtener_cuentas_balancegeneral():
    return ejecutar_db("SELECT nombre, tipo, monto FROM cuentas_balance")

# Función para actualizar la tabla de cuentas
def actualizar_tabla_cuentas(tabla):
    for fila in tabla.get_children():
        tabla.delete(fila)
    for nombre, tipo, monto in obtener_cuentas_balancegeneral():
        tabla.insert("", tk.END, values=(nombre, tipo, formatear_numero(monto)))

# Función para mostrar mensaje de "En desarrollo"
def mostrar_mensaje_en_desarrollo():
    messagebox.showinfo("En desarrollo", "Esta función está en desarrollo y estará disponible próximamente.")

# Interfaz de "Crear Cuenta - Balance General"
def crear_cuenta_balance_general(frame_principal):
    for widget in frame_principal.winfo_children():
        widget.destroy()

    # Crear un frame para los datos de entrada
    frame_datos = tk.Frame(frame_principal, bg="#a7c7e7", bd=2, relief="groove")  # Sección con fondo azul claro
    frame_datos.pack(padx=10, pady=10, fill="x")

    # Etiquetas y campos de entrada
    tk.Label(frame_datos, text="Nombre de la Cuenta:", bg="#a7c7e7", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="e")
    entry_nombre = tk.Entry(frame_datos, width=30)
    entry_nombre.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(frame_datos, text="Tipo de Cuenta:", bg="#a7c7e7", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky="e")
    tipo_var = tk.StringVar(value="Activos circulantes")
    opciones_tipo = ["Activos circulantes", "Activos no circulantes", "Pasivos circulantes", "Pasivos no circulantes", "Capital"]
    tk.OptionMenu(frame_datos, tipo_var, *opciones_tipo).grid(row=1, column=1, padx=10, pady=10, sticky="w")

    tk.Label(frame_datos, text="Monto:", bg="#a7c7e7", font=("Arial", 12, "bold")).grid(row=2, column=0, padx=10, pady=10, sticky="e")
    entry_monto = tk.Entry(frame_datos, width=30)
    entry_monto.grid(row=2, column=1, padx=10, pady=10)

    # Botón Guardar
    tk.Button(frame_datos, text="Guardar", command=lambda: guardar_cuenta(entry_nombre.get(), tipo_var.get(), float(entry_monto.get())), bg="#1c3847", fg="white", width=15, height=1, font=("Arial", 10, "bold")).grid(row=3, column=0, columnspan=2, pady=10)

    # Tabla para mostrar cuentas en otro frame
    frame_tabla = tk.Frame(frame_principal, bg="#a7c7e7")
    frame_tabla.pack(padx=10, pady=10, fill="x")

    tabla = ttk.Treeview(frame_tabla, columns=("Nombre", "Tipo", "Monto"), show='headings', height=5)
    tabla.heading("Nombre", text="Nombre")
    tabla.heading("Tipo", text="Tipo")
    tabla.heading("Monto", text="Monto")
    tabla.pack(padx=10, pady=10, fill="x")

    # Crear otro frame para la búsqueda y los botones de acciones
    frame_acciones = tk.Frame(frame_principal, bg="#a7c7e7", bd=2, relief="groove")
    frame_acciones.pack(padx=10, pady=10, fill="x")

    # Campo de entrada y etiqueta para búsqueda
    tk.Label(frame_acciones, text="Ingrese cuenta a buscar:", bg="#a7c7e7", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="e")
    entry_buscar = tk.Entry(frame_acciones, width=25)
    entry_buscar.grid(row=0, column=1, padx=10, pady=10)

    # Colocar los botones en la misma línea que el campo de entrada
    tk.Button(frame_acciones, text="Buscar Cuenta", command=lambda: buscar_cuenta_gui(entry_buscar.get(), tabla, entry_nombre, tipo_var, entry_monto), bg="#1c3847", fg="white", width=15, height=1, font=("Arial", 10, "bold")).grid(row=0, column=2, padx=10)
    tk.Button(frame_acciones, text="Eliminar Cuenta", command=lambda: eliminar_cuenta_gui(entry_nombre.get(), tabla), bg="#1c3847", fg="white", width=15, height=1, font=("Arial", 10, "bold")).grid(row=0, column=3, padx=10)
    tk.Button(frame_acciones, text="Editar Cuenta", command=lambda: editar_cuenta_gui(entry_nombre.get(), tipo_var.get(), float(entry_monto.get()), tabla), bg="#1c3847", fg="white", width=15, height=1, font=("Arial", 10, "bold")).grid(row=0, column=4, padx=10)

    actualizar_tabla_cuentas(tabla)  # Llenar tabla al cargar

# Funciones adicionales
def buscar_cuenta_gui(nombre, tabla, entry_nombre, tipo_var, entry_monto):
    cuenta = ejecutar_db("SELECT nombre, tipo, monto FROM cuentas_balance WHERE nombre = ?", (nombre,), fetchone=True)
    if cuenta:
        entry_nombre.delete(0, tk.END)
        entry_nombre.insert(0, cuenta[0])
        tipo_var.set(cuenta[1])
        entry_monto.delete(0, tk.END)
        entry_monto.insert(0, cuenta[2])
        actualizar_tabla_cuentas(tabla)
        messagebox.showinfo("Resultado de búsqueda", f"Cuenta encontrada:\nNombre: {cuenta[0]}\nTipo: {cuenta[1]}\nMonto: {formatear_numero(cuenta[2])}")
    else:
        messagebox.showerror("Error", "La cuenta no existe.")

def eliminar_cuenta_gui(nombre, tabla):
    if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar la cuenta '{nombre}'?"):
        ejecutar_db("DELETE FROM cuentas_balance WHERE nombre = ?", (nombre,))
        actualizar_tabla_cuentas(tabla)
        messagebox.showinfo("Éxito", "Cuenta eliminada correctamente.")

def editar_cuenta_gui(nombre, tipo, monto, tabla):
    if ejecutar_db("SELECT COUNT(*) FROM cuentas_balance WHERE nombre = ?", (nombre,), fetchone=True)[0] > 0:
        ejecutar_db("UPDATE cuentas_balance SET tipo = ?, monto = ? WHERE nombre = ?", (tipo, monto, nombre))
        actualizar_tabla_cuentas(tabla)
        messagebox.showinfo("Éxito", "Cuenta actualizada correctamente.")
    else:
        messagebox.showerror("Error", "La cuenta no existe.")

def mostrar_balance_general(frame_principal):
    for widget in frame_principal.winfo_children():
        widget.destroy()

    contenido_frame = tk.Frame(frame_principal, bg="#f0e68c")
    contenido_frame.pack(expand=True, fill="both", padx=20, pady=20)

    secciones = {
        "Activos circulantes": (1, 0),
        "Pasivos circulantes": (1, 1),
        "Activos no circulantes": (3, 0),
        "Pasivos no circulantes": (3, 1),
        "Capital": (5, 1)
    }

    tablas = {}
    for tipo, (fila, columna) in secciones.items():
        tk.Label(contenido_frame, text=tipo.upper(), bg="#f0e68c", font=("Arial", 14, "bold")).grid(row=fila, column=columna, padx=10, pady=10)
        tree = ttk.Treeview(contenido_frame, columns=("Nombre", "Monto"), show="headings", height=5)
        tree.heading("Nombre", text="Nombre")
        tree.heading("Monto", text="Monto")
        tree.grid(row=fila + 1, column=columna, padx=10, pady=10)
        tablas[tipo] = tree

    cargar_datos_balance(tablas)

def cargar_datos_balance(tablas):
    cuentas = obtener_cuentas_balancegeneral()
    totales = {tipo: 0 for tipo in tablas}
    for nombre, tipo, monto in cuentas:
        monto_formateado = formatear_numero(monto)
        if tipo in tablas:
            tablas[tipo].insert("", tk.END, values=(nombre, monto_formateado))
            totales[tipo] += monto

    for tipo, total in totales.items():
        tablas[tipo].insert("", tk.END, values=(f"Total de {tipo.lower()}", formatear_numero(total)), tags=("total",))

# Función del menú principal
def menu_principal():
    ventana_principal = tk.Tk()
    ventana_principal.title("Sistema de Contabilidad")
    screen_width = ventana_principal.winfo_screenwidth()
    screen_height = ventana_principal.winfo_screenheight()
    ventana_principal.geometry(f"{int(screen_width * 0.9)}x{int(screen_height * 0.9)}")
    ventana_principal.configure(bg="#6399b1")
    ventana_principal.resizable(True, True)

    ventana_principal.grid_rowconfigure(0, weight=1)
    ventana_principal.grid_columnconfigure(0, weight=1)  
    ventana_principal.grid_columnconfigure(1, weight=4)

    # Contenedor izquierdo (menú) con tamaño fijo
    frame_menu = tk.Frame(ventana_principal, bg="#6399b1", width=250)
    frame_menu.grid(row=0, column=0, sticky="ns")
    frame_menu.grid_propagate(False)  # Desactivar la propagación del tamaño

    # Contenedor derecho (principal)
    frame_principal = tk.Frame(ventana_principal, bg="#ffffff")
    frame_principal.grid(row=0, column=1, sticky="nsew")

    opciones = [
        ("Crear Cuenta - Estado de Resultado", mostrar_mensaje_en_desarrollo),
        ("Crear Cuenta - Balance General", lambda: crear_cuenta_balance_general(frame_principal)),
        ("Mostrar Estado de Resultado", mostrar_mensaje_en_desarrollo),
        ("Mostrar Balance General", lambda: mostrar_balance_general(frame_principal)),
        ("Salir", ventana_principal.quit)
    ]

    for texto, comando in opciones:
        color = "#a83232" if texto == "Salir" else "#1c3847"
        tk.Button(frame_menu, text=texto, command=comando, bg=color, fg="white", width=30, height=2, font=("Arial", 12, "bold")).pack(pady=10)

    crear_cuenta_balance_general(frame_principal)
    ventana_principal.mainloop()

menu_principal()
