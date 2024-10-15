import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re
from tkinter import simpledialog

# FUNCION PARA VALIDAR QUE SOLO SE INGRESEN LETRAS Y ESPACIOS
def validar_solo_letras(cadena):
    if all(caracter.isalpha() or caracter.isspace() for caracter in cadena):
        return True
    else:
        return False

# FUNCION PARA VALIDAR QUE SOLO SE ACEPTEN DOS DECIMALES
def validar_dos_decimales(cadena):
    patron = r'^\d+(\.\d{1,2})?$'
    return re.match(patron, cadena) is not None

# FUNCION PARA CREAR LA CONEXION A LA BASE DE DATOS
def crear_conexion():
    return sqlite3.connect('contabilidad.db')

# FUNCION PARA CREAR LA TABLA EN LA BASE DE DATOS
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

# FUNCION PARA VALIDAR SI EL NOMBRE DE CUENTA YA EXISTE
def cuenta_existe(nombre):
    with crear_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cuentas_balance WHERE nombre = ?", (nombre,))
        return cursor.fetchone()[0] > 0

# FUNCION PARA GUARDAR LA CUENTA EN LA BASE DE DATOS
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

#*********************************************************************************************************************************#
#MOSTRAR LA TABLA PARA EDITAR CUENTAS
def obtener_cuentas_balancegeneral():
    conexion = crear_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT nombre, tipo, monto FROM cuentas_balance")
    filas = cursor.fetchall()
    conexion.close()
    return filas
#*******************************************************************************************************************************#

# FUNCION PARA CREAR UNA CUENTA DE BALANCE GENERAL
def crear_cuenta_balance_general():
    # Ventana para solicitar los datos
    ventana_datos = tk.Toplevel()
    ventana_datos.title("Crear Cuenta - Balance General")
    ventana_datos.geometry("620x500")
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

    # Función para guardar los datos ingresados
    def submit_datos():
        nombre = entry_nombre.get().strip()
        tipo = tipo_var.get()
        monto_texto = entry_monto.get().strip()

        if nombre == "" and monto_texto == "":
            messagebox.showerror("Error", "No puede dejar campos vacíos.")
            return
        elif nombre == "":  # Si el nombre está vacío
            messagebox.showerror("Error", "El nombre de la cuenta no puede estar vacío.")
            return
        elif monto_texto == "":  # Si el monto está vacío
            messagebox.showerror("Error", "El monto de la cuenta no puede estar vacío.")
            return
        elif not nombre or not validar_solo_letras(nombre):
            messagebox.showerror("Error", "El nombre de la cuenta solo puede contener letras.")
            return
        elif not monto_texto or not validar_dos_decimales(monto_texto):
            messagebox.showerror("Error", "El monto debe ser un número con máximo dos decimales.")
            return

        try:
            monto = float(monto_texto)
            guardar_cuenta(nombre, tipo, monto)
            actualizar_tabla_cuentas()  # Actualiza la tabla después de guardar
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número válido.")

    # Widget Treeview para mostrar las cuentas
    tabla = ttk.Treeview(ventana_datos, columns=("Nombre", "Tipo", "Monto"), show='headings')
    tabla.heading("Nombre", text="Nombre")
    tabla.heading("Tipo", text="Tipo")
    tabla.heading("Monto", text="Monto")
    tabla.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    def actualizar_tabla_cuentas():
        for fila in tabla.get_children():
            tabla.delete(fila)
        cuentas = obtener_cuentas_balancegeneral()
        for cuenta in cuentas:
            tabla.insert("", tk.END, values=cuenta)

    actualizar_tabla_cuentas()  # Cargar los datos al iniciar

    # Botón para guardar la cuenta
    btn_guardar = tk.Button(ventana_datos, text="Guardar", command=submit_datos, bg="#1c3847", fg="white", width=30, height=2)
    btn_guardar.grid(row=3, column=0, columnspan=2, pady=10)

