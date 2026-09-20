"""Player spaceship for the Asteroids game."""

import math

import pygame

from settings import (
    CYAN,
    DIRECT_TURN_SPEED,
    ORANGE,
    PLAYER_BRAKE,
    PLAYER_DRAG,
    PLAYER_INVULNERABLE_TIME,
    PLAYER_MAX_SPEED,
    PLAYER_THRUST,
    PLAYER_TURN_SPEED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WHITE,
)


class Player:
    """A spaceship controlled with the keyboard arrow keys."""

    def __init__(self):
        self.x = SCREEN_WIDTH / 2
        self.y = SCREEN_HEIGHT / 2
        self.velocity_x = 0
        self.velocity_y = 0
        self.angle = 0
        self.thrusting = False
        self.shot_timer = 0
        self.invulnerable_timer = 0

    def reset_position(self):
        """Move the ship to the center after losing a life."""
        self.x = SCREEN_WIDTH / 2
        self.y = SCREEN_HEIGHT / 2
        self.velocity_x = 0
        self.velocity_y = 0
        self.angle = 0
        self.invulnerable_timer = PLAYER_INVULNERABLE_TIME

    def update(self, keys, delta_time, control_mode="classic"):
        """Turn, accelerate, and move the spaceship."""
        if control_mode == "direct":
            self.update_direct_controls(keys, delta_time)
        else:
            self.update_classic_controls(keys, delta_time)

        # Drag slows the ship gently when the engine is not accelerating it.
        drag = PLAYER_DRAG ** (delta_time * 60)
        self.velocity_x *= drag
        self.velocity_y *= drag
        self.limit_speed()

        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time
        self.wrap_around_screen()

        self.shot_timer = max(0, self.shot_timer - delta_time)
        self.invulnerable_timer = max(
            0, self.invulnerable_timer - delta_time
        )

    def update_classic_controls(self, keys, delta_time):
        """Use arrows or WASD to rotate, thrust, and brake."""
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle -= PLAYER_TURN_SPEED * delta_time
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle += PLAYER_TURN_SPEED * delta_time

        self.thrusting = keys[pygame.K_UP] or keys[pygame.K_w]
        if self.thrusting:
            angle_radians = math.radians(self.angle)
            self.velocity_x += (
                math.sin(angle_radians) * PLAYER_THRUST * delta_time
            )
            self.velocity_y -= (
                math.cos(angle_radians) * PLAYER_THRUST * delta_time
            )

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            brake_amount = max(0, 1 - PLAYER_BRAKE * delta_time)
            self.velocity_x *= brake_amount
            self.velocity_y *= brake_amount

    def update_direct_controls(self, keys, delta_time):
        """Use WASD to point and move in screen directions."""
        direction_x = 0
        direction_y = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction_y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction_y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction_x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction_x += 1

        self.thrusting = direction_x != 0 or direction_y != 0
        if not self.thrusting:
            return

        # Normalize diagonal input so it is not faster than one direction.
        direction_length = math.hypot(direction_x, direction_y)
        direction_x /= direction_length
        direction_y /= direction_length

        target_angle = math.degrees(
            math.atan2(direction_x, -direction_y)
        )
        self.turn_toward(target_angle, delta_time)

        # Movement responds immediately while the ship turns to face it.
        self.velocity_x += direction_x * PLAYER_THRUST * delta_time
        self.velocity_y += direction_y * PLAYER_THRUST * delta_time

    def turn_toward(self, target_angle, delta_time):
        """Rotate toward a target using the shortest direction."""
        difference = (target_angle - self.angle + 180) % 360 - 180
        turn_amount = DIRECT_TURN_SPEED * delta_time

        if abs(difference) <= turn_amount:
            self.angle = target_angle
        elif difference > 0:
            self.angle += turn_amount
        else:
            self.angle -= turn_amount

        self.angle %= 360

    def limit_speed(self):
        """Keep the spaceship from moving too quickly."""
        speed = math.hypot(self.velocity_x, self.velocity_y)
        if speed > PLAYER_MAX_SPEED:
            scale = PLAYER_MAX_SPEED / speed
            self.velocity_x *= scale
            self.velocity_y *= scale

    def wrap_around_screen(self):
        """Move the ship to the opposite edge when it leaves the screen."""
        if self.x < 0:
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = 0

        if self.y < 0:
            self.y = SCREEN_HEIGHT
        elif self.y > SCREEN_HEIGHT:
            self.y = 0

    def can_shoot(self):
        """Return True when the shot cooldown has finished."""
        return self.shot_timer == 0

    def start_shot_cooldown(self, delay):
        """Prevent another shot until the delay has passed."""
        self.shot_timer = delay

    def get_nose_position(self):
        """Return the front point of the spaceship."""
        angle_radians = math.radians(self.angle)
        nose_x = self.x + math.sin(angle_radians) * 22
        nose_y = self.y - math.cos(angle_radians) * 22
        return nose_x, nose_y

    def rotate_points(self, points):
        """Rotate local drawing points around the ship's center."""
        angle_radians = math.radians(self.angle)
        cosine = math.cos(angle_radians)
        sine = math.sin(angle_radians)
        rotated_points = []

        for point_x, point_y in points:
            screen_x = self.x + point_x * cosine - point_y * sine
            screen_y = self.y + point_x * sine + point_y * cosine
            rotated_points.append((screen_x, screen_y))

        return rotated_points

    def draw(self, screen):
        """Draw the spaceship and its engine flame."""
        # Blink briefly after the player loses a life.
        if self.invulnerable_timer > 0:
            if int(self.invulnerable_timer * 10) % 2 == 0:
                return

        ship_points = [(0, -22), (15, 17), (0, 11), (-15, 17)]
        pygame.draw.polygon(
            screen,
            WHITE,
            self.rotate_points(ship_points),
            2
        )

        # The inner line gives the ship a small neon cockpit.
        cockpit_points = [(-5, 7), (0, -7), (5, 7)]
        pygame.draw.lines(
            screen,
            CYAN,
            False,
            self.rotate_points(cockpit_points),
            2
        )

        if self.thrusting:
            flame_points = [(-7, 15), (0, 30), (7, 15)]
            pygame.draw.lines(
                screen,
                ORANGE,
                False,
                self.rotate_points(flame_points),
                3
            )
