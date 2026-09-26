"""Main game loop and rules for Neon Asteroids."""

import math
import random

import pygame

from asteroid import Asteroid
from bullet import Bullet
from player import Player
from records import load_scores, save_score
from settings import (
    BACKGROUND_BOTTOM,
    BACKGROUND_TOP,
    CYAN,
    DARK_PANEL,
    ENABLE_TEST_WIN,
    FPS,
    GAME_TITLE,
    LEVELS,
    LIGHT_BLUE,
    ORANGE,
    PLAYER_RADIUS,
    PURPLE,
    RED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHOT_DELAY,
    STARTING_LIVES,
    WHITE,
)


class Game:
    """Manage input, levels, collisions, drawing, and game states."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.SCALED
        )
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Pygame's bundled font keeps text sizes consistent across devices.
        self.title_font = self.make_font(100, bold=True)
        self.heading_font = self.make_font(46, bold=True)
        self.body_font = self.make_font(32)
        self.small_font = self.make_font(25)
        self.key_font = self.make_font(22, bold=True)

        self.background = self.make_background()
        self.player = Player()
        self.asteroids = []
        self.bullets = []
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

    def make_font(self, size, bold=False):
        """Create a font bundled with Pygame for consistent sizing."""
        font = pygame.font.Font(None, size)
        font.set_bold(bold)
        return font

    def make_background(self):
        """Create a reusable gradient background with random stars."""
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Draw the dark blue vertical gradient one row at a time.
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

        # Different star sizes make the background feel deeper.
        random.seed(7)
        for _ in range(150):
            x_position = random.randrange(SCREEN_WIDTH)
            y_position = random.randrange(SCREEN_HEIGHT)
            radius = random.choice([1, 1, 1, 2])
            brightness = random.randint(100, 220)
            star_color = (brightness, brightness, brightness)
            pygame.draw.circle(
                background,
                star_color,
                (x_position, y_position),
                radius
            )
        random.seed()

        return background

    def run(self):
        """Run the game until the player closes the window."""
        while self.running:
            delta_time = min(self.clock.tick(FPS) / 1000, 0.05)
            self.handle_events()
            self.update(delta_time)
            self.draw()

        pygame.quit()

    def handle_events(self):
        """Handle window, menu, shooting, and pause events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.state == "playing":
                    self.request_confirmation("quit")
                else:
                    self.running = False

            if event.type == pygame.KEYDOWN:
                if self.confirm_action is not None:
                    self.handle_confirmation_key(event.key)
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
                    elif event.key == pygame.K_v and ENABLE_TEST_WIN:
                        self.show_test_win()
                    elif self.paused and event.key == pygame.K_m:
                        self.request_confirmation("menu")
                    elif self.paused and event.key == pygame.K_c:
                        self.toggle_control_mode()
                    elif self.paused and event.key == pygame.K_q:
                        self.request_confirmation("quit")
                    elif event.key == pygame.K_SPACE and not self.paused:
                        self.fire_bullet()

    def request_confirmation(self, action):
        """Pause play and ask whether the score should be saved."""
        self.paused = True
        self.confirm_action = action

    def handle_confirmation_key(self, key):
        """Handle save, discard, or cancel from the confirmation dialog."""
        if key == pygame.K_y:
            self.record_current_score()
            self.complete_confirmed_action()
        elif key == pygame.K_n:
            self.complete_confirmed_action()
        elif key == pygame.K_ESCAPE:
            self.confirm_action = None

    def complete_confirmed_action(self):
        """Continue to the menu or quit after a confirmation choice."""
        action = self.confirm_action
        self.confirm_action = None

        if action == "menu":
            self.return_to_menu()
        elif action == "quit":
            self.running = False

    def toggle_control_mode(self):
        """Switch between classic and screen-direction controls."""
        if self.control_mode == "classic":
            self.control_mode = "direct"
        else:
            self.control_mode = "classic"

    def return_to_menu(self):
        """Leave the current run and return to the title screen."""
        self.state = "title"
        self.paused = False
        self.confirm_action = None
        self.high_scores = load_scores()

    def start_game(self):
        """Reset all game data and begin at level one."""
        self.player = Player()
        self.bullets = []
        self.score = 0
        self.lives = STARTING_LIVES
        self.level_index = 0
        self.paused = False
        self.state = "playing"
        self.score_recorded = False
        self.confirm_action = None
        self.start_level()

    def start_level(self):
        """Create the large asteroids for the current level."""
        self.asteroids = []
        self.bullets = []
        level = LEVELS[self.level_index]

        for _ in range(level["asteroids"]):
            x_position, y_position = self.get_spawn_position()
            speed = level["speed"] * random.uniform(0.85, 1.15)
            asteroid = Asteroid(x_position, y_position, speed)
            self.asteroids.append(asteroid)

        self.player.reset_position()
        self.level_message_timer = 2.0

    def get_spawn_position(self):
        """Choose a position safely away from the player's ship."""
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
        """Fire one bullet from the nose of the spaceship."""
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

    def update(self, delta_time):
        """Update moving objects and check the game rules."""
        if self.state != "playing" or self.paused:
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys, delta_time, self.control_mode)

        for bullet in self.bullets:
            bullet.update(delta_time)
        self.bullets = [
            bullet for bullet in self.bullets if bullet.is_alive()
        ]

        for asteroid in self.asteroids:
            asteroid.update(delta_time)

        self.check_bullet_collisions()
        self.check_player_collisions()

        self.level_message_timer = max(
            0, self.level_message_timer - delta_time
        )

        if not self.asteroids and self.state == "playing":
            self.finish_level()

    def check_bullet_collisions(self):
        """Destroy hit asteroids and add any smaller fragments."""
        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                distance = math.hypot(
                    bullet.x - asteroid.x,
                    bullet.y - asteroid.y
                )

                if distance < asteroid.radius:
                    self.bullets.remove(bullet)
                    self.asteroids.remove(asteroid)
                    self.asteroids.extend(asteroid.split())
                    self.score += (4 - asteroid.size) * 100
                    break

    def check_player_collisions(self):
        """Remove a life when the ship touches an asteroid."""
        if self.player.invulnerable_timer > 0:
            return

        for asteroid in self.asteroids:
            distance = math.hypot(
                self.player.x - asteroid.x,
                self.player.y - asteroid.y
            )

            if distance < PLAYER_RADIUS + asteroid.radius:
                self.lives -= 1
                if self.lives <= 0:
                    self.state = "game_over"
                    self.record_current_score()
                else:
                    self.player.reset_position()
                break

    def finish_level(self):
        """Advance to the next level or show the victory screen."""
        if self.level_index == len(LEVELS) - 1:
            self.state = "win"
            self.record_current_score()
        else:
            self.level_index += 1
            self.start_level()

    def show_test_win(self):
        """Jump to the normal victory screen when testing is enabled."""
        self.level_index = len(LEVELS) - 1
        self.asteroids = []
        self.finish_level()

    def record_current_score(self):
        """Save one completed run to the local leaderboard."""
        if not self.score_recorded:
            self.high_scores = save_score(self.score)
            self.score_recorded = True

    def draw(self):
        """Draw the current game screen."""
        self.screen.blit(self.background, (0, 0))

        if self.state == "title":
            self.draw_title_screen()
        elif self.state == "playing":
            self.draw_playing_screen()
        elif self.state == "game_over":
            self.draw_playing_screen()
            self.draw_end_screen("GAME OVER", RED)
        elif self.state == "win":
            self.draw_playing_screen()
            self.draw_end_screen("SECTOR CLEARED", CYAN)

        pygame.display.flip()

    def draw_playing_screen(self):
        """Draw all game objects and the heads-up display."""
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        self.player.draw(self.screen)
        self.draw_hud()

        if self.level_message_timer > 0 and self.state == "playing":
            level = LEVELS[self.level_index]
            self.draw_centered_text(
                "LEVEL " + str(self.level_index + 1),
                self.heading_font,
                CYAN,
                SCREEN_HEIGHT / 2 - 24
            )
            self.draw_centered_text(
                level["name"],
                self.body_font,
                WHITE,
                SCREEN_HEIGHT / 2 + 18
            )

        if self.paused:
            self.draw_pause_screen()
            if self.confirm_action is not None:
                self.draw_confirmation_dialog()

    def draw_hud(self):
        """Draw score, level, lives, and the pause reminder."""
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
        right_edge = SCREEN_WIDTH - 24
        self.screen.blit(
            mode_surface,
            (right_edge - mode_surface.get_width(), 20)
        )
        self.screen.blit(
            pause_surface,
            (right_edge - pause_surface.get_width(), 47)
        )

    def draw_title_screen(self):
        """Draw the title, aligned controls, and local records."""
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
        self.draw_panel_heading(
            mode_name,
            control_panel
        )
        self.draw_control_rows(control_panel, control_panel.y + 80)

        self.draw_panel_heading(
            "TOP 5 RECORDS",
            record_panel
        )
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
        self.draw_centered_text(
            "ESC quits from this menu",
            self.small_font,
            LIGHT_BLUE,
            657
        )

    def draw_pause_screen(self):
        """Show controls and navigation options over the paused game."""
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
            "M", "MAIN MENU", panel.centerx - 180, 535,
            LIGHT_BLUE
        )
        self.draw_shortcut(
            "Q", "QUIT", panel.centerx + 180, 535,
            LIGHT_BLUE
        )

    def draw_confirmation_dialog(self):
        """Ask whether to save before leaving the current game."""
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

    def draw_end_screen(self, message, color):
        """Draw the game-over or victory message."""
        self.draw_overlay()
        self.draw_centered_text(
            message, self.title_font, color, SCREEN_HEIGHT / 2 - 65
        )
        self.draw_centered_text(
            "FINAL SCORE  " + str(self.score).zfill(6),
            self.heading_font,
            WHITE,
            SCREEN_HEIGHT / 2 + 25
        )
        self.draw_centered_text(
            "Press Enter or R to play again",
            self.body_font,
            LIGHT_BLUE,
            SCREEN_HEIGHT / 2 + 85
        )
        self.draw_centered_text(
            "Press M for the main menu",
            self.small_font,
            WHITE,
            SCREEN_HEIGHT / 2 + 125
        )

    def get_control_rows(self):
        """Return labels for the currently selected control mode."""
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
        """Draw controls using key badges and a separate action column."""
        key_width = 170
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
        """Draw a keyboard key label inside a small neon badge."""
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
        """Draw one menu shortcut with a distinct key and action."""
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
        """Draw one small spaceship icon for each remaining life."""
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
        """Draw up to five local high scores."""
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
        """Draw a reusable dark menu panel with a blue outline."""
        pygame.draw.rect(self.screen, DARK_PANEL, panel, border_radius=12)
        pygame.draw.rect(
            self.screen, LIGHT_BLUE, panel, 2, border_radius=12
        )

    def draw_panel_heading(self, text, panel):
        """Fit and center a heading inside a menu panel."""
        font_size = 46
        available_width = panel.width - 40
        font = self.make_font(font_size, bold=True)

        while font.size(text)[0] > available_width and font_size > 24:
            font_size -= 2
            font = self.make_font(font_size, bold=True)

        text_surface = font.render(text, True, CYAN)
        x_position = panel.centerx - text_surface.get_width() / 2
        self.screen.blit(text_surface, (x_position, panel.y + 25))

    def draw_overlay(self):
        """Darken the game beneath a menu message."""
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
