# Screen
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
TITLE = "ZombieShooter"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
DARK_GREEN = (20, 120, 20)
BLUE = (50, 100, 220)
YELLOW = (255, 220, 0)
ORANGE = (255, 140, 0)
GRAY = (120, 120, 120)
DARK_GRAY = (40, 40, 40)
LIGHT_GRAY = (200, 200, 200)
PURPLE = (160, 32, 240)
BG_COLOR = (30, 30, 30)

# Player
PLAYER_SPEED = 200           # pixels per second
PLAYER_MAX_HP = 100
PLAYER_RADIUS = 16
PLAYER_COLOR = BLUE
PLAYER_SHOOT_COOLDOWN = 0.3  # seconds between shots
PLAYER_BULLET_SPEED = 500
PLAYER_BULLET_DAMAGE = 25
PLAYER_BULLET_RANGE = 600    # pixels

# XP & Leveling
XP_PER_KILL = 10
LEVEL_XP_BASE = 50           # XP required for level 2
LEVEL_XP_MULTIPLIER = 1.4    # each level costs more XP

# Upgrades offered on level-up
UPGRADE_OPTIONS = [
    {"name": "Max HP +20",      "stat": "max_hp",          "value": 20},
    {"name": "Speed +30",       "stat": "speed",           "value": 30},
    {"name": "Fire Rate +20%",  "stat": "shoot_cooldown",  "value": -0.06},
    {"name": "Bullet Dmg +10",  "stat": "bullet_damage",   "value": 10},
    {"name": "Bullet Speed +100","stat": "bullet_speed",   "value": 100},
    {"name": "Bullet Range +150","stat": "bullet_range",   "value": 150},
]
UPGRADE_CHOICES = 3          # options shown per level-up

# Enemies
ENEMY_RADIUS = 14
ENEMY_COLOR = RED
ENEMY_SPEED_BASE = 80        # pixels per second
ENEMY_SPEED_SCALE = 5        # extra speed added per wave
ENEMY_HP_BASE = 40
ENEMY_HP_SCALE = 10          # extra HP per wave
ENEMY_DAMAGE = 15            # damage dealt to player on contact
ENEMY_KNOCKBACK = 120        # pixels per second applied to player

# Spawning
SPAWN_MARGIN = 60            # how far outside screen edges enemies spawn
WAVE_DURATION = 15.0         # seconds before next wave
WAVE_ENEMIES_BASE = 8        # enemies in wave 1
WAVE_ENEMIES_SCALE = 4       # extra enemies per wave

# HUD
HUD_MARGIN = 12
HP_BAR_WIDTH = 180
HP_BAR_HEIGHT = 18
XP_BAR_WIDTH = 180
XP_BAR_HEIGHT = 12
