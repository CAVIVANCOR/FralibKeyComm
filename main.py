import tkinter as tk
from tkinter import ttk, messagebox
from ui_module import SerialAppUI
from serial_module import SerialCommunication
from utils_module import AutoStartManager
import serial.tools.list_ports
import logging
from datetime import datetime
import os
import sys
import win32api
import win32con
from configAccesos import CLAVE_INSTALACION, CLAVE_PARAMETROS

def setup_logging():
    try:
        log_file = os.path.join(os.path.dirname(sys.executable), 'SerialApp_startup.log')
        logging.basicConfig(
            filename=log_file,
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return log_file
    except Exception as e:
        logging.error(f"Error al configurar el logging: {str(e)}")
        raise

def leer_clave_registro():
    try:
        clave = win32api.RegQueryValueEx(win32con.HKEY_CURRENT_USER, "Software\\MiAplicacion\\Clave")
        if clave is not None:
            return clave[0]
        else:
            return None
    except OSError as e:
        print(f"Error al leer la clave: {e}")
        messagebox.showerror("Error", f"Error al leer la clave:{e}")
        return None
    except WindowsError as e:
        print(f"Error al leer la clave: {e}")
        messagebox.showerror("Error", f"Error al leer la clave:{e}")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        messagebox.showerror("Error", f"Error inesperado:{e}") 
        return None

def guardar_clave_registro(clave):
    try:
        win32api.RegSetValueEx(win32con.HKEY_CURRENT_USER, "Software\\MiAplicacion\\Clave", 0, win32con.REG_SZ, clave)
        print("La clave se ha guardado correctamente")
        messagebox.showinfo("Éxito", "La clave se ha guardado correctamente")
    except OSError as e:
        print(f"Error al guardar la clave: {e}")
        messagebox.showerror("Error", "Error al guardar la clave")
    except WindowsError as e:
        print(f"Error al guardar la clave: {e}")
        messagebox.showerror("Error", "Error al guardar la clave")
    except Exception as e:
        print(f"Error inesperado: {e}")
        messagebox.showerror("Error", "Error inesperado")

def borrar_clave_registro():
    try:
        # Verifica la existencia de la clave
        clave = win32api.RegQueryValueEx(win32con.HKEY_CURRENT_USER, "Software\\MiAplicacion\\Clave")
        if clave is not None:
            win32api.RegDeleteValue(win32con.HKEY_CURRENT_USER, "Software\\MiAplicacion\\Clave")
            print("La clave se ha borrado correctamente")
            messagebox.showinfo("Exito", "La clave se ha borrado correctamente")
        else:
            print("La clave no existe")
            messagebox.showinfo("Información", "La clave no existe")
    except OSError as e:
        print(f"Error al borrar la clave: {e}")
        messagebox.showerror("Error", "Error al borrar la clave")
    except WindowsError as e:
        print(f"Error al borrar la clave: {e}")
        messagebox.showerror("Error", "Error al borrar la clave")
    except Exception as e:
        print(f"Error inesperado: {e}")
        messagebox.showerror("Error", "Error inesperado")

def verificar_clave():
    clave = None
    clave_guardada = leer_clave_registro()
    if clave_guardada is None:
        # Pide la clave la primera vez
        root = tk.Tk()
        root.title("Ingrese su clave")
        label = tk.Label(root, text="Ingrese su clave:")
        label.pack()
        entry = tk.Entry(root, show="*")
        entry.pack()
        def comprobar_clave():
            clave_ingresada = entry.get()
            if clave_ingresada == CLAVE_INSTALACION:
                nonlocal clave
                clave = clave_ingresada
                guardar_clave_registro(clave_ingresada)
                print("Clave correcta! Se ha grabado en el registro.")
                root.destroy()
            else:
                print("Clave incorrecta. Intente de nuevo.")
                entry.delete(0, tk.END)
                
        button = tk.Button(root, text="Aceptar", command=comprobar_clave)
        button.pack()
        root.mainloop()
    else:
        # Lee la clave del registro y la compara con la clave fija
        if clave_guardada == CLAVE_INSTALACION:
            clave = clave_guardada
            print("Clave correcta! Acceso permitido.")
        else:
            print("Clave NO COINCIDE CON EL REGISTRO. Acceso denegado.")
            messagebox.showerror("Error", f"Error ACCESO DENEGADO : CLAVE DE INSTALACION NO COINCIDE")
            # Pide la clave de corrección
            root = tk.Tk()
            root.title("FRALIB SAC - MODIFICAR CLAVE INSTALACION")
            label = tk.Label(root, text="Ingrese la clave para Corregir Parametros:")
            label.pack()
            entry = tk.Entry(root, show="*")
            entry.pack()
            
            def corregir_clave():
                clave_correccion = entry.get()
                if clave_correccion == CLAVE_PARAMETROS:
                    # Grabar la clave de instalación en el registro
                    nonlocal clave
                    clave = CLAVE_INSTALACION
                    guardar_clave_registro(CLAVE_INSTALACION)
                    print("Clave correcta! Se ha grabado en el registro.")
                    messagebox.showinfo("Exito", "Clave correcta! Se ha grabado en el registro.")
                    root.destroy()
                else:
                    print("Clave de corrección incorrecta. Intente de nuevo.")
                    entry.delete(0, tk.END)

            button = tk.Button(root, text="Aceptar", command=corregir_clave)
            button.pack()
            root.mainloop()
    return clave



def verify_available_ports():
    try:
        ports = serial.tools.list_ports.comports()
        if not ports:
            logging.warning("No se encontraron puertos COM disponibles")
            messagebox.showwarning("Advertencia", "No se encontraron puertos COM disponibles")
        else:
            logging.info(f"Se encontraron {len(ports)} puertos COM disponibles")
    except Exception as e:
        logging.error(f"Error al verificar puertos COM: {str(e)}")
        messagebox.showerror("Error", f"Error al verificar puertos COM: {str(e)}")

def main(decimal_separator='.'):
    try:
        clave = verificar_clave()
        if clave is None:
            return

        # Inicializar el registro
        log_file = setup_logging()
        logging.info(f"Inicio de la aplicación. Archivo de log: {log_file}")
        
        root = tk.Tk()
        root.title("Configuración del Puerto COM")
        logging.info("Ventana principal inicializada correctamente")
        
        # Inicializar componentes
        serial_comm = SerialCommunication()
        logging.info("Componente SerialCommunication inicializado correctamente")
        
        auto_start_manager = AutoStartManager()
        logging.info("Componente AutoStartManager inicializado correctamente")
        
        app_ui = SerialAppUI(root, serial_comm, auto_start_manager, decimal_separator)
        logging.info("Interfaz gráfica inicializada correctamente")
        
        # Verificar puertos disponibles
        verify_available_ports()
        
        # Iniciar bucle principal
        logging.info("Iniciando bucle principal de la aplicación")
        root.mainloop()
        
    except Exception as e:
        logging.error(f"Error al iniciar la aplicación: {str(e)}", exc_info=True)
        messagebox.showerror("Error", f"Error al iniciar la aplicación: {str(e)}")
        root.destroy()

if __name__ == "__main__":
    main()
    