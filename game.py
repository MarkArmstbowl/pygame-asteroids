"""Game rules, keyboard input, and screen drawing."""

import math
import random

import pygame

from asteroid import Asteroid
from bullet import Bullet
from particle import Particle
from player import Player
from records import load_scores, save_score
from sound import SoundManager
from star import Star
from settings import (
    ASTEROID_OUTLINE,
    BACKGROUND_BOTTOM,
    BACKGROUND_TOP,
    CYAN,
    DARK_PANEL,
    ENABLE_TEST_LEVEL_SKIP,
    FPS,
    GAME_TITLE,
    LEVELS,
    LEVEL_INTRO_TIME,
    LIGHT_BLUE,
    MUSIC_VOLUMES,
    ORANGE,
    PLAYER_RADIUS,
    PURPLE,
    RED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHOT_DELAY,
    SOUND_ENABLED,
    SOUND_VOLUME,
    STAR_LAYERS,
    STARTING_LIVES,
    WHITE,
)


class Game:
    """Keep track of the game and draw the current screen."""

    def __init__(self):
        pygame.init()
        self.sounds = SoundManager(
            SOUND_ENABLED, SOUND_VOLUME, MUSIC_VOLUMES
        )
        try:
            self.screen = pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT),
                pygame.SCALED
            )
        except pygame.error:
            # Try a normal window if scaling is not available.
            self.screen = pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Use Pygame's own font so other computers use the same one.
        self.title_font = self.make_font(100, bold=True)
        self.heading_font = self.make_font(46, bold=True)
        self.body_font = self.make_font(32)
        self.small_font = self.make_font(25)
        self.key_font = self.make_font(22, bold=True)

        self.background = self.make_background()
        self.stars = self._make_stars()
        self.player = Player()
        self.asteroids = []
        self.bullets = []
        self.particles = []
        self.state = "title"
        self.paused = False
        self.level_index = 0
        self.level_message_timer = 0
        self.score = 0
        self.lives = STARTING_LIVES
        self.control_mode = "classic"
        self.high_scores = load_scores()
        self.score_recorded = False
        self.confirm_action = None
        self.shake_timer = 0
        self.shake_strength = 0
        self.flash_timer = 0
        self.flash_color = WHITE

    def make_font(self, size, bold=False):
        """Make a font using Pygame's default font."""
        font = pygame.font.Font(None, size)
        font.set_bold(bold)
        return font

    def make_background(self):
        """Make a dark blue background that gets lighter near the bottom."""
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Draw one row at a time, changing the color from top to bottom.
        for y_position in range(SCREEN_HEIGHT):
            amount = y_position / SCREEN_HEIGHT
            color = []
            for index in range(3):
                color_value = (
                    BACKGROUND_TOP[index]
                    + (BACKGROUND_BOTTOM[index] - BACKGROUND_TOP[index])
                    * amount
                )
                color.append(round(color_value))
            pygame.draw.line(
                background,
                tuple(color),
                (0, y_position),
                (SCREEN_WIDTH, y_position)
            )

        return background

    def _make_stars(self):
        """Make the stars in each background layer."""
        stars = []
        # Use the same starting star positions each time.
        star_random = random.Random(7)

        for layer in STAR_LAYERS:
            for _ in range(layer["count"]):
                brightness = star_random.randint(*layer["brightness"])
                star = Star(
                    star_random.randrange(SCREEN_WIDTH),
                    star_random.randrange(SCREEN_HEIGHT),
                    layer["speed"],
                    layer["radius"],
                    brightness
                )
                stars.append(star)

        return stars

    def run(self):
        """Read input, move objects, and draw each frame."""
        while self.running:
            # Use seconds between frames, with a limit for slow frames.
            delta_time = min(self.clock.tick(FPS) / 1000, 0.05)
            self.handle_events()
            self.update(delta_time)
            self.draw()

        pygame.quit()

    def handle_events(self):
        """Read key presses and requests to close the window."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.state == "playing":
                    self.request_confirmation("quit")
                else:
                    self.running = False

            if event.type == pygame.KEYDOWN:
                # N means 'don't save' here, so check this question first.
                if self.confirm_action is not None:
                    self.handle_confirmation_key(event.key)
                    continue

                if event.key == pygame.K_n:
                    self.sounds.toggle()
                    continue

                if self.state == "title":
                    if event.key == pygame.K_RETURN:
                        self.start_game()
                    elif event.key == pygame.K_c:
                        self.toggle_control_mode()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

                elif self.state in ("game_over", "win"):
                    if event.key in (pygame.K_RETURN, pygame.K_r):
                        self.start_game()
                    elif event.key == pygame.K_m:
                        self.return_to_menu()

                elif self.state == "playing":
                    if event.key in (pygame.K_p, pygame.K_ESCAPE):
                        self.paused = not self.paused
                    elif (
                            event.key == pygame.K_v
                            and ENABLE_TEST_LEVEL_SKIP):
                        self.skip_test_level()
                    elif self.paused and event.key == pygame.K_m:
                        self.request_confirmation("menu")
                    elif self.paused and event.key == pygame.K_c:
                        self.toggle_control_mode()
                    elif self.paused and event.key == pygame.K_q:
                        self.request_confirmation("quit")
                    elif (
                            event.key == pygame.K_SPACE
                            and not self.paused
                            and self.level_message_timer <= 0):
                        self.fire_bullet()

    def request_confirmation(self, action):
        """Pause the game and show the save question."""
        self.paused = True
        self.confirm_action = action

    def handle_confirmation_key(self, key):
        """Read Y, N, or Escape for the save question."""
        if key == pygame.K_y:
            self.record_current_score()
            self.complete_confirmed_action()
        elif key == pygame.K_n:
            self.complete_confirmed_action()
        elif key == pygame.K_ESCAPE:
            self.confirm_action = None

    def complete_confirmed_action(self):
        """Return to the menu or quit after the player's choice."""
        action = self.confirm_action
        self.confirm_action = None

        if action == "menu":
            self.return_to_menu()
        elif action == "quit":
            self.running = False

    def toggle_control_mode(self):
        """Switch between Classic and Direct controls."""
        if self.control_mode == "classic":
            self.control_mode = "direct"
        else:
            self.control_mode = "classic"

    def return_to_menu(self):
        """Go back to the main menu and reload the high scores."""
        self.sounds.play_music(0)
        self.state = "title"
        self.paused = False
        self.confirm_action = None
        self.high_scores = load_scores()

    def start_game(self):
        """Reset the score and lives, then start level one."""
        self.player = Player()
        self.bullets = []
        self.particles = []
        self.score = 0
        self.lives = STARTING_LIVES
        self.level_index = 0
        self.paused = False
        self.state = "playing"
        self.score_recorded = False
        self.confirm_action = None
        self.start_level()

    def start_level(self):
        """Clear old objects and create this level's asteroids."""
        self.asteroids = []
        self.bullets = []
        self.particles = []
        level = LEVELS[self.level_index]

        # Give each asteroid its own starting point and slightly varied speed.
        for _ in range(level["asteroids"]):
            x_position, y_position = self.get_spawn_position()
            speed = level["speed"] * random.uniform(0.85, 1.15)
            asteroid = Asteroid(x_position, y_position, speed)
            self.asteroids.append(asteroid)

        self.player.reset_position()
        self.level_message_timer = LEVEL_INTRO_TIME
        self.sounds.play_music(self.level_index)
        self.sounds.play("level_start")

    def get_spawn_position(self):
        """Pick a starting point away from the center."""
        while True:
            x_position = random.randint(50, SCREEN_WIDTH - 50)
            y_position = random.randint(50, SCREEN_HEIGHT - 50)
            distance = math.hypot(
                x_position - SCREEN_WIDTH / 2,
                y_position - SCREEN_HEIGHT / 2
            )
            if distance > 210:
                return x_position, y_position

    def fire_bullet(self):
        """Create a bullet at the front of the ship."""
        # Wait for the shooting timer before allowing another shot.
        if not self.player.can_shoot():
            return

        bullet_x, bullet_y = self.player.get_nose_position()
        bullet = Bullet(
            bullet_x,
            bullet_y,
            self.player.angle,
            self.player.velocity_x,
            self.player.velocity_y
        )
        self.bullets.append(bullet)
        self.player.start_shot_cooldown(SHOT_DELAY)
        self.sounds.play("shoot")

    def update(self, delta_time):
        """Move game objects and check for hits."""
        self._update_screen_effects(delta_time)
        for star in self.stars:
            star.update(delta_time)

        if self.state != "playing" or self.paused:
            return

        # Wait until the level message is gone before moving game objects.
        if self.level_message_timer > 0:
            self.level_message_timer = max(
                0, self.level_message_timer - delta_time
            )
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys, delta_time, self.control_mode)
        if self.player.thrusting:
            self.add_thruster_particle()

        for bullet in self.bullets:
            bullet.update(delta_time)
            self.add_bullet_trail(bullet)
        # Remove bullets once their time runs out.
        self.bullets = [
            bullet for bullet in self.bullets if bullet.is_alive()
        ]

        for particle in self.particles:
            particle.update(delta_time)
        # Remove particles once they have faded.
        self.particles = [
            particle for particle in self.particles
            if particle.is_alive()
        ]

        for asteroid in self.asteroids:
            asteroid.update(delta_time)

        self.check_bullet_collisions()
        self.check_player_collisions()

        self.level_message_timer = max(
            0, self.level_message_timer - delta_time
        )

        # The level ends only when every asteroid and piece is gone.
        if not self.asteroids and self.state == "playing":
            self.finish_level()

    def check_bullet_collisions(self):
        """Remove hit asteroids and add their smaller pieces."""
        # Loop over copies because hits remove items from these lists.
        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                distance = math.hypot(
                    bullet.x - asteroid.x,
                    bullet.y - asteroid.y
                )

                if distance < asteroid.radius:
                    self.sounds.play(
                        "asteroid_" + str(asteroid.size)
                    )
                    particle_count = 8 + asteroid.size * 4
                    particle_speed = 90 + asteroid.size * 35
                    self.add_explosion(
                        asteroid.x,
                        asteroid.y,
                        particle_count,
                        particle_speed,
                        ASTEROID_OUTLINE
                    )
                    self.bullets.remove(bullet)
                    self.asteroids.remove(asteroid)
                    self.asteroids.extend(asteroid.split())
                    # Small asteroids give more points than large ones.
                    self.score += (4 - asteroid.size) * 100
                    break

    def check_player_collisions(self):
        """Take away a life when the ship hits an asteroid."""
        # Ignore hits during the short protection time after a reset.
        if self.player.invulnerable_timer > 0:
            return

        for asteroid in self.asteroids:
            distance = math.hypot(
                self.player.x - asteroid.x,
                self.player.y - asteroid.y
            )

            if distance < PLAYER_RADIUS + asteroid.radius:
                self._start_screen_effects(3, 0.10, ORANGE)
                self.add_explosion(
                    self.player.x,
                    self.player.y,
                    26,
                    230,
                    ORANGE
                )
                self.lives -= 1
                if self.lives <= 0:
                    self.sounds.stop_music()
                    self.sounds.play("game_over")
                    self.state = "game_over"
                    self.record_current_score()
                else:
                    self.sounds.play("player_hit")
                    self.player.reset_position()
                break

    def finish_level(self):
        """Show the win screen after the last level, or start the next one."""
        if self.level_index == len(LEVELS) - 1:
            self.sounds.play("win")
            self.sounds.soften_music()
            self.state = "win"
            self.record_current_score()
        else:
            self.level_index += 1
            self.start_level()

    def skip_test_level(self):
        """Skip one level for testing when the setting is turned on."""
        self.asteroids = []
        self.finish_level()

    def add_bullet_trail(self, bullet):
        """Add a short trail behind a bullet."""
        particle = Particle(
            (bullet.x, bullet.y),
            (
                -bullet.velocity_x * 0.04,
                -bullet.velocity_y * 0.04
            ),
            CYAN,
            3,
            0.18
        )
        self.particles.append(particle)

    def add_thruster_particle(self):
        """Add a small engine flame particle behind the ship."""
        angle = math.radians(self.player.angle)
        spread_angle = angle + random.uniform(-0.25, 0.25)
        particle_speed = random.uniform(75, 145)
        particle_x = self.player.x - math.sin(angle) * 18
        particle_y = self.player.y + math.cos(angle) * 18
        particle = Particle(
            (particle_x, particle_y),
            (
                self.player.velocity_x
                - math.sin(spread_angle) * particle_speed,
                self.player.velocity_y
                + math.cos(spread_angle) * particle_speed
            ),
            random.choice((ORANGE, PURPLE)),
            random.uniform(2, 4),
            random.uniform(0.25, 0.45)
        )
        self.particles.append(particle)

    def add_explosion(
            self, x_position, y_position, particle_count,
            maximum_speed, color):
        """Make small dots spread out from a hit."""
        for _ in range(particle_count):
            direction = random.uniform(0, math.tau)
            speed = random.uniform(maximum_speed * 0.35, maximum_speed)
            particle = Particle(
                (x_position, y_position),
                (
                    math.cos(direction) * speed,
                    math.sin(direction) * speed
                ),
                color,
                random.uniform(2, 5),
                random.uniform(0.35, 0.75)
            )
            self.particles.append(particle)

    def _start_screen_effects(self, strength, duration, color):
        """Start a brief screen shake and flash."""
        self.shake_strength = strength
        self.shake_timer = duration
        self.flash_timer = duration
        self.flash_color = color

    def _update_screen_effects(self, delta_time):
        """Reduce the time left for the shake and flash."""
        self.shake_timer = max(0, self.shake_timer - delta_time)
        self.flash_timer = max(0, self.flash_timer - delta_time)

    def record_current_score(self):
        """Save the current score once per game."""
        if not self.score_recorded:
            self.high_scores = save_score(self.score)
            self.score_recorded = True

    def draw(self):
        """Draw the current game screen."""
        self.screen.blit(self.background, (0, 0))
        for star in self.stars:
            star.draw(self.screen)

        if self.state == "title":
            self.draw_title_screen()
        elif self.state == "playing":
            self.draw_playing_screen()
        elif self.state == "game_over":
            self.draw_playing_screen()
            self.draw_end_screen(
                "MISSION FAILED", "NO SHIPS REMAINING", RED
            )
        elif self.state == "win":
            self.draw_playing_screen()
            self.draw_end_screen(
                "MISSION COMPLETE",
                "ALL THREE SECTORS CLEARED",
                CYAN
            )

        self._draw_screen_effects()
        pygame.display.flip()

    def _draw_screen_effects(self):
        """Draw the short flash and shake after a hit."""
        if self.flash_timer > 0:
            flash = pygame.Surface(
                (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
            )
            flash.fill((*self.flash_color, 16))
            self.screen.blit(flash, (0, 0))

        if self.shake_timer > 0:
            frame = self.screen.copy()
            offset_x = random.randint(
                -self.shake_strength, self.shake_strength
            )
            offset_y = random.randint(
                -self.shake_strength, self.shake_strength
            )
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(frame, (offset_x, offset_y))

    def draw_playing_screen(self):
        """Draw game objects, score, lives, and any open menus."""
        showing_level_intro = (
            self.level_message_timer > 0 and self.state == "playing"
        )

        if not showing_level_intro:
            for asteroid in self.asteroids:
                asteroid.draw(self.screen)
            for particle in self.particles:
                particle.draw(self.screen)
            for bullet in self.bullets:
                bullet.draw(self.screen)
            self.player.draw(self.screen)

        self.draw_hud()

        if showing_level_intro:
            self._draw_level_intro()

        if self.paused:
            self.draw_pause_screen()
            if self.confirm_action is not None:
                self.draw_confirmation_dialog()

    def draw_hud(self):
        """Show the level, score, lives, controls, and sound status."""
        level_text = "LEVEL " + str(self.level_index + 1)
        score_text = "SCORE  " + str(self.score).zfill(6)

        self.draw_text(level_text, self.small_font, LIGHT_BLUE, 24, 20)
        self.draw_text(score_text, self.small_font, WHITE, 24, 47)
        self.draw_text("LIVES", self.small_font, CYAN, 24, 74)
        self.draw_life_icons(92, 87)

        mode_text = "MODE  " + self.control_mode.upper()
        mode_surface = self.small_font.render(mode_text, True, CYAN)
        pause_surface = self.small_font.render(
            "P / ESC  PAUSE", True, LIGHT_BLUE
        )
        sound_surface = self.small_font.render(
            "N  " + self._sound_status_text(),
            True,
            LIGHT_BLUE
        )
        right_edge = SCREEN_WIDTH - 24
        self.screen.blit(
            mode_surface,
            (right_edge - mode_surface.get_width(), 20)
        )
        self.screen.blit(
            pause_surface,
            (right_edge - pause_surface.get_width(), 47)
        )
        self.screen.blit(
            sound_surface,
            (right_edge - sound_surface.get_width(), 74)
        )

    def draw_title_screen(self):
        """Show the title, controls, and top five scores."""
        self.draw_centered_text("NEON", self.title_font, CYAN, 38)
        self.draw_centered_text("ASTEROIDS", self.title_font, WHITE, 105)
        self.draw_centered_text(
            "THREE SECTORS. THREE LIVES. ONE WAY HOME.",
            self.small_font,
            PURPLE,
            190
        )

        control_panel = pygame.Rect(65, 235, 555, 305)
        record_panel = pygame.Rect(645, 235, 290, 305)
        self.draw_panel(control_panel)
        self.draw_panel(record_panel)

        mode_name = self.control_mode.upper() + " FLIGHT"
        self.draw_panel_heading(mode_name, control_panel)
        self.draw_control_rows(control_panel, control_panel.y + 80)

        self.draw_panel_heading("TOP 5 RECORDS", record_panel)
        self.draw_records(record_panel)

        self.draw_centered_text(
            "C  SWITCH CONTROL MODE",
            self.small_font,
            LIGHT_BLUE,
            567
        )
        self.draw_centered_text(
            "PRESS ENTER TO LAUNCH",
            self.heading_font,
            ORANGE,
            607
        )
        self.draw_shortcut(
            "N", self._sound_status_text(), 385, 657,
            LIGHT_BLUE
        )
        self.draw_shortcut(
            "ESC", "QUIT", 625, 657, LIGHT_BLUE
        )

    def draw_pause_screen(self):
        """Show the controls and menu options while paused."""
        self.draw_overlay()
        self.draw_centered_text("PAUSED", self.title_font, ORANGE, 46)

        panel = pygame.Rect(130, 140, 740, 500)
        self.draw_panel(panel)
        self.draw_panel_heading(
            self.control_mode.upper() + " FLIGHT CONTROLS",
            panel
        )
        self.draw_control_rows(panel, 220)

        pygame.draw.line(
            self.screen,
            (65, 105, 135),
            (panel.x + 35, 450),
            (panel.right - 35, 450),
            1
        )
        self.draw_shortcut(
            "P / ESC", "RESUME", panel.centerx - 180, 477
        )
        self.draw_shortcut(
            "C", "SWITCH MODE", panel.centerx + 180, 477
        )
        self.draw_shortcut(
            "M", "MAIN MENU", panel.centerx - 240, 535,
            LIGHT_BLUE
        )
        self.draw_shortcut(
            "N", self._sound_status_text(), panel.centerx, 535,
            LIGHT_BLUE
        )
        self.draw_shortcut(
            "Q", "QUIT", panel.centerx + 240, 535,
            LIGHT_BLUE
        )

    def draw_confirmation_dialog(self):
        """Ask whether to save before leaving the game."""
        self.draw_overlay()
        panel = pygame.Rect(190, 195, 620, 315)
        self.draw_panel(panel)

        if self.confirm_action == "menu":
            action_text = "RETURN TO MAIN MENU?"
        else:
            action_text = "QUIT THE GAME?"

        self.draw_centered_text(
            action_text, self.heading_font, ORANGE, 225
        )
        self.draw_centered_text(
            "CURRENT SCORE  " + str(self.score).zfill(6),
            self.body_font,
            WHITE,
            300
        )
        self.draw_centered_text(
            "SAVE THIS SCORE FIRST?",
            self.body_font,
            CYAN,
            350
        )
        self.draw_shortcut("Y", "SAVE", 300, 420)
        self.draw_shortcut("N", "DON'T SAVE", 500, 420)
        self.draw_shortcut(
            "ESC", "CANCEL", 700, 420, LIGHT_BLUE
        )

    def draw_end_screen(self, heading, subtitle, color):
        """Show the final score after winning or losing."""
        self.draw_overlay()
        panel = pygame.Rect(180, 125, 640, 450)
        self.draw_panel(panel)

        self.draw_centered_text(
            heading, self.heading_font, color, 165
        )
        self.draw_centered_text(
            subtitle, self.small_font, LIGHT_BLUE, 220
        )

        pygame.draw.line(
            self.screen,
            (65, 105, 135),
            (panel.x + 45, 265),
            (panel.right - 45, 265),
            1
        )
        self.draw_centered_text(
            "FINAL SCORE", self.small_font, WHITE, 300
        )
        self.draw_centered_text(
            str(self.score).zfill(6), self.heading_font, color, 335
        )

        if self.score > 0 and self.high_scores:
            if self.score == self.high_scores[0]:
                result_text = "NEW HIGH SCORE"
            else:
                result_text = "TOP SCORE  " + str(
                    self.high_scores[0]
                ).zfill(6)
        elif self.state == "win":
            result_text = "THE VOID IS QUIET"
        else:
            result_text = (
                "REACHED SECTOR " + str(self.level_index + 1)
                + " OF " + str(len(LEVELS))
            )

        self.draw_centered_text(
            result_text, self.small_font, PURPLE, 395
        )
        pygame.draw.line(
            self.screen,
            (65, 105, 135),
            (panel.x + 45, 435),
            (panel.right - 45, 435),
            1
        )
        self.draw_shortcut(
            "ENTER / R", "PLAY AGAIN", panel.centerx - 165, 475
        )
        self.draw_shortcut(
            "M", "MAIN MENU", panel.centerx + 175, 475,
            LIGHT_BLUE
        )
        self.draw_shortcut(
            "N", self._sound_status_text(), panel.centerx, 525,
            LIGHT_BLUE
        )

    def _sound_status_text(self):
        """Get the sound-on or sound-off label."""
        if self.sounds.is_sound_on():
            return "SOUND ON"
        return "SOUND OFF"

    def _draw_level_intro(self):
        """Show the level name, asteroid count, and speed."""
        level = LEVELS[self.level_index]
        # Fade the message in and out at the start and end.
        elapsed_time = LEVEL_INTRO_TIME - self.level_message_timer
        fade_in = min(1, elapsed_time / 0.25)
        fade_out = min(1, self.level_message_timer / 0.40)
        alpha = round(255 * min(fade_in, fade_out))

        card = pygame.Surface((560, 190), pygame.SRCALPHA)
        card_rect = card.get_rect()
        pygame.draw.rect(
            card, (*DARK_PANEL, 235), card_rect, border_radius=14
        )
        pygame.draw.rect(
            card, (*LIGHT_BLUE, 255), card_rect, 2,
            border_radius=14
        )
        pygame.draw.line(
            card, (*PURPLE, 190), (42, 55), (518, 55), 2
        )

        self._draw_centered_on_surface(
            card,
            "SECTOR 0" + str(self.level_index + 1),
            self.small_font,
            CYAN,
            20
        )
        self._draw_centered_on_surface(
            card, level["name"], self.heading_font, WHITE, 72
        )
        details = (
            str(level["asteroids"]) + " LARGE ASTEROIDS"
            + "     SPEED " + str(level["speed"])
        )
        self._draw_centered_on_surface(
            card, details, self.small_font, LIGHT_BLUE, 132
        )

        card.set_alpha(alpha)
        card_position = card.get_rect(
            center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        )
        self.screen.blit(card, card_position)

    @staticmethod
    def _draw_centered_on_surface(
            surface, text, font, color, y_position):
        """Center text across a small menu surface."""
        text_surface = font.render(text, True, color)
        x_position = (surface.get_width() - text_surface.get_width()) / 2
        surface.blit(text_surface, (x_position, y_position))

    def get_control_rows(self):
        """Get the key names and actions for the selected controls."""
        if self.control_mode == "direct":
            return [
                ("UP / W", "Move up"),
                ("DOWN / S", "Move down"),
                ("LEFT / A", "Move left"),
                ("RIGHT / D", "Move right"),
                ("SPACE", "Shoot"),
                ("P / ESC", "Pause game"),
            ]

        return [
            ("LEFT / A", "Rotate left"),
            ("RIGHT / D", "Rotate right"),
            ("UP / W", "Fire thruster"),
            ("DOWN / S", "Brake"),
            ("SPACE", "Shoot"),
            ("P / ESC", "Pause game"),
        ]

    def draw_control_rows(self, panel, start_y):
        """Draw the keys and their actions in two columns."""
        key_width = 170
        # Measure the widest action so the whole group can be centered.
        action_width = max(
            self.body_font.size(action_text)[0]
            for _, action_text in self.get_control_rows()
        )
        group_width = key_width + 35 + action_width
        key_x = panel.centerx - group_width / 2
        action_x = key_x + key_width + 35

        for index, (key_text, action_text) in enumerate(
                self.get_control_rows()):
            y_position = start_y + index * 36
            key_rect = pygame.Rect(key_x, y_position, key_width, 28)
            self.draw_key_badge(key_text, key_rect)
            self.draw_text(
                action_text, self.body_font, WHITE,
                action_x, y_position - 1
            )

    def draw_key_badge(self, key_text, key_rect):
        """Draw a small box around a key name."""
        pygame.draw.rect(
            self.screen, (15, 35, 58), key_rect, border_radius=6
        )
        pygame.draw.rect(
            self.screen, LIGHT_BLUE, key_rect, 1, border_radius=6
        )
        key_surface = self.key_font.render(key_text, True, CYAN)
        text_rect = key_surface.get_rect(center=key_rect.center)
        self.screen.blit(key_surface, text_rect)

    def draw_shortcut(
            self, key_text, action_text, center_x, y_position,
            action_color=WHITE):
        """Draw a key box with its action beside it."""
        key_width = self.key_font.size(key_text)[0] + 24
        action_width = self.small_font.size(action_text)[0]
        total_width = key_width + 12 + action_width
        start_x = center_x - total_width / 2
        key_rect = pygame.Rect(start_x, y_position, key_width, 30)
        self.draw_key_badge(key_text, key_rect)
        self.draw_text(
            action_text,
            self.small_font,
            action_color,
            key_rect.right + 12,
            y_position + 2
        )

    def draw_life_icons(self, start_x, center_y):
        """Draw one small ship for each life left."""
        for index in range(self.lives):
            center_x = start_x + index * 25
            ship_points = [
                (center_x, center_y - 10),
                (center_x + 8, center_y + 9),
                (center_x, center_y + 5),
                (center_x - 8, center_y + 9),
            ]
            pygame.draw.polygon(self.screen, CYAN, ship_points, 2)

    def draw_records(self, panel):
        """Show up to five saved high scores."""
        if not self.high_scores:
            self.draw_text(
                "No completed runs yet",
                self.small_font,
                LIGHT_BLUE,
                panel.x + 24,
                panel.y + 96
            )
            return

        for index, score in enumerate(self.high_scores):
            place = str(index + 1) + "."
            score_text = str(score).zfill(6)
            y_position = panel.y + 90 + index * 39
            self.draw_text(
                place, self.body_font, LIGHT_BLUE, panel.x + 30, y_position
            )
            self.draw_text(
                score_text, self.body_font, WHITE, panel.x + 95, y_position
            )

    def draw_panel(self, panel):
        """Draw a dark menu box with a blue border."""
        pygame.draw.rect(self.screen, DARK_PANEL, panel, border_radius=12)
        pygame.draw.rect(
            self.screen, LIGHT_BLUE, panel, 2, border_radius=12
        )

    def draw_panel_heading(self, text, panel):
        """Center the heading and make it smaller if needed."""
        font_size = 46
        available_width = panel.width - 40
        font = self.make_font(font_size, bold=True)

        # Keep long headings inside the menu box.
        while font.size(text)[0] > available_width and font_size > 24:
            font_size -= 2
            font = self.make_font(font_size, bold=True)

        text_surface = font.render(text, True, CYAN)
        x_position = panel.centerx - text_surface.get_width() / 2
        self.screen.blit(text_surface, (x_position, panel.y + 25))

    def draw_overlay(self):
        """Darken the game behind a menu."""
        overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((3, 7, 18, 205))
        self.screen.blit(overlay, (0, 0))

    def draw_text(self, text, font, color, x_position, y_position):
        """Draw text using its top-left position."""
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x_position, y_position))

    def draw_centered_text(self, text, font, color, y_position):
        """Draw one line of text centered horizontally."""
        text_surface = font.render(text, True, color)
        x_position = (SCREEN_WIDTH - text_surface.get_width()) / 2
        self.screen.blit(text_surface, (x_position, y_position))
