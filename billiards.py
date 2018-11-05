# billiards.py

import sys
import traceback

sys.path.append(r'C:\dev\pyMath2D')

from PyQt5 import QtGui, QtWidgets

def exception_hook(cls, exc, tb):
    sys.__excepthook__(cls, exc, tb)

if __name__ == '__main__':
    sys.excepthook = exception_hook

    try:
        app = QtWidgets.QApplication(sys.argv)

        from window import Window

        win = Window()
        win.resize(1000, 800)
        win.show()

        sys.exit(app.exec_())

    except Exception as ex:
        ex_type, ex, tb = sys.exc_info()
        traceback.print_tb(tb)
        error = str(ex)
        print('ERROR: ' + error)