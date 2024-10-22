import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re
import locale

# Configuración de locale
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

# Funciones de formateo de números
def formatear_numero(numero):
    return locale.format_string('%.2f', numero, grouping=True)

def desformatear_numero(numero_str):
    return numero_str.replace(',', '')

# Funciones de la interfaz gráfica
def crear_cuentas_Estados_Financieros(frame):
    for widget in frame.winfo_children():
        widget.destroy()

    frame.configure(bg="#E0F2FE")  # Fondo azul claro

    # Frame principal
    main_frame = tk.Frame(frame, bg="#E0F2FE")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Frame para los campos de entrada (parte superior)
    input_frame = tk.Frame(main_frame, bg="#E0F2FE", relief="raised", borderwidth=1)
    input_frame.pack(fill=tk.X, pady=(0, 20))

    # Campos de entrada
    campos = [
        ("Nombre de la Cuenta:", "entry_nombre"),
        ("Tipo de Cuenta:", "tipo_var"),
        ("Monto:", "entry_monto")
    ]

    widgets = {}
    for i, (label_text, widget_name) in enumerate(campos):
        tk.Label(input_frame, text=label_text, bg="#E0F2FE", font=("Arial", 11, "bold"), fg="#1E3A8A").grid(row=i, column=0, padx=10, pady=10, sticky="e")
        if widget_name == "tipo_var":
            var = tk.StringVar(value="Activos circulantes")
            widget = ttk.Combobox(input_frame, textvariable=var, values=["Activos circulantes", "Activos no circulantes", "Pasivos circulantes", "Pasivos no circulantes", "Capital"], state="readonly", width=28)
            widgets[widget_name] = var
        else:
            widget = tk.Entry(input_frame, width=30, bg="#F3F4F6")  # Fondo gris suave para entradas
            widgets[widget_name] = widget
        widget.grid(row=i, column=1, padx=10, pady=10, sticky="w")

    # Frame para la tabla (parte central)
    table_frame = tk.Frame(main_frame, bg="#E0F2FE", relief="raised", borderwidth=1)
    table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

    # Tabla de cuentas
    tabla = ttk.Treeview(table_frame, columns=("Nombre", "Tipo", "Monto"), show='headings', height=5)
    for col in tabla['columns']:
        tabla.heading(col, text=col)
        tabla.column(col, width=150)
    tabla.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Frame para la búsqueda y botones (parte inferior)
    search_frame = tk.Frame(main_frame, bg="#E0F2FE", relief="raised", borderwidth=1)
    search_frame.pack(fill=tk.X)

    tk.Label(search_frame, text="Ingrese cuenta a buscar:", bg="#E0F2FE", font=("Arial", 10, "bold"), fg="#1E3A8A").pack(side=tk.LEFT, padx=(10, 5), pady=10)
    entry_buscarCuenta = tk.Entry(search_frame, width=30, bg="#F3F4F6")
    entry_buscarCuenta.pack(side=tk.LEFT, padx=5, pady=10)

    botones = [
        ("Buscar Cuenta", lambda: buscar_cuenta_gui()),
        ("Eliminar Cuenta", lambda: eliminar_cuenta_gui()),
        ("Editar Cuenta", lambda: editar_cuenta_gui())
    ]

    for texto, comando in botones:
        tk.Button(search_frame, text=texto, command=comando, bg="#1E3A8A", fg="white", activebackground="#00587A", width=15, height=1, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5, pady=10)

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

    tk.Button(input_frame, text="Guardar", command=submit_datos, bg="#1E3A8A", fg="white", activebackground="#00587A", width=15, height=1, font=("Arial", 10, "bold")).grid(row=3, column=1, pady=10, sticky="w")
    botones_frame = tk.Frame(frame, bg="#E0F2FE")
    botones_frame.pack(fill=tk.X, pady=10)

    actualizar_tabla_cuentas()

