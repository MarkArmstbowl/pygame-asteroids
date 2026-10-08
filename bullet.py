"""Bullets fired by the player's spaceship."""

import math

import pygame

from settings import (
    BULLET_LIFETIME,
    BULLET_SPEED,
    CYAN,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WHITE,
)


class Bullet:
    """A bullet that moves straight ahead until its time runs out."""

    def __init__(self, x, y, angle, ship_velocity_x, ship_velocity_y):
        self.x = x
        self.y = y
        # Aim along the ship's angle and add the ship's current movement.
        angle_radians = math.radians(angle)
        self.velocity_x = (
            math.sin(angle_radians) * BULLET_SPEED + ship_velocity_x
        )
        self.velocity_y = (
            -math.cos(angle_radians) * BULLET_SPEED + ship_velocity_y
        )
        self.life_remaining = BULLET_LIFETIME

    def update(self, delta_time):
        """Move the bullet and reduce the time it has left."""
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time
        self.life_remaining -= delta_time

        # Reappear on the other side after crossing a screen edge.
        self.x %= SCREEN_WIDTH
        self.y %= SCREEN_HEIGHT

    def is_alive(self):
        """Check whether the bullet still has time left."""
        return self.life_remaining > 0

    def draw(self, screen):
        """Draw a bright center with a small cyan glow."""
        position = (round(self.x), round(self.y))
        pygame.draw.circle(screen, CYAN, position, 5, 1)
        pygame.draw.circle(screen, WHITE, position, 2)
