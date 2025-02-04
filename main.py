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

def setup_logging():
    # Configura el sistema de registro (logging) de la aplicación.
    # Crea un archivo de log en el directorio de ejecución de la aplicación
    # y configura los parámetros básicos del registro.
    # Returns:
    # str: Ruta del archivo de log creado
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
        return clave[0]
    except:
        return None

def guardar_clave_registro(clave):
    win32api.RegSetValueEx(win32con.HKEY_CURRENT_USER, "Software\\MiAplicacion\\Clave", 0, win32con.REG_SZ, clave)

def verificar_clave():
    clave_guardada = leer_clave_registro()
    if clave_guardada is None:
        clave = input("Ingrese su clave: ")
        guardar_clave_registro(clave)
        return clave
    else:
        return clave_guardada

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
    