"""Quiet, original sound effects generated when the game starts."""

import math
import struct

import pygame


class SoundManager:
    """Create and play small retro sounds without external audio files."""

    SAMPLE_RATE = 22050

    def __init__(self, enabled, volume):
        self.enabled = False
        self.sounds = {}

        if not enabled:
            return

        try:
            # One channel is enough for these short generated sounds.
            pygame.mixer.quit()
            pygame.mixer.init(
                frequency=self.SAMPLE_RATE,
                size=-16,
                channels=1,
                buffer=512
            )
            self.sounds = {
                "shoot": self._make_sweep(720, 440, 0.07, 0.28),
                "asteroid_3": self._make_sweep(105, 55, 0.18, 0.42),
                "asteroid_2": self._make_sweep(145, 75, 0.14, 0.38),
                "asteroid_1": self._make_sweep(210, 115, 0.10, 0.34),
                "player_hit": self._make_sweep(180, 45, 0.24, 0.46),
                "level_start": self._make_sweep(360, 620, 0.20, 0.28),
                "win": self._make_sweep(420, 900, 0.42, 0.30),
                "game_over": self._make_sweep(300, 90, 0.38, 0.34),
            }
            self.set_volume(volume)
            self.enabled = True
        except (pygame.error, ValueError):
            # The game remains fully playable without an audio device.
            self.sounds = {}

    def _make_sweep(
            self, start_frequency, end_frequency, duration, strength):
        """Create one fading tone that moves between two frequencies."""
        sample_count = round(self.SAMPLE_RATE * duration)
        sound_data = bytearray()
        phase = 0

        for index in range(sample_count):
            progress = index / sample_count
            frequency = (
                start_frequency
                + (end_frequency - start_frequency) * progress
            )
            phase += math.tau * frequency / self.SAMPLE_RATE

            fade_out = (1 - progress) ** 2
            fade_in = min(1, index / (self.SAMPLE_RATE * 0.008))
            sample = math.sin(phase) * fade_in * fade_out * strength
            sound_data.extend(struct.pack("<h", round(sample * 32767)))

        return pygame.mixer.Sound(buffer=bytes(sound_data))

    def set_volume(self, volume):
        """Set one quiet master volume for every generated sound."""
        safe_volume = max(0, min(1, volume))
        for sound in self.sounds.values():
            sound.set_volume(safe_volume)

    def play(self, sound_name):
        """Play a sound when audio is available on this computer."""
        if not self.enabled or sound_name not in self.sounds:
            return

        try:
            self.sounds[sound_name].play()
        except pygame.error:
            self.enabled = False
