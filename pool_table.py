# pool_table.py

import math
import random

from ball import Ball
from OpenGL.GL import *
from math2d_vector import Vector
from math2d_line_segment import LineSegment
from math2d_aa_rect import AxisAlignedRectangle
from math2d_polygon import Polygon

class PoolTable(object):
    def __init__(self, pocket_radius, ball_radius=None):
        self._recalculate_geometry(pocket_radius)
        
        if ball_radius is None:
            ball_radius = pocket_radius / 2.0
        
        self.ball_list = []
        for i in range(0, 16):
            mass = 0.17 if i == 0 else 0.16
            ball = Ball(ball_radius, mass, i)
            self.ball_list.append(ball)
        
        self.reset_balls()
    
    def find_ball(self, number):
        for i in range(len(self.ball_list)):
            ball = self.ball_list[i]
            if ball.number == number:
                return i
    
    def yield_rack_positions(self):
        translate = Vector(-1.3, 0.0)
        
        max_radius = 0.0
        for i in range(len(self.ball_list)):
            ball = self.ball_list[i]
            if ball.radius > max_radius and ball.number != 0:
                max_radius = ball.radius
        
        radius = max_radius / math.cos(math.pi / 6.0)
        for i in range(0, 3):
            angle = 2.0 * math.pi * (float(i) / 3.0)
            yield Vector(radius * math.cos(angle), radius * math.sin(angle)) + translate
        
        position_list = []
        radius *= 4.0
        for i in range(0, 3):
            angle = 2.0 * math.pi * (float(i) / 3.0)
            position_list.append(Vector(radius * math.cos(angle), radius * math.sin(angle)))
        
        for i in range(0, 3):
            line_segment = LineSegment(position_list[i], position_list[(i + 1) % 3])
            for j in range(0, 4):
                yield line_segment.Lerp(float(j) / 4.0) + translate
    
    def reset_balls(self):
        cue_ball = self.ball_list.pop(self.find_ball(0))
        cue_ball.position = Vector(1.7, 0.0)
        cue_ball.velocity = Vector(0.0, 0.0)
        
        j = 0
        random.shuffle(self.ball_list)
        for rack_position in self.yield_rack_positions():
            ball = self.ball_list[j]
            ball.position = rack_position
            ball.velocity = Vector(0.0, 0.0)
            j += 1
        
        self.ball_list.append(cue_ball)

    def _recalculate_geometry(self, pocket_radius):
        sqrt2 = math.sqrt(2.0)
        offset = pocket_radius * sqrt2
        self.segment_list = [
            LineSegment(Vector(pocket_radius, -1.0 - pocket_radius), Vector(offset, -1.0)),
            LineSegment(Vector(offset, -1.0), Vector(2.0 - offset, -1.0)),
            LineSegment(Vector(2.0 - offset, -1.0), Vector(2.0, -1.0 - offset)),
            
            LineSegment(Vector(2.0 + offset, -1.0), Vector(2.0, -1.0 + offset)),
            LineSegment(Vector(2.0, -1.0 + offset), Vector(2.0, 1.0 - offset)),
            LineSegment(Vector(2.0, 1.0 - offset), Vector(2.0 + offset, 1.0)),
            
            LineSegment(Vector(2.0, 1.0 + offset), Vector(2.0 - offset, 1.0)),
            LineSegment(Vector(2.0 - offset, 1.0), Vector(offset, 1.0)),
            LineSegment(Vector(offset, 1.0), Vector(pocket_radius, 1.0 + pocket_radius)),
            
            LineSegment(Vector(-pocket_radius, 1.0 + pocket_radius), Vector(-offset, 1.0)),
            LineSegment(Vector(-offset, 1.0), Vector(-2.0 + offset, 1.0)),
            LineSegment(Vector(-2.0 + offset, 1.0), Vector(-2.0, 1.0 + offset)),
            
            LineSegment(Vector(-2.0 - offset, 1.0), Vector(-2.0, 1.0 - offset)),
            LineSegment(Vector(-2.0, 1.0 - offset), Vector(-2.0, -1.0 + offset)),
            LineSegment(Vector(-2.0, -1.0 + offset), Vector(-2.0 - offset, -1.0)),
            
            LineSegment(Vector(-2.0, -1.0 - offset), Vector(-2.0 + offset, -1.0)),
            LineSegment(Vector(-2.0 + offset, -1.0), Vector(-offset, -1.0)),
            LineSegment(Vector(-offset, -1.0), Vector(-pocket_radius, -1.0 - pocket_radius))
        ]
        pocket_sides = 12
        offset = pocket_radius / (2.0 * sqrt2)
        self.pocket_list = [
            Polygon().MakeRegularPolygon(pocket_sides, pocket_radius, Vector(2.0 + offset, 1.0 + offset)),
            Polygon().MakeRegularPolygon(pocket_sides, pocket_radius, Vector(0.0, 1.0 + pocket_radius)),
            Polygon().MakeRegularPolygon(pocket_sides, pocket_radius, Vector(-2.0 - offset, 1.0 + offset)),
            Polygon().MakeRegularPolygon(pocket_sides, pocket_radius, Vector(-2.0 - offset, -1.0 - offset)),
            Polygon().MakeRegularPolygon(pocket_sides, pocket_radius, Vector(0.0, -1.0 - pocket_radius)),
            Polygon().MakeRegularPolygon(pocket_sides, pocket_radius, Vector(2.0 + offset, -1.0 - offset))
        ]
        for pocket in self.pocket_list:
            pocket.Tessellate()
        offset = pocket_radius * (1.0 + sqrt2 / 2.0)
        self.border_rect = AxisAlignedRectangle()
        self.border_rect.max_point = Vector(2.0 + offset, 1.0 + offset)
        self.border_rect.min_point = Vector(-2.0 - offset, -1.0 - offset)
    
    def draw(self):
        
        # Draw the bumpers.
        glBegin(GL_LINES)
        try:
            glColor3f(1.0, 1.0, 1.0)
            for segment in self.segment_list:
                glVertex2f(segment.point_a.x, segment.point_a.y)
                glVertex2f(segment.point_b.x, segment.point_b.y)
        finally:
            glEnd()
        
        # Draw the pockets.
        glColor3f(0.5, 0.5, 0.5)
        for pocket in self.pocket_list:
            pocket.mesh.Render()
        
        # Draw the balls.
        for ball in self.ball_list:
            ball.render(wire_frame=True)