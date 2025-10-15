# tagAgents.py
# ------------
# Custom agents for the Tag game where Pacman and a Ghost play tag

from game import Agent
from game import Directions
from game import Actions
from util import manhattanDistance
import random
import util

class TagPacmanAgent(Agent):
    """
    Pacman agent for tag game.
    When Pacman is 'it', he chases the ghost.
    When the ghost is 'it', Pacman runs away.
    """
    def __init__(self, index=0):
        self.index = index
        
    def getAction(self, state):
        """
        Get action based on whether Pacman is 'it' or not.
        """
        # Get game state information
        legal = state.getLegalActions(self.index)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        
        if not legal:
            return Directions.STOP
            
        # Get positions
        pacmanPos = state.getPacmanPosition()
        ghostPos = state.getGhostPosition(1)
        
        # Check who is 'it' - READ DIRECTLY from state
        pacman_is_it = state.data.pacman_is_it if hasattr(state.data, 'pacman_is_it') else True
        
        # Debug: Print current state occasionally
        if hasattr(state.data, 'move_count') and state.data.move_count % 50 == 0:
            behavior = "CHASING Ghost" if pacman_is_it else "FLEEING from Ghost"
            print(f"[Pacman] Move {state.data.move_count}: {behavior}, pacman_is_it={pacman_is_it}")
        
        # Calculate distances for each legal action
        actionDistances = []
        for action in legal:
            successor = state.generatePacmanSuccessor(action)
            if successor is None:
                continue
            newPos = successor.getPacmanPosition()
            dist = manhattanDistance(newPos, ghostPos)
            actionDistances.append((action, dist))
        
        if not actionDistances:
            return random.choice(legal) if legal else Directions.STOP
        
        if pacman_is_it:
            # Pacman is IT - Chase the ghost (minimize distance)
            bestAction = min(actionDistances, key=lambda x: x[1])[0]
        else:
            # Ghost is IT - Run from the ghost (maximize distance)
            bestAction = max(actionDistances, key=lambda x: x[1])[0]
        
        return bestAction


class TagGhostAgent(Agent):
    """
    Ghost agent for tag game.
    When the ghost is 'it', it chases Pacman using DirectionalGhost algorithm.
    When Pacman is 'it', the ghost runs away.
    """
    def __init__(self, index=1):
        self.index = index
        self.prob_attack = 0.8  # Probability of chasing when IT
        self.prob_flee = 0.8    # Probability of fleeing when not IT
        
    def getAction(self, state):
        """
        Get action based on whether the ghost is 'it' or not.
        Uses DirectionalGhost algorithm for realistic chasing.
        """
        # Get legal actions
        legal = state.getLegalActions(self.index)
        if not legal:
            return Directions.STOP
            
        # Get positions
        pacmanPos = state.getPacmanPosition()
        ghostPos = state.getGhostPosition(self.index)
        
        # Check who is 'it' - READ DIRECTLY from state
        pacman_is_it = state.data.pacman_is_it if hasattr(state.data, 'pacman_is_it') else True
        ghost_is_it = not pacman_is_it
        
        # Ghost color is managed by TagGameRules.process(), not here
        ghostState = state.getGhostState(self.index)
        
        # Debug: Print current state occasionally
        if hasattr(state.data, 'move_count') and state.data.move_count % 50 == 0:
            behavior = "FLEEING (scared)" if pacman_is_it else "CHASING (aggressive)"
            print(f"[Ghost] Move {state.data.move_count}: {behavior}, ghost_is_it={ghost_is_it}, scaredTimer={ghostState.scaredTimer}")
        
        # Use DirectionalGhost algorithm
        from game import Actions
        speed = 1
        actionVectors = [Actions.directionToVector(a, speed) for a in legal]
        newPositions = [(ghostPos[0] + a[0], ghostPos[1] + a[1]) for a in actionVectors]
        
        # Calculate distances to Pacman for each possible action
        distancesToPacman = [manhattanDistance(pos, pacmanPos) for pos in newPositions]
        
        if pacman_is_it:
            # Ghost should RUN AWAY - maximize distance
            bestScore = max(distancesToPacman)
            bestProb = self.prob_flee
        else:
            # Ghost is IT - CHASE Pacman - minimize distance
            bestScore = min(distancesToPacman)
            bestProb = self.prob_attack
        
        # Find all actions that achieve the best score
        bestActions = [action for action, distance in zip(legal, distancesToPacman) if distance == bestScore]
        
        # Construct probability distribution (like DirectionalGhost)
        import util
        dist = util.Counter()
        for a in bestActions:
            dist[a] = bestProb / len(bestActions)
        for a in legal:
            dist[a] += (1 - bestProb) / len(legal)
        dist.normalize()
        
        # Choose action based on distribution
        return util.chooseFromDistribution(dist)


class KeyboardTagPacmanAgent(Agent):
    """
    Keyboard-controlled Pacman for tag game.
    """
    WEST_KEY  = 'a'
    EAST_KEY  = 'd'
    NORTH_KEY = 'w'
    SOUTH_KEY = 's'
    STOP_KEY = 'q'
    
    def __init__(self, index=0):
        self.lastMove = Directions.STOP
        self.index = index
        self.keys = []
        
    def getAction(self, state):
        from graphicsUtils import keys_waiting
        from graphicsUtils import keys_pressed
        keys = list(keys_waiting()) + list(keys_pressed())
        if keys != []:
            self.keys = keys
            
        legal = state.getLegalActions(self.index)
        move = self.getMove(legal)
        
        if move == Directions.STOP:
            if self.lastMove in legal:
                move = self.lastMove
                
        if (self.STOP_KEY in self.keys) and Directions.STOP in legal:
            move = Directions.STOP
            
        if move not in legal:
            move = random.choice(legal)
            
        self.lastMove = move
        return move
        
    def getMove(self, legal):
        move = Directions.STOP
        if (self.WEST_KEY in self.keys or 'Left' in self.keys) and Directions.WEST in legal:
            move = Directions.WEST
        if (self.EAST_KEY in self.keys or 'Right' in self.keys) and Directions.EAST in legal:
            move = Directions.EAST
        if (self.NORTH_KEY in self.keys or 'Up' in self.keys) and Directions.NORTH in legal:
            move = Directions.NORTH
        if (self.SOUTH_KEY in self.keys or 'Down' in self.keys) and Directions.SOUTH in legal:
            move = Directions.SOUTH
        return move

