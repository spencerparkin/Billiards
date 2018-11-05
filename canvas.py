# canvas.py

from PyQt5 import QtGui, QtCore, QtWidgets, QtOpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from math2d_aa_rect import AxisAlignedRectangle

class Canvas(QtOpenGL.QGLWidget):
    def __init__(self, parent):
        gl_format = QtOpenGL.QGLFormat()
        gl_format.setAlpha(True)
        gl_format.setDepth(False)
        gl_format.setDoubleBuffer(True)

        super().__init__(gl_format, parent)
        
        from pool_table import PoolTable
        self.pool_table = PoolTable(1.0 / 9.0)
    
    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        
    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)

        viewport = glGetIntegerv(GL_VIEWPORT)
        viewport_rect = AxisAlignedRectangle()
        viewport_rect.min_point.x = 0.0
        viewport_rect.min_point.y = 0.0
        viewport_rect.max_point.x = float(viewport[2])
        viewport_rect.max_point.y = float(viewport[3])
        
        proj_rect = self.pool_table.border_rect.Clone()
        proj_rect.ExpandToMatchAspectRatioOf(viewport_rect)
        proj_rect.Scale(1.1)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(proj_rect.min_point.x, proj_rect.max_point.x, proj_rect.min_point.y, proj_rect.max_point.y)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        self.pool_table.draw()
        
        glFlush()