import re
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from dataclasses import dataclass
from typing import Optional
import os
from tkinter import filedialog
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime

# Funcion para validar que la cadena tenga solo letras
def validar_solo_letras(cadena):
    return all(caracter.isalpha() or caracter.isspace() for caracter in cadena)

#Funcion para validar que la cadena tenga dos decimales
def validar_dos_decimales(cadena):
    return re.match(r'^\d+(\.\d{1,2})?$', cadena) is not None

@dataclass
class Account:
    code: str
    name: str
    parent_code: Optional[str]

class AccountCatalog:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.create_table()
        self.initialize_main_accounts()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            parent_code TEXT,
            FOREIGN KEY (parent_code) REFERENCES accounts (code)
        )
        ''')
        self.conn.commit()

    def initialize_main_accounts(self):
        main_accounts = [
            ("1", "ACTIVO", None),
            ("2", "PASIVO", None),
            ("3", "PATRIMONIO", None),
            ("4", "CUENTAS DE RESULTADO DEUDORAS", None),
            ("5", "CUENTAS DE RESULTADO ACREEDORAS", None),
            ("6", "CUENTA DE PUENTE DE CIERRE", None)
        ]

        cursor = self.conn.cursor()
        for code, name, parent in main_accounts:
            cursor.execute('''
            INSERT OR IGNORE INTO accounts (code, name, parent_code)
            VALUES (?, ?, ?)
            ''', (code, name, parent))
        self.conn.commit()

    def validate_account_code(self, code: str, parent_code: str) -> bool:
        if not code.isdigit():
            return False

        if parent_code and not code.startswith(parent_code):
            return False

        if len(code) not in [1, 2, 4, 6, 8]:
            return False

        return True

    def create_account(self, code: str, name: str, parent_code: str) -> bool:
        try:
            if not self.validate_account_code(code, parent_code):
                return False

            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO accounts (code, name, parent_code)
            VALUES (?, ?, ?)
            ''', (code, name, parent_code if parent_code else None))

            self.conn.commit()
            return True

        except Exception as e:
            print(f"Error al crear la cuenta: {e}")
            return False

    def buscar_cuenta_por_codigo(self, code: str) -> Optional[Account]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT code, name, parent_code FROM accounts WHERE code = ?', (code,))
        row = cursor.fetchone()
        if row:
            return Account(code=row[0], name=row[1], parent_code=row[2])
        return None

    def editar_cuenta(self, codigo_original: str, nuevo_codigo: str, nuevo_nombre: str, nuevo_padre: str) -> bool:
        try:
            if nuevo_padre and not self.validate_account_code(nuevo_codigo, nuevo_padre):
                return False

            cursor = self.conn.cursor()
            cursor.execute('''
            UPDATE accounts
            SET code = ?, name = ?, parent_code = ?
            WHERE code = ?
            ''', (nuevo_codigo, nuevo_nombre, nuevo_padre if nuevo_padre else None, codigo_original))

            self.conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            print(f"Error al editar la cuenta: {e}")
            return False

    def eliminar_cuenta(self, code: str) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM accounts WHERE code = ?', (code,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al eliminar la cuenta: {e}")
            return False

    def get_all_accounts(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT code, name, parent_code FROM accounts ORDER BY code')
        return [Account(code, name, parent_code) for code, name, parent_code in cursor.fetchall()]

def ver_catalogo_cuentas(frame):
    for widget in frame.winfo_children():
        widget.destroy()

    frame.configure(bg="#E0F2FE")  # Fondo azul claro

    # Frame principal
    main_frame = tk.Frame(frame, bg="#E0F2FE")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Título
    titulo = tk.Label(main_frame,
                     text="Catálogo de Cuentas",
                     bg="#E0F2FE",
                     font=("Arial", 16, "bold"),
                     fg="#1E3A8A")
    titulo.pack(pady=(0, 20))

    # Frame para la tabla
    table_frame = tk.Frame(main_frame, bg="#E0F2FE", relief="raised", borderwidth=1)
    table_frame.pack(fill=tk.BOTH, expand=True)

    # Crear tabla
    tabla = ttk.Treeview(table_frame,
                        columns=("Código", "Nombre", "Código Padre"),
                        show='headings',
                        height=20)

    # Configurar columnas
    tabla.heading("Código", text="Código")
    tabla.heading("Nombre", text="Nombre")
    tabla.heading("Código Padre", text="Código Padre")

    tabla.column("Código", width=150)
    tabla.column("Nombre", width=400)
    tabla.column("Código Padre", width=150)

    # Agregar scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tabla.yview)
    tabla.configure(yscrollcommand=scrollbar.set)

    # Empaquetar tabla y scrollbar
    tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Cargar datos
    db = AccountCatalog("catalogo_cuentas.db")
    accounts = db.get_all_accounts()

    # Insertar datos en la tabla
    for account in accounts:
        tabla.insert("", tk.END, values=(
            account.code,
            account.name,
            account.parent_code if account.parent_code else ""
        ))

    # Agregar contador de cuentas
    total_cuentas = len(accounts)
    contador = tk.Label(main_frame,
                       text=f"Total de cuentas: {total_cuentas}",
                       bg="#E0F2FE",
                       font=("Arial", 11, "bold"),
                       fg="#1E3A8A")
    contador.pack(pady=10)

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
        ("Código:", "entry_codigo"),
        ("Nombre de la Cuenta:", "entry_nombre"),
        ("Código Padre:", "entry_padre")
    ]

    widgets = {}
    for i, (label_text, widget_name) in enumerate(campos):
        tk.Label(input_frame, text=label_text, bg="#E0F2FE", font=("Arial", 11, "bold"), fg="#1E3A8A").grid(row=i, column=0, padx=10, pady=10, sticky="e")
        widget = tk.Entry(input_frame, width=30, bg="#F3F4F6")
        widgets[widget_name] = widget
        widget.grid(row=i, column=1, padx=10, pady=10, sticky="w")

    # Frame para la tabla (parte central)
    table_frame = tk.Frame(main_frame, bg="#E0F2FE", relief="raised", borderwidth=1)
    table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

    # Tabla de cuentas
    tabla = ttk.Treeview(table_frame, columns=("Código", "Nombre", "Código Padre"), show='headings', height=10)
    for col in tabla['columns']:
        tabla.heading(col, text=col)
        tabla.column(col, width=150)
    tabla.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Agregar scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tabla.yview)
    tabla.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Frame para la búsqueda y botones (parte inferior)
    search_frame = tk.Frame(main_frame, bg="#E0F2FE", relief="raised", borderwidth=1)
    search_frame.pack(fill=tk.X)

    tk.Label(search_frame, text="Ingrese código a buscar:", bg="#E0F2FE", font=("Arial", 10, "bold"), fg="#1E3A8A").pack(side=tk.LEFT, padx=(10, 5), pady=10)
    entry_buscarCuenta = tk.Entry(search_frame, width=30, bg="#F3F4F6")
    entry_buscarCuenta.pack(side=tk.LEFT, padx=5, pady=10)

    # Variable para almacenar el código original durante la edición
    codigo_original = tk.StringVar()

    # Inicializar la base de datos
    db = AccountCatalog("catalogo_cuentas.db")

    def actualizar_tabla():
        for item in tabla.get_children():
            tabla.delete(item)
        accounts = db.get_all_accounts()
        for account in accounts:
            tabla.insert("", tk.END, values=(
                account.code,
                account.name,
                account.parent_code if account.parent_code else ""
            ))

    def limpiar_campos():
        for widget in widgets.values():
            widget.delete(0, tk.END)
        entry_buscarCuenta.delete(0, tk.END)
        codigo_original.set('')

    def agregar_cuenta():
        codigo = widgets['entry_codigo'].get().strip()
        nombre = widgets['entry_nombre'].get().strip()
        padre = widgets['entry_padre'].get().strip()

        if not codigo or not nombre:
            messagebox.showerror("Error", "El código y nombre son obligatorios.")
            return

        if not validar_solo_letras(nombre):
            messagebox.showerror("Error", "El nombre solo puede contener letras y espacios.")
            return

        if db.create_account(codigo, nombre, padre):
            actualizar_tabla()
            limpiar_campos()
            messagebox.showinfo("Éxito", "Cuenta agregada correctamente")
        else:
            messagebox.showerror("Error", "No se pudo crear la cuenta. Verifique el formato del código y que el código padre exista.")

    def buscar_cuenta():
        codigo = entry_buscarCuenta.get().strip()
        if not codigo:
            messagebox.showerror("Error", "Ingrese un código para buscar.")
            return

        cuenta = db.buscar_cuenta_por_codigo(codigo)
        if cuenta:
            widgets['entry_codigo'].delete(0, tk.END)
            widgets['entry_codigo'].insert(0, cuenta.code)
            widgets['entry_nombre'].delete(0, tk.END)
            widgets['entry_nombre'].insert(0, cuenta.name)
            widgets['entry_padre'].delete(0, tk.END)
            if cuenta.parent_code:
                widgets['entry_padre'].insert(0, cuenta.parent_code)
            codigo_original.set(cuenta.code)
            messagebox.showinfo("Éxito", "Cuenta encontrada.")
        else:
            messagebox.showerror("Error", "La cuenta no existe.")

    def editar_cuenta():
        if not codigo_original.get():
            messagebox.showerror("Error", "Primero debe buscar una cuenta para editar.")
            return

        codigo = widgets['entry_codigo'].get().strip()
        nombre = widgets['entry_nombre'].get().strip()
        padre = widgets['entry_padre'].get().strip()

        if not codigo or not nombre:
            messagebox.showerror("Error", "El código y nombre son obligatorios.")
            return

        if db.editar_cuenta(codigo_original.get(), codigo, nombre, padre):
            actualizar_tabla()
            limpiar_campos()
            messagebox.showinfo("Éxito", "Cuenta actualizada correctamente")
        else:
            messagebox.showerror("Error", "No se pudo actualizar la cuenta.")

    def eliminar_cuenta():
        if not codigo_original.get():
            messagebox.showerror("Error", "Primero debe buscar una cuenta para eliminar.")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta cuenta?"):
            if db.eliminar_cuenta(codigo_original.get()):
                actualizar_tabla()
                limpiar_campos()
                messagebox.showinfo("Éxito", "Cuenta eliminada correctamente")
            else:
                messagebox.showerror("Error", "No se pudo eliminar la cuenta.")

    # Botones del frame de búsqueda
    botones = [
        ("Buscar Cuenta", buscar_cuenta),
        ("Editar Cuenta", editar_cuenta),
        ("Eliminar Cuenta", eliminar_cuenta)
    ]

    for texto, comando in botones:
        tk.Button(search_frame,
                 text=texto,
                 command=comando,
                 bg="#1E3A8A",
                 fg="white",
                 activebackground="#00587A",
                 width=15,
                 height=1,
                 font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5, pady=10)

    # Botón para guardar
    tk.Button(
        input_frame,
        text="Guardar",
        command=agregar_cuenta,
        bg="#1E3A8A",
        fg="white",
        activebackground="#00587A",
        width=15,
        height=1,
        font=("Arial", 10, "bold")
    ).grid(row=len(campos), column=1, pady=10, sticky="w")

    # Inicializar tabla
    actualizar_tabla()

