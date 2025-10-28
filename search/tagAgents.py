from game import Agent
from game import Directions
from game import Actions
from util import manhattanDistance
import random
import util
import search
from game import Grid

class TagPacmanAgent(Agent):
    def __init__(self, index=0):
        self.index = index
        
    def getAction(self, state):
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
    def __init__(self, index=1):
        self.index = index
        self.prob_attack = 0.8  # Probability of chasing when IT
        self.prob_flee = 0.8    # Probability of fleeing when not IT
        
    def getAction(self, state):
        # Get legal actions
        legal = state.getLegalActions(self.index)
        if not legal:
            return Directions.STOP
            
        # Get positions
        pacmanPos = state.getPacmanPosition()
        ghostPos = state.getGhostPosition(self.index)
        
        # Check who is 'it' 
        pacman_is_it = state.data.pacman_is_it if hasattr(state.data, 'pacman_is_it') else True
        ghost_is_it = not pacman_is_it
        
        # Ghost color is managed by TagGameRules.process()
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


class ChaseProblem:
    def __init__(self, gameState, ghostIndex, targetPos, walls):
     
        #gameState: The current game state
        #ghostIndex: The index of the ghost agent
        #targetPos: Position to reach (Pacman's position)
        #walls: Grid of walls
       
        self.startState = gameState.getGhostPosition(ghostIndex)
        self.goal = targetPos
        self.walls = walls
        self.expanded = 0
        
    def getStartState(self):
        return self.startState
    
    def isGoalState(self, state):
        return state == self.goal
    
    def getGoal(self):
        return self.goal
    
    def getSuccessors(self, state):
        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x, y = state
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                successors.append((nextState, action, 1))
        self.expanded += 1
        return successors
    
    def getCostOfActions(self, actions):
        if actions is None:
            return 999999
        x, y = self.getStartState()
        cost = 0
        for action in actions:
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]:
                return 999999
            cost += 1
        return cost


class SmartTagGhostAgent(Agent):
    def __init__(self, index=1):
        self.index = index
        self.plannedPath = []  # Store planned path
        self.replanCounter = 0  # Counter to trigger replanning
        
    def getAction(self, state):
        legal = state.getLegalActions(self.index)
        if not legal:
            return Directions.STOP
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        if not legal:
            return Directions.STOP
            
        # Get positions
        pacmanPos = state.getPacmanPosition()
        ghostPos = state.getGhostPosition(self.index)
        
        # Check who is 'it'
        pacman_is_it = state.data.pacman_is_it if hasattr(state.data, 'pacman_is_it') else True
        ghost_is_it = not pacman_is_it
        
        # Replan every 5 moves or if path is empty
        self.replanCounter += 1
        shouldReplan = (self.replanCounter % 5 == 0) or (len(self.plannedPath) == 0)
        
        if ghost_is_it:
            # CHASE PACMAN using A* search
            if shouldReplan or len(self.plannedPath) == 0:
                # Create search problem to reach Pacman
                problem = ChaseProblem(state, self.index, pacmanPos, state.getWalls())
                # Use A* with Manhattan heuristic for fast pathfinding
                self.plannedPath = search.aStarSearch(problem, search.manhattanHeuristic)
                
                # Debug output
                if hasattr(state.data, 'move_count') and state.data.move_count % 50 == 0:
                    print(f"[Smart Ghost] CHASING - Planned path length: {len(self.plannedPath)}, Distance: {manhattanDistance(ghostPos, pacmanPos)}")
            
            # Follow the planned path
            if self.plannedPath and len(self.plannedPath) > 0:
                nextAction = self.plannedPath[0]
                self.plannedPath = self.plannedPath[1:]  # Remove first action
                if nextAction in legal:
                    return nextAction
                else:
                    # Path blocked, replan next turn
                    self.plannedPath = []
        else:
            # Use greedy approach but look ahead more
            bestAction = None
            bestDist = -1
            
            for action in legal:
                # Look two steps ahead if possible
                successor = self.getSuccessorPosition(ghostPos, action, state.getWalls())
                if successor:
                    dist = manhattanDistance(successor, pacmanPos)
                    if dist > bestDist:
                        bestDist = dist
                        bestAction = action
            
            if bestAction:
                return bestAction
        
        # Fallback: use greedy approach
        actionDistances = []
        for action in legal:
            successor = self.getSuccessorPosition(ghostPos, action, state.getWalls())
            if successor:
                dist = manhattanDistance(successor, pacmanPos)
                actionDistances.append((action, dist))
        
        if actionDistances:
            if ghost_is_it:
                return min(actionDistances, key=lambda x: x[1])[0]
            else:
                return max(actionDistances, key=lambda x: x[1])[0]
        
        return random.choice(legal) if legal else Directions.STOP
    
    def getSuccessorPosition(self, position, action, walls):
        dx, dy = Actions.directionToVector(action)
        nextx, nexty = int(position[0] + dx), int(position[1] + dy)
        if not walls[nextx][nexty]:
            return (nextx, nexty)
        return None


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

