"""Settings for the game window, sound, objects, and levels."""

# Window settings
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60
GAME_TITLE = "Neon Asteroids"
LEVEL_INTRO_TIME = 2.2

# Keep sounds quiet. Press N in the game to turn sound on or off.
SOUND_ENABLED = True
SOUND_VOLUME = 0.22
# Music volume for levels 1, 2, and 3. Volumes range from 0 to 1.
MUSIC_VOLUMES = [0.08, 0.07, 0.06]

# Set this to True to let V skip one level during testing.
# Keep it False in the submitted version.
ENABLE_TEST_LEVEL_SKIP = False

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

# Use three groups of stars with different brightness and speed.
STAR_LAYERS = [
    {"count": 75, "speed": 5, "radius": 1, "brightness": (70, 125)},
    {"count": 45, "speed": 12, "radius": 1, "brightness": (120, 185)},
    {"count": 22, "speed": 24, "radius": 2, "brightness": (175, 235)},
]

# Ship movement and starting lives
PLAYER_TURN_SPEED = 240
DIRECT_TURN_SPEED = 540
PLAYER_THRUST = 320
PLAYER_DRAG = 0.985
PLAYER_BRAKE = 4
PLAYER_MAX_SPEED = 420
PLAYER_RADIUS = 16
PLAYER_INVULNERABLE_TIME = 2.0
STARTING_LIVES = 3

# Bullet speed, time on screen, and time between shots
BULLET_SPEED = 620
BULLET_LIFETIME = 1.2
SHOT_DELAY = 0.18

# Later levels start with more asteroids and a higher base speed.
LEVELS = [
    {"name": "ORBIT", "asteroids": 5, "speed": 85},
    {"name": "DEEP SPACE", "asteroids": 7, "speed": 125},
    {"name": "VOID STORM", "asteroids": 9, "speed": 165},
]