def mostrar_estado_resultado(root_frame):
    for widget in root_frame.winfo_children():
        widget.destroy()

    frame = tk.Frame(root_frame)
    frame.pack(fill="both", expand=True, padx=10, pady=10)
    frame.configure(bg="#E0F2FE")

    # Conexión con la base de datos
    conn = sqlite3.connect('estado_cuentas.db')
    c = conn.cursor()

    # Intentar agregar la columna tipo si no existe
    try:
        c.execute("ALTER TABLE cuentas ADD COLUMN tipo TEXT")
    except sqlite3.OperationalError:
        pass

    # Crear tablas si no existen
    c.execute('''
        CREATE TABLE IF NOT EXISTS estados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_empresa TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS cuentas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estado_id INTEGER,
            nombre_cuenta TEXT NOT NULL,
            valor REAL NOT NULL,
            tipo TEXT NOT NULL,
            FOREIGN KEY (estado_id) REFERENCES estados (id)
        )
    ''')

    conn.commit()

    # Variables
    nombre_empresa = tk.StringVar()
    fecha = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
    nombre_cuenta = tk.StringVar()
    valor_cuenta = tk.DoubleVar()
    tipo_cuenta = tk.StringVar(value="Ingreso")

    # Formulario para la empresa
    tk.Label(frame, text="Nombre de la Empresa:", bg="#E0F2FE", font=("Arial", 11)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
    tk.Entry(frame, textvariable=nombre_empresa, width=30).grid(row=0, column=1, padx=5, pady=5, sticky="w")

    tk.Label(frame, text="Fecha de Realización:", bg="#E0F2FE", font=("Arial", 11)).grid(row=1, column=0, padx=5, pady=5, sticky="w")
    tk.Entry(frame, textvariable=fecha, width=30).grid(row=1, column=1, padx=5, pady=5, sticky="w")

    # Frame para agregar cuentas
    tk.Label(frame, text="Nombre de la Cuenta:", bg="#E0F2FE", font=("Arial", 11)).grid(row=2, column=0, padx=5, pady=5, sticky="w")
    tk.Entry(frame, textvariable=nombre_cuenta, width=30).grid(row=2, column=1, padx=5, pady=5, sticky="w")

    tk.Label(frame, text="Valor de la Cuenta:", bg="#E0F2FE", font=("Arial", 11)).grid(row=3, column=0, padx=5, pady=5, sticky="w")
    tk.Entry(frame, textvariable=valor_cuenta, width=30).grid(row=3, column=1, padx=5, pady=5, sticky="w")

    tk.Label(frame, text="Tipo de Cuenta:", bg="#E0F2FE", font=("Arial", 11)).grid(row=4, column=0, padx=5, pady=5, sticky="w")
    tipo_menu = ttk.Combobox(frame, textvariable=tipo_cuenta, values=["Ingreso", "Costo", "Gasto de Operación"], width=27)
    tipo_menu.grid(row=4, column=1, padx=5, pady=5, sticky="w")

    # Función para agregar cuenta
    def agregar_cuenta():
        nombre = nombre_cuenta.get()
        valor = valor_cuenta.get()
        tipo = tipo_cuenta.get()
        if nombre and valor:
            cuentas.append((nombre, valor, tipo))
            lista_cuentas.insert(tk.END, f"{tipo}: {nombre} - ${valor:.2f}")
            nombre_cuenta.set("")
            valor_cuenta.set(0.0)
        else:
            messagebox.showwarning("Advertencia", "Por favor ingrese el nombre, valor y tipo de la cuenta.")

    tk.Button(frame, text="Agregar Cuenta", command=agregar_cuenta, width=27).grid(row=5, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

    cuentas = []

    # Lista de cuentas
    lista_cuentas = tk.Listbox(frame, width=50)
    lista_cuentas.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

    # Botones para generar estado
    tk.Button(frame, text="Generar Estado de Cuentas", command=lambda: generar_estado(conn, c)).grid(row=7, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

    # Configurar expansión del frame y widgets
    for i in range(8):
        frame.grid_rowconfigure(i, weight=1)
    frame.grid_columnconfigure(1, weight=1)

    def generar_estado(conn, c):
        empresa = nombre_empresa.get()
        fecha_val = fecha.get()

        if empresa and cuentas:
            # Guardar estado en la base de datos
            c.execute("INSERT INTO estados (nombre_empresa, fecha) VALUES (?, ?)", (empresa, fecha_val))
            estado_id = c.lastrowid

            # Guardar cuentas en la base de datos
            for nombre, valor, tipo in cuentas:
                c.execute("INSERT INTO cuentas (estado_id, nombre_cuenta, valor, tipo) VALUES (?, ?, ?, ?)", (estado_id, nombre, valor, tipo))

            conn.commit()

            # Calcular totales
            ingresos = sum(valor for _, valor, tipo in cuentas if tipo == "Ingreso")
            costos = sum(valor for _, valor, tipo in cuentas if tipo == "Costo")
            gastos_operacion = sum(valor for _, valor, tipo in cuentas if tipo == "Gasto de Operación")

            # Cálculos de utilidades
            utilidad_bruta = ingresos - costos
            utilidad_operacion = utilidad_bruta - gastos_operacion
            utilidad_antes_impuestos = utilidad_operacion
            utilidad_neta = utilidad_antes_impuestos  # Sin impuestos para este ejemplo

            # Crear PDF
            generar_pdf(empresa, fecha_val, ingresos, costos, gastos_operacion, utilidad_bruta, utilidad_operacion, utilidad_antes_impuestos, utilidad_neta)

            # Limpiar datos
            nombre_empresa.set("")
            fecha.set(datetime.now().strftime('%Y-%m-%d'))
            lista_cuentas.delete(0, tk.END)
            cuentas.clear()
        else:
            messagebox.showwarning("Advertencia", "Ingrese el nombre de la empresa y al menos una cuenta.")

    def generar_pdf(empresa, fecha_val, ingresos, costos, gastos_operacion, utilidad_bruta, utilidad_operacion, utilidad_antes_impuestos, utilidad_neta):
        # Preguntar al usuario dónde guardar el PDF
        pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], title="Guardar Estado de Cuentas como PDF")
        if not pdf_path:
            return  # Si el usuario cancela, salir de la función

        pdf = canvas.Canvas(pdf_path, pagesize=letter)
        pdf.setTitle("Estado de Cuentas")

        # Encabezado
        pdf.drawString(30, 750, f"Estado de Cuentas - {empresa}")
        pdf.drawString(30, 735, f"Fecha: {fecha_val}")

        # Encabezados de tabla
        y = 700
        pdf.drawString(30, y, "Tipo de Cuenta")
        pdf.drawString(200, y, "Nombre de Cuenta")
        pdf.drawString(400, y, "Valor")

        y -= 20

        # Filtrar y ordenar las cuentas por tipo (Ingreso, Costo, Gasto de Operación)
        cuentas_ordenadas = {
            "Ingreso": [(nombre, valor) for nombre, valor, tipo in cuentas if tipo == "Ingreso"],
            "Costo": [(nombre, valor) for nombre, valor, tipo in cuentas if tipo == "Costo"],
            "Gasto de Operación": [(nombre, valor) for nombre, valor, tipo in cuentas if tipo == "Gasto de Operación"]
        }

        # Mostrar cuentas en orden: Ingresos, Costos, Gastos de Operación
        for tipo in ["Ingreso", "Costo", "Gasto de Operación"]:
            for nombre, valor in cuentas_ordenadas[tipo]:
                pdf.drawString(30, y, tipo)
                pdf.drawString(200, y, nombre)
                pdf.drawString(400, y, f"${valor:.2f}")
                y -= 15

        # Totales y utilidades
        y -= 25
        pdf.drawString(30, y, f"Total Ingresos: ${ingresos:.2f}")
        y -= 15
        pdf.drawString(30, y, f"Total Costos: ${costos:.2f}")
        y -= 15
        pdf.drawString(30, y, f"Utilidad Bruta: ${utilidad_bruta:.2f}")
        y -= 15
        pdf.drawString(30, y, f"Total Gastos de Operación: ${gastos_operacion:.2f}")
        y -= 15
        pdf.drawString(30, y, f"Utilidad de Operación: ${utilidad_operacion:.2f}")
        y -= 15
        pdf.drawString(30, y, f"Utilidad Antes de Impuestos: ${utilidad_antes_impuestos:.2f}")
        y -= 15
        pdf.drawString(30, y, f"Utilidad Neta: ${utilidad_neta:.2f}")

        pdf.save()
        messagebox.showinfo("PDF Generado", f"El estado de cuentas se ha guardado en '{pdf_path}'.")


def mostrar_balance_general(frame):
    for widget in frame.winfo_children():
        widget.destroy()

    frame.configure(bg="#E0F2FE")

    # Frame principal con título
    titulo_frame = tk.Frame(frame, bg="#E0F2FE")
    titulo_frame.pack(fill=tk.X, padx=20, pady=10)

    tk.Label(titulo_frame,
            text="Balance General",
            bg="#E0F2FE",
            font=("Arial", 16, "bold"),
            fg="#1E3A8A").pack()

    # Frame para la fecha
    fecha_frame = tk.Frame(frame, bg="#E0F2FE")
    fecha_frame.pack(fill=tk.X, padx=20, pady=5)

    tk.Label(fecha_frame,
            text="Fecha del Balance:",
            bg="#E0F2FE",
            font=("Arial", 11)).pack(side=tk.LEFT, padx=5)

    fecha_entry = ttk.Entry(fecha_frame)
    fecha_entry.pack(side=tk.LEFT, padx=5)
    fecha_entry.insert(0, "31/12/2024")  # Fecha por defecto

    # Frame para la empresa
    empresa_frame = tk.Frame(frame, bg="#E0F2FE")
    empresa_frame.pack(fill=tk.X, padx=20, pady=5)

    tk.Label(empresa_frame,
            text="Nombre de la Empresa:",
            bg="#E0F2FE",
            font=("Arial", 11)).pack(side=tk.LEFT, padx=5)

    empresa_entry = ttk.Entry(empresa_frame, width=50)
    empresa_entry.pack(side=tk.LEFT, padx=5)

    # Frame principal para activos y pasivos+patrimonio
    contenido_frame = tk.Frame(frame, bg="#E0F2FE")
    contenido_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    # Frame izquierdo para Activos
    activos_frame = tk.LabelFrame(contenido_frame, text="ACTIVO", bg="#E0F2FE", font=("Arial", 12, "bold"))
    activos_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

    # Frame derecho para Pasivos y Patrimonio
    pasivos_frame = tk.LabelFrame(contenido_frame, text="PASIVO Y PATRIMONIO", bg="#E0F2FE", font=("Arial", 12, "bold"))
    pasivos_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

    contenido_frame.grid_columnconfigure(0, weight=1)
    contenido_frame.grid_columnconfigure(1, weight=1)

    def agregar_cuenta(parent_frame, tipo_cuenta):
        cuenta_frame = tk.Frame(parent_frame, bg="#E0F2FE")
        cuenta_frame.pack(fill=tk.X, padx=5, pady=2)

        # Combobox para seleccionar cuenta del catálogo
        db = AccountCatalog("catalogo_cuentas.db")
        cuentas = db.get_all_accounts()

        # Filtrar cuentas según el tipo y la sección
        filtro_codigo = {
            'activo_corriente': '11',      # Activos Corrientes
            'activo_no_corriente': '12',   # Activos No Corrientes
            'pasivo_corriente': '21',      # Pasivos Corrientes
            'pasivo_no_corriente': '22',   # Pasivos No Corrientes
            'patrimonio': '3'              # Patrimonio
        }

        codigo_filtro = filtro_codigo.get(tipo_cuenta, '')

        # Filtrado específico basado en el tipo de cuenta
        codigos_cuentas = []
        for cuenta in cuentas:
            if cuenta.code.startswith(codigo_filtro) and len(cuenta.code) > len(codigo_filtro):
                codigos_cuentas.append(f"{cuenta.code} - {cuenta.name}")

        cuenta_combo = ttk.Combobox(cuenta_frame, values=codigos_cuentas, width=40)
        cuenta_combo.pack(side=tk.LEFT, padx=2)

        monto_entry = ttk.Entry(cuenta_frame, width=15)
        monto_entry.pack(side=tk.LEFT, padx=2)

        def eliminar_fila():
            cuenta_frame.destroy()
            actualizar_totales()

        ttk.Button(cuenta_frame, text="X", width=3, command=eliminar_fila).pack(side=tk.LEFT, padx=2)
        return cuenta_combo, monto_entry

    def agregar_seccion(parent_frame, titulo, tipo_cuenta):
        seccion_frame = tk.LabelFrame(parent_frame, text=titulo, bg="#E0F2FE")
        seccion_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
                seccion_frame,
                text="+ Agregar cuenta",
                command=lambda: agregar_cuenta(seccion_frame, tipo_cuenta)
            ).pack(anchor=tk.W, padx=5, pady=5)

    # Secciones de Activos
    agregar_seccion(activos_frame, "ACTIVOS CORRIENTES", "activo_corriente")
    agregar_seccion(activos_frame, "ACTIVOS NO CORRIENTES", "activo_no_corriente")

    # Secciones de Pasivos y Patrimonio
    agregar_seccion(pasivos_frame, "PASIVOS CORRIENTES", "pasivo_corriente")
    agregar_seccion(pasivos_frame, "PASIVOS NO CORRIENTES", "pasivo_no_corriente")
    agregar_seccion(pasivos_frame, "PATRIMONIO", "patrimonio")

    # Frame para totales
    totales_frame = tk.Frame(frame, bg="#E0F2FE")
    totales_frame.pack(fill=tk.X, padx=20, pady=10)

    total_activos_label = tk.Label(totales_frame, text="Total Activos: $0.00", bg="#E0F2FE", font=("Arial", 12, "bold"))
    total_activos_label.pack(side=tk.LEFT, padx=20)

    total_pasivos_label = tk.Label(totales_frame, text="Total Pasivos y Patrimonio: $0.00", bg="#E0F2FE", font=("Arial", 12, "bold"))
    total_pasivos_label.pack(side=tk.RIGHT, padx=20)

    def actualizar_totales():
        # Conectar a la base de datos
        conn = sqlite3.connect('catalogo_cuentas.db')
        cursor = conn.cursor()

        # Sumar los totales de activos, pasivos y capital
        cursor.execute("SELECT SUM(monto) FROM cuentas_balance WHERE tipo IN ('Activo Circulante', 'Activo No Circulante')")
        total_activos = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(monto) FROM cuentas_balance WHERE tipo IN ('Pasivo Circulante', 'Pasivo No Circulante')")
        total_pasivos = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(monto) FROM cuentas_balance WHERE tipo = 'Capital'")
        total_capital = cursor.fetchone()[0] or 0

        # Calcular el capital usando la fórmula: Activo = Pasivo + Capital
        balance_equilibrado = (total_activos == total_pasivos + total_capital)

        conn.close()
        return total_activos, total_pasivos, total_capital, balance_equilibrado

    # Frame para botones de acción
    botones_frame = tk.Frame(frame, bg="#E0F2FE")
    botones_frame.pack(fill=tk.X, padx=20, pady=10)

    def guardar_balance():
        # Validar campos obligatorios
        if not fecha_entry.get().strip():
            messagebox.showerror("Error", "La fecha es obligatoria")
            return
        
        if not empresa_entry.get().strip():
            messagebox.showerror("Error", "El nombre de la empresa es obligatorio")
            return

        # Validar formato de fecha (dd/mm/yyyy)
        fecha = fecha_entry.get().strip()
        if not re.match(r'^\d{2}/\d{2}/\d{4}$', fecha):
            messagebox.showerror("Error", "El formato de fecha debe ser dd/mm/yyyy")
            return

        # Obtener todos los frames de cuentas
        total_activos = 0
        total_pasivos = 0
        total_patrimonio = 0
        
        # Bandera para verificar si hay al menos una cuenta en cada sección
        tiene_activos = False
        tiene_pasivos = False
        tiene_patrimonio = False

        # Función auxiliar para extraer y validar el monto de un entry
        def extraer_monto(entry, combo):
            try:
                texto = entry.get().strip()
                if not texto:
                    return 0
                    
                # Verificar que se haya seleccionado una cuenta
                if not combo.get().strip():
                    messagebox.showerror("Error", "Debe seleccionar una cuenta para cada entrada")
                    return None
                    
                if validar_dos_decimales(texto):
                    # Validar que el monto sea positivo
                    monto = float(texto.replace('$', '').replace(',', ''))
                    if monto <= 0:
                        messagebox.showerror("Error", "Los montos deben ser mayores a cero")
                        return None
                    return monto
                else:
                    messagebox.showerror("Error", "El monto debe tener un máximo de dos decimales")
                    return None
            except ValueError:
                messagebox.showerror("Error", "Monto inválido")
                return None

        # Recorrer todos los frames de activos
        for child in activos_frame.winfo_children():
            if isinstance(child, tk.LabelFrame):  # Verificar si es un frame de sección
                for cuenta_frame in child.winfo_children():
                    if isinstance(cuenta_frame, tk.Frame):
                        combo = None
                        entry = None
                        # Buscar el combobox y entry en el frame de la cuenta
                        for widget in cuenta_frame.winfo_children():
                            if isinstance(widget, ttk.Combobox):
                                combo = widget
                            elif isinstance(widget, ttk.Entry):
                                entry = widget
                        
                        if combo and entry:
                            monto = extraer_monto(entry, combo)
                            if monto is None:  # Si hay error en la validación
                                return
                            if monto > 0:
                                tiene_activos = True
                                total_activos += monto

        # Recorrer todos los frames de pasivos y patrimonio
        for child in pasivos_frame.winfo_children():
            if isinstance(child, tk.LabelFrame):
                for cuenta_frame in child.winfo_children():
                    if isinstance(cuenta_frame, tk.Frame):
                        combo = None
                        entry = None
                        for widget in cuenta_frame.winfo_children():
                            if isinstance(widget, ttk.Combobox):
                                combo = widget
                            elif isinstance(widget, ttk.Entry):
                                entry = widget
                        
                        if combo and entry:
                            monto = extraer_monto(entry, combo)
                            if monto is None:  # Si hay error en la validación
                                return
                            if monto > 0:
                                if "PASIVO" in child.cget("text"):
                                    tiene_pasivos = True
                                    total_pasivos += monto
                                else:  # Es patrimonio
                                    tiene_patrimonio = True
                                    total_patrimonio += monto

        # Validar que haya al menos una cuenta en cada sección
        if not tiene_activos:
            messagebox.showerror("Error", "Debe incluir al menos una cuenta de activos")
            return
        
        if not tiene_pasivos:
            messagebox.showerror("Error", "Debe incluir al menos una cuenta de pasivos")
            return
            
        if not tiene_patrimonio:
            messagebox.showerror("Error", "Debe incluir al menos una cuenta de patrimonio")
            return

        # Verificar que los totales cuadren (permitiendo una pequeña diferencia por redondeo)
        diferencia = abs(total_activos - (total_pasivos + total_patrimonio))
        if diferencia > 0.01:
            messagebox.showerror("Error",
                f"El balance no cuadra:\nTotal Activos: ${total_activos:,.2f}\n" +
                f"Total Pasivos + Patrimonio: ${total_pasivos + total_patrimonio:,.2f}\n" +
                f"Diferencia: ${diferencia:,.2f}")
            return

        try:
            # Crear la tabla si no existe
            conn = sqlite3.connect('catalogo_cuentas.db')
            cursor = conn.cursor()

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS balance_general (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                empresa TEXT,
                total_activos REAL,
                total_pasivos REAL,
                total_patrimonio REAL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # Guardar el balance
            cursor.execute('''
            INSERT INTO balance_general (fecha, empresa, total_activos, total_pasivos, total_patrimonio)
            VALUES (?, ?, ?, ?, ?)
            ''', (fecha, empresa_entry.get().strip(), total_activos, total_pasivos, total_patrimonio))

            conn.commit()
            conn.close()

            # Actualizar las etiquetas de totales
            total_activos_label.config(text=f"Total Activos: ${total_activos:,.2f}")
            total_pasivos_label.config(text=f"Total Pasivos y Patrimonio: ${total_pasivos + total_patrimonio:,.2f}")

            messagebox.showinfo("Éxito", "Balance guardado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el balance: {str(e)}")

    def generar_pdf():
        # Validar que haya datos para generar el PDF
        if not fecha_entry.get().strip() or not empresa_entry.get().strip():
            messagebox.showerror("Error", "Debe ingresar la fecha y el nombre de la empresa")
            return

        # Solicitar ubicación para guardar el PDF
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"Balance_General_{empresa_entry.get().strip()}_{fecha_entry.get().replace('/', '_')}.pdf"
        )
        
        if not file_path:  # Si el usuario cancela la selección
            return

        try:
            # Crear el documento PDF
            doc = SimpleDocTemplate(
                file_path,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            # Lista para almacenar los elementos del PDF
            elements = []

            # Estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                alignment=1,  # Centrado
                spaceAfter=30
            )
            
            subtitle_style = ParagraphStyle(
                'CustomSubTitle',
                parent=styles['Heading2'],
                fontSize=12,
                alignment=1,
                spaceAfter=20
            )
            
            normal_style = styles["Normal"]
            
            # Título y encabezado
            elements.append(Paragraph(empresa_entry.get().strip().upper(), title_style))
            elements.append(Paragraph("BALANCE GENERAL", title_style))
            elements.append(Paragraph(f"Al {fecha_entry.get()}", subtitle_style))
            elements.append(Paragraph(f"(Expresado en dólares de los Estados Unidos de América)", subtitle_style))
            elements.append(Spacer(1, 20))

            # Recolectar datos de activos
            activos_data = [["ACTIVOS", "Monto"]]
            total_activos = 0
            
            # Función auxiliar para extraer monto
            def extraer_monto(entry):
                try:
                    texto = entry.get().strip()
                    if texto and validar_dos_decimales(texto):
                        return float(texto.replace('$', '').replace(',', ''))
                except ValueError:
                    pass
                return 0
            
            # Procesar activos corrientes
            activos_corrientes = []
            activos_corrientes_total = 0
            for child in activos_frame.winfo_children():
                if isinstance(child, tk.LabelFrame) and "CORRIENTES" in child.cget("text"):
                    for cuenta_frame in child.winfo_children():
                        if isinstance(cuenta_frame, tk.Frame):
                            combo = None
                            entry = None
                            for widget in cuenta_frame.winfo_children():
                                if isinstance(widget, ttk.Combobox):
                                    combo = widget
                                elif isinstance(widget, ttk.Entry):
                                    entry = widget
                            if combo and entry and combo.get().strip():
                                monto = extraer_monto(entry)
                                if monto > 0:
                                    cuenta = combo.get().split(' - ')[1]  # Obtener solo el nombre de la cuenta
                                    activos_corrientes.append(["    " + cuenta, f"${monto:,.2f}"])
                                    activos_corrientes_total += monto
            
            if activos_corrientes:
                activos_data.append(["ACTIVOS CORRIENTES", ""])
                activos_data.extend(activos_corrientes)
                activos_data.append(["Total Activos Corrientes", f"${activos_corrientes_total:,.2f}"])
                total_activos += activos_corrientes_total

            # Procesar activos no corrientes
            activos_no_corrientes = []
            activos_no_corrientes_total = 0
            for child in activos_frame.winfo_children():
                if isinstance(child, tk.LabelFrame) and "NO CORRIENTES" in child.cget("text"):
                    for cuenta_frame in child.winfo_children():
                        if isinstance(cuenta_frame, tk.Frame):
                            combo = None
                            entry = None
                            for widget in cuenta_frame.winfo_children():
                                if isinstance(widget, ttk.Combobox):
                                    combo = widget
                                elif isinstance(widget, ttk.Entry):
                                    entry = widget
                            if combo and entry and combo.get().strip():
                                monto = extraer_monto(entry)
                                if monto > 0:
                                    cuenta = combo.get().split(' - ')[1]
                                    activos_no_corrientes.append(["    " + cuenta, f"${monto:,.2f}"])
                                    activos_no_corrientes_total += monto

            if activos_no_corrientes:
                activos_data.append(["ACTIVOS NO CORRIENTES", ""])
                activos_data.extend(activos_no_corrientes)
                activos_data.append(["Total Activos No Corrientes", f"${activos_no_corrientes_total:,.2f}"])
                total_activos += activos_no_corrientes_total

            activos_data.append(["TOTAL ACTIVOS", f"${total_activos:,.2f}"])

            # Crear tabla de activos
            activos_table = Table(activos_data, colWidths=[4*inch, 2*inch])
            activos_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('TOPPADDING', (0, -1), (-1, -1), 12),
                ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
            ]))

            elements.append(activos_table)
            elements.append(Spacer(1, 20))

            # Recolectar datos de pasivos y patrimonio
            pasivos_patrimonio_data = [["PASIVOS Y PATRIMONIO", "Monto"]]
            total_pasivos = 0
            total_patrimonio = 0

            # Procesar pasivos corrientes
            pasivos_corrientes = []
            pasivos_corrientes_total = 0
            for child in pasivos_frame.winfo_children():
                if isinstance(child, tk.LabelFrame) and "CORRIENTES" in child.cget("text"):
                    for cuenta_frame in child.winfo_children():
                        if isinstance(cuenta_frame, tk.Frame):
                            combo = None
                            entry = None
                            for widget in cuenta_frame.winfo_children():
                                if isinstance(widget, ttk.Combobox):
                                    combo = widget
                                elif isinstance(widget, ttk.Entry):
                                    entry = widget
                            if combo and entry and combo.get().strip():
                                monto = extraer_monto(entry)
                                if monto > 0:
                                    cuenta = combo.get().split(' - ')[1]
                                    pasivos_corrientes.append(["    " + cuenta, f"${monto:,.2f}"])
                                    pasivos_corrientes_total += monto

            if pasivos_corrientes:
                pasivos_patrimonio_data.append(["PASIVOS CORRIENTES", ""])
                pasivos_patrimonio_data.extend(pasivos_corrientes)
                pasivos_patrimonio_data.append(["Total Pasivos Corrientes", f"${pasivos_corrientes_total:,.2f}"])
                total_pasivos += pasivos_corrientes_total

            # Procesar pasivos no corrientes
            pasivos_no_corrientes = []
            pasivos_no_corrientes_total = 0
            for child in pasivos_frame.winfo_children():
                if isinstance(child, tk.LabelFrame) and "NO CORRIENTES" in child.cget("text"):
                    for cuenta_frame in child.winfo_children():
                        if isinstance(cuenta_frame, tk.Frame):
                            combo = None
                            entry = None
                            for widget in cuenta_frame.winfo_children():
                                if isinstance(widget, ttk.Combobox):
                                    combo = widget
                                elif isinstance(widget, ttk.Entry):
                                    entry = widget
                            if combo and entry and combo.get().strip():
                                monto = extraer_monto(entry)
                                if monto > 0:
                                    cuenta = combo.get().split(' - ')[1]
                                    pasivos_no_corrientes.append(["    " + cuenta, f"${monto:,.2f}"])
                                    pasivos_no_corrientes_total += monto

            if pasivos_no_corrientes:
                pasivos_patrimonio_data.append(["PASIVOS NO CORRIENTES", ""])
                pasivos_patrimonio_data.extend(pasivos_no_corrientes)
                pasivos_patrimonio_data.append(["Total Pasivos No Corrientes", f"${pasivos_no_corrientes_total:,.2f}"])
                total_pasivos += pasivos_no_corrientes_total

            pasivos_patrimonio_data.append(["TOTAL PASIVOS", f"${total_pasivos:,.2f}"])

            # Procesar patrimonio
            patrimonio_items = []
            for child in pasivos_frame.winfo_children():
                if isinstance(child, tk.LabelFrame) and "PATRIMONIO" in child.cget("text"):
                    for cuenta_frame in child.winfo_children():
                        if isinstance(cuenta_frame, tk.Frame):
                            combo = None
                            entry = None
                            for widget in cuenta_frame.winfo_children():
                                if isinstance(widget, ttk.Combobox):
                                    combo = widget
                                elif isinstance(widget, ttk.Entry):
                                    entry = widget
                            if combo and entry and combo.get().strip():
                                monto = extraer_monto(entry)
                                if monto > 0:
                                    cuenta = combo.get().split(' - ')[1]
                                    patrimonio_items.append(["    " + cuenta, f"${monto:,.2f}"])
                                    total_patrimonio += monto

            if patrimonio_items:
                pasivos_patrimonio_data.append(["PATRIMONIO", ""])
                pasivos_patrimonio_data.extend(patrimonio_items)
                pasivos_patrimonio_data.append(["TOTAL PATRIMONIO", f"${total_patrimonio:,.2f}"])

            pasivos_patrimonio_data.append(["TOTAL PASIVOS Y PATRIMONIO", f"${(total_pasivos + total_patrimonio):,.2f}"])

            # Crear tabla de pasivos y patrimonio
            pasivos_patrimonio_table = Table(pasivos_patrimonio_data, colWidths=[4*inch, 2*inch])
            pasivos_patrimonio_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('TOPPADDING', (0, -1), (-1, -1), 12),
                ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
            ]))

            elements.append(pasivos_patrimonio_table)
            
            # Agregar espacio para firmas
            elements.append(Spacer(1, 50))
            
            # Crear tabla para firmas
            firma_data = [
                ["_______________________", "_______________________", "_______________________"],
                ["Representante Legal", "Contador", "Auditor"],
            ]
            firma_table = Table(firma_data, colWidths=[2.5*inch, 2.5*inch, 2.5*inch])
            firma_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, 1), 10),
                ('TOPPADDING', (0, 1), (-1, 1), 5),
            ]))
            
            elements.append(firma_table)

            # Generar el PDF
            doc.build(elements)
            
            # Mostrar mensaje de éxito y preguntar si desea abrir el PDF
            if messagebox.askyesno("Éxito", "PDF generado correctamente. ¿Desea abrirlo?"):
                os.startfile(file_path) if os.name == 'nt' else os.system(f'xdg-open {file_path}')

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar el PDF: {str(e)}")

    ttk.Button(botones_frame, text="Guardar Balance", command=guardar_balance).pack(side=tk.LEFT, padx=5)
    ttk.Button(botones_frame, text="Generar PDF", command=generar_pdf).pack(side=tk.LEFT, padx=5)

