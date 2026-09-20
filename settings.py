"""Settings shared by the Asteroids game files."""

# Window settings
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60
GAME_TITLE = "Neon Asteroids"

# Colors
BACKGROUND_TOP = (4, 8, 22)
BACKGROUND_BOTTOM = (10, 20, 45)
WHITE = (235, 245, 255)
LIGHT_BLUE = (125, 220, 255)
CYAN = (45, 240, 235)
PURPLE = (175, 95, 255)
ORANGE = (255, 165, 70)
RED = (255, 85, 105)
DARK_PANEL = (9, 17, 38)
ASTEROID_FILL = (26, 35, 58)
ASTEROID_OUTLINE = (165, 195, 220)

# Player settings
PLAYER_TURN_SPEED = 240
PLAYER_THRUST = 320
PLAYER_DRAG = 0.985
PLAYER_MAX_SPEED = 420
PLAYER_RADIUS = 16
PLAYER_INVULNERABLE_TIME = 2.0
STARTING_LIVES = 3

# Bullet settings
BULLET_SPEED = 620
BULLET_LIFETIME = 1.2
SHOT_DELAY = 0.18

# Each level increases both asteroid count and asteroid speed.
LEVELS = [
    {"name": "ORBIT", "asteroids": 5, "speed": 85},
    {"name": "DEEP SPACE", "asteroids": 7, "speed": 125},
    {"name": "VOID STORM", "asteroids": 9, "speed": 165},
]
