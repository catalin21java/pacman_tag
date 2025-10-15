# Pacman Tag Game

A fun twist on the classic Pacman game where Pacman and a Ghost play tag! When one catches the other, they switch roles - the chaser becomes the one being chased.

## Game Description

- **Pacman** starts as "IT"
- When Pacman tags the Ghost, the Ghost becomes "IT"
- When the Ghost tags Pacman, Pacman becomes "IT"
- The game continues until a maximum number of tags or moves is reached

## Files Created

1. **runTag.py** - Main script to run the tag game
2. **tagGame.py** - Game rules and logic for tag mechanics
3. **tagAgents.py** - AI agents for Pacman and Ghost (with keyboard control option)

## How to Run

### Basic Usage

Run the tag game with default settings:
```bash
python runTag.py
```

### With Keyboard Control

Control Pacman yourself using the keyboard:
```bash
python runTag.py --keyboard
```

**Keyboard Controls:**
- `W` or `Up Arrow` - Move North
- `S` or `Down Arrow` - Move South  
- `A` or `Left Arrow` - Move West
- `D` or `Right Arrow` - Move East
- `Q` - Stop

### Custom Options

Choose a different map:
```bash
python runTag.py --layout mediumClassic
```

Set maximum tags before game ends:
```bash
python runTag.py --maxTags 20
```

Set maximum moves before game ends:
```bash
python runTag.py --maxMoves 500
```

Use text graphics (no GUI):
```bash
python runTag.py --textGraphics
```

Adjust game speed (seconds between frames):
```bash
python runTag.py --frameTime 0.2
```

Zoom in/out:
```bash
python runTag.py --zoom 2.0
```

### Combined Examples

Keyboard control on a medium maze with 15 tags:
```bash
python runTag.py --keyboard --layout mediumMaze --maxTags 15
```

Fast-paced AI game:
```bash
python runTag.py --layout smallClassic --frameTime 0.05 --maxTags 10
```

## All Command Line Options

```
-l, --layout LAYOUT      Layout from layouts folder (default: mediumMaze)
-k, --keyboard           Use keyboard control for Pacman
-z, --zoom FLOAT         Zoom the graphics window (default: 1.0)
-f, --frameTime FLOAT    Time delay between frames in seconds (default: 0.1)
-t, --textGraphics       Display output as text only
-q, --quietTextGraphics  Generate minimal output
--maxTags INT            Maximum tags before game ends (default: 10)
--maxMoves INT           Maximum moves before game ends (default: 1000)
--timeout INT            Maximum time for agent computation (default: 30)
```

## Available Layouts

The game works with any layout from the `layouts/` folder. Recommended layouts:
- `mediumClassic` - Classic Pacman map with ghosts  
- `mediumMaze` - Medium-sized maze
- `smallClassic` - Smaller version for quick games
- `openMaze` - Open space for high-speed chases
- `tinyMaze` - Very small map for quick tests

## Game Mechanics

### AI Behavior

**When Pacman is IT:**
- Pacman chases the Ghost (tries to minimize distance)
- Ghost runs away from Pacman (tries to maximize distance)

**When Ghost is IT:**
- Ghost chases Pacman (tries to minimize distance)  
- Pacman runs away from Ghost (tries to maximize distance)

### Scoring

- Each tag awards +10 points
- Movement has a time penalty
- Final score reflects total tags and game efficiency

## Technical Details

- Built on the UC Berkeley Pacman AI framework
- Uses Manhattan distance for AI path planning
- Tag detection uses collision tolerance from original Pacman rules
- Supports both graphical and text-based display modes

## Troubleshooting

**Problem:** No tags are happening
**Solution:** Make sure you're using a layout with ghost spawn points (like `mediumClassic`). Some maze layouts don't have ghost positions defined.

**Problem:** Game runs too fast/slow
**Solution:** Adjust `--frameTime` parameter (higher = slower, lower = faster)

**Problem:** Can't see the game window
**Solution:** Try using `--textGraphics` for console-only display

## Example Game Sessions

Watch AI play (medium speed):
```bash
python runTag.py --layout mediumClassic --maxTags 5 --frameTime 0.15
```

Play yourself:
```bash
python runTag.py --keyboard --layout mediumClassic --maxTags 10
```

Quick test:
```bash
python runTag.py --layout tinyMaze --maxTags 3 --frameTime 0.1
```

Enjoy playing tag with Pacman!

