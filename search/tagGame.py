from game import GameStateData, Game, Directions, Actions
from pacman import GameState, PacmanRules, GhostRules, COLLISION_TOLERANCE, TIME_PENALTY
from util import manhattanDistance, nearestPoint
import util
import layout
import sys
import types
import time
import random
import os

class TagGameStateData(GameStateData):
    def __init__(self, prevState=None):
        # Call parent init first
        GameStateData.__init__(self, prevState)
        
        # Initialize tag-specific attributes  
        if prevState is None:
            # Brand new state
            self.pacman_is_it = True
            self.tag_count = 0
            self.move_count = 0
            self.tag_cooldown = 0
            self.pacman_score = 0
            self.phantom_score = 0
        else:
            # Copy from previous state
            self.pacman_is_it = getattr(prevState, 'pacman_is_it', True)
            self.tag_count = getattr(prevState, 'tag_count', 0)
            self.move_count = getattr(prevState, 'move_count', 0)
            self.tag_cooldown = getattr(prevState, 'tag_cooldown', 0)
            self.pacman_score = getattr(prevState, 'pacman_score', 0)
            self.phantom_score = getattr(prevState, 'phantom_score', 0)
        
    def deepCopy(self):
        # Create a NEW TagGameStateData (not GameStateData!)
        state = TagGameStateData.__new__(TagGameStateData)
        # Manually copy all attributes from parent class
        state.food = self.food.deepCopy()
        state.layout = self.layout.deepCopy()
        state._agentMoved = self._agentMoved
        state._foodEaten = self._foodEaten
        state._foodAdded = self._foodAdded
        state._capsuleEaten = self._capsuleEaten
        state.agentStates = self.copyAgentStates(self.agentStates)
        state.score = self.score
        state._eaten = self._eaten[:]
        state.scoreChange = self.scoreChange
        state._lose = self._lose
        state._win = self._win
        state.capsules = self.capsules[:]
        # NOW copy our tag attributes
        state.pacman_is_it = self.pacman_is_it
        state.tag_count = self.tag_count
        state.move_count = self.move_count
        state.tag_cooldown = self.tag_cooldown
        state.pacman_score = self.pacman_score
        state.phantom_score = self.phantom_score
        return state

