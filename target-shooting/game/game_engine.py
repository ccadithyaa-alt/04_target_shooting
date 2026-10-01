"""
GameEngine: owns moving targets, scoring, and player-click handling.
"""

import random
import time
from math import ceil

from game.target import Target
from game.hit_detection import check_hit
from game.renderer import WIDTH, HEIGHT

NUM_TARGETS = 3
TARGET_RADIUS = 28
BASE_HIT_SCORE = 10
ROUND_DURATION = 30
MOTION_PATTERNS = ((2, 0), (0, 3), (-3, -2))


class GameEngine:
    def __init__(self):
        self._next_motion_pattern = 0
        self.start_new_round()

    def start_new_round(self):
        """Reset round state and start a fresh 30-second round."""
        self.targets = [self._random_target() for _ in range(NUM_TARGETS)]
        self.hits = 0
        self.misses = 0
        self.score = 0
        self.combo_multiplier = 1
        self.game_over = False
        self._round_started_at = time.monotonic()
        self.time_remaining = ROUND_DURATION

    def _update_timer(self):
        elapsed = time.monotonic() - self._round_started_at
        self.time_remaining = max(0, ceil(ROUND_DURATION - elapsed))
        if self.time_remaining == 0:
            self.game_over = True

    def _random_target(self):
        x = random.randint(TARGET_RADIUS + 10, WIDTH - TARGET_RADIUS - 10)
        y = random.randint(TARGET_RADIUS + 10, HEIGHT - TARGET_RADIUS - 10)
        vx, vy = MOTION_PATTERNS[self._next_motion_pattern]
        self._next_motion_pattern = (self._next_motion_pattern + 1) % len(MOTION_PATTERNS)
        return Target(x, y, radius=TARGET_RADIUS, vx=vx, vy=vy)

    def handle_click(self, pos):
        self._update_timer()
        if self.game_over:
            return

        target = check_hit(self.targets, pos)
        if target is not None:
            self.hits += 1
            self.score += BASE_HIT_SCORE * self.combo_multiplier
            self.combo_multiplier += 1
            self.targets.remove(target)
            self.targets.append(self._random_target())
        else:
            self.misses += 1
            self.combo_multiplier = 1

    def update(self):
        self._update_timer()
        if self.game_over:
            return

        for target in self.targets:
            target.update(WIDTH, HEIGHT)

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.targets)
        renderer.draw_text(
            surface,
            font,
            f"Time: {self.time_remaining}s  Score: {self.score}  Combo: x{self.combo_multiplier}  Hits: {self.hits}  Misses: {self.misses}",
            (10, 10),
        )
        if self.game_over:
            renderer.draw_banner(
                surface,
                font,
                f"TIME'S UP! Final score: {self.score} - Press R to play again",
            )
