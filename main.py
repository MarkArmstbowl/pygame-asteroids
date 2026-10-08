"""Start Neon Asteroids."""

from game import Game


if __name__ == "__main__":
    # Start the game only when this file is run directly.
    asteroids_game = Game()
    asteroids_game.run()