class TagGameRules:
    def __init__(self, timeout=30, maxTags=10, maxMoves=1000):
        self.timeout = timeout
        self.maxTags = maxTags  # Game ends after this many tags
        self.maxMoves = maxMoves  # Game ends after this many moves
        self.last_status_move = 0  # Track when we last showed status
        
    def newGame(self, layout, pacmanAgent, ghostAgents, display, quiet=False, catchExceptions=False):
        # Ensure we have exactly one ghost
        if len(ghostAgents) == 0:
            raise Exception("Tag game requires at least one ghost agent")
        agents = [pacmanAgent] + [ghostAgents[0]]  # Only one ghost for tag
        initState = TagGameState()
        # Get the number of ghosts actually in the layout
        num_layout_ghosts = layout.getNumGhosts()
        if num_layout_ghosts == 0:
            # If layout has no ghosts, we need to add one programmatically
            # Use at least 1 ghost position
            initState.initialize(layout, max(1, num_layout_ghosts))
        else:
            # Use the ghosts from the layout, but limit to 1
            initState.initialize(layout, 1)
        game = Game(agents, display, self, catchExceptions=catchExceptions)
        game.state = initState
        self.initialState = initState.deepCopy()
        self.quiet = quiet
        return game
        
    def process(self, state, game):
        # Override any win/lose conditions from standard Pacman
        state.data._win = False
        state.data._lose = False
        
        # Initialize if needed
        if not hasattr(state.data, 'pacman_is_it'):
            state.data.pacman_is_it = True
        if not hasattr(state.data, 'tag_count'):
            state.data.tag_count = 0
        if not hasattr(state.data, 'move_count'):
            state.data.move_count = 0
        if not hasattr(state.data, 'tag_cooldown'):
            state.data.tag_cooldown = 0
        if not hasattr(state.data, 'pacman_score'):
            state.data.pacman_score = 0
        if not hasattr(state.data, 'phantom_score'):
            state.data.phantom_score = 0
            
        # Decrement cooldown timer
        if state.data.tag_cooldown > 0:
            state.data.tag_cooldown -= 1
        
        # UPDATE GHOST STATE BASED ON WHO IS IT
        ghostState = state.data.agentStates[1]  # Ghost is always index 1
        if state.data.pacman_is_it:
            # Pacman is IT - Ghost should be scared (blue)
            ghostState.scaredTimer = 999
        else:
            # Ghost is IT - Ghost should be normal (red)
            ghostState.scaredTimer = 0
            
        # Check for tag (collision)
        pacmanPos = state.getPacmanPosition()
        ghostPos = state.getGhostPosition(1)
        distance = manhattanDistance(pacmanPos, ghostPos)
        
        if self.checkTag(pacmanPos, ghostPos):
            self.handleTag(state, game)
            # Update ghost appearance immediately after tag
            if state.data.pacman_is_it:
                state.data.agentStates[1].scaredTimer = 999
            else:
                state.data.agentStates[1].scaredTimer = 0
        
        if state.data.pacman_is_it:
            # Pacman is IT (chasing), so Phantom gets points for being chased
            state.data.phantom_score += 3.33
        else:
            # Phantom is IT (chasing), so Pacman gets points for being chased
            state.data.pacman_score += 3.33
        
        if not self.quiet and state.data.move_count - self.last_status_move >= 20:
            self.last_status_move = state.data.move_count
            who_is_it = "PACMAN (Chasing)" if state.data.pacman_is_it else "GHOST (Chasing)"
            ghost_scared = state.data.agentStates[1].scaredTimer > 0
            print(f"[Move {state.data.move_count}] IT: {who_is_it} | Tags: {state.data.tag_count} | Distance: {distance:.1f} | Pacman: {int(state.data.pacman_score)} | Phantom: {int(state.data.phantom_score)}")
            
        # Check win condition - first to 1000 points wins
        if state.data.pacman_score >= 1000:
            self.winGame(state, game, "PACMAN")
            return
        if state.data.phantom_score >= 1000:
            self.winGame(state, game, "PHANTOM")
            return
            
        # Check other end conditions for tag game
        if hasattr(state.data, 'tag_count') and state.data.tag_count >= self.maxTags:
            self.endGame(state, game)
        
        if hasattr(state.data, 'move_count') and state.data.move_count >= self.maxMoves:
            self.endGame(state, game)
            
    def checkTag(self, pacmanPos, ghostPos):
        # Increased tolerance from 0.7 to 1.5 to make tags easier
        return manhattanDistance(pacmanPos, ghostPos) <= 1.5
        
    def handleTag(self, state, game):
        # Initialize tag tracking attributes
        if not hasattr(state.data, 'pacman_is_it'):
            state.data.pacman_is_it = True
        if not hasattr(state.data, 'tag_cooldown'):
            state.data.tag_cooldown = 0
        if not hasattr(state.data, 'tag_count'):
            state.data.tag_count = 0
            
        # Cooldown mechanism: prevent multiple tags in quick succession
        if state.data.tag_cooldown > 0:
            # Still in cooldown, ignore this tag
            if not self.quiet and state.data.tag_cooldown % 3 == 0:
                print(f"[Tag ignored - cooldown: {state.data.tag_cooldown}]")
            return
            
        # We have a new tag!
        old_state = state.data.pacman_is_it
        state.data.pacman_is_it = not state.data.pacman_is_it
        state.data.tag_count += 1
        state.data.tag_cooldown = 20  
        
        # Display tag message with visual flair
        if not self.quiet:
            who_is_it = "Pacman" if state.data.pacman_is_it else "Ghost"
            chasing_who = "Ghost" if state.data.pacman_is_it else "Pacman"
            ghost_color = "SCARED (Blue/White)" if state.data.pacman_is_it else "AGGRESSIVE (Red)"
            print("\n" + "="*60)
            print(f"    *** TAG! TAG! TAG! ***")
            print(f"    BEFORE: {'Pacman' if old_state else 'Ghost'} was IT")
            print(f"    NOW: {who_is_it.upper()} IS IT!")
            print(f"    {who_is_it} will now CHASE {chasing_who}!")
            print(f"    {chasing_who} will now RUN AWAY!")
            print(f"    Ghost color: {ghost_color}")
            print(f"    Tag Count: {state.data.tag_count}")
            print(f"    Cooldown set to: 20 moves")
            print("="*60 + "\n")
            
        # Add points for successful tag
        state.data.scoreChange += 100
            
    def winGame(self, state, game, winner):
        if not self.quiet:
            tag_count = getattr(state.data, 'tag_count', 0)
            move_count = getattr(state.data, 'move_count', 0)
            pacman_score = int(getattr(state.data, 'pacman_score', 0))
            phantom_score = int(getattr(state.data, 'phantom_score', 0))
            print("\n" + "="*60)
            print(f"{'🏆 GAME OVER - ' + winner + ' WINS! 🏆':^60}")
            print("="*60)
            print(f"  Final Scores:")
            print(f"    Pacman:  {pacman_score} points")
            print(f"    Phantom: {phantom_score} points")
            print(f"  ")
            print(f"  Total Tags: {tag_count}")
            print(f"  Total Moves: {move_count}")
            print("="*60 + "\n")
        
        # Display win message graphically
        if hasattr(game, 'display') and hasattr(game.display, 'infoPane'):
            if hasattr(game.display.infoPane, 'showWinMessage'):
                game.display.infoPane.showWinMessage(winner)
        
        # Set win/loss appropriately
        if winner == "PACMAN":
            state.data._win = True
        else:
            state.data._lose = True
        
        game.gameOver = True
        game.winner = winner  # Store winner for display
    
    def endGame(self, state, game):
        if not self.quiet:
            tag_count = getattr(state.data, 'tag_count', 0)
            move_count = getattr(state.data, 'move_count', 0)
            pacman_score = int(getattr(state.data, 'pacman_score', 0))
            phantom_score = int(getattr(state.data, 'phantom_score', 0))
            print(f"\n=== Game Over! ===")
            print(f"Total Tags: {tag_count}")
            print(f"Total Moves: {move_count}")
            print(f"Pacman Score: {pacman_score}")
            print(f"Phantom Score: {phantom_score}")
        game.gameOver = True
        
    def win(self, state, game):
        """Tag game doesn't have traditional win condition."""
        self.endGame(state, game)
        
    def lose(self, state, game):
        """Tag game doesn't have traditional lose condition."""
        self.endGame(state, game)
        
    def getProgress(self, game):
        """Return game progress as a fraction."""
        if hasattr(game.state.data, 'move_count'):
            return min(1.0, float(game.state.data.move_count) / self.maxMoves)
        return 0.0
        
    def agentCrash(self, game, agentIndex):
        if agentIndex == 0:
            print("Pacman crashed")
        else:
            print("Ghost crashed")
            
    def getMaxTotalTime(self, agentIndex):
        return self.timeout
        
    def getMaxStartupTime(self, agentIndex):
        return self.timeout
        
    def getMoveWarningTime(self, agentIndex):
        return self.timeout
        
    def getMoveTimeout(self, agentIndex):
        return self.timeout
        
    def getMaxTimeWarnings(self, agentIndex):
        return 0


