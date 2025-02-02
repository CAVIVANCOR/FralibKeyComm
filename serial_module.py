import serial
import serial.tools.list_ports
import threading
import time
import re
import pyautogui
import tkinter as tk
from tkinter import messagebox

class SerialCommunication:
    def __init__(self):
        self.serial_port = None
        self.running = False  # Bandera para controlar el bucle
        self.read_thread = None  # Para manejar el hilo de lectura

    def get_available_ports(self):
        return [port.device for port in serial.tools.list_ports.comports()]

    def start_reading(self, port_name, baud_rate, parity, length, stop_bit, terminator, capture_all, decimal_separator):
        try:
            # Cerrar puerto si estaba abierto
            if self.serial_port and self.serial_port.is_open:
                self.close_port()
                time.sleep(0.5)  # Esperar un momento para asegurar el cierre

            # Verificar si el puerto ya estaba en uso
            if self.serial_port and self.serial_port.is_open:
                messagebox.showerror("Error", f"El puerto {port_name} ya está en uso")
                return

            # Configurar puerto serial
            self.serial_port = serial.Serial(
                port=port_name,
                baudrate=baud_rate,
                bytesize=length,
                parity=parity,
                stopbits=stop_bit,
                timeout=1
            )

            # Limpiar buffers
            self.serial_port.flushInput()
            self.serial_port.flushOutput()
            time.sleep(0.5)  # Esperar un momento para asegurar la configuración

            # Iniciar hilo de lectura
            self.running = True
            self.read_thread = threading.Thread(
                target=self.read_from_port,
                args=(port_name, baud_rate, parity, length, stop_bit, terminator, capture_all, decimal_separator)
            )
            self.read_thread.daemon = True
            self.read_thread.start()

            # Mensaje de éxito
            messagebox.showinfo("Éxito", f"Puerto {port_name} abierto correctamente")

        except serial.SerialException as e:
            print(f"Error al abrir el puerto serial: {e}")
            self.close_port()
            messagebox.showerror("Error de puerto serial", f"No se pudo abrir el puerto {port_name}. Verifique los permisos y que no esté en uso por otra aplicación.")
            return

    def read_from_port(self, port_name, baud_rate, parity, length, stop_bit, terminator, capture_all, decimal_separator):
        try:
            last_data = None
            parity_map = {'N': serial.PARITY_NONE, 'E': serial.PARITY_EVEN, 'O': serial.PARITY_ODD}
            
            while self.running:
                if self.serial_port.in_waiting > 0:
                    serial_data = self.serial_port.readline().decode('utf-8').rstrip()
                    if terminator == 'CR':
                        serial_data = serial_data.replace('\r', '')
                    
                    if capture_all:
                        if serial_data != last_data:
                            self.send_data(serial_data)
                            last_data = serial_data
                    else:
                        number = self.extract_number(serial_data, decimal_separator)
                        if number and number != last_data:
                            self.send_data(number)
                            last_data = number
        except serial.SerialException as e:
            print(f"Se Detuvo la Comunicacion Serial: Error al leer del puerto serial: {e}")
            self.close_port()
            # messagebox.showerror("Se Detuvo la Comunicacion Serial", f"Error de puerto serial", f"Error al leer del puerto {port_name}: {e}")
        finally:
            self.close_port()
            self.running = False
    def extract_number(self, data, decimal_separator):
        if decimal_separator == ',':
            data = data.replace(',', '.')
        match = re.search(r'-?\d+(\.\d+)?', data)
        return match.group(0) if match else None

    def send_data(self, data):
        pyautogui.typewrite(data)
        pyautogui.typewrite('\n')
        print("Datos enviados a la aplicación activa: ", data)

    def close_port(self):
        try:
            if self.serial_port and self.serial_port.is_open:
                # Limpiar buffers antes de cerrar
                self.serial_port.flushInput()
                self.serial_port.flushOutput()
                self.serial_port.close()
                print(f"Puerto serial {self.serial_port.port} cerrado correctamente")
        except Exception as e:
            print(f"Error al cerrar el puerto serial: {e}")

    def is_valid_number(self, data, decimal_separator):
        if decimal_separator == ',':
            data = data.replace(',', '.')
        try:
            float(data)
            return True
        except ValueError:
            return False