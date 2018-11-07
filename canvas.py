# canvas.py

import time
import math

from PyQt5 import QtGui, QtCore, QtWidgets, QtOpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from math2d_aa_rect import AxisAlignedRectangle
from math2d_text import TextRenderer
from math2d_vector import Vector
from pool_table import PoolTable
from cue_stick import CueStick

class Canvas(QtOpenGL.QGLWidget):
    MODE_PLACE_CUE_BALL = 1
    MODE_SHOOT_CUE_BALL = 2
    
    def __init__(self, parent):
        gl_format = QtOpenGL.QGLFormat()
        gl_format.setAlpha(True)
        gl_format.setDepth(False)
        gl_format.setDoubleBuffer(True)

        super().__init__(gl_format, parent)
        
        self.pool_table = None
        
        self.animation_timer = QtCore.QTimer()
        self.animation_timer.start(1)
        self.animation_timer.timeout.connect(self.animation_step)
        
        self.last_render_time = time.time()
        self.last_animation_time = time.time()
        self.frame_count = 0
        self.fps_text = ''
        self.text_renderer = TextRenderer()
        
        self.cue_stick = CueStick()
        
        self.mode = self.MODE_PLACE_CUE_BALL
    
    def initializeGL(self):
        glClearColor(0.0, 0.4, 0.0, 0.0)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        self.pool_table = PoolTable(1.0 / 9.0)
        
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
        
        if self.pool_table.is_settled():
            if self.mode == self.MODE_SHOOT_CUE_BALL:
                cue_ball = self.pool_table.find_cue_ball()
                if cue_ball is not None:
                    self.cue_stick.draw(cue_ball)
            elif self.mode == self.MODE_PLACE_CUE_BALL:
                cue_ball = self.pool_table.find_cue_ball()
                if cue_ball is not None:
                    glColor3f(1.0, 1.0, 1.0)
                    Vector(0.2, 0.0).Render(cue_ball.position, arrow_head_length=0.05)
                    Vector(-0.2, 0.0).Render(cue_ball.position, arrow_head_length=0.05)
                    Vector(0.0, 0.2).Render(cue_ball.position, arrow_head_length=0.05)
                    Vector(0.0, -0.2).Render(cue_ball.position, arrow_head_length=0.05)
        
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

        self._handle_key_presses(elapsed_time)
        
        self.pool_table.advance_simulation(elapsed_time)

        if self.mode == self.MODE_SHOOT_CUE_BALL:
            cue_ball = self.pool_table.find_cue_ball()
            if cue_ball is None:
                self.pool_table.replace_cue_ball()
                self.mode = self.MODE_PLACE_CUE_BALL
        
        self.update()
    
    def key_strike(self, key):
        if self.mode == self.MODE_SHOOT_CUE_BALL:
            if key == QtCore.Qt.Key_Return:
                cue_ball = self.pool_table.find_cue_ball()
                cue_ball.velocity += self.cue_stick.calc_velocity()
        elif self.mode == self.MODE_PLACE_CUE_BALL:
            if key == QtCore.Qt.Key_Return:
                self.mode = self.MODE_SHOOT_CUE_BALL
        if key == QtCore.Qt.Key_Escape:
            self.pool_table.reset_balls()
            self.mode = self.MODE_PLACE_CUE_BALL
    
    def _handle_key_presses(self, elapsed_time):
        window = self.parent()
        if self.pool_table.is_settled():
            if self.mode == self.MODE_SHOOT_CUE_BALL:
                angle_change_speed = math.pi / 5.0
                if window.is_key_down(QtCore.Qt.Key_Shift):
                    angle_change_speed = math.pi / 30.0
                angle_delta = angle_change_speed * elapsed_time
                speed_change_speed = 2.0
                speed_delta = speed_change_speed * elapsed_time
                if window.is_key_down(QtCore.Qt.Key_Left):
                    self.cue_stick.rotate(angle_delta)
                if window.is_key_down(QtCore.Qt.Key_Right):
                    self.cue_stick.rotate(-angle_delta)
                if window.is_key_down(QtCore.Qt.Key_Up):
                    self.cue_stick.adjust_speed(speed_delta)
                if window.is_key_down(QtCore.Qt.Key_Down):
                    self.cue_stick.adjust_speed(-speed_delta)
            elif self.mode == self.MODE_PLACE_CUE_BALL:
                cue_ball = self.pool_table.find_cue_ball()
                move_ball_speed = 0.3
                delta = move_ball_speed * elapsed_time
                if cue_ball is not None:
                    if window.is_key_down(QtCore.Qt.Key_Left):
                        cue_ball.position.x -= delta
                    if window.is_key_down(QtCore.Qt.Key_Right):
                        cue_ball.position.x += delta
                    if window.is_key_down(QtCore.Qt.Key_Down):
                        cue_ball.position.y -= delta
                    if window.is_key_down(QtCore.Qt.Key_Up):
                        cue_ball.position.y += delta