class TagGameState(GameState):
    def __init__(self, prevState=None):
        # Don't call super().__init__ to avoid creating regular GameStateData
        if prevState != None:
            self.data = TagGameStateData(prevState.data)
        else:
            self.data = TagGameStateData()
                
    def deepCopy(self):
        state = TagGameState(self)
        state.data = self.data.deepCopy()
        return state
    
    def generateSuccessor(self, agentIndex, action):
        # Check that successors exist
        if self.isWin() or self.isLose():
            raise Exception('Can\'t generate a successor of a terminal state.')

        # Copy current state
        state = TagGameState(self)

        # Let agent's logic deal with its action's effects on the board
        if agentIndex == 0:  # Pacman is moving
            TagPacmanRules.applyAction(state, action)
        else:  # A ghost is moving
            TagGhostRules.applyAction(state, action, agentIndex)

        # Time passes
        if agentIndex == 0:
            state.data.scoreChange += -TIME_PENALTY  # Penalty for passing time
        else:
            TagGhostRules.decrementTimer(state.data.agentStates[agentIndex])

        # Increment move counter
        if not hasattr(state.data, 'move_count'):
            state.data.move_count = 0
        state.data.move_count += 1

        # Book keeping
        state.data._agentMoved = agentIndex
        state.data.score += state.data.scoreChange
        return state


class TagPacmanRules(PacmanRules):
    @staticmethod
    def applyAction(state, action):
        """
        Apply action without food/capsule logic.
        """
        legal = PacmanRules.getLegalActions(state)
        if action not in legal:
            raise Exception("Illegal action " + str(action))
            
        pacmanState = state.data.agentStates[0]
        vector = Actions.directionToVector(action, PacmanRules.PACMAN_SPEED)
        pacmanState.configuration = pacmanState.configuration.generateSuccessor(vector)


class TagGhostRules(GhostRules):
    @staticmethod
    def checkDeath(state, agentIndex):
        """
        Override - no death in tag game, just position tracking.
        """
        pass  # No death mechanics in tag
        
    @staticmethod
    def collide(state, ghostState, agentIndex):
        """
        Override - no collision damage in tag game.
        """
        pass  # Tags are handled by TagGameRules
    
    @staticmethod
    def applyAction(state, action, ghostIndex):
        legal = GhostRules.getLegalActions(state, ghostIndex)
        if action not in legal:
            raise Exception("Illegal ghost action " + str(action))

        ghostState = state.data.agentStates[ghostIndex]
        
        speed = GhostRules.GHOST_SPEED  
        
        from game import Actions
        vector = Actions.directionToVector(action, speed)
        ghostState.configuration = ghostState.configuration.generateSuccessor(vector)
    
    @staticmethod
    def decrementTimer(ghostState):
        # Do nothing - scaredTimer is managed by TagGameRules.process()
        pass

