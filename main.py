import tkinter as tk
from ui_module import SerialAppUI
from serial_module import SerialCommunication
from utils_module import AutoStartManager

def main():
    root = tk.Tk()
    serial_comm = SerialCommunication()
    auto_start_manager = AutoStartManager()
    app_ui = SerialAppUI(root, serial_comm, auto_start_manager)
    root.mainloop()

if __name__ == "__main__":
    main()