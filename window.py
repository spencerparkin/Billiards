# window.py

from PyQt5 import QtGui, QtCore, QtWidgets

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Billiards')
        
        from canvas import Canvas
        self.canvas = Canvas(self)
        
        self.setCentralWidget(self.canvas)
        
        self.key_map = {}
    
    def is_key_down(self, key):
        return self.key_map.get(key, False)
    
    def keyPressEvent(self, event):
        key = event.key()
        self.key_map[key] = True
        self.canvas.key_strike(event.key())
    
    def keyReleaseEvent(self, event):
        key = event.key()
        self.key_map[key] = False