def menu_principal():
    ventana_principal = tk.Tk()
    ventana_principal.title("Sistema de Contabilidad")
    ventana_principal.geometry("1200x600")
    ventana_principal.configure(bg="#E0F2FE")
    ventana_principal.resizable(True, True)

    frame_botones = tk.Frame(ventana_principal, bg="#1E3A8A", width=290, height=400)
    frame_botones.pack(side=tk.LEFT, fill=tk.Y)
    frame_botones.pack_propagate(False)

    frame_contenido = tk.Frame(ventana_principal, bg="#E0F2FE")
    frame_contenido.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    botones = [
        ("Ver catalogo de cuentas", lambda: ver_catalogo_cuentas(frame_contenido)),
        ("Crear Cuenta - Para catalogo de cuentas", lambda: crear_cuentas_Estados_Financieros(frame_contenido)),
        ("Mostrar Estado de Resultado", lambda: mostrar_estado_resultado(frame_contenido)),
        ("Mostrar Balance General", lambda: mostrar_balance_general(frame_contenido)),
        ("Salir", lambda: cerrar_aplicacion(ventana_principal))
    ]

    for texto, comando in botones:
        color = "#DC2626" if texto == "Salir" else "#1E3A8A"
        tk.Button(frame_botones, text=texto, command=comando, bg=color, fg="white", activebackground="#00587A", width=33, height=2, font=("Arial", 10, "bold")).pack(pady=5)

    ventana_principal.protocol("WM_DELETE_WINDOW", lambda: cerrar_aplicacion(ventana_principal))
    ventana_principal.mainloop()

def cerrar_aplicacion(ventana):
    ventana.quit()
    ventana.destroy()
    import sys
    sys.exit()

if __name__ == "__main__":
    menu_principal()