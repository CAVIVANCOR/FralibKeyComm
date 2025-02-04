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
import win32com.client

# Configurar el registro
def setup_logging():
    """
    Configura el sistema de registro (logging) de la aplicación.
    
    Crea un archivo de log en el directorio de ejecución de la aplicación
    y configura los parámetros básicos del registro.
    
    Returns:
        str: Ruta del archivo de log creado
    """
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

    