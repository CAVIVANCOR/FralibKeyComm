import os
import sys
import logging
from datetime import datetime
import win32com.client
from tkinter import messagebox
from parametros_serial import save_config, load_config
def setup_logging():
    log_file = os.path.join(os.path.dirname(sys.executable), 'SerialApp_startup.log')
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return log_file

class AutoStartManager:
    def __init__(self):
        self.startup_path = os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup')
        self.shortcut_path = os.path.join(self.startup_path, 'SerialApp.lnk')
        self.log_file = os.path.join(os.path.dirname(sys.executable), 'SerialApp_startup.log')
        
        # Configurar el registro
        logging.basicConfig(
            filename=self.log_file,
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def _save_auto_start_params(self, params):
        save_config(params)

    def _load_auto_start_params(self):
        return load_config()
    def toggle_auto_start(self, enable, params=None):
        try:
            if enable:
                self._create_auto_start()
                self._log_info("Inicio automático habilitado correctamente")
                if params:
                    self._save_auto_start_params(params)
                # messagebox.showinfo("Éxito", "La aplicación se configuró correctamente para iniciar automáticamente.")
            else:
                self._remove_auto_start()
                self._log_info("Inicio automático deshabilitado correctamente")
                messagebox.showinfo("Éxito", "La aplicación ya no iniciará automáticamente.")
            return True
        except Exception as e:
            error_msg = f"Ocurrió un error al configurar el inicio automático: {str(e)}"
            self._log_error(error_msg)
            messagebox.showerror("Error", error_msg)
            return False

    def check_auto_start(self):
        try:
            if os.path.exists(self.shortcut_path):
                shell = win32com.client.Dispatch('WScript.Shell')
                shortcut = shell.CreateShortcut(self.shortcut_path)
                expected_target = self._get_executable_path()
                
                if shortcut.TargetPath == expected_target:
                    return True
            self._log_warning("Inicio automático no está configurado correctamente")
            return False
        except Exception as e:
            error_msg = f"Ocurrió un error al verificar el inicio automático: {str(e)}"
            self._log_error(error_msg)
            messagebox.showerror("Error", error_msg)
            return False

    def _create_auto_start(self):
        try:
            shell = win32com.client.Dispatch('WScript.Shell')
            shortcut = shell.CreateShortcut(self.shortcut_path)
            shortcut.TargetPath = self._get_executable_path()
            shortcut.WorkingDirectory = os.path.dirname(self._get_executable_path())
            shortcut.IconLocation = self._get_executable_path()
            shortcut.save()
            
            # Verificar si el acceso directo se creó correctamente
            if not os.path.exists(self.shortcut_path):
                raise Exception("No se pudo crear el acceso directo")
            
            self._log_info("Acceso directo creado correctamente")
        except Exception as e:
            self._log_error(f"Error al crear el acceso directo: {str(e)}")
            raise

    def _remove_auto_start(self):
        try:
            if os.path.exists(self.shortcut_path):
                os.remove(self.shortcut_path)
                self._log_info("Acceso directo eliminado correctamente")
        except Exception as e:
            self._log_error(f"Error al eliminar el acceso directo: {str(e)}")
            raise

    def _get_executable_path(self):
        try:
            if getattr(sys, 'frozen', False):
                return sys.executable
            else:
                return os.path.abspath(__file__)
        except Exception as e:
            self._log_error(f"Error al obtener la ruta del ejecutable: {str(e)}")
            raise

    def _log_info(self, message):
        logging.info(message)
        self._write_to_log_file(message, level='INFO')

    def _log_warning(self, message):
        logging.warning(message)
        self._write_to_log_file(message, level='WARNING')

    def _log_error(self, message):
        logging.error(message)
        self._write_to_log_file(message, level='ERROR')

    def _write_to_log_file(self, message, level='INFO'):
        with open(self.log_file, 'a') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] [{level}] {message}\n")
            