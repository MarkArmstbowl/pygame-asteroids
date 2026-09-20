# Neon Asteroids

A three-level Asteroids-style arcade game built with Python and Pygame.
The game uses original vector graphics drawn directly with Pygame, so no
external art files are required.

## Features

- Arrow-key spaceship controls with momentum and screen wrapping
- Three levels with increasing asteroid counts and speeds
- Five or more independently moving asteroids on screen
- Large asteroids that split into medium and then small asteroids
- Global score, three player lives, and temporary respawn protection
- Victory, game-over, pause, and title screens
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
| Left / Right arrow | Rotate the spaceship |
| Up arrow | Fire the thruster |
| Space | Shoot |
| P | Pause or continue |
| Enter | Start or restart |
| Escape | Quit |

## Project Structure

```text
main.py       Starts the program
game.py       Runs the game loop, levels, collisions, and screens
player.py     Controls spaceship movement and drawing
asteroid.py   Controls asteroid movement, shapes, and splitting
bullet.py     Controls fired projectiles
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
