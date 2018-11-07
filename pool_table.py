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
        
        self.max_advance_distance = ball_radius
        self.friction = 0.995
    
    def find_cue_ball(self):
        return self.ball_list[self.find_ball(0)]
    
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
        
        ball_8 = self.ball_list.pop(self.find_ball(8))
        random.shuffle(self.ball_list)
        self.ball_list.insert(0, ball_8)
        
        j = 0
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
            ball.render()
    
    def _calc_max_speed(self):
        max_speed = 0.0
        for ball in self.ball_list:
            speed = ball.velocity.Length()
            if speed > max_speed:
                max_speed = speed
        return max_speed
    
    def is_settled(self, epsilon=1e-2):
        max_speed = self._calc_max_speed()
        return True if max_speed < epsilon else False
    
    def advance_simulation(self, elapsed_time):
    
        # To prevent tunnelling, we need to know how fast the fastest ball is moving,
        # and then only let the simulation advance in steps where the fastest ball does
        # not move further than a certain distance at each of those steps.
        max_speed = self._calc_max_speed()
        
        max_distance = max_speed * elapsed_time
        if max_distance > self.max_advance_distance:
            time_step = self.max_advance_distance / max_speed
        else:
            time_step = elapsed_time
        
        while elapsed_time > 0.0:
            delta_time = time_step if time_step < elapsed_time else elapsed_time
            self._advance_balls(delta_time)
            elapsed_time -= delta_time
    
    def _advance_balls(self, delta_time):
        # We begin with the assumption that no ball is in collision with any other, or any bumper.
        # After moving all the balls, we then are going to check for collisions.
        # To simplify matters, we're not going to try to calculate the exact time of impact.
        # We're going to approximate the time of impact and the contact normal.
        # After this call, nothing should be in collision with anything else.
        
        # Move all the balls.
        for ball in self.ball_list:
            ball.position += ball.velocity * delta_time
        
        # Go find and resolve all collisions.
        while True:
            ball_a, ball_b = self._find_random_ball_with_ball_collision()
            if ball_a is not None and ball_b is not None:
                self._resolve_ball_with_ball_collision(ball_a, ball_b)
                continue
            
            ball, contact_point, contact_normal = self._find_random_ball_with_bumper_collision()
            if ball is not None:
                self._resolve_ball_with_bumper_collision(ball, contact_point, contact_normal)
                continue
            
            break
        
        # TODO: If a ball goes in a pocket, we can remove it from our list.
        
        # Lastly, simulate friction with a simple scale.
        for ball in self.ball_list:
            ball.velocity *= self.friction
    
    def _find_random_ball_with_bumper_collision(self, epsilon=1e-7):
        random.shuffle(self.ball_list)
        for ball in self.ball_list:
            contact_segment_list = []
            for segment in self.segment_list:
                if segment.Distance(ball.position) < ball.radius - epsilon:
                    contact_segment_list.append(segment)
            if len(contact_segment_list) > 0:
                contact_normal = Vector(0.0, 0.0)
                contact_point = Vector(0.0, 0.0)
                for segment in contact_segment_list:
                    contact_normal += (segment.point_b - segment.point_a).RotatedCCW90().Normalized()
                    contact_point += segment.ClosestPoint(ball.position)
                contact_normal.Normalize()
                contact_point.Scale(1.0 / float(len(contact_segment_list)))
                return ball, contact_point, contact_normal
        return None, None, None
    
    def _resolve_ball_with_bumper_collision(self, ball, contact_point, contact_normal):
        ball.velocity = ball.velocity - contact_normal * 2.0 * ball.velocity.Dot(contact_normal)
        ball.position = ball.position + contact_normal * (ball.radius - (ball.position - contact_point).Length())
    
    def _find_random_ball_with_ball_collision(self, epsilon=1e-7):
        random.shuffle(self.ball_list)
        for i in range(len(self.ball_list)):
            ball_a = self.ball_list[i]
            for j in range(i + 1, len(self.ball_list)):
                ball_b = self.ball_list[j]
                if (ball_a.position - ball_b.position).Length() < ball_a.radius + ball_b.radius - epsilon:
                    return ball_a, ball_b
        return None, None
    
    def _resolve_ball_with_ball_collision(self, ball_a, ball_b):
        contact_normal = ball_b.position - ball_a.position
        contact_normal.Normalize()
        
        total_mass = ball_a.mass + ball_b.mass
        
        b_dot_n = ball_b.velocity.Dot(contact_normal)
        a_dot_n = ball_a.velocity.Dot(contact_normal)
        
        scale = 2.0 * ball_b.mass / total_mass * b_dot_n
        scale += (((ball_a.mass - ball_b.mass) / total_mass) - 1.0) * a_dot_n
        new_velocity_a = ball_a.velocity + contact_normal * scale
        
        scale = 2.0 * ball_a.mass / total_mass * a_dot_n
        scale += (((ball_b.mass - ball_a.mass) / total_mass) - 1.0) * b_dot_n
        new_velocity_b = ball_b.velocity + contact_normal * scale
        
        ball_a.velocity = new_velocity_a
        ball_b.velocity = new_velocity_b

        translate = contact_normal * ((ball_a.radius + ball_b.radius - (ball_b.position - ball_a.position).Length()) / 2.0)
        
        ball_a.position -= translate
        ball_b.position += translate