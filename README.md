# Space Invaders (Python + Turtle)

![Python](https://img.shields.io/badge/language-Python-3776AB?logo=python&logoColor=white)
![Status](https://img.shields.io/badge/status-functional-brightgreen)

A small Space Invaders clone I built in Python using only the standard library (`turtle`). You move along the bottom, shoot the enemies drifting down the screen, and try not to get hit. It started as a university project (IPRP) and grew into something I actually enjoy playing.

## Features

- Player movement with screen-edge clamping
- Shooting with a cooldown, so no spamming
- Enemies that drift sideways, randomly change direction and fire back
- Collision detection for bullets, enemies and the player
- Win / lose screens with your final score
- Top 10 highscore table saved to a text file
- Save and load your game mid-run (`g` to save)

## Getting started

You need Python 3.8+ (no extra packages, `turtle` ships with Python).

```bash
git clone https://github.com/<your-username>/space-invaders.git
cd space-invaders
python spaceinvaders.py
```

The game expects these sprites in the same folder as the script:

```
player.gif
enemy.gif
player_bullet.gif
enemy_bullet.gif
```

On start it asks whether you want to load a saved game. Type the file name (letters only, without `.txt`) or just press Return for a new game.

## Controls

| Key | Action |
|-----|--------|
| Left / Right arrows | Move |
| Space | Shoot |
| G | Save game |
| Esc | Quit |

## How it works

The game runs a single main loop at roughly 60 FPS. Each frame it moves bullets and enemies, rolls the dice for enemy fire, checks collisions, and redraws the screen in one go (`tracer(0)` + `update()`) to avoid flicker. All game data lives in one `state` dictionary that gets passed around, which also made save/load simple: the state is written to a plain text file as `TYPE x y` lines and parsed back on load.

Highscores are stored as `score:name` lines, kept sorted, and capped at the top 10.

## Project structure

```
spaceinvaders.py     # all the game logic
highscores.txt       # created on first score
*.gif                # sprites
```

## Things I'd improve

- Split the code into modules instead of one file
- Replace the parallel lists used for save data with proper structures
- Add enemy waves, shields and difficulty levels
- Fix a few edge cases in bullet removal and collision loops
- Add sound effects

## What I practiced

Built with a focus on clean, readable code and the fundamentals:

Python 3 · procedural programming · functions and decomposition · dictionaries, lists and tuples · event-driven programming (keyboard callbacks) · game loop design · collision detection · randomness and probability · file I/O and text parsing · data persistence (save/load, leaderboards) · input validation · constants and configuration · code commenting and documentation · debugging and problem solving

## Author

Made by [Enzo R. Pinto](https://github.com/enzoribeiropinto). Feedback is welcome!
