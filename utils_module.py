# utils_module.py
import os
import sys
import win32com.client

class AutoStartManager:
    def toggle_auto_start(self, enable):
        startup_path = os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup')
        shortcut_path = os.path.join(startup_path, 'SerialApp.lnk')
        if enable:
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
        return os.path.exists(shortcut_path)