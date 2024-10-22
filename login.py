import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

def iniciar_sesion(event=None): 
    usuario = entry_usuario.get()
    contrasena = entry_contrasena.get()

    
    if usuario == "admin" and contrasena == "admin":
        messagebox.showinfo("Inicio de sesión", "¡Inicio de sesión exitoso!")
        ventana_login.destroy()
        abrir_menu()
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")


def abrir_menu():
    import menu  
    menu.menu_principal()


ventana_login = tk.Tk()
ventana_login.title("Login")
ventana_login.geometry("400x600")  
ventana_login.configure(bg="#F0F4F8")  

imagen = Image.open("calculo.png") 
imagen = imagen.resize((120, 120), Image.LANCZOS)  
imagen_tk = ImageTk.PhotoImage(imagen)


frame_contenido = tk.Frame(ventana_login, bg="#FFFFFF", bd=2, relief="flat", padx=20, pady=20)
frame_contenido.place(relx=0.5, rely=0.5, anchor="center")  

label_imagen = tk.Label(frame_contenido, image=imagen_tk, bg="#FFFFFF")
label_imagen.pack(pady=10)


label_titulo = tk.Label(frame_contenido, text="Inicio de Sesión", font=("Helvetica", 20, "bold"), bg="#FFFFFF", fg="#333333")
label_titulo.pack(pady=20)

label_usuario = tk.Label(frame_contenido, text="Usuario", font=("Helvetica", 14), bg="#FFFFFF", fg="#333333")
label_usuario.pack(pady=10)
entry_usuario = tk.Entry(frame_contenido, font=("Helvetica", 14), width=30, bd=1, relief="solid")
entry_usuario.pack(pady=5, ipady=5)


label_contrasena = tk.Label(frame_contenido, text="Contraseña", font=("Helvetica", 14), bg="#FFFFFF", fg="#333333")
label_contrasena.pack(pady=10)
entry_contrasena = tk.Entry(frame_contenido, show="*", font=("Helvetica", 14), width=30, bd=1, relief="solid")
entry_contrasena.pack(pady=5, ipady=5)

btn_login = tk.Button(frame_contenido, text="Iniciar Sesión", command=iniciar_sesion, font=("Helvetica", 14, "bold"), 
                      bg="#007BFF", fg="white", width=20, height=2, bd=0, relief="flat", cursor="hand2", activebackground="#0056b3")
btn_login.pack(pady=20)


ventana_login.bind('<Return>', iniciar_sesion)


ventana_login.mainloop()
