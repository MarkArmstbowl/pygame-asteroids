"""Small moving dots for trails and explosions."""

import pygame


class Particle:
    """A colored dot that moves, fades, and disappears."""

    def __init__(self, position, velocity, color, radius, lifetime):
        self.x, self.y = position
        self.velocity_x, self.velocity_y = velocity
        self.color = color
        self.radius = radius
        self.life_remaining = lifetime
        self.starting_life = lifetime

    def update(self, delta_time):
        """Move the dot and count down its remaining time."""
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time
        self.life_remaining -= delta_time

        # Slow the dot down a little as it moves.
        drag = 0.97 ** (delta_time * 60)
        self.velocity_x *= drag
        self.velocity_y *= drag

    def is_alive(self):
        """Check whether the dot still has time left."""
        return self.life_remaining > 0

    def draw(self, screen):
        """Make the dot smaller and dimmer as its time runs out."""
        # Use the time left to work out its color and size.
        life_amount = max(0, self.life_remaining / self.starting_life)
        faded_color = tuple(
            round(color_value * life_amount)
            for color_value in self.color
        )
        draw_radius = max(1, round(self.radius * life_amount))
        position = (round(self.x), round(self.y))
        pygame.draw.circle(screen, faded_color, position, draw_radius)
