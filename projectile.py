import pygame
from settings import YELLOW, WHITE


class Projectile(pygame.sprite.Sprite):
    """A bullet fired by the player."""

    RADIUS = 5
    COLOR = YELLOW

    def __init__(
        self,
        pos: pygame.math.Vector2,
        direction: pygame.math.Vector2,
        speed: float,
        damage: int,
        max_range: float,
    ):
        super().__init__()
        self.pos = pos.copy()
        self.direction = direction.copy()
        self.speed = speed
        self.damage = damage
        self.max_range = max_range
        self._distance_traveled = 0.0

        r = self.RADIUS
        self.image = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.COLOR, (r, r), r)
        self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, dt: float, *args):
        move = self.direction * self.speed * dt
        self.pos += move
        self._distance_traveled += move.length()
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        if self._distance_traveled >= self.max_range:
            self.kill()
