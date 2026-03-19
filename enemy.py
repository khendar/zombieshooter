import pygame
import math
import random
from settings import (
    ENEMY_RADIUS, ENEMY_COLOR, ENEMY_SPEED_BASE, ENEMY_SPEED_SCALE,
    ENEMY_HP_BASE, ENEMY_HP_SCALE, ENEMY_DAMAGE, SCREEN_WIDTH,
    SCREEN_HEIGHT, SPAWN_MARGIN, WHITE, RED, DARK_GRAY,
)


class Enemy(pygame.sprite.Sprite):
    """A basic zombie enemy that moves toward the player."""

    def __init__(self, wave: int = 1):
        super().__init__()
        self.radius = ENEMY_RADIUS
        self.wave = wave

        # Stats scale with wave number
        self.max_hp: float = ENEMY_HP_BASE + ENEMY_HP_SCALE * (wave - 1)
        self.hp: float = self.max_hp
        self.speed: float = ENEMY_SPEED_BASE + ENEMY_SPEED_SCALE * (wave - 1)
        self.damage: float = ENEMY_DAMAGE

        # Build image
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self._draw_sprite()
        self.rect = self.image.get_rect()

        # Spawn outside screen edges
        self.pos = pygame.math.Vector2(self._random_spawn_pos())
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, dt: float, player_pos: pygame.math.Vector2):
        direction = player_pos - self.pos
        if direction.length() > 0:
            direction = direction.normalize()
            self.pos += direction * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def take_damage(self, amount: float) -> bool:
        """Apply damage; returns True if enemy died."""
        self.hp -= amount
        # Redraw with updated HP tint
        self._draw_sprite()
        return self.hp <= 0

    @property
    def hp_fraction(self) -> float:
        return max(0.0, self.hp / self.max_hp)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _draw_sprite(self):
        self.image.fill((0, 0, 0, 0))
        # Body color shifts toward white as HP drops (hit flash)
        ratio = self.hp_fraction
        r = int(ENEMY_COLOR[0] + (255 - ENEMY_COLOR[0]) * (1 - ratio) * 0.4)
        g = int(ENEMY_COLOR[1] + (255 - ENEMY_COLOR[1]) * (1 - ratio) * 0.4)
        b = int(ENEMY_COLOR[2] + (255 - ENEMY_COLOR[2]) * (1 - ratio) * 0.4)
        color = (min(255, r), min(255, g), min(255, b))
        pygame.draw.circle(self.image, color, (self.radius, self.radius), self.radius)
        # Menacing "X" eyes
        eye_y = self.radius - 4
        for ex in (self.radius - 5, self.radius + 5):
            pygame.draw.line(self.image, DARK_GRAY, (ex - 2, eye_y - 2), (ex + 2, eye_y + 2), 2)
            pygame.draw.line(self.image, DARK_GRAY, (ex + 2, eye_y - 2), (ex - 2, eye_y + 2), 2)

    @staticmethod
    def _random_spawn_pos() -> tuple[float, float]:
        edge = random.randint(0, 3)
        m = SPAWN_MARGIN
        if edge == 0:  # top
            return random.uniform(0, SCREEN_WIDTH), -m
        elif edge == 1:  # bottom
            return random.uniform(0, SCREEN_WIDTH), SCREEN_HEIGHT + m
        elif edge == 2:  # left
            return -m, random.uniform(0, SCREEN_HEIGHT)
        else:  # right
            return SCREEN_WIDTH + m, random.uniform(0, SCREEN_HEIGHT)