def mostrar_balance_general(frame):
    for widget in frame.winfo_children():
        widget.destroy()

    frame.configure(bg="#E0F2FE")

    categorias = [
        ("ACTIVOS CIRCULANTES", 0, 0),
        ("ACTIVOS NO CIRCULANTES", 1, 0),
        ("PASIVOS CIRCULANTES", 0, 1),
        ("PASIVOS NO CIRCULANTES", 1, 1),
        ("CAPITAL", 2, 1)
    ]

    trees = {}
    for titulo, row, col in categorias:
        frame_categoria = tk.Frame(frame, bg="#E0F2FE")
        frame_categoria.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        tk.Label(frame_categoria, text=titulo, bg="#E0F2FE", font=("Arial", 12, "bold"), fg="#1E3A8A").pack()

        tree = ttk.Treeview(frame_categoria, columns=("Nombre", "Monto"), show='headings', height=5)
        tree.heading("Nombre", text="Nombre")
        tree.heading("Monto", text="Monto")
        tree.column("Nombre", width=170)
        tree.column("Monto", width=100)
        tree.pack(fill=tk.BOTH, expand=True)

        trees[titulo.lower().replace(" ", "_")] = tree

    filas = obtener_cuentas_balancegeneral()
    totales = {categoria: 0 for categoria in trees.keys()}

    for nombre, tipo, monto in filas:
        categoria = tipo.lower().replace(" ", "_")
        monto_formateado = formatear_numero(monto)
        trees[categoria].insert("", tk.END, values=(nombre, monto_formateado))
        totales[categoria] += monto

    for tipo, tree in trees.items():
        total_formateado = formatear_numero(totales[tipo])
        tree.insert("", tk.END, values=(f"Total de {tipo.lower()}", total_formateado), tags=("total",))
        tree.tag_configure("total", background="#1E3A8A", foreground="white")

    total_activos = totales["activos_circulantes"] + totales["activos_no_circulantes"]
    total_pasivos_patrimonio = sum(totales[tipo] for tipo in ["pasivos_circulantes", "pasivos_no_circulantes", "capital"])

    tk.Label(frame, bg="#E0F2FE", fg="#a83232", text=f"Total de activos = ${formatear_numero(total_activos)}", font=("Arial", 14, "bold")).grid(row=3, column=0, columnspan=1, padx=10, pady=10)
    tk.Label(frame, bg="#E0F2FE", fg="#a83232", text=f"Total de pasivos + patrimonio = ${formatear_numero(total_pasivos_patrimonio)}", font=("Arial", 14, "bold")).grid(row=3, column=1, columnspan=1, padx=10, pady=10)

#Cerrar la aplicación
def cerrar_aplicacion(ventana):
    ventana.quit()
    ventana.destroy()
    import sys
    sys.exit()

def menu_principal():
    ventana_principal = tk.Tk()
    ventana_principal.title("Sistema de Contabilidad")
    ventana_principal.geometry("1200x600")
    ventana_principal.configure(bg="#E0F2FE")  # Fondo azul claro
    ventana_principal.resizable(True, True)

    frame_botones = tk.Frame(ventana_principal, bg="#1E3A8A", width=290, height=400)  # Azul oscuro para menú lateral
    frame_botones.pack(side=tk.LEFT, fill=tk.Y)
    frame_botones.pack_propagate(False)

    frame_contenido = tk.Frame(ventana_principal, bg="#E0F2FE")  # Fondo azul claro
    frame_contenido.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    botones = [
        ("Ver catalogo de cuentas", None),
        ("Crear Cuenta - Para catalogo de cuentas", lambda: crear_cuentas_Estados_Financieros(frame_contenido)),
        ("Mostrar Estado de Resultado", None),
        ("Mostrar Balance General", lambda: mostrar_balance_general(frame_contenido)),
        ("Salir", lambda: cerrar_aplicacion(ventana_principal))
    ]

    for texto, comando in botones:
        color = "#DC2626" if texto == "Salir" else "#1E3A8A"  
        tk.Button(frame_botones, text=texto, command=comando, bg=color, fg="white", activebackground="#00587A", width=33, height=2, font=("Arial", 10, "bold")).pack(pady=5)

    ventana_principal.protocol("WM_DELETE_WINDOW", lambda: cerrar_aplicacion(ventana_principal))
    ventana_principal.mainloop()

if __name__ == "__main__":
    menu_principal() 