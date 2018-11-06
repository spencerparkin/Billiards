# pool_table.py

import math

from OpenGL.GL import *
from math2d_vector import Vector
from math2d_line_segment import LineSegment
from math2d_aa_rect import AxisAlignedRectangle
from math2d_polygon import Polygon

class PoolTable(object):
    def __init__(self, pocket_radius):
        self._recalculate_geometry(pocket_radius)

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
        glBegin(GL_LINES)
        try:
            glColor3f(1.0, 1.0, 1.0)
            for segment in self.segment_list:
                glVertex2f(segment.point_a.x, segment.point_a.y)
                glVertex2f(segment.point_b.x, segment.point_b.y)
        finally:
            glEnd()
        glColor3f(0.5, 0.5, 0.5)
        for pocket in self.pocket_list:
            pocket.mesh.Render()