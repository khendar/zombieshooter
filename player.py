import pygame
import math
from settings import (
    PLAYER_SPEED, PLAYER_MAX_HP, PLAYER_RADIUS, PLAYER_COLOR,
    PLAYER_SHOOT_COOLDOWN, PLAYER_BULLET_SPEED, PLAYER_BULLET_DAMAGE,
    PLAYER_BULLET_RANGE, XP_PER_KILL, LEVEL_XP_BASE, LEVEL_XP_MULTIPLIER,
    UPGRADE_OPTIONS, UPGRADE_CHOICES, WHITE, DARK_GRAY,
)


class Player(pygame.sprite.Sprite):
    """Player character controlled with WASD / arrow keys.

    Auto-fires bullets toward the nearest enemy.
    """

    def __init__(self, x: float, y: float):
        super().__init__()
        self.radius = PLAYER_RADIUS

        # Build image
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, PLAYER_COLOR, (self.radius, self.radius), self.radius)
        # Direction indicator (small triangle at the top)
        pygame.draw.polygon(
            self.image, WHITE,
            [(self.radius, 2), (self.radius - 5, self.radius - 2), (self.radius + 5, self.radius - 2)],
        )

        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)

        # Stats (can be modified by upgrades)
        self.max_hp: int = PLAYER_MAX_HP
        self.hp: float = float(self.max_hp)
        self.speed: float = PLAYER_SPEED
        self.shoot_cooldown: float = PLAYER_SHOOT_COOLDOWN
        self.bullet_speed: float = PLAYER_BULLET_SPEED
        self.bullet_damage: int = PLAYER_BULLET_DAMAGE
        self.bullet_range: float = PLAYER_BULLET_RANGE

        # XP / leveling
        self.xp: int = 0
        self.level: int = 1
        self.xp_to_next: int = LEVEL_XP_BASE

        # Shooting timer
        self._shoot_timer: float = 0.0

        # Knockback velocity
        self._kb_vel: pygame.math.Vector2 = pygame.math.Vector2(0, 0)
        self._kb_decay: float = 8.0  # how fast knockback fades

        # Pending level-ups (filled by game loop)
        self.pending_levelups: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, dt: float, enemies: pygame.sprite.Group) -> list:
        """Update player each frame.

        Returns a list of newly spawned :class:`Projectile` instances.
        """
        self._handle_movement(dt)
        self._handle_knockback(dt)
        self._clamp_to_screen()

        self._shoot_timer = max(0.0, self._shoot_timer - dt)
        new_bullets = self._try_shoot(dt, enemies)
        return new_bullets

    def take_damage(self, amount: float, source_pos: pygame.math.Vector2 | None = None):
        self.hp = max(0.0, self.hp - amount)
        if source_pos is not None:
            direction = self.pos - source_pos
            if direction.length() > 0:
                direction = direction.normalize()
                from settings import ENEMY_KNOCKBACK
                self._kb_vel = direction * ENEMY_KNOCKBACK

    def gain_xp(self, amount: int):
        self.xp += amount
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = int(LEVEL_XP_BASE * (LEVEL_XP_MULTIPLIER ** (self.level - 1)))
            self.pending_levelups += 1

    def apply_upgrade(self, upgrade: dict):
        stat = upgrade["stat"]
        value = upgrade["value"]
        if stat == "max_hp":
            self.max_hp += value
            self.hp = min(self.hp + value, self.max_hp)
        elif stat == "speed":
            self.speed += value
        elif stat == "shoot_cooldown":
            self.shoot_cooldown = max(0.05, self.shoot_cooldown + value)
        elif stat == "bullet_damage":
            self.bullet_damage += value
        elif stat == "bullet_speed":
            self.bullet_speed += value
        elif stat == "bullet_range":
            self.bullet_range += value

    @property
    def is_dead(self) -> bool:
        return self.hp <= 0

    @property
    def xp_fraction(self) -> float:
        return self.xp / self.xp_to_next

    @property
    def hp_fraction(self) -> float:
        return self.hp / self.max_hp

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _handle_movement(self, dt: float):
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        move = pygame.math.Vector2(dx, dy)
        if move.length() > 0:
            move = move.normalize() * self.speed * dt
            self.pos += move

    def _handle_knockback(self, dt: float):
        if self._kb_vel.length() > 0:
            self.pos += self._kb_vel * dt
            self._kb_vel *= max(0.0, 1.0 - self._kb_decay * dt)
            if self._kb_vel.length() < 1:
                self._kb_vel = pygame.math.Vector2(0, 0)

    def _clamp_to_screen(self):
        from settings import SCREEN_WIDTH, SCREEN_HEIGHT
        self.pos.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.pos.y))
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def _try_shoot(self, dt: float, enemies: pygame.sprite.Group) -> list:
        if self._shoot_timer > 0 or not enemies:
            return []
        target = self._nearest_enemy(enemies)
        if target is None:
            return []
        self._shoot_timer = self.shoot_cooldown
        from projectile import Projectile
        direction = pygame.math.Vector2(target.pos - self.pos)
        if direction.length() == 0:
            return []
        direction = direction.normalize()
        bullet = Projectile(
            self.pos.copy(), direction,
            self.bullet_speed, self.bullet_damage, self.bullet_range,
        )
        return [bullet]

    def _nearest_enemy(self, enemies: pygame.sprite.Group):
        nearest = None
        nearest_dist = float("inf")
        for enemy in enemies:
            dist = self.pos.distance_to(enemy.pos)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest = enemy
        return nearest
