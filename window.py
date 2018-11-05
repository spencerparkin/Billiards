# window.py

from PyQt5 import QtGui, QtCore, QtWidgets

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Billiards')
        
        from canvas import Canvas
        self.canvas = Canvas(self)
        
        self.setCentralWidget(self.canvas)