# ball.py

import math

from math2d_vector import Vector
from OpenGL.GL import *
from OpenGL.GLU import *

class Ball(object):
    def __init__(self, radius, mass, number):
        self.position = Vector(0.0, 0.0)
        self.velocity = Vector(0.0, 0.0)
        self.radius = radius
        self.mass = mass
        self.number = number
        self.texture = None
    
    def load_texture(self):
        try:
            image = None
            
            from PIL import Image
            import numpy
            
            image_file = 'Textures/ball_%d.png' % self.number
            image = Image.open(image_file).transpose(Image.FLIP_TOP_BOTTOM)
            image_data = numpy.fromstring(image.tobytes(), numpy.uint8)
            
            self.texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            #glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.size[0], image.size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

            gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, image.size[0], image.size[1], GL_RGBA, GL_UNSIGNED_BYTE, image_data)
            
        except Exception as ex:
            error = str(ex)
            
            self.texture = None
        finally:
            if image is not None:
                image.close()
        
    def render(self, wire_frame=False):
        if wire_frame or self.texture is None:
            glBegin(GL_LINE_LOOP)
            try:
                sides = 12
                for i in range(sides):
                    angle = 2.0 * math.pi * (float(i) / float(sides))
                    glVertex2f(self.position.x + self.radius * math.cos(angle), self.position.y + self.radius * math.sin(angle))
            finally:
                glEnd()
        else:
            glColor3f(1.0, 1.0, 1.0)
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            glBegin(GL_QUADS)
            try:
                glTexCoord2f(0.0, 0.0)
                glVertex2f(self.position.x - self.radius, self.position.y - self.radius)
                
                glTexCoord2f(1.0, 0.0)
                glVertex2f(self.position.x + self.radius, self.position.y - self.radius)
                
                glTexCoord2f(1.0, 1.0)
                glVertex2f(self.position.x + self.radius, self.position.y + self.radius)
                
                glTexCoord2f(0.0, 1.0)
                glVertex2f(self.position.x - self.radius, self.position.y + self.radius)
            finally:
                glEnd()
                glDisable(GL_TEXTURE_2D)