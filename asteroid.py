"""Moving and splitting asteroids."""

import math
import random

import pygame

from settings import (
    ASTEROID_FILL,
    ASTEROID_OUTLINE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


class Asteroid:
    """A rock with its own shape, speed, and direction."""

    # Size 3 is large, size 2 is medium, and size 1 is small.
    RADII = {3: 48, 2: 31, 1: 18}

    def __init__(self, x, y, speed, size=3, direction=None):
        self.x = x
        self.y = y
        self.size = size
        self.radius = self.RADII[size]

        # New rocks get a random direction; fragments use their given one.
        if direction is None:
            direction = random.uniform(0, math.tau)

        self.velocity_x = math.cos(direction) * speed
        self.velocity_y = math.sin(direction) * speed
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-55, 55)
        self.shape = self.make_shape()

    def make_shape(self):
        """Make uneven points around the rock's edge."""
        points = []
        point_count = random.randint(9, 12)

        for index in range(point_count):
            angle = math.tau * index / point_count
            distance = self.radius * random.uniform(0.78, 1.15)
            points.append((angle, distance))

        return points

    def update(self, delta_time):
        """Move and rotate the rock, then check the screen edges."""
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time
        self.rotation += self.rotation_speed * delta_time
        self.wrap_around_screen()

    def wrap_around_screen(self):
        """Move the asteroid to the opposite edge of the screen."""
        # Allow extra space beyond each edge based on the rock's radius.
        margin = self.radius

        if self.x < -margin:
            self.x = SCREEN_WIDTH + margin
        elif self.x > SCREEN_WIDTH + margin:
            self.x = -margin

        if self.y < -margin:
            self.y = SCREEN_HEIGHT + margin
        elif self.y > SCREEN_HEIGHT + margin:
            self.y = -margin

    def get_draw_points(self):
        """Find the rock's screen points after rotating it."""
        rotation_radians = math.radians(self.rotation)
        draw_points = []

        for angle, distance in self.shape:
            final_angle = angle + rotation_radians
            point_x = self.x + math.cos(final_angle) * distance
            point_y = self.y + math.sin(final_angle) * distance
            draw_points.append((point_x, point_y))

        return draw_points

    def split(self):
        """Split a large or medium rock into two smaller rocks."""
        # Small rocks disappear instead of splitting again.
        if self.size == 1:
            return []

        current_direction = math.atan2(self.velocity_y, self.velocity_x)
        current_speed = math.hypot(self.velocity_x, self.velocity_y)
        fragments = []

        # Send the two faster fragments in slightly different directions.
        for angle_change in (-0.65, 0.65):
            fragment = Asteroid(
                self.x,
                self.y,
                current_speed * 1.2,
                self.size - 1,
                current_direction + angle_change
            )
            fragments.append(fragment)

        return fragments

    def draw(self, screen):
        """Draw the rock with a fill color and an outline."""
        points = self.get_draw_points()
        pygame.draw.polygon(screen, ASTEROID_FILL, points)
        pygame.draw.polygon(screen, ASTEROID_OUTLINE, points, 2)