# FUNCION PARA MOSTRAR EL BALANCE GENERAL
def mostrar_balance_general():
    ventana_tabla = tk.Toplevel()
    ventana_tabla.title("Balance General")
    ventana_tabla.configure(bg="#6399b1")
    ventana_tabla.resizable(False, False)

    #FUNCION PARA CERRAR LA VENTANA
    def cerrar_ventana():
        ventana_tabla.destroy()

    # FUNCION PARA BORRAR EL CONTENIDO DE LA BASE DE DATOS
    def borrar_contenido():
        try:
            with crear_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cuentas_balance")  # Elimina todas las filas de la tabla
                conn.commit()
            messagebox.showinfo("Éxito", "Se han borrado todos los registros correctamente.")
            ventana_tabla.destroy()  # Cerrar la ventana después de borrar
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo borrar los registros: {e}")

    # Crear etiquetas para las secciones
    tk.Label(ventana_tabla, text="ACTIVOS CIRCULANTES", bg="#6399b1", font=("Arial", 14, "bold")).grid(row=0, column=0, padx=10, pady=10)
    tk.Label(ventana_tabla, text="ACTIVOS NO CIRCULANTES", bg="#6399b1", font=("Arial", 14, "bold")).grid(row=2, column=0, padx=10, pady=10)
    tk.Label(ventana_tabla, text="PASIVOS CIRCULANTES", bg="#6399b1", font=("Arial", 14, "bold")).grid(row=0, column=1, padx=10, pady=10)
    tk.Label(ventana_tabla, text="PASIVOS NO CIRCULANTES", bg="#6399b1", font=("Arial", 14, "bold")).grid(row=2, column=1, padx=10, pady=10)
    tk.Label(ventana_tabla, text="PATRIMONIO", bg="#6399b1", font=("Arial", 14, "bold")).grid(row=4, column=1, padx=10, pady=10)

    btn_borrar_contenido = tk.Button(ventana_tabla, text="Borrar Contenido", command=borrar_contenido, bg="#a83232", fg="white", width=30, height=2 , font=("Arial", 10, "bold"))
    btn_borrar_contenido.grid(row=0, column=2, padx=10, pady=10)

    btn_cerrar = tk.Button(ventana_tabla, text="Cerrar", command=cerrar_ventana, bg="#a83232", fg="white", width=30, height=2, font=("Arial", 10, "bold"))
    btn_cerrar.grid(row=2, column=2, padx=10, pady=10)

    # Crear Treeview para cada tipo de cuenta
    tree_activos_circulantes = ttk.Treeview(ventana_tabla, columns=("Nombre", "Monto"), show='headings')
    tree_activos_circulantes.heading("Nombre", text="Nombre de la Cuenta")
    tree_activos_circulantes.heading("Monto", text="Monto")
    tree_activos_circulantes.grid(row=1, column=0, padx=10, pady=10)

    tree_activos_no_circulantes = ttk.Treeview(ventana_tabla, columns=("Nombre", "Monto"), show='headings')
    tree_activos_no_circulantes.heading("Nombre", text="Nombre de la Cuenta")
    tree_activos_no_circulantes.heading("Monto", text="Monto")
    tree_activos_no_circulantes.grid(row=3, column=0, padx=10, pady=10)

    tree_pasivos_circulantes = ttk.Treeview(ventana_tabla, columns=("Nombre", "Monto"), show='headings')
    tree_pasivos_circulantes.heading("Nombre", text="Nombre de la Cuenta")
    tree_pasivos_circulantes.heading("Monto", text="Monto")
    tree_pasivos_circulantes.grid(row=1, column=1, padx=10, pady=10)

    tree_pasivos_no_circulantes = ttk.Treeview(ventana_tabla, columns=("Nombre", "Monto"), show='headings')
    tree_pasivos_no_circulantes.heading("Nombre", text="Nombre de la Cuenta")
    tree_pasivos_no_circulantes.heading("Monto", text="Monto")
    tree_pasivos_no_circulantes.grid(row=3, column=1, padx=10, pady=10)

    tree_patrimonio = ttk.Treeview(ventana_tabla, columns=("Nombre", "Monto"), show='headings')
    tree_patrimonio.heading("Nombre", text="Nombre de la Cuenta")
    tree_patrimonio.heading("Monto", text="Monto")
    tree_patrimonio.grid(row=5, column=1, padx=10, pady=10)

    # Obtener los datos de la base de datos
    with crear_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, tipo, monto FROM cuentas_balance")
        filas = cursor.fetchall()

    # Clasificar y agregar cuentas a la tabla correspondiente
    total_activos_circulantes = total_activos_no_circulantes = total_pasivos_circulantes = total_pasivos_no_circulantes = total_patrimonio = 0
    for fila in filas:
        nombre, tipo, monto = fila
        monto_formateado = f"{monto:,.2f}"  # Formatea el monto con comas y dos decimales

        if tipo == "Activos circulantes":
            tree_activos_circulantes.insert("", tk.END, values=(nombre, monto_formateado))
            total_activos_circulantes += monto
        elif tipo == "Activos no circulantes":
            tree_activos_no_circulantes.insert("", tk.END, values=(nombre, monto_formateado))
            total_activos_no_circulantes += monto
        elif tipo == "Pasivos circulantes":
            tree_pasivos_circulantes.insert("", tk.END, values=(nombre, monto_formateado))
            total_pasivos_circulantes += monto
        elif tipo == "Pasivos no circulantes":
            tree_pasivos_no_circulantes.insert("", tk.END, values=(nombre, monto_formateado))
            total_pasivos_no_circulantes += monto
        elif tipo == "Capital":
            tree_patrimonio.insert("", tk.END, values=(nombre, monto_formateado))
            total_patrimonio += monto

    # Formatear los totales con comas y dos decimales
    total_activos_circulantes_formateado = f"{total_activos_circulantes:,.2f}"
    total_activos_no_circulantes_formateado = f"{total_activos_no_circulantes:,.2f}"
    total_pasivos_circulantes_formateado = f"{total_pasivos_circulantes:,.2f}"
    total_pasivos_no_circulantes_formateado = f"{total_pasivos_no_circulantes:,.2f}"
    total_patrimonio_formateado = f"{total_patrimonio:,.2f}"

    # Configura el color de las filas con la etiqueta 'total'
    tree_activos_circulantes.tag_configure("total", background="#3a596b", foreground="white")
    tree_activos_no_circulantes.tag_configure("total", background="#3a596b", foreground="white")
    tree_pasivos_circulantes.tag_configure("total", background="#3a596b", foreground="white")
    tree_pasivos_no_circulantes.tag_configure("total", background="#3a596b", foreground="white")
    tree_patrimonio.tag_configure("total", background="#3a596b", foreground="white")

    # Inserta los totales con etiquetas (tags) para aplicar color
    tree_activos_circulantes.insert("", tk.END, values=("Total de activos circulantes", total_activos_circulantes_formateado), tags=("total",))
    tree_activos_no_circulantes.insert("", tk.END, values=("Total de activos no circulantes", total_activos_no_circulantes_formateado), tags=("total",))
    tree_pasivos_circulantes.insert("", tk.END, values=("Total de pasivos circulantes", total_pasivos_circulantes_formateado), tags=("total",))
    tree_pasivos_no_circulantes.insert("", tk.END, values=("Total de pasivos no circulantes", total_pasivos_no_circulantes_formateado), tags=("total",))
    tree_patrimonio.insert("", tk.END, values=("Total de patrimonio", total_patrimonio_formateado), tags=("total",))

    #Suma total de activos
    total_activos = total_activos_circulantes + total_activos_no_circulantes
    tk.Label(ventana_tabla, bg="#6399b1", fg="#a83232", text=f"Total de activos = ${total_activos:,.2f}", font=("Arial", 14, "bold")).grid(row=6, column=0, columnspan=1, padx=10, pady=10)

    #Suma total de pasivos y patrimonio
    total_pasivos_patrimonio = total_pasivos_circulantes + total_pasivos_no_circulantes + total_patrimonio
    tk.Label(ventana_tabla, bg="#6399b1", fg="#a83232", text=f"Total de pasivos + patrimonio = ${total_pasivos_patrimonio:,.2f}", font=("Arial", 14, "bold")).grid(row=6, column=1, columnspan=1, padx=10, pady=10)


