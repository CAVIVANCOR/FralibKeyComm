import serial
import serial.tools.list_ports
import threading
import time
import re
import pyautogui

class SerialCommunication:
    def __init__(self):
        self.serial_port = None

    def get_available_ports(self):
        return [port.device for port in serial.tools.list_ports.comports()]

    def start_reading(self, port_name, baud_rate, parity, length, stop_bit, terminator, capture_all, decimal_separator='.'):
        try:
            self.close_port()
            self.serial_port = serial.Serial(port_name, baud_rate, bytesize=length, parity=parity, stopbits=stop_bit, timeout=1)
            self.serial_port.flushInput()
            time.sleep(1)
            thread = threading.Thread(target=self.read_from_port, args=(port_name, baud_rate, parity, length, stop_bit, terminator, capture_all, decimal_separator))
            thread.daemon = True
            thread.start()
        except serial.SerialException as e:
            print("Error al abrir el puerto serial: ", e)
            # Intenta reiniciar el puerto serial
            self.close_port()
            time.sleep(1)
            try:
                self.serial_port = serial.Serial(port_name, baud_rate, bytesize=length, parity=parity, stopbits=stop_bit, timeout=1)
                self.serial_port.flushInput()
                time.sleep(10)
                thread = threading.Thread(target=self.read_from_port, args=(port_name, baud_rate, parity, length, stop_bit, terminator, capture_all, decimal_separator))
                thread.daemon = True
                thread.start()
            except serial.SerialException as e:
                print("Error al reiniciar el puerto serial: ", e)

    def read_from_port(self, port_name, baud_rate, parity, length, stop_bit, terminator, capture_all, decimal_separator):
        try:
            last_data = None
            parity_map = {'N': serial.PARITY_NONE, 'E': serial.PARITY_EVEN, 'O': serial.PARITY_ODD}
            while True:
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
            print("Error al leer del puerto serial: ", e)
        finally:
            self.close_port()

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
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

    def is_valid_number(self, data, decimal_separator):
        if decimal_separator == ',':
            data = data.replace(',', '.')
        try:
            float(data)
            return True
        except ValueError:
            return False