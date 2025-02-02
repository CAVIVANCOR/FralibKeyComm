import tkinter as tk
from tkinter import ttk, messagebox
from ui_module import SerialAppUI
from serial_module import SerialCommunication
from utils_module import AutoStartManager
import serial.tools.list_ports
def verify_available_ports():
    ports = serial.tools.list_ports.comports()
    if not ports:
        messagebox.showwarning("Advertencia", "No se encontraron puertos COM disponibles")

def main(decimal_separator='.'):
    root = tk.Tk()
    root.title("Configuración del Puerto COM")
    
    try:
        serial_comm = SerialCommunication()
        auto_start_manager = AutoStartManager()
        app_ui = SerialAppUI(root, serial_comm, auto_start_manager, decimal_separator)
        verify_available_ports()
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Error al iniciar la aplicación: {str(e)}")
        root.destroy()

if __name__ == "__main__":
    main()