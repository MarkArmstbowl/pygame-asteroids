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
    """A small projectile that travels in a straight line."""

    def __init__(self, x, y, angle, ship_velocity_x, ship_velocity_y):
        self.x = x
        self.y = y
        angle_radians = math.radians(angle)
        self.velocity_x = (
            math.sin(angle_radians) * BULLET_SPEED + ship_velocity_x
        )
        self.velocity_y = (
            -math.cos(angle_radians) * BULLET_SPEED + ship_velocity_y
        )
        self.life_remaining = BULLET_LIFETIME

    def update(self, delta_time):
        """Move the bullet, wrap it, and reduce its remaining lifetime."""
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time
        self.life_remaining -= delta_time

        # Classic Asteroids objects reappear at the opposite screen edge.
        self.x %= SCREEN_WIDTH
        self.y %= SCREEN_HEIGHT

    def is_alive(self):
        """Return True until the bullet's short lifetime ends."""
        return self.life_remaining > 0

    def draw(self, screen):
        """Draw a bright center with a small cyan glow."""
        position = (round(self.x), round(self.y))
        pygame.draw.circle(screen, CYAN, position, 5, 1)
        pygame.draw.circle(screen, WHITE, position, 2)
