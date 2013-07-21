__author__ = 'tinyms'

import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
        name = "310game",
        version = "1.0",
        description = "310game web app",
        #options = {"build_exe" : {"includes" : ["PyQt5.QtWebKitWidgets","PyQt5.QtNetwork"] }},
        executables = [Executable("web/server.py", base = base)])
