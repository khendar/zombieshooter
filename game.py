"""Main game module – contains the Game class and the game loop."""

import sys
import random
import pygame
import pygame.freetype

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    BG_COLOR, WHITE, BLACK, RED, GREEN, DARK_GREEN, YELLOW,
    ORANGE, GRAY, DARK_GRAY, LIGHT_GRAY, PURPLE,
    HUD_MARGIN, HP_BAR_WIDTH, HP_BAR_HEIGHT, XP_BAR_WIDTH, XP_BAR_HEIGHT,
    WAVE_DURATION, WAVE_ENEMIES_BASE, WAVE_ENEMIES_SCALE, SPAWN_MARGIN,
    ENEMY_DAMAGE, UPGRADE_OPTIONS, UPGRADE_CHOICES, XP_PER_KILL,
)
from player import Player
from enemy import Enemy
from projectile import Projectile


class Game:
    """Manages game state, the main loop and all subsystems."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # Font
        self.font_large = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 22)
        self.font_small = pygame.font.SysFont("Arial", 16)

        self._reset()

    # ------------------------------------------------------------------
    # Public entry-point
    # ------------------------------------------------------------------

    def run(self):
        """Start the game loop."""
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)  # cap dt to avoid spiral of death

            self._handle_events()

            if self.state == "playing":
                self._update(dt)
                self._draw_playing()
            elif self.state == "upgrade":
                self._draw_upgrade()
            elif self.state == "game_over":
                self._draw_game_over()
            elif self.state == "title":
                self._draw_title()

            pygame.display.flip()

    # ------------------------------------------------------------------
    # Initialisation / reset
    # ------------------------------------------------------------------

    def _reset(self):
        self.state = "title"

        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()

        # Player
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.all_sprites.add(self.player)

        # Wave
        self.wave = 1
        self.wave_timer = WAVE_DURATION
        self.kill_count = 0

        # Upgrade screen state
        self._upgrade_choices: list[dict] = []

        # Score (survival time in seconds)
        self.score: float = 0.0

        # Background grid (decorative)
        self._bg_surface = self._make_bg()

    def _make_bg(self) -> pygame.Surface:
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surf.fill(BG_COLOR)
        grid_color = (45, 45, 45)
        for x in range(0, SCREEN_WIDTH, 48):
            pygame.draw.line(surf, grid_color, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 48):
            pygame.draw.line(surf, grid_color, (0, y), (SCREEN_WIDTH, y))
        return surf

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.state == "title" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._start_game()
                elif self.state == "game_over" and event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_r):
                    self._reset()
                    self._start_game()
                elif self.state == "upgrade":
                    if event.key == pygame.K_1 and len(self._upgrade_choices) >= 1:
                        self._select_upgrade(0)
                    elif event.key == pygame.K_2 and len(self._upgrade_choices) >= 2:
                        self._select_upgrade(1)
                    elif event.key == pygame.K_3 and len(self._upgrade_choices) >= 3:
                        self._select_upgrade(2)
            if event.type == pygame.MOUSEBUTTONDOWN and self.state == "upgrade":
                self._handle_upgrade_click(event.pos)

    def _start_game(self):
        self.state = "playing"
        self._spawn_wave()

    # ------------------------------------------------------------------
    # Update (playing state)
    # ------------------------------------------------------------------

    def _update(self, dt: float):
        self.score += dt

        # Player
        new_bullets = self.player.update(dt, self.enemies)
        for b in new_bullets:
            self.all_sprites.add(b)
            self.bullets.add(b)

        # Enemies
        for enemy in self.enemies:
            enemy.update(dt, self.player.pos)

        # Bullets
        self.bullets.update(dt)

        # Bullet–enemy collisions
        self._resolve_bullet_hits()

        # Player–enemy collisions (contact damage)
        self._resolve_player_contact(dt)

        # Wave timer
        self.wave_timer = max(0.0, self.wave_timer - dt)
        if self.wave_timer == 0:
            self.wave += 1
            self.wave_timer = WAVE_DURATION
            self._spawn_wave()

        # Check level-up
        if self.player.pending_levelups > 0:
            self.player.pending_levelups -= 1
            self._begin_upgrade()

        # Check death
        if self.player.is_dead:
            self.state = "game_over"

    def _spawn_wave(self):
        count = WAVE_ENEMIES_BASE + WAVE_ENEMIES_SCALE * (self.wave - 1)
        for _ in range(count):
            e = Enemy(self.wave)
            self.all_sprites.add(e)
            self.enemies.add(e)

    def _resolve_bullet_hits(self):
        hits = pygame.sprite.groupcollide(
            self.bullets, self.enemies,
            False, False,
            collided=pygame.sprite.collide_circle,
        )
        for bullet, hit_enemies in hits.items():
            bullet.kill()
            for enemy in hit_enemies:
                died = enemy.take_damage(bullet.damage)
                if died:
                    self.kill_count += 1
                    self.player.gain_xp(XP_PER_KILL)
                    enemy.kill()

    def _resolve_player_contact(self, dt: float):
        touching = pygame.sprite.spritecollide(
            self.player, self.enemies, False,
            collided=pygame.sprite.collide_circle,
        )
        for enemy in touching:
            self.player.take_damage(enemy.damage * dt, enemy.pos)

    # ------------------------------------------------------------------
    # Upgrade flow
    # ------------------------------------------------------------------

    def _begin_upgrade(self):
        self.state = "upgrade"
        num = min(UPGRADE_CHOICES, len(UPGRADE_OPTIONS))
        self._upgrade_choices = random.sample(UPGRADE_OPTIONS, num)

    def _select_upgrade(self, index: int):
        if 0 <= index < len(self._upgrade_choices):
            self.player.apply_upgrade(self._upgrade_choices[index])
        self.state = "playing"
        self._upgrade_choices = []

    def _handle_upgrade_click(self, mouse_pos: tuple[int, int]):
        for i, rect in enumerate(self._upgrade_rects):
            if rect.collidepoint(mouse_pos):
                self._select_upgrade(i)
                return

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _draw_playing(self):
        self.screen.blit(self._bg_surface, (0, 0))
        self.all_sprites.draw(self.screen)
        self._draw_enemy_hp_bars()
        self._draw_hud()

    def _draw_enemy_hp_bars(self):
        for enemy in self.enemies:
            if enemy.hp_fraction < 1.0:
                bar_w = enemy.radius * 2
                bar_h = 4
                x = enemy.rect.left
                y = enemy.rect.top - 7
                pygame.draw.rect(self.screen, DARK_GRAY, (x, y, bar_w, bar_h))
                pygame.draw.rect(self.screen, GREEN, (x, y, int(bar_w * enemy.hp_fraction), bar_h))

    def _draw_hud(self):
        m = HUD_MARGIN

        # --- HP bar ---
        hp_x, hp_y = m, m
        self._draw_bar(hp_x, hp_y, HP_BAR_WIDTH, HP_BAR_HEIGHT,
                       self.player.hp_fraction, RED, DARK_GRAY)
        hp_text = self.font_small.render(
            f"HP  {int(self.player.hp)}/{self.player.max_hp}", True, WHITE)
        self.screen.blit(hp_text, (hp_x + HP_BAR_WIDTH + 8, hp_y + 1))

        # --- XP bar ---
        xp_y = hp_y + HP_BAR_HEIGHT + 6
        self._draw_bar(m, xp_y, XP_BAR_WIDTH, XP_BAR_HEIGHT,
                       self.player.xp_fraction, PURPLE, DARK_GRAY)
        xp_text = self.font_small.render(
            f"LV {self.player.level}  {self.player.xp}/{self.player.xp_to_next} XP", True, WHITE)
        self.screen.blit(xp_text, (m + XP_BAR_WIDTH + 8, xp_y))

        # --- Wave & timer ---
        wave_text = self.font_medium.render(
            f"Wave {self.wave}  |  Next: {self.wave_timer:.1f}s", True, YELLOW)
        self.screen.blit(wave_text, (SCREEN_WIDTH // 2 - wave_text.get_width() // 2, m))

        # --- Kill count ---
        kill_text = self.font_small.render(f"Kills: {self.kill_count}", True, LIGHT_GRAY)
        self.screen.blit(kill_text, (SCREEN_WIDTH - kill_text.get_width() - m, m))

        # --- Survival time ---
        time_text = self.font_small.render(f"Time: {int(self.score)}s", True, LIGHT_GRAY)
        self.screen.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - m,
                                      m + kill_text.get_height() + 4))

    def _draw_bar(self, x, y, w, h, fraction, color_fill, color_bg):
        pygame.draw.rect(self.screen, color_bg, (x, y, w, h), border_radius=3)
        fill_w = max(0, int(w * fraction))
        if fill_w > 0:
            pygame.draw.rect(self.screen, color_fill, (x, y, fill_w, h), border_radius=3)
        pygame.draw.rect(self.screen, GRAY, (x, y, w, h), 1, border_radius=3)

    def _draw_upgrade(self):
        self.screen.blit(self._bg_surface, (0, 0))
        self.all_sprites.draw(self.screen)

        # Dim overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        title = self.font_large.render("LEVEL UP! Choose an upgrade:", True, YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

        card_w, card_h = 260, 90
        gap = 24
        total_w = len(self._upgrade_choices) * card_w + (len(self._upgrade_choices) - 1) * gap
        start_x = SCREEN_WIDTH // 2 - total_w // 2
        card_y = SCREEN_HEIGHT // 2 - card_h // 2

        self._upgrade_rects = []
        for i, upgrade in enumerate(self._upgrade_choices):
            card_x = start_x + i * (card_w + gap)
            card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
            self._upgrade_rects.append(card_rect)

            # Check hover
            mx, my = pygame.mouse.get_pos()
            hovered = card_rect.collidepoint(mx, my)
            bg_color = (80, 80, 120) if hovered else (50, 50, 80)

            pygame.draw.rect(self.screen, bg_color, card_rect, border_radius=10)
            pygame.draw.rect(self.screen, YELLOW if hovered else GRAY, card_rect, 2, border_radius=10)

            # Key hint
            key_surf = self.font_large.render(str(i + 1), True, YELLOW)
            self.screen.blit(key_surf, (card_x + 12, card_y + 8))

            # Upgrade name
            name_surf = self.font_medium.render(upgrade["name"], True, WHITE)
            self.screen.blit(name_surf, (
                card_x + card_w // 2 - name_surf.get_width() // 2,
                card_y + card_h // 2 - name_surf.get_height() // 2,
            ))

        hint = self.font_small.render("Press 1 / 2 / 3  or  click a card", True, LIGHT_GRAY)
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                                 card_y + card_h + 20))

    def _draw_title(self):
        self.screen.blit(self._bg_surface, (0, 0))

        title = self.font_large.render("ZOMBIE SHOOTER", True, YELLOW)
        subtitle = self.font_medium.render("Survivor.io style – top-down shooter", True, LIGHT_GRAY)
        controls = [
            "WASD / Arrow Keys  – Move",
            "Auto-fire           – Shoots nearest zombie",
            "Kill zombies to earn XP and level up",
            "Survive as long as you can!",
        ]
        start = self.font_large.render("Press ENTER or SPACE to start", True, GREEN)

        self.screen.blit(title,
                         (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 3 - 40))
        self.screen.blit(subtitle,
                         (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, SCREEN_HEIGHT // 3 + 20))

        for i, line in enumerate(controls):
            surf = self.font_small.render(line, True, WHITE)
            self.screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2,
                                     SCREEN_HEIGHT // 2 + i * 26))

        self.screen.blit(start,
                         (SCREEN_WIDTH // 2 - start.get_width() // 2, SCREEN_HEIGHT * 3 // 4))

    def _draw_game_over(self):
        self.screen.blit(self._bg_surface, (0, 0))

        over = self.font_large.render("GAME OVER", True, RED)
        score_surf = self.font_medium.render(
            f"Survived: {int(self.score)}s   |   Kills: {self.kill_count}   |   Level: {self.player.level}",
            True, WHITE,
        )
        restart = self.font_medium.render("Press ENTER / R to restart", True, GREEN)

        self.screen.blit(over, (SCREEN_WIDTH // 2 - over.get_width() // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(score_surf, (SCREEN_WIDTH // 2 - score_surf.get_width() // 2,
                                       SCREEN_HEIGHT // 3 + 60))
        self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2,
                                    SCREEN_HEIGHT // 2))
