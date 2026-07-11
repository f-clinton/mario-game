# Super Python Bros

A small Mario-style platformer built with [pygame](https://www.pygame.org/).

Run, jump, stomp Goombas, collect coins, and reach the flagpole across two
side-scrolling levels.

## Setup

```bash
pip install -r requirements.txt
python main.py
```

## Controls

| Key | Action |
| --- | --- |
| Left / Right or A / D | Move |
| Space, Up, or W | Jump |
| Enter | Start / restart |
| Esc | Quit |

## Gameplay

- Jump on top of Goombas to squish them; touching them from the side costs a life.
- Hit `?` blocks from below to pop out a coin.
- Watch out for pits — falling off the bottom of the screen costs a life.
- Reach the flagpole to clear the level. Clear both levels to win.

## Project structure

- `settings.py` — screen size, physics constants, colors
- `levels.py` — declarative level layouts (ground gaps, blocks, pipes, enemies, coins, flag)
- `entities.py` — `Player` and `Goomba` classes with movement/collision
- `game.py` — main game loop, level building, HUD, and state machine
- `main.py` — entry point
