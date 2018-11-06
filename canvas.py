# canvas.py

import time

from PyQt5 import QtGui, QtCore, QtWidgets, QtOpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from math2d_aa_rect import AxisAlignedRectangle
from math2d_text import TextRenderer
from pool_table import PoolTable

class Canvas(QtOpenGL.QGLWidget):
    def __init__(self, parent):
        gl_format = QtOpenGL.QGLFormat()
        gl_format.setAlpha(True)
        gl_format.setDepth(False)
        gl_format.setDoubleBuffer(True)

        super().__init__(gl_format, parent)
        
        self.pool_table = PoolTable(1.0 / 9.0)
        
        self.animation_timer = QtCore.QTimer()
        self.animation_timer.start(1)
        self.animation_timer.timeout.connect(self.animation_step)
        
        self.last_render_time = time.time()
        self.last_animation_time = time.time()
        self.frame_count = 0
        self.fps_text = ''
        self.text_renderer = TextRenderer()
    
    def initializeGL(self):
        glClearColor(0.0, 0.4, 0.0, 0.0)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        for ball in self.pool_table.ball_list:
            ball.load_texture()
        
    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        
    def paintGL(self):
        
        current_render_time = time.time()
        elapsed_time = current_render_time - self.last_render_time
        self.last_render_time = current_render_time
        frames_per_second = 1.0 / elapsed_time
        
        glClear(GL_COLOR_BUFFER_BIT)

        viewport = glGetIntegerv(GL_VIEWPORT)
        viewport_rect = AxisAlignedRectangle()
        viewport_rect.min_point.x = 0.0
        viewport_rect.min_point.y = 0.0
        viewport_rect.max_point.x = float(viewport[2])
        viewport_rect.max_point.y = float(viewport[3])
        
        proj_rect = self.pool_table.border_rect.Copy()
        proj_rect.ExpandToMatchAspectRatioOf(viewport_rect)
        proj_rect.Scale(1.1)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(proj_rect.min_point.x, proj_rect.max_point.x, proj_rect.min_point.y, proj_rect.max_point.y)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        self.pool_table.draw()
        
        self.frame_count += 1
        if self.frame_count % 10 == 0:
            self.fps_text = 'FPS: %1.2f' % frames_per_second
        rect = proj_rect.Copy()
        rect.max_point.y = rect.min_point.y + (rect.max_point.y - rect.min_point.y) * 0.05
        self.text_renderer.render_text(self.fps_text, rect)
        
        glFlush()
    
    def animation_step(self):
        
        current_animation_time = time.time()
        elapsed_time = current_animation_time - self.last_animation_time
        self.last_animation_time = current_animation_time
        
        self.pool_table.advance_simulation(elapsed_time)
        
        self.update()
    
    def mousePressEvent(self, event):
        i = self.pool_table.find_ball(0)
        cue_ball = self.pool_table.ball_list[i]
        cue_ball.velocity.x = -10.0