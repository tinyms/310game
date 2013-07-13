__author__ = 'tinyms'
import sys
from PyQt5 import QtWidgets
from WaterPress import Workbench
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Workbench()
    window.show()
    sys.exit(app.exec_())