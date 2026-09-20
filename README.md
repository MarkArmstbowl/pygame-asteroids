# Neon Asteroids

A three-level Asteroids-style arcade game built with Python and Pygame.
The game uses original vector graphics drawn directly with Pygame, so no
external art files are required.

## Features

- Classic arrow-key controls and optional screen-direction WASD controls
- Three levels with increasing asteroid counts and speeds
- Five or more independently moving asteroids on screen
- Large asteroids that split into medium and then small asteroids
- Global score, three player lives, and temporary respawn protection
- Victory, game-over, pause, and title screens
- Pause-menu instructions, main-menu navigation, and local top-five scores
- Real-time neon graphics, star field, and heads-up display

## Setup

Create or activate a Python virtual environment, then install the dependency:

```bash
python -m pip install -r requirements.txt
```

Run the game:

```bash
python main.py
```

## Controls

| Key | Action |
| --- | --- |
| Left/Right or A/D | Rotate in Classic mode |
| Up or W | Fire the thruster in Classic mode |
| Down or S | Brake in Classic mode |
| Arrow keys or WASD | Move by screen direction in Direct mode |
| Space | Shoot |
| P / Escape | Pause or continue during a game |
| C | Switch control mode on the title or pause screen |
| M | Return to the main menu from pause or an end screen |
| Enter | Start or restart |
| Escape | Quit from the title screen |

Leaving an unfinished game through the pause menu opens a confirmation dialog.
Press `Y` to save the current score, `N` to leave without saving, or `Escape`
to cancel and remain paused.

## Project Structure

```text
main.py       Starts the program
game.py       Runs the game loop, levels, collisions, and screens
player.py     Controls spaceship movement and drawing
asteroid.py   Controls asteroid movement, shapes, and splitting
bullet.py     Controls fired projectiles
records.py    Stores and retrieves local high scores
settings.py   Stores shared game settings and level difficulty
assets/       Reserved for future sound or image files
```

## Level Progression

| Level | Large Asteroids | Base Speed |
| --- | ---: | ---: |
| 1 - Orbit | 5 | 85 |
| 2 - Deep Space | 7 | 125 |
| 3 - Void Storm | 9 | 165 |

Clearing all three levels wins the game. Colliding with asteroids removes a
life, and losing all three lives leads to the game-over screen.
