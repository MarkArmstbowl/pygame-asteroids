"""Moving background stars for the game screens."""

import pygame

from settings import SCREEN_HEIGHT, SCREEN_WIDTH


class Star:
    """A background star that drifts and wraps around the screen."""

    def __init__(self, x_position, y_position, speed, radius, brightness):
        self.x = x_position
        self.y = y_position
        self.speed = speed
        self.radius = radius
        self.color = (brightness, brightness, brightness)

    def update(self, delta_time):
        """Move the star slowly down and slightly to the left."""
        self.x -= self.speed * 0.12 * delta_time
        self.y += self.speed * delta_time

        if self.y > SCREEN_HEIGHT:
            self.y = 0
        if self.x < 0:
            self.x = SCREEN_WIDTH

    def draw(self, screen):
        """Draw the star at its current position."""
        position = (round(self.x), round(self.y))
        pygame.draw.circle(screen, self.color, position, self.radius)
