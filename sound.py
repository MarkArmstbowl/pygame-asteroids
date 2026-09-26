"""Play generated sound effects and bundled background music."""

import math
import os
import struct

import pygame


class SoundManager:
    """Manage generated sound effects and bundled background music."""

    SAMPLE_RATE = 44100

    def __init__(self, enabled, effects_volume, music_volumes):
        self.enabled = False
        self.muted = True
        self.sounds = {}
        self.music_loaded = False
        self.current_track = None
        self.music_volumes = [
            max(0, min(1, volume)) for volume in music_volumes
        ]
        music_directory = os.path.join(
            os.path.dirname(__file__), "assets", "music"
        )
        self.music_paths = [
            os.path.join(music_directory, "ambient_loop.ogg"),
            os.path.join(music_directory, "level_2_space_arp.ogg"),
            os.path.join(music_directory, "level_3_space_battle.ogg"),
        ]

        if not enabled:
            return

        try:
            # One channel is enough for these short generated sounds.
            pygame.mixer.quit()
            pygame.mixer.init(
                frequency=self.SAMPLE_RATE,
                size=-16,
                channels=2,
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
                "game_over": self._make_death_sound(),
            }
            self.set_effects_volume(effects_volume)
            self.enabled = True
            self.muted = False
            self.play_music(0)
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
            sample_value = round(sample * 32767)
            sound_data.extend(struct.pack("<hh", sample_value, sample_value))

        return pygame.mixer.Sound(buffer=bytes(sound_data))

    def _make_death_sound(self):
        """Create a longer falling arcade sound for game over."""
        duration = 0.9
        sample_count = round(self.SAMPLE_RATE * duration)
        sound_data = bytearray()
        phase = 0

        for index in range(sample_count):
            progress = index / sample_count
            wobble = math.sin(progress * math.tau * 9) * 32
            frequency = 460 - (380 * progress) + wobble
            phase += math.tau * frequency / self.SAMPLE_RATE

            fade_in = min(1, index / (self.SAMPLE_RATE * 0.01))
            fade_out = (1 - progress) ** 0.7
            sample = math.sin(phase) * fade_in * fade_out * 0.48
            sample_value = round(sample * 32767)
            sound_data.extend(struct.pack("<hh", sample_value, sample_value))

        return pygame.mixer.Sound(buffer=bytes(sound_data))

    def set_effects_volume(self, volume):
        """Set one quiet master volume for every generated sound."""
        safe_volume = max(0, min(1, volume))
        for sound in self.sounds.values():
            sound.set_volume(safe_volume)

    def play_music(self, track_index):
        """Switch to the looping music selected for one game level."""
        if not self.enabled:
            return

        safe_index = max(0, min(len(self.music_paths) - 1, track_index))
        target_volume = self.music_volumes[safe_index]

        try:
            if (
                    safe_index == self.current_track
                    and self.music_loaded
                    and pygame.mixer.music.get_busy()):
                volume = 0 if self.muted else target_volume
                pygame.mixer.music.set_volume(volume)
                return

            pygame.mixer.music.load(self.music_paths[safe_index])
            pygame.mixer.music.set_volume(
                0 if self.muted else target_volume
            )
            pygame.mixer.music.play(-1, fade_ms=800)
            self.current_track = safe_index
            self.music_loaded = True
        except (pygame.error, OSError):
            self.music_loaded = False

    def soften_music(self):
        """Lower the music behind the victory screen."""
        if self.enabled and self.music_loaded:
            try:
                if not self.muted:
                    current_volume = self.music_volumes[
                        self.current_track
                    ]
                    pygame.mixer.music.set_volume(current_volume * 0.45)
            except pygame.error:
                self.music_loaded = False

    def stop_music(self):
        """Stop the current background track until music starts again."""
        if not self.enabled:
            return

        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass

        self.music_loaded = False
        self.current_track = None

    def toggle(self):
        """Turn all music and sound effects on or off."""
        if not self.enabled:
            return False

        self.muted = not self.muted
        try:
            if self.muted:
                pygame.mixer.stop()
                pygame.mixer.music.set_volume(0)
            elif self.music_loaded:
                pygame.mixer.music.set_volume(
                    self.music_volumes[self.current_track]
                )
        except pygame.error:
            self.enabled = False
            self.muted = True
            return False
        return not self.muted

    def is_sound_on(self):
        """Return True when audio is available and not muted."""
        return self.enabled and not self.muted

    def play(self, sound_name):
        """Play a sound when audio is available on this computer."""
        if (
                not self.enabled
                or self.muted
                or sound_name not in self.sounds):
            return

        try:
            self.sounds[sound_name].play()
        except pygame.error:
            self.enabled = False
