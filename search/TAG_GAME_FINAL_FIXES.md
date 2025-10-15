# Tag Game - Final Fixes Summary

## Issue 1: State Not Persisting (Tag Count Stuck at 1)

### Problem
- Tag count remained at 1 even after multiple tags
- Ghost behavior didn't change when becoming "IT"
- Custom attributes were lost between moves

### Root Cause
The game framework creates deep copies of `GameState` on every move via `generateSuccessor()`. Our custom tag attributes weren't being preserved during these copies.

### Fix
1. **Created `TagGameStateData` class** - Extends `GameStateData`
   - Overrides `__init__` to initialize/copy tag attributes
   - Overrides `deepCopy()` to explicitly copy all attributes
   
2. **Created `TagGameState` class** - Extends `GameState`
   - Uses `TagGameStateData` instead of regular `GameStateData`
   - Overrides `generateSuccessor()` to return `TagGameState` instances
   - Increments `move_count` in `generateSuccessor()`

### Code
```python
class TagGameStateData(GameStateData):
    def __init__(self, prevState=None):
        GameStateData.__init__(self, prevState)
        if prevState is None:
            self.pacman_is_it = True
            self.tag_count = 0
            self.move_count = 0
            self.tag_cooldown = 0
        else:
            self.pacman_is_it = getattr(prevState, 'pacman_is_it', True)
            self.tag_count = getattr(prevState, 'tag_count', 0)
            self.move_count = getattr(prevState, 'move_count', 0)
            self.tag_cooldown = getattr(prevState, 'tag_cooldown', 0)

class TagGameState(GameState):
    def generateSuccessor(self, agentIndex, action):
        state = TagGameState(self)  # NOT GameState!
        # ... apply actions ...
        state.data.move_count += 1
        return state
```

---

## Issue 2: Ghost Color Not Changing

### Problem
- Ghost appeared the same color whether IT or not
- No visual indication of who was chasing

### Root Cause
Ghost color changes weren't persisting because they were being applied in the agent, not in the game rules. The changes were lost during state copies.

### Fix
Ghost appearance is now updated in `TagGameRules.process()` **every frame**:

```python
def process(self, state, game):
    # Update ghost appearance EVERY frame
    ghostState = state.data.agentStates[1]
    if state.data.pacman_is_it:
        ghostState.scaredTimer = 999  # Blue/white (scared)
    else:
        ghostState.scaredTimer = 0    # Red (aggressive)
```

---

## Issue 3: Ghost Going Through Walls

### Problem
- After tagging, ghost would escape maze boundaries
- Distance kept increasing infinitely (10.0 → 47.5 → 91.5 → ...)
- Ghost disappeared off screen

### Root Cause
When `scaredTimer > 0`, the default `GhostRules.applyAction` halves the ghost's speed to 0.5. This can cause fractional positions that escape the grid over time.

### Fix
Override `TagGhostRules.applyAction()` to **always use normal speed (1.0)**, regardless of `scaredTimer`:

```python
class TagGhostRules(GhostRules):
    @staticmethod
    def applyAction(state, action, ghostIndex):
        legal = GhostRules.getLegalActions(state, ghostIndex)
        if action not in legal:
            raise Exception("Illegal ghost action " + str(action))

        ghostState = state.data.agentStates[ghostIndex]
        
        # ALWAYS use normal speed (ignore scaredTimer for speed)
        speed = GhostRules.GHOST_SPEED  # Always 1.0
        
        from game import Actions
        vector = Actions.directionToVector(action, speed)
        ghostState.configuration = ghostState.configuration.generateSuccessor(vector)
    
    @staticmethod
    def decrementTimer(ghostState):
        # DON'T decrement scaredTimer - it's for visual indication only
        pass
```

**Key Points:**
- `scaredTimer` is now used ONLY for color, NOT for speed
- Ghost always moves at speed 1.0 (same as Pacman)
- Ghost respects wall boundaries (legal actions are checked)

---

## Issue 4: Multiple Rapid Tags

### Problem
- Tags were happening too frequently
- Hard to separate tag events

### Fix
Increased cooldown from 10 to 20 moves:

```python
def handleTag(self, state, game):
    if state.data.tag_cooldown > 0:
        return  # Ignore during cooldown
    
    state.data.pacman_is_it = not state.data.pacman_is_it
    state.data.tag_count += 1
    state.data.tag_cooldown = 20  # 20 move cooldown
```

Added debug messages for ignored tags:
```python
if state.data.tag_cooldown > 0:
    if not self.quiet and state.data.tag_cooldown % 3 == 0:
        print(f"[Tag ignored - cooldown: {state.data.tag_cooldown}]")
    return
```

---

## Complete Architecture

### File Structure
```
tagGame.py
├── TagGameStateData (extends GameStateData)
│   ├── __init__() - Initialize tag attributes
│   └── deepCopy() - Copy all attributes
├── TagGameRules
│   ├── process() - Update ghost color every frame, check tags
│   ├── checkTag() - Collision detection
│   └── handleTag() - Switch roles, increment counter
├── TagGameState (extends GameState)
│   ├── __init__() - Use TagGameStateData
│   └── generateSuccessor() - Return TagGameState
├── TagPacmanRules
│   └── applyAction() - Movement without food logic
└── TagGhostRules
    ├── applyAction() - Normal speed always
    ├── decrementTimer() - No-op (don't change scaredTimer)
    └── checkDeath() - No-op (no death in tag)

tagAgents.py
├── TagPacmanAgent
│   └── getAction() - Chase when IT, flee when not
└── TagGhostAgent
    └── getAction() - DirectionalGhost algorithm
```

### Data Flow
1. **Game Loop** calls `TagGameState.generateSuccessor(agentIndex, action)`
2. `generateSuccessor()` creates new `TagGameState` with `TagGameStateData`
3. **Agent rules** apply action (TagPacmanRules or TagGhostRules)
4. `move_count` increments
5. **TagGameRules.process()** runs:
   - Updates ghost color based on `pacman_is_it`
   - Checks for tag collision
   - If tag: calls `handleTag()` to switch roles
6. State is returned with all attributes preserved

---

## Testing Checklist

✅ **State Persistence**
- Tag count increments: 0 → 1 → 2 → 3 ...
- `pacman_is_it` toggles with each tag
- Move count increases continuously

✅ **Ghost Color**
- Blue/white when Pacman is IT
- Red when Ghost is IT
- Color changes immediately after tag

✅ **Ghost Movement**
- Ghost stays within maze boundaries
- Distance changes reasonably (not infinitely increasing)
- Ghost visible on screen at all times

✅ **Ghost Behavior**
- Ghost chases when IT (minimizes distance)
- Ghost flees when not IT (maximizes distance)
- Behavior switches immediately after tag

✅ **Cooldown System**
- 20 moves between valid tags
- Messages show cooldown countdown
- Tags ignored during cooldown

---

## Run the Game

```bash
# Normal game
python runTag.py --keyboard --layout mediumClassic --maxTags 10

# Faster gameplay
python runTag.py --keyboard --layout mediumClassic --maxTags 10 --frameTime 0.05

# Smaller maze
python runTag.py --keyboard --layout smallClassic --maxTags 5 --frameTime 0.15
```

### Expected Console Output
```
============================================================
    *** TAG! TAG! TAG! ***
    BEFORE: Pacman was IT
    NOW: GHOST IS IT!
    Ghost will now CHASE Pacman!
    Pacman will now RUN AWAY!
    Ghost color: AGGRESSIVE (Red)
    Tag Count: 1
    Cooldown set to: 20 moves
============================================================

[Move 80] IT: GHOST (Chasing) | Tags: 1 | Distance: 8.5 | Ghost scared: False

============================================================
    *** TAG! TAG! TAG! ***
    BEFORE: Ghost was IT
    NOW: PACMAN IS IT!
    Pacman will now CHASE Ghost!
    Ghost will now RUN AWAY!
    Ghost color: SCARED (Blue/White)
    Tag Count: 2
    Cooldown set to: 20 moves
============================================================
```

---

## Summary

All issues have been fixed by properly managing state persistence and separating visual indicators (`scaredTimer`) from game mechanics (speed). The game now correctly:

1. ✅ Tracks tags and increments counter
2. ✅ Changes ghost color based on who is IT
3. ✅ Keeps ghost within maze boundaries
4. ✅ Switches behavior when roles change
5. ✅ Prevents rapid re-tagging with cooldown system