# MENÚ PRINCIPAL CON TODOS LOS BOTONES
def menu_principal():
    ventana_principal = tk.Tk()
    ventana_principal.title("Sistema de Contabilidad")
    ventana_principal.geometry("400x360")
    ventana_principal.configure(bg="#6399b1")
    ventana_principal.resizable(False, False)

    # Botones del menú
    btn_crear_cuenta_estado_resultado = tk.Button(ventana_principal, text="Crear Cuenta - Estado de Resultado", command=None, bg="#1c3847", fg="white", width=30, height=2, font=("Arial", 12, "bold"))
    btn_crear_cuenta_estado_resultado.pack(pady=10)

    btn_crear_cuenta_balance_general = tk.Button(ventana_principal, text="Crear Cuenta - Balance General", command=crear_cuenta_balance_general, bg="#1c3847", fg="white", width=30, height=2, font=("Arial", 12, "bold"))
    btn_crear_cuenta_balance_general.pack(pady=10)

    btn_mostrar_estado_resultado = tk.Button(ventana_principal, text="Mostrar Estado de Resultado", command=None, bg="#1c3847", fg="white", width=30, height=2, font=("Arial", 12, "bold"))
    btn_mostrar_estado_resultado.pack(pady=10)

    btn_mostrar_balance_general = tk.Button(ventana_principal, text="Mostrar Balance General", command=mostrar_balance_general, bg="#1c3847", fg="white", width=30, height=2, font=("Arial", 12, "bold"))
    btn_mostrar_balance_general.pack(pady=10)

    btn_salir = tk.Button(ventana_principal, text="Salir", command=ventana_principal.quit, bg="#a83232", fg="white", width=30, height=2, font=("Arial", 12, "bold"))
    btn_salir.pack(pady=10)

    ventana_principal.mainloop()

# Iniciar la aplicación
menu_principal()