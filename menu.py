import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re
import locale
from dataclasses import dataclass
from typing import Optional
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tkinter import messagebox


# Configuración de locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

@dataclass
class Account:
    code: str
    name: str
    parent_code: Optional[str]

# Funciones de validación
def validar_solo_letras(cadena):
    return all(caracter.isalpha() or caracter.isspace() for caracter in cadena)

#NO SE UTILIZA
def validar_dos_decimales(cadena):
    return re.match(r'^\d+(\.\d{1,2})?$', cadena) is not None

#NO SE UTILIZA
# Funciones de formateo de números
def formatear_numero(numero):
    return locale.format_string('%.2f', numero, grouping=True)

def desformatear_numero(numero_str):
    return numero_str.replace(',', '')

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
        # Obtener todos los frames de cuentas
        total_activos = 0
        total_pasivos = 0
        total_patrimonio = 0
        
        # Función auxiliar para extraer el monto de un entry
        def extraer_monto(entry):
            try:
                texto = entry.get().strip()
                if not texto:
                    return 0
                # Eliminar cualquier formato de moneda y convertir a float
                monto = float(texto.replace('$', '').replace(',', ''))
                return monto
            except ValueError:
                return 0

        # Recorrer todos los frames de activos
        for child in activos_frame.winfo_children():
            if isinstance(child, tk.LabelFrame):  # Verificar si es un frame de sección
                for cuenta_frame in child.winfo_children():
                    if isinstance(cuenta_frame, tk.Frame):
                        # Buscar el entry de monto en el frame de la cuenta
                        for widget in cuenta_frame.winfo_children():
                            if isinstance(widget, ttk.Entry):
                                total_activos += extraer_monto(widget)

        # Recorrer todos los frames de pasivos y patrimonio
        for child in pasivos_frame.winfo_children():
            if isinstance(child, tk.LabelFrame):
                for cuenta_frame in child.winfo_children():
                    if isinstance(cuenta_frame, tk.Frame):
                        for widget in cuenta_frame.winfo_children():
                            if isinstance(widget, ttk.Entry):
                                if "PASIVO" in child.cget("text"):
                                    total_pasivos += extraer_monto(widget)
                                else:  # Es patrimonio
                                    total_patrimonio += extraer_monto(widget)

        # Verificar que los totales cuadren
        if abs(total_activos - (total_pasivos + total_patrimonio)) < 0.01:  # Permitir pequeñas diferencias por redondeo
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
            fecha = fecha_entry.get()
            empresa = empresa_entry.get()
            
            cursor.execute('''
            INSERT INTO balance_general (fecha, empresa, total_activos, total_pasivos, total_patrimonio)
            VALUES (?, ?, ?, ?, ?)
            ''', (fecha, empresa, total_activos, total_pasivos, total_patrimonio))
            
            conn.commit()
            conn.close()
            
            # Actualizar las etiquetas de totales
            total_activos_label.config(text=f"Total Activos: ${total_activos:,.2f}")
            total_pasivos_label.config(text=f"Total Pasivos y Patrimonio: ${total_pasivos + total_patrimonio:,.2f}")
            
            messagebox.showinfo("Éxito", "Balance guardado correctamente")
        else:
            messagebox.showerror("Error", 
                f"El balance no cuadra:\nTotal Activos: ${total_activos:,.2f}\n" +
                f"Total Pasivos + Patrimonio: ${total_pasivos + total_patrimonio:,.2f}\n" +
                f"Diferencia: ${abs(total_activos - (total_pasivos + total_patrimonio)):,.2f}")

    def generar_pdf():
         pass
     
    ttk.Button(botones_frame, text="Guardar Balance", command=guardar_balance).pack(side=tk.LEFT, padx=5)
    ttk.Button(botones_frame, text="Generar PDF", command=generar_pdf).pack(side=tk.LEFT, padx=5)
    
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
        ("Ver catalogo de cuentas", lambda: ver_catalogo_cuentas(frame_contenido)),
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