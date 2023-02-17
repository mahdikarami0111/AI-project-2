# multiAgents.py
# --------------
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


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent
from pacman import GameState


class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """

    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState: GameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        if successorGameState.isWin():
            return 99999

        newFood = newFood.asList()
        currentFood = currentGameState.getFood().asList()
        currentPos = currentGameState.getPacmanPosition()
        currentGhostState = currentGameState.getGhostStates()
        currentScaredTimes = [ghostState.scaredTimer for ghostState in currentGhostState]

        newFoodDist = []
        for food in newFood:
            newFoodDist.append(manhattanDist(newPos, food))

        currentFoodDist = []
        for food in currentFood:
            currentFoodDist.append(manhattanDist(currentPos, food))

        newGhostDist = []
        for ghost in newGhostStates:
            newGhostDist.append(manhattanDist(ghost.getPosition(), newPos))

        currentGhostDist = []
        for ghost in currentGhostState:
            currentGhostDist.append(manhattanDist(ghost.getPosition(), currentPos))

        currentScared = 0
        for time in newScaredTimes:
            currentScared += time

        newScared = 0
        for time in currentScaredTimes:
            newScared += time

        newCapsuleDist = []
        for pos in successorGameState.getCapsules():
            newCapsuleDist.append(manhattanDist(newPos, pos))

        currentCapsuleDist = []
        for pos in currentGameState.getCapsules():
            currentCapsuleDist.append(manhattanDist(currentPos, pos))



        score = 0
        score += successorGameState.getScore() - currentGameState.getScore()

        if len(newFood) < len(currentFood):
            score += 150

        if newScared > 0:
            if min(newGhostDist) < min(currentGhostDist):
                score += 300
        else:
            if min(newGhostDist) > min(currentGhostDist):
                score += 100

        if min(newFoodDist) < min(currentFoodDist):
            score += 100

        if sum(newGhostDist) < sum(currentGhostDist):
            score += 75

        if newPos in currentGameState.getCapsules():
            score += 200

        if newCapsuleDist and currentCapsuleDist and min(newCapsuleDist) < min(currentCapsuleDist):
            score += 100

        if newPos == currentPos:
            score -= 50

        score -= len(newFood) * 15

        return score


def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn='scoreEvaluationFunction', depth='2'):
        self.index = 0  # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"

        def minValue(state, currentDepth, index):
            if state.isWin() or state.isLose():
                return self.evaluationFunction(state)
            minimum = 999999
            lastGhost = (index == state.getNumAgents() - 1)
            for action in state.getLegalActions(index):
                successor = state.generateSuccessor(index, action)
                if lastGhost:
                    minimum = min(minimum, maxValue(successor, currentDepth))
                else:
                    minimum = min(minimum, minValue(successor, currentDepth, index + 1))
            return minimum

        def maxValue(state: GameState, currentDepth):
            if state.isWin() or state.isLose() or (currentDepth + 1) == self.depth:
                return self.evaluationFunction(state)
            maximum = -999999
            for action in state.getLegalActions(0):
                successor = state.generateSuccessor(0, action)
                maximum = max(maximum, minValue(successor, currentDepth + 1, 1))
            return maximum

        depth = 0
        actions = gameState.getLegalActions(0)
        currentScore = -999999
        returnAction = ''
        for action in actions:
            nextState = gameState.generateSuccessor(0, action)
            score = minValue(nextState, 0, 1)
            if score > currentScore:
                returnAction = action
                currentScore = score
        return returnAction




        util.raiseNotDefined()


class AlphaBetaAgent(MultiAgentSearchAgent):
    def getAction(self, gameState):
        "*** YOUR CODE HERE ***"
        def minValue(state, currentDepth, index, alpha, beta):
            if state.isWin() or state.isLose():
                return self.evaluationFunction(state)
            minimum = 999999
            lastGhost = (index == state.getNumAgents() - 1)
            for action in state.getLegalActions(index):
                successor = state.generateSuccessor(index, action)
                if lastGhost:
                    minimum = min(minimum, maxValue(successor, currentDepth, alpha, beta))
                else:
                    minimum = min(minimum, minValue(successor, currentDepth, index + 1, alpha, beta))
                if minimum < alpha:
                    return minimum
                beta = min(beta, minimum)
            return minimum

        def maxValue(state: GameState, currentDepth, alpha, beta):
            if state.isWin() or state.isLose() or (currentDepth + 1) == self.depth:
                return self.evaluationFunction(state)


            maximum = -999999
            for action in state.getLegalActions(0):
                successor = state.generateSuccessor(0, action)
                maximum = max(maximum, minValue(successor, currentDepth + 1, 1, alpha, beta))
                if maximum > beta:
                    return maximum
                alpha = max(alpha, maximum)
            return maximum

        depth = 0
        actions = gameState.getLegalActions(0)
        currentScore = -999999
        returnAction = ''
        alpha = -999999
        beta = 999999
        for action in actions:
            nextState = gameState.generateSuccessor(0, action)
            score = minValue(nextState, 0, 1, alpha, beta)
            if score > currentScore:
                returnAction = action
                currentScore = score
            if score > beta:
                return returnAction
            alpha = max(alpha, score)
        return returnAction


        util.raiseNotDefined()


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        def minValue(state, currentDepth, index):
            if state.isWin() or state.isLose():
                return self.evaluationFunction(state)
            temp = 0
            lastGhost = (index == state.getNumAgents() - 1)
            for action in state.getLegalActions(index):
                successor = state.generateSuccessor(index, action)
                if lastGhost:
                    temp += maxValue(successor, currentDepth)
                else:
                    temp += minValue(successor, currentDepth, index + 1)
            return temp/len(state.getLegalActions(index))

        def maxValue(state: GameState, currentDepth):
            if state.isWin() or state.isLose() or (currentDepth + 1) == self.depth:
                return self.evaluationFunction(state)
            maximum = -999999
            for action in state.getLegalActions(0):
                successor = state.generateSuccessor(0, action)
                maximum = max(maximum, minValue(successor, currentDepth + 1, 1))
            return maximum

        depth = 0
        actions = gameState.getLegalActions(0)
        currentScore = -999999
        returnAction = ''
        for action in actions:
            nextState = gameState.generateSuccessor(0, action)
            score = minValue(nextState, 0, 1)
            if score > currentScore:
                returnAction = action
                currentScore = score
        return returnAction


def betterEvaluationFunction(currentGameState : GameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    Don't forget to use pacmanPosition, foods, scaredTimers, ghostPositions!
    DESCRIPTION: <write something here so we know what you did>
    """

    pacmanPosition = currentGameState.getPacmanPosition()
    gridFoods = currentGameState.getFood()
    ghostStates = currentGameState.getGhostStates()
    scaredTimers = [ghostState.scaredTimer for ghostState in ghostStates]
    ghostPositions = currentGameState.getGhostPositions()

    "*** YOUR CODE HERE ***"
    foods = gridFoods.asList()
    score = 0
    foodDist = []
    ghostDist = []
    capsuleDist = []

    if currentGameState.isWin():
        return 99999

    for capsule in currentGameState.getCapsules():
        capsuleDist.append(manhattanDist(capsule, pacmanPosition))

    for food in foods:
        foodDist.append(manhattanDist(food, pacmanPosition))

    for ghostPosition in ghostPositions:
        ghostDist.append(manhattanDist(ghostPosition, pacmanPosition))

    if ghostDist:
        if sum(scaredTimers) > 0:
            score -= min(ghostDist) * 3
        else:
            score += sum(ghostDist)/(2 * len(ghostDist))
            score += min(ghostDist)/2

    if capsuleDist:
        score -= min(capsuleDist) * 3

    score += len(gridFoods.asList(False))

    if foodDist:
        score -= sum(foodDist)/len(foodDist)

    return score + currentGameState.getScore()

    util.raiseNotDefined()



def manhattanDist(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


# Abbreviation
better = betterEvaluationFunction
