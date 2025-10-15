# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util
from game import Directions
from typing import List

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()




def tinyMazeSearch(problem: SearchProblem) -> List[Directions]:
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

def depthFirstSearch(problem: SearchProblem) -> List[Directions]:
    
    from util import Stack

    start = problem.getStartState()
    if problem.isGoalState(start):
        return []

    frontier = Stack()
    frontier.push((start, []))
    explored = set()


    while not frontier.isEmpty():
        state, actions = frontier.pop()
        if state in explored:
            continue
        explored.add(state)

        if problem.isGoalState(state):
            return actions

        for successor, action, stepCost in problem.getSuccessors(state):
            if successor not in explored:
                frontier.push((successor, actions + [action]))

    return []

def breadthFirstSearch(problem: SearchProblem) -> List[Directions]:
    """Search the shallowest nodes in the search tree first."""
    from util import Queue

    start = problem.getStartState()
    if problem.isGoalState(start):
        return []

    frontier = Queue()
    frontier.push((start, []))
    explored = set()
    enqueued = set([start])

    while not frontier.isEmpty():
        state, actions = frontier.pop()
        if problem.isGoalState(state):
            return actions

        explored.add(state)

        for successor, action, stepCost in problem.getSuccessors(state):
            if successor not in explored and successor not in enqueued:
                enqueued.add(successor)
                frontier.push((successor, actions + [action]))

    return []

def uniformCostSearch(problem: SearchProblem) -> List[Directions]:
    """Search the node of least total cost first."""
    from util import PriorityQueue

    start = problem.getStartState()
    if problem.isGoalState(start):
        return []

    frontier = PriorityQueue()
    frontier.push((start, [], 0), 0)
    best_cost = {start: 0}

    while not frontier.isEmpty():
        state, actions, cost = frontier.pop()

        if state in best_cost and cost > best_cost[state]:
            continue

        if problem.isGoalState(state):
            return actions

        for successor, action, stepCost in problem.getSuccessors(state):
            newCost = cost + stepCost
            if successor not in best_cost or newCost < best_cost[successor]:
                best_cost[successor] = newCost
                frontier.push((successor, actions + [action], newCost), newCost)

    return []

def nullHeuristic(state, problem=None) -> float:
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def manhattanHeuristic(state, problem=None) -> float:
    """
    A heuristic function that uses Manhattan distance to estimate the cost
    from the current state to the nearest goal.
    """
    if problem is None:
        return 0
    
    # Get the current position (assuming state is a position tuple)
    current_pos = state
    
    # Get all goal positions
    if hasattr(problem, 'getGoal'):
        # For single goal problems
        goal_pos = problem.getGoal()
        return abs(current_pos[0] - goal_pos[0]) + abs(current_pos[1] - goal_pos[1])
    elif hasattr(problem, 'getGoals'):
        # For multiple goal problems, find the minimum distance to any goal
        goals = problem.getGoals()
        if not goals:
            return 0
        min_distance = float('inf')
        for goal_pos in goals:
            distance = abs(current_pos[0] - goal_pos[0]) + abs(current_pos[1] - goal_pos[1])
            min_distance = min(min_distance, distance)
        return min_distance
    
    return 0

def euclideanHeuristic(state, problem=None) -> float:
    """
    A heuristic function that uses Euclidean distance to estimate the cost
    from the current state to the nearest goal.
    """
    if problem is None:
        return 0

    current_pos = state
    if hasattr(problem, 'getGoal'):
        goal_pos = problem.getGoal()
        return ( (current_pos[0] - goal_pos[0]) ** 2 + (current_pos[1] - goal_pos[1]) ** 2 ) ** 0.5
    elif hasattr(problem, 'getGoals'):
        goals = problem.getGoals()
        if not goals:
            return 0
        min_distance = float('inf')
        for goal_pos in goals:
            distance = ( (current_pos[0] - goal_pos[0]) ** 2 + (current_pos[1] - goal_pos[1]) ** 2 ) ** 0.5
            min_distance = min(min_distance, distance)
        return min_distance
    
    return 0

def aStarSearch(problem: SearchProblem, heuristic=euclideanHeuristic) -> List[Directions]:
    """Search the node that has the lowest combined cost and heuristic first."""
    from util import PriorityQueue

    start = problem.getStartState()
    if problem.isGoalState(start):
        return []

    frontier = PriorityQueue()
    frontier.push((start, [], 0), 0)
    best_cost = {start: 0}

    while not frontier.isEmpty():
        state, actions, cost = frontier.pop()

        if state in best_cost and cost > best_cost[state]:
            continue

        if problem.isGoalState(state):
            return actions

        for successor, action, stepCost in problem.getSuccessors(state):
            newCost = cost + stepCost
            if successor not in best_cost or newCost < best_cost[successor]:
                best_cost[successor] = newCost
                frontier.push((successor, actions + [action], newCost), newCost + heuristic(successor, problem))

    return []

# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
