__author__ = 'tinyms'

import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="WaterPress",
    version="1.0",
    description="WaterPress for football match game",
    options={"build_exe": {"includes": ["sip","PyQt5.QtCore","PyQt5.QtGui","psycopg2._psycopg",
                                        "PyQt5.QtWidgets","PyQt5.QtNetwork","PyQt5.QtOpenGL",
                                        "PyQt5.QtWebKit","PyQt5.QtPrintSupport","PyQt5.QtXmlPatterns",
                                        "PyQt5.QtWebKitWidgets"
                                        ]}},
    executables=[Executable(script="Main.py",
                            targetName="WaterPress.exe",
                            icon= "images/ball.ico",
                            base=base)])
