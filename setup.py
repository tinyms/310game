__author__ = 'tinyms'

import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
        name = "WaterPress",
        version = "3.2",
        description = "WaterPress for football match",
        options = {"build_exe" : {"includes" : ["PyQt5.QtWebKitWidgets","PyQt5.QtNetwork"] }},
        executables = [Executable("Main.py", base = base)])
