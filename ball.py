# ball.py

import math

from math2d_vector import Vector
from OpenGL.GL import *

class Ball(object):
    def __init__(self, radius, mass, number):
        self.position = Vector(0.0, 0.0)
        self.velocity = Vector(0.0, 0.0)
        self.radius = radius
        self.mass = mass
        self.number = number
        
    def render(self, wire_frame=False):
        if wire_frame:
            glBegin(GL_LINE_LOOP)
            try:
                sides = 12
                for i in range(sides):
                    angle = 2.0 * math.pi * (float(i) / float(sides))
                    glVertex2f(self.position.x + self.radius * math.cos(angle), self.position.y + self.radius * math.sin(angle))
            finally:
                glEnd()
        else:
            pass # TODO: Draw textured quad.