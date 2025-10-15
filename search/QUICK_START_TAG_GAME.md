# Tag Game - Quick Start Guide

## Running the Game

### Basic Usage
```bash
python runTag.py --keyboard --layout mediumClassic
```

### All Options
```bash
python runTag.py [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--layout LAYOUT` | `mediumClassic` | Map layout to use |
| `--keyboard` | Off | Use keyboard controls (WASD/arrows) |
| `--maxTags N` | `10` | Game ends after N tags |
| `--maxMoves N` | `1000` | Game ends after N moves |
| `--frameTime T` | `0.1` | Seconds per frame (lower = faster) |
| `--textGraphics` | Off | Use text-only display |
| `--quiet` | Off | Suppress status messages |

### Example Commands
```bash
# Slower game for beginners
python runTag.py --keyboard --layout smallClassic --frameTime 0.2

# Fast-paced game
python runTag.py --keyboard --layout mediumClassic --frameTime 0.05 --maxTags 20

# Text mode (no graphics)
python runTag.py --keyboard --layout tinyMaze --textGraphics

# Watch AI play (no keyboard)
python runTag.py --layout mediumClassic --maxTags 5
```

## Keyboard Controls
- **W** or **Up Arrow** - Move North
- **S** or **Down Arrow** - Move South  
- **A** or **Left Arrow** - Move West
- **D** or **Right Arrow** - Move East
- **Q** - Stop (not recommended, you'll be tagged!)

## Game Rules

### Objective
Tag the other player as many times as possible before time/move limit.

### How It Works
1. **Pacman starts as IT** - Chase the ghost!
2. **Tag by touching** - Get close enough (within 1.5 Manhattan distance)
3. **Roles switch** - The tagged player becomes IT
4. **IT chases, other runs** - Behavior changes automatically
5. **Visual indicator** - Ghost color shows who is IT:
   - **Blue/White Ghost** = Pacman is IT (Ghost is scared, runs away)
   - **Red Ghost** = Ghost is IT (Ghost chases Pacman)

### Cooldown System
After a tag, there's a 20-move cooldown to prevent immediate re-tagging.

## Visual Indicators

### Ghost Color
- **Red** = Ghost is IT (aggressive, chasing)
- **Blue/White** = Pacman is IT (ghost is scared, fleeing)

### Console Messages
```
============================================================
    *** TAG! TAG! TAG! ***
    GHOST IS NOW IT!
    Ghost will now CHASE Pacman!
    Pacman will now RUN AWAY!
    Ghost color: AGGRESSIVE (Red)
    Tag Count: 2
    Cooldown set to: 20 moves
============================================================
```

### Status Updates (Every 20 Moves)
```
[Move 60] IT: GHOST (Chasing) | Tags: 3 | Distance: 5.0 | Ghost scared: False
```

## Strategies

### When You're IT
- Chase aggressively
- Cut corners to catch the ghost
- Use walls to trap the ghost

### When You're NOT IT
- Keep maximum distance
- Use maze structure to your advantage
- Don't get cornered!

## Troubleshooting

### Game ends immediately
- Make sure `--maxTags` and `--maxMoves` are set high enough
- Check that layout exists in `layouts/` folder

### Can't tag the ghost
- Collision tolerance is 1.5 Manhattan distance
- You need to be very close (adjacent or diagonal)
- Wait for cooldown to expire (20 moves)

### Ghost not changing behavior
- This was fixed in the latest version
- Ghost now uses `DirectionalGhost` algorithm
- Behavior switches automatically when roles change

### Ghost not changing color
- This was fixed in the latest version  
- Color is updated every frame in `TagGameRules.process()`
- Red = chasing, Blue/White = fleeing

## Files
- `runTag.py` - Main game launcher
- `tagGame.py` - Game rules and state management
- `tagAgents.py` - AI for Pacman and Ghost
- `layouts/*.lay` - Map files

## Have Fun!
The game is designed to be fast-paced and exciting. Try different layouts and frame times to find your perfect difficulty level!

