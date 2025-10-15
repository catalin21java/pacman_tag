# Ghost Wall Penetration - Technical Explanation

## The Bug

After tagging the ghost, it would go through walls and escape the maze. The distance would keep increasing:
```
[Move 80] IT: GHOST (Chasing) | Tags: 1 | Distance: 2.5 | Ghost scared: False
[Move 100] IT: GHOST (Chasing) | Tags: 1 | Distance: 8.5 | Ghost scared: False
[Move 120] IT: GHOST (Chasing) | Tags: 1 | Distance: 17.5 | Ghost scared: False
[Move 140] IT: GHOST (Chasing) | Tags: 1 | Distance: 27.5 | Ghost scared: False
[Move 160] IT: GHOST (Chasing) | Tags: 1 | Distance: 37.5 | Ghost scared: False
...
```

The ghost would literally disappear off the screen.

## Root Cause Analysis

### The scaredTimer Mechanism

In the original Pacman game, `scaredTimer` serves a dual purpose:
1. **Visual**: Makes ghosts appear blue/white when scared
2. **Mechanical**: Changes ghost behavior and speed

From `pacman.py` line 408-410:
```python
def applyAction(state, action, ghostIndex):
    ghostState = state.data.agentStates[ghostIndex]
    speed = GhostRules.GHOST_SPEED
    if ghostState.scaredTimer > 0: 
        speed /= 2.0  # HALF SPEED when scared!
```

### Our Tag Game Use

In the tag game, we set `scaredTimer = 999` when Pacman is IT to make the ghost appear blue. But this had an unintended consequence:

```python
# In TagGameRules.process()
if state.data.pacman_is_it:
    ghostState.scaredTimer = 999  # Ghost appears blue (GOOD)
    # BUT: This also causes speed = 0.5 (BAD!)
```

### The Fractional Position Problem

When ghost speed is 0.5, the ghost moves in increments of 0.5 grid units:

```
Start position: (10, 10)
After move 1:   (10.5, 10)    # Half a grid cell
After move 2:   (11.0, 10)    # One full grid cell
After move 3:   (11.5, 10)    # Half a grid cell again
...
```

#### Why This Causes Wall Penetration

The game's collision detection checks if positions are valid **discrete grid positions**. When positions become fractional:

1. **Configuration.generateSuccessor()** creates new positions using fractional movement
2. **Walls are checked at integer positions** (grid cells)
3. **Fractional positions can "slip through"** wall checks

Example:
```
Grid:  [9][10][11][12][13]
Walls:         ██

Ghost at (10, y), wall at (11, y)
- Legal actions checked at (10, y) - OK
- Ghost moves with speed=0.5 → new position (10.5, y)
- Next move from (10.5, y) with speed=0.5 → new position (11.0, y)
  - This position overlaps the wall!
- Fractional math errors accumulate
- Eventually ghost escapes grid boundaries entirely
```

From `game.py`, the `Configuration.generateSuccessor()` method:
```python
def generateSuccessor(self, vector):
    x, y = self.pos
    dx, dy = vector
    # This can create fractional positions!
    return Configuration((x + dx, y + dy), direction)
```

### Visual Evidence

The distance kept growing linearly, indicating the ghost was moving in a straight line without obstacle avoidance:
- **Move 80**: Distance 2.5
- **Move 100**: Distance 8.5 (increased by 6.0 in 20 moves)
- **Move 120**: Distance 17.5 (increased by 9.0 in 20 moves)
- **Move 140**: Distance 27.5 (increased by 10.0 in 20 moves)

This linear growth pattern shows the ghost was no longer constrained by the maze.

## The Fix

### Solution 1: Override applyAction

Force ghosts to **always use normal speed (1.0)**, regardless of `scaredTimer`:

```python
class TagGhostRules(GhostRules):
    @staticmethod
    def applyAction(state, action, ghostIndex):
        legal = GhostRules.getLegalActions(state, ghostIndex)
        if action not in legal:
            raise Exception("Illegal ghost action " + str(action))

        ghostState = state.data.agentStates[ghostIndex]
        
        # CRITICAL: Always use normal speed
        speed = GhostRules.GHOST_SPEED  # 1.0, not 0.5
        
        from game import Actions
        vector = Actions.directionToVector(action, speed)
        ghostState.configuration = ghostState.configuration.generateSuccessor(vector)
```

### Solution 2: Override decrementTimer

Prevent `scaredTimer` from being modified by game mechanics:

```python
@staticmethod
def decrementTimer(ghostState):
    """
    Don't decrement scaredTimer - we manage it manually in TagGameRules.process()
    """
    pass  # No-op
```

Without this, `GhostRules.decrementTimer` would:
1. Decrement `scaredTimer` from 999 → 998 → 997 → ...
2. When it reaches 1, snap ghost to nearest integer position
3. When it reaches 0, reset ghost state

We don't want any of this - we want full manual control.

## Why This Works

### Integer Positions Only

With speed = 1.0, all movements are in increments of 1.0:
```
Start position: (10, 10)
After move 1:   (11, 10)  # Integer position
After move 2:   (12, 10)  # Integer position
After move 3:   (13, 10)  # Integer position
...
```

### Wall Checks Are Reliable

`GhostRules.getLegalActions()` checks walls at integer positions:
```python
possibleActions = Actions.getPossibleActions(conf, state.data.layout.walls)
```

From `game.py`:
```python
def getPossibleActions(config, walls):
    possible = []
    x, y = config.pos
    # Check each direction at integer positions
    for dir, vec in Actions._directionsAsList:
        dx, dy = vec
        next_x = x + dx  # Integer arithmetic when speed=1.0
        next_y = y + dy
        if not walls[next_x][next_y]:
            possible.append(dir)
    return possible
```

When positions are always integers, wall checks are always accurate.

### Separation of Concerns

Now `scaredTimer` serves **only one purpose** in tag game:
- **Visual indicator** (blue/white vs red ghost)
- **NOT** a speed modifier
- **NOT** a game mechanic timer

## Alternative Solutions Considered

### Option A: Use Different Visual Indicator
Instead of `scaredTimer`, create a new attribute like `isChaser`.
- **Rejected**: Would require modifying graphics rendering code

### Option B: Fix Speed Calculation in generateSuccessor
Patch `Configuration.generateSuccessor()` to round positions.
- **Rejected**: Would affect other parts of the game, risky

### Option C: Keep Speed=0.5 but Add Wall Checks
Add extra wall validation after each move.
- **Rejected**: Complex, error-prone, performance overhead

### Option D: Our Solution ✓
Override `applyAction` to always use speed=1.0.
- **Accepted**: Simple, clean, no side effects

## Lessons Learned

1. **Reusing Existing Attributes**: Be careful when repurposing attributes (like `scaredTimer`) for different purposes. Understand all their side effects.

2. **Fractional Positions**: Games with discrete grids can have subtle bugs when positions become fractional.

3. **Inheritance Pitfalls**: When extending classes, you must understand what the parent methods do, including their side effects.

4. **Testing Edge Cases**: Visual bugs (ghost disappearing) often indicate deeper issues (position calculation errors).

## Verification

After the fix, ghost behavior should be:
- ✓ Distance changes in a bounded, realistic way (5.0 → 8.5 → 3.0 → 11.5)
- ✓ Ghost always visible on screen
- ✓ Ghost respects walls
- ✓ Ghost color changes work (blue when scared, red when aggressive)
- ✓ No performance issues

Test command:
```bash
python runTag.py --keyboard --layout mediumClassic --maxTags 10 --frameTime 0.1
```

After tagging the ghost, watch the distance values. They should fluctuate naturally (sometimes increasing, sometimes decreasing) as the ghost chases you through the maze, NOT increase linearly without bound.

