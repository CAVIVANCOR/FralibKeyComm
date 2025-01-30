import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import pyautogui
import threading
import time
import webbrowser
from PIL import Image, ImageTk
import os
import sys
import win32com.client
from pystray import Icon as pystrayIcon, MenuItem as item, Menu
from tkinter import Toplevel
class SerialApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Configuración del Puerto COM")
        self.frame = ttk.Frame(self.master, padding="10 10 10 10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        #self.logo_image = Image.open("./assets/logoFralib.png")
        self.logo_image = Image.open(os.path.join(os.path.dirname(__file__), "assets", "logoFralib.png"))

        self.original_logo_image = self.logo_image.resize((16, 16), Image.Resampling.LANCZOS)
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = ttk.Label(self.frame, image=self.logo_photo, cursor="hand2")
        self.logo_label.grid(row=0, column=0, columnspan=3)
        self.logo_url = "https://www.fralib.com/"
        self.logo_label.bind("<Button-1>", lambda e: webbrowser.open_new(self.logo_url))

        self.com_label = ttk.Label(self.frame, text="Seleccione el puerto COM:")
        self.com_label.grid(row=1, column=0, sticky=tk.W)
        self.com_var = tk.StringVar()
        self.com_dropdown = ttk.Combobox(self.frame, textvariable=self.com_var, state='readonly')
        self.com_dropdown.grid(row=1, column=1, sticky=(tk.W, tk.E))
        self.refresh_ports()

        self.start_button = ttk.Button(self.frame, text="Iniciar", command=self.start_reading)
        self.start_button.grid(row=2, column=0)

        self.about_button = ttk.Button(self.frame, text="Desarrollado por", command=self.show_designer_info)
        self.about_button.grid(row=2, column=1)

        self.exit_button = ttk.Button(self.frame, text="Salir", command=self.quit_from_tray)
        self.exit_button.grid(row=2, column=2)

        self.auto_start_var = tk.BooleanVar()
        self.auto_start_check = ttk.Checkbutton(self.frame, text="Iniciar automáticamente con Windows",
                                                variable=self.auto_start_var, command=self.toggle_auto_start)
        self.auto_start_check.grid(row=3, column=1, sticky=tk.W)
        self.check_auto_start()

        self.master.protocol("WM_DELETE_WINDOW", self.hide_window)

    def refresh_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.com_dropdown['values'] = ports if ports else ["No disponible"]
        if ports:
            self.com_dropdown.current(0)

    def start_reading(self):
        port_name = self.com_var.get()
        thread = threading.Thread(target=self.read_from_port, args=(port_name,))
        thread.daemon = True
        thread.start()

    def read_from_port(self, port_name):
        try:
            with serial.Serial(port_name, 9600, timeout=1) as ser:
                ser.flushInput()
                time.sleep(10)
                while True:
                    if ser.in_waiting > 0:
                        serial_data = ser.readline().decode('utf-8').rstrip()
                        pyautogui.typewrite(serial_data)
                        pyautogui.typewrite('\n')
                        print("Datos enviados a la aplicación activa: ", serial_data)
        except serial.SerialException as e:
            print("Error al abrir el puerto serial: ", e)

    def show_designer_info(self):
        top = Toplevel(self.master)
        top.title("Desarrollado por")
        top.geometry("300x300")
        #designer_image = Image.open("./assets/logo13Cuadrado.png")
        designer_image = Image.open(os.path.join(os.path.dirname(__file__), "assets", "logo13Cuadrado.png"))
        designer_image.thumbnail((290, 290), Image.Resampling.LANCZOS)
        designer_photo = ImageTk.PhotoImage(designer_image)
        designer_label = ttk.Label(top, image=designer_photo, cursor="hand2")
        designer_label.image = designer_photo
        designer_label.pack(padx=5, pady=5)
        designer_url = "https://www.13elfuturohoy.com/"
        designer_label.bind("<Button-1>", lambda e: webbrowser.open_new(designer_url))

    def hide_window(self):
        self.master.withdraw()
        menu = Menu(item('Restore', self.show_window), item('Exit', self.quit_from_tray))
        icon = pystrayIcon("SerialApp", self.original_logo_image, "SerialApp", menu)
        icon.run()

    def show_window(self, icon, item):
        icon.stop()
        self.master.deiconify()

    def quit_from_tray(self, icon=None, item=None):
        if icon:
            icon.stop()
        self.master.destroy()

    def toggle_auto_start(self):
        startup_path = os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup')
        shortcut_path = os.path.join(startup_path, 'SerialApp.lnk')
        if self.auto_start_var.get():
            shell = win32com.client.Dispatch('WScript.Shell')
            shortcut = shell.CreateShortcut(shortcut_path)
            shortcut.TargetPath = sys.executable
            shortcut.Arguments = f' "{os.path.realpath(__file__)}"'
            shortcut.WorkingDirectory = os.path.dirname(os.path.realpath(__file__))
            shortcut.save()
        else:
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)

    def check_auto_start(self):
        startup_path = os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup')
        shortcut_path = os.path.join(startup_path, 'SerialApp.lnk')
        self.auto_start_var.set(os.path.exists(shortcut_path))

def main():
    root = tk.Tk()
    app = SerialApp(root)
    root.after(0, app.hide_window)  # Oculta la ventana principal al iniciar la aplicación
    root.mainloop()

if __name__ == "__main__":
    main()
