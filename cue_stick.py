# cue_stick.py

import math

from math2d_vector import Vector
from OpenGL.GL import *

class CueStick(object):
    def __init__(self):
        self.angle = math.pi
        self.speed = 10.0
    
    def rotate(self, delta_angle):
        self.angle += delta_angle

    def adjust_speed(self, delta):
        self.speed += delta
        min_speed = 0.1
        max_speed = 10.0
        if self.speed < min_speed:
            self.speed = min_speed
        elif self.speed > max_speed:
            self.speed = max_speed
    
    def calc_velocity(self):
        return Vector(radius=self.speed, angle=self.angle)

    def draw(self, cue_ball):
        glColor3f(1.0, 1.0, 1.0)
        velocity = self.calc_velocity()
        velocity *= 0.1
        velocity.Render(cue_ball.position, arrow_head_length=0.05)