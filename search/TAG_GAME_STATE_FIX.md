# Tag Game - Critical State Management Fixes

## Problem Summary
The tag game had a critical issue where state was NOT persisting correctly between moves:
- Tag count remained stuck at 1
- Ghost did not change behavior when becoming "IT"
- Ghost color did not change
- Tags were being detected but roles weren't switching

## Root Cause
The game framework creates deep copies of `GameState` objects on every move using `generateSuccessor()`. Our custom tag attributes (`pacman_is_it`, `tag_count`, etc.) were being lost during these copies.

## Solution Architecture

### 1. Custom GameStateData Class (`TagGameStateData`)
Created a custom data class that properly preserves tag attributes:

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
            # Copy from previous state
            self.pacman_is_it = getattr(prevState, 'pacman_is_it', True)
            self.tag_count = getattr(prevState, 'tag_count', 0)
            self.move_count = getattr(prevState, 'move_count', 0)
            self.tag_cooldown = getattr(prevState, 'tag_cooldown', 0)
    
    def deepCopy(self):
        # CRITICAL: Return TagGameStateData, not GameStateData!
        state = TagGameStateData.__new__(TagGameStateData)
        # ... copy all parent attributes ...
        # ... copy all tag attributes ...
        return state
```

**Key Points:**
- Inherits from `GameStateData`
- Initializes tag attributes in `__init__`
- Overrides `deepCopy()` to explicitly copy ALL attributes (parent + custom)

### 2. Custom GameState Class (`TagGameState`)
Extended GameState to use our custom data class:

```python
class TagGameState(GameState):
    def __init__(self, prevState=None):
        if prevState != None:
            self.data = TagGameStateData(prevState.data)
        else:
            self.data = TagGameStateData()
    
    def generateSuccessor(self, agentIndex, action):
        # CRITICAL: Return TagGameState, not GameState!
        state = TagGameState(self)
        # ... apply actions ...
        state.data.move_count += 1
        return state
```

**Key Points:**
- Uses `TagGameStateData` instead of `GameStateData`
- Overrides `generateSuccessor()` to return `TagGameState` instances
- Increments `move_count` in `generateSuccessor()` to track game progress

### 3. Ghost Color Management (in `TagGameRules.process()`)
Ghost color is now updated EVERY frame, not just when tags occur:

```python
def process(self, state, game):
    # Update ghost appearance based on who is IT (EVERY frame!)
    ghostState = state.data.agentStates[1]
    if state.data.pacman_is_it:
        ghostState.scaredTimer = 999  # Blue/white color
    else:
        ghostState.scaredTimer = 0    # Red color
    
    # Check for tags
    if self.checkTag(pacmanPos, ghostPos):
        self.handleTag(state, game)
```

**Why This Works:**
- `scaredTimer > 0` makes ghosts appear blue/white (scared)
- `scaredTimer = 0` makes ghosts appear red (aggressive)
- Setting this EVERY frame ensures the color is always correct

### 4. Tag Cooldown System
Prevents multiple tags from registering in rapid succession:

```python
def handleTag(self, state, game):
    if state.data.tag_cooldown > 0:
        return  # Ignore tag during cooldown
    
    # Execute tag
    state.data.pacman_is_it = not state.data.pacman_is_it
    state.data.tag_count += 1
    state.data.tag_cooldown = 20  # 20 move cooldown
```

The cooldown is decremented in `process()` each frame.

### 5. Ghost AI Behavior (in `TagGhostAgent`)
Ghost uses `DirectionalGhost` algorithm from the main game:

```python
def getAction(self, state):
    # Read who is IT from state
    pacman_is_it = state.data.pacman_is_it
    
    # Calculate distances for each action
    distancesToPacman = [...]
    
    if pacman_is_it:
        # Pacman is IT - Ghost RUNS AWAY (maximize distance)
        bestScore = max(distancesToPacman)
    else:
        # Ghost is IT - Ghost CHASES (minimize distance)
        bestScore = min(distancesToPacman)
    
    # Build probability distribution and choose action
    return util.chooseFromDistribution(dist)
```

## Testing
Run the game with:
```bash
python runTag.py --keyboard --layout mediumClassic --maxTags 10
```

**Expected Behavior:**
1. Pacman starts as IT (Ghost appears blue/white, runs away)
2. When Pacman tags Ghost:
   - Ghost becomes IT (turns red, starts chasing)
   - Tag count increments
   - 20-move cooldown begins
3. When Ghost tags Pacman:
   - Pacman becomes IT (Ghost turns blue/white again)
   - Tag count increments again
   - Roles continue to switch with each tag

## Key Takeaways
1. **State Persistence**: When extending framework classes, you must override ALL copy methods
2. **Deep Copies**: Ensure `deepCopy()` returns the correct class type
3. **generateSuccessor**: This is called on every move - it must preserve custom state
4. **Visual Indicators**: Use existing framework features (like `scaredTimer`) for visual feedback
5. **Debugging**: Print statements help track state across frames

