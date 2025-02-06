import os
import tkinter as tk
from tkinter import ttk, Toplevel, messagebox
from PIL import Image, ImageTk
import webbrowser
from pystray import Icon as pystrayIcon, Menu, MenuItem as item
import json
from configAccesos import CLAVE_PARAMETROS

class SerialAppUI:
    def __init__(self, master, serial_comm, auto_start_manager, decimal_separator='.'):
        self.master = master
        self.serial_comm = serial_comm
        self.auto_start_manager = auto_start_manager
        self.master.title("Configuración del Puerto COM")
        self.frame = ttk.Frame(self.master, padding="10 10 10 10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        # Configurar ruta correcta del logo
        logo_path = self._get_resource_path("./assets/logoFralib.png")
        self.logo_image=self._load_logo(logo_path)
        # Inicializar variables
        self.com_var = tk.StringVar()
        self.baud_rate_var = tk.StringVar()
        self.parity_var = tk.StringVar()
        self.length_var = tk.StringVar()
        self.stop_bit_var = tk.StringVar()
        self.terminator_var = tk.StringVar()
        self.capture_mode_var = tk.StringVar()
        self.decimal_separator_var = tk.StringVar()
        # Cargar Datos del Archivo JSON
        self.load_config()

        self.com_label = ttk.Label(self.frame, text="Seleccione el puerto COM:")
        self.com_label.grid(row=1, column=0, sticky=tk.W)
        if not self.com_var.get():
            self.com_var = tk.StringVar()
        self.com_dropdown = ttk.Combobox(self.frame, textvariable=self.com_var, state='disabled')
        self.com_dropdown.grid(row=1, column=1, sticky=(tk.W, tk.E))
        self.refresh_ports()

        # Parámetros seriales
        self.baud_rate_label = ttk.Label(self.frame, text="Baud Rate:")
        self.baud_rate_label.grid(row=2, column=0, sticky=tk.W)
        if not self.baud_rate_var.get():
            self.baud_rate_var = tk.StringVar(value="9600")
        self.baud_rate_entry = ttk.Entry(self.frame, textvariable=self.baud_rate_var, state='readonly')
        self.baud_rate_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))

        self.parity_label = ttk.Label(self.frame, text="Parity:")
        self.parity_label.grid(row=3, column=0, sticky=tk.W)
        if not self.parity_var.get():
            self.parity_var = tk.StringVar(value="N")
        self.parity_dropdown = ttk.Combobox(self.frame, textvariable=self.parity_var, values=["N", "E", "O"], state='disabled')
        self.parity_dropdown.grid(row=3, column=1, sticky=(tk.W, tk.E))

        self.length_label = ttk.Label(self.frame, text="Length:")
        self.length_label.grid(row=4, column=0, sticky=tk.W)
        if not self.length_var.get():
            self.length_var = tk.StringVar(value="8")
        self.length_entry = ttk.Entry(self.frame, textvariable=self.length_var, state='readonly')
        self.length_entry.grid(row=4, column=1, sticky=(tk.W, tk.E))

        self.stop_bit_label = ttk.Label(self.frame, text="Stop Bit:")
        self.stop_bit_label.grid(row=5, column=0, sticky=tk.W)
        if not self.stop_bit_var.get():
            self.stop_bit_var = tk.StringVar(value="1")
        self.stop_bit_entry = ttk.Entry(self.frame, textvariable=self.stop_bit_var, state='readonly')
        self.stop_bit_entry.grid(row=5, column=1, sticky=(tk.W, tk.E))

        self.terminator_label = ttk.Label(self.frame, text="Terminator:")
        self.terminator_label.grid(row=6, column=0, sticky=tk.W)
        if not self.terminator_var.get():
            self.terminator_var = tk.StringVar(value="CR")
        self.terminator_entry = ttk.Entry(self.frame, textvariable=self.terminator_var, state='readonly')
        self.terminator_entry.grid(row=6, column=1, sticky=(tk.W, tk.E))

        # Opciones de captura
        self.capture_mode_label = ttk.Label(self.frame, text="Modo de Captura:")
        self.capture_mode_label.grid(row=7, column=0, sticky=tk.W)
        if not self.capture_mode_var.get():
            self.capture_mode_var = tk.StringVar(value="Todo")
        self.capture_mode_dropdown = ttk.Combobox(self.frame, textvariable=self.capture_mode_var, values=["Todo", "Números"], state='disabled')
        self.capture_mode_dropdown.grid(row=7, column=1, sticky=(tk.W, tk.E))

        # Campo para seleccionar el separador decimal
        self.decimal_separator_label = ttk.Label(self.frame, text="Separador decimal:")
        self.decimal_separator_label.grid(row=7, column=2, sticky=tk.W)
        if not self.decimal_separator_var.get():
            self.decimal_separator_var = tk.StringVar(value=decimal_separator)
        self.decimal_separator_dropdown = ttk.Combobox(self.frame, textvariable=self.decimal_separator_var, values=['.', ','], state='disabled')
        self.decimal_separator_dropdown.grid(row=7, column=3, sticky=(tk.W, tk.E))
        # Botones
        self.edit_params_button = ttk.Button(self.frame, text="Editar Parámetros", command=self.edit_params)
        self.edit_params_button.grid(row=8, column=0)

        self.start_button = ttk.Button(self.frame, text="Iniciar", command=self.start_reading)
        self.start_button.grid(row=8, column=1)
        self.close_port_button = ttk.Button(self.frame, text="Cerrar Puerto", command=self.close_port_connection)
        self.close_port_button.grid(row=8, column=2, sticky=tk.W)

        self.about_button = ttk.Button(self.frame, text="Desarrollado por", command=self.show_designer_info)
        self.about_button.grid(row=8, column=3)
        self.exit_button = ttk.Button(self.frame, text="Salir", command=self.quit_from_tray)
        self.exit_button.grid(row=8, column=4)

        self.auto_start_var = tk.BooleanVar()
        self.auto_start_check = ttk.Checkbutton(self.frame, text="Iniciar automáticamente con Windows",
                                               variable=self.auto_start_var, command=self.toggle_auto_start)
        self.auto_start_check.grid(row=9, column=1, sticky=tk.W)
        self.check_auto_start()

        self.master.protocol("WM_DELETE_WINDOW", self.hide_window)
    def edit_params(self):
        root_parametros = tk.Tk()
        root_parametros.title("Ingrese su clave")
        label = tk.Label(root_parametros, text="Clave Parametros:")
        label.pack()
        entry_parametros = tk.Entry(root_parametros, show="*")
        entry_parametros.pack()
        
        def comprobar_clave_parametros():
            clave_ingresada = entry_parametros.get()
            if clave_ingresada == CLAVE_PARAMETROS:
                self.com_dropdown.configure(state="normal")
                self.baud_rate_entry.configure(state="normal")
                self.parity_dropdown.configure(state="normal")
                self.length_entry.configure(state="normal")
                self.stop_bit_entry.configure(state="normal")
                self.terminator_entry.configure(state="normal")
                self.capture_mode_dropdown.configure(state="normal")
                self.decimal_separator_dropdown.configure(state="normal")
                print("Clave correcta! Los Parametros pueden ser editados.")
                root_parametros.destroy()
            else:
                print("Clave incorrecta. Intente de nuevo.")
                messagebox.showerror("Error", "Clave incorrecta")
                entry_parametros.delete(0, tk.END)
        
        button_parametros = tk.Button(root_parametros, text="Aceptar", command=comprobar_clave_parametros)
        button_parametros.pack()
        root_parametros.mainloop()

    def _get_resource_path(self, relative_path):
        """Obtiene la ruta absoluta del recurso"""
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            return os.path.join(base_path, relative_path)
        except Exception as e:
            print(f"Error al obtener ruta del recurso: {str(e)}")
            return None

    def _load_logo(self, logo_path):
        """Carga y muestra el logo"""
        try:
            if not logo_path or not os.path.exists(logo_path):
                raise FileNotFoundError(f"El archivo de logo {logo_path} no existe")

            self.logo_image = Image.open(logo_path)
            resized_image = self.logo_image.resize((295, 84), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(resized_image)

            self.logo_label = ttk.Label(self.frame, image=self.logo_photo, cursor="hand2")
            self.logo_label.grid(row=0, column=0, columnspan=3)
            self.logo_url = "https://www.fralib.com/"
            self.logo_label.bind("<Button-1>", lambda e: webbrowser.open_new(self.logo_url))
            return self.logo_image

        except Exception as e:
            print(f"Error al cargar el logo: {str(e)}")

    def refresh_ports(self):
        ports = self.serial_comm.get_available_ports()
        self.com_dropdown['values'] = ports if ports else ["No disponible"]
        if ports:
            if self.com_var.get() in self.com_dropdown['values']:
                self.com_dropdown.set(self.com_var.get())

    def start_reading(self):
        if self.serial_comm.serial_port and self.serial_comm.serial_port.is_open:
            self.serial_comm.serial_port.close()

        port_name = self.com_var.get()
        baud_rate = int(self.baud_rate_var.get())
        parity = self.parity_var.get()
        length = int(self.length_var.get())
        stop_bit = int(self.stop_bit_var.get())
        terminator = self.terminator_var.get()
        capture_all = self.capture_mode_var.get() == "Todo"
        decimal_separator = self.decimal_separator_var.get()
        self.save_config()
        self.serial_comm.start_reading(port_name, baud_rate, parity, length, stop_bit, terminator, capture_all, decimal_separator)
        self.hide_window()

    def close_port_connection(self):
        if self.serial_comm.serial_port and self.serial_comm.serial_port.is_open:
            self.serial_comm.close_port()
            print("Puerto serial cerrado")

    def show_designer_info(self):
        top = Toplevel(self.master)
        top.title("Desarrollado por")
        top.geometry("300x300")

        designer_path = self._get_resource_path("assets/logo13Cuadrado.png")
        if designer_path and os.path.exists(designer_path):
            designer_image = Image.open(designer_path)
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
        icon = pystrayIcon("SerialApp", self.logo_image, "SerialApp", menu)
        icon.run()

    def show_window(self, icon, item):
        icon.stop()
        self.master.deiconify()

    def quit_from_tray(self, icon=None, item=None):
        if icon:
            icon.stop()
        self.master.destroy()

    def toggle_auto_start(self):
        self.auto_start_manager.toggle_auto_start(self.auto_start_var.get())

    def check_auto_start(self):
        self.auto_start_var.set(self.auto_start_manager.check_auto_start())

    def save_config(self):
        config = {
            'com_port': self.com_var.get(),
            'baud_rate': self.baud_rate_var.get(),
            'parity': self.parity_var.get(),
            'length': self.length_var.get(),
            'stop_bit': self.stop_bit_var.get(),
            'terminator': self.terminator_var.get(),
            'capture_mode': self.capture_mode_var.get(),
            'decimal_separator': self.decimal_separator_var.get()
        }
        with open('config.json', 'w') as f:
            json.dump(config, f)

    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                self.com_var.set(config['com_port'])
                self.baud_rate_var.set(config['baud_rate'])
                self.parity_var.set(config['parity'])
                self.length_var.set(config['length'])
                self.stop_bit_var.set(config['stop_bit'])
                self.terminator_var.set(config['terminator'])
                self.capture_mode_var.set(config['capture_mode'])
                self.decimal_separator_var.set(config['decimal_separator'])
        except FileNotFoundError:
            pass
