# ZombieShooter

A **survivor.io style top-down shooter** built with Python + pygame.

![Gameplay screenshot](https://github.com/user-attachments/assets/20e49348-e644-43ba-a3fa-3f1e69f9d1c5)

## Features

- **WASD / Arrow Keys** to move the player
- **Auto-fire** – the player automatically shoots the nearest zombie
- **Wave system** – each wave spawns more / tougher zombies
- **XP & Levelling** – kill zombies to earn XP; level up to choose an upgrade
- **Upgrades** – Max HP, Speed, Fire Rate, Bullet Damage, Bullet Speed, Bullet Range
- **HUD** – HP bar, XP bar, wave counter, kill count, survival timer
- Knockback when hit by zombies

## File structure

| File | Purpose |
|------|---------|
| `main.py` | Entry point – run this to start the game |
| `game.py` | `Game` class: main loop, spawning, collision, HUD, state machine |
| `player.py` | `Player` sprite: movement, auto-shoot, XP/levelling |
| `enemy.py` | `Enemy` sprite: chase AI, scaled stats per wave |
| `projectile.py` | `Projectile` sprite: straight-line bullet with range limit |
| `settings.py` | All tunable constants (speeds, colours, wave timing, …) |
| `requirements.txt` | Python dependencies |

## Requirements

- Python 3.10+
- pygame 2.1+

```
pip install -r requirements.txt
```

## Running

```
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| W / A / S / D or Arrow Keys | Move |
| *(automatic)* | Shoot nearest enemy |
| 1 / 2 / 3 or click | Pick upgrade on level-up |
| R / Enter | Restart after game over |