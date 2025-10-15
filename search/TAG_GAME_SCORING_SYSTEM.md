# Tag Game Scoring System

## Overview
The tag game now features a competitive scoring system where Pacman and Phantom (Ghost) race to 1000 points!

## How It Works

### Scoring
- **Points are awarded when you're being chased** (i.e., when you're NOT "it")
- You earn **3.33 points per move** while being chased
- Approximately **30 seconds of being chased = 1000 points**

### Win Condition
- **First player to reach 1000 points wins!**
- The game ends immediately when a player reaches 1000 points
- A graphical win message is displayed on screen
- Console output shows the final statistics

### Display
The game now shows **two separate score counters**:
- **PACMAN score** (displayed in yellow on the left)
- **PHANTOM score** (displayed in red on the right)

Both scores are updated in real-time during gameplay.

### Strategy
- When you're "it" (the chaser), you want to tag the other player quickly
- When you're being chased, try to evade as long as possible to earn points
- Tags switch who is "it", so the game is very dynamic!

## Example Game Flow

1. **Start**: Pacman is "it" and starts chasing the Phantom
   - Phantom earns ~3.33 points per move
   
2. **Tag!**: Pacman catches the Phantom
   - Roles switch: Phantom becomes "it"
   - Pacman now earns points while being chased
   
3. **Continue**: The chase continues with roles reversing at each tag

4. **Victory**: First to 1000 points wins!
   - Win message appears on screen
   - Final statistics are displayed

## Technical Details

### Files Modified
1. **tagGame.py**
   - Added `pacman_score` and `phantom_score` to `TagGameStateData`
   - Modified `process()` to award points each move
   - Added `winGame()` method for handling victories
   - Updated status messages to show both scores

2. **graphicsDisplay.py**
   - Added `updateTagScores()` to `InfoPane` class
   - Added `showWinMessage()` for victory display
   - Modified `update()` to call score updates

### Scoring Rate Calculation
- Frame time: 0.1 seconds (default)
- Target time: 30 seconds
- Moves in 30 seconds: ~300 moves (alternating between players)
- Points needed: 1000
- Points per move: 1000 / 300 ≈ **3.33 points/move**

## Running the Game

```bash
# Standard game
python runTag.py

# Faster gameplay
python runTag.py --frameTime 0.05

# With keyboard control
python runTag.py --keyboard

# Different layout
python runTag.py --layout mediumMaze
```

Enjoy the competitive tag game!

