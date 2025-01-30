import tkinter as tk
from tkinter import ttk, Toplevel
from PIL import Image, ImageTk
import webbrowser
from pystray import Icon as pystrayIcon, Menu, MenuItem as item

class SerialAppUI:
    def __init__(self, master, serial_comm, auto_start_manager):
        self.master = master
        self.serial_comm = serial_comm
        self.auto_start_manager = auto_start_manager
        self.master.title("Configuración del Puerto COM")
        self.frame = ttk.Frame(self.master, padding="10 10 10 10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.logo_image = Image.open("assets/logoFralib.png")
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

        # Serial parameters
        self.baud_rate_label = ttk.Label(self.frame, text="Baud Rate:")
        self.baud_rate_label.grid(row=2, column=0, sticky=tk.W)
        self.baud_rate_var = tk.StringVar(value="9600")
        self.baud_rate_entry = ttk.Entry(self.frame, textvariable=self.baud_rate_var)
        self.baud_rate_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))

        self.parity_label = ttk.Label(self.frame, text="Parity:")
        self.parity_label.grid(row=3, column=0, sticky=tk.W)
        self.parity_var = tk.StringVar(value="N")
        self.parity_dropdown = ttk.Combobox(self.frame, textvariable=self.parity_var, values=["N", "E", "O"])
        self.parity_dropdown.grid(row=3, column=1, sticky=(tk.W, tk.E))

        self.length_label = ttk.Label(self.frame, text="Length:")
        self.length_label.grid(row=4, column=0, sticky=tk.W)
        self.length_var = tk.StringVar(value="8")
        self.length_entry = ttk.Entry(self.frame, textvariable=self.length_var)
        self.length_entry.grid(row=4, column=1, sticky=(tk.W, tk.E))

        self.stop_bit_label = ttk.Label(self.frame, text="Stop Bit:")
        self.stop_bit_label.grid(row=5, column=0, sticky=tk.W)
        self.stop_bit_var = tk.StringVar(value="1")
        self.stop_bit_entry = ttk.Entry(self.frame, textvariable=self.stop_bit_var)
        self.stop_bit_entry.grid(row=5, column=1, sticky=(tk.W, tk.E))

        self.terminator_label = ttk.Label(self.frame, text="Terminator:")
        self.terminator_label.grid(row=6, column=0, sticky=tk.W)
        self.terminator_var = tk.StringVar(value="CR")
        self.terminator_entry = ttk.Entry(self.frame, textvariable=self.terminator_var)
        self.terminator_entry.grid(row=6, column=1, sticky=(tk.W, tk.E))

        # Data capture options
        self.capture_mode_label = ttk.Label(self.frame, text="Modo de Captura:")
        self.capture_mode_label.grid(row=7, column=0, sticky=tk.W)
        self.capture_mode_var = tk.StringVar(value="Todo")
        self.capture_mode_dropdown = ttk.Combobox(self.frame, textvariable=self.capture_mode_var, values=["Todo", "Números"])
        self.capture_mode_dropdown.grid(row=7, column=1, sticky=(tk.W, tk.E))

        self.start_button = ttk.Button(self.frame, text="Iniciar", command=self.start_reading)
        self.start_button.grid(row=8, column=0)

        self.about_button = ttk.Button(self.frame, text="Desarrollado por", command=self.show_designer_info)
        self.about_button.grid(row=8, column=1)

        self.exit_button = ttk.Button(self.frame, text="Salir", command=self.quit_from_tray)
        self.exit_button.grid(row=8, column=2)

        self.auto_start_var = tk.BooleanVar()
        self.auto_start_check = ttk.Checkbutton(self.frame, text="Iniciar automáticamente con Windows",
                                                variable=self.auto_start_var, command=self.toggle_auto_start)
        self.auto_start_check.grid(row=9, column=1, sticky=tk.W)
        self.check_auto_start()

        self.master.protocol("WM_DELETE_WINDOW", self.hide_window)

    def refresh_ports(self):
        ports = self.serial_comm.get_available_ports()
        self.com_dropdown['values'] = ports if ports else ["No disponible"]
        if ports:
            self.com_dropdown.current(0)

    def start_reading(self):
        # Close the port if it's already open
        if self.serial_comm.serial_port and self.serial_comm.serial_port.is_open:
            self.serial_comm.serial_port.close()

        port_name = self.com_var.get()
        baud_rate = int(self.baud_rate_var.get())
        parity = self.parity_var.get()
        length = int(self.length_var.get())
        stop_bit = int(self.stop_bit_var.get())
        terminator = self.terminator_var.get()
        capture_all = self.capture_mode_var.get() == "Todo"

        self.serial_comm.start_reading(port_name, baud_rate, parity, length, stop_bit, terminator, capture_all)
        self.hide_window()  # Minimize to tray after starting data capture

    def show_designer_info(self):
        top = Toplevel(self.master)
        top.title("Desarrollado por")
        top.geometry("300x300")
        designer_image = Image.open("assets/logo13Cuadrado.png")
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
        self.auto_start_manager.toggle_auto_start(self.auto_start_var.get())

    def check_auto_start(self):
        self.auto_start_var.set(self.auto_start_manager.check_auto_start())