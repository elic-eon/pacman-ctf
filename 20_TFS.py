# myTeam.py
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


from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

g_intorState = ["start", "start", "start", "start", "start", "start"]

def createTeam(firstIndex, secondIndex, thirdIndex, isRed,
               first = 'TopLaneAgent', second = 'MidLaneAgent', third = 'BotLaneAgent'):
    return [eval(first)(firstIndex), eval(second)(secondIndex), eval(third)(thirdIndex)]

##########
# Agents #
##########

class BaseAgent(CaptureAgent):
    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.start = gameState.getAgentPosition(self.index)
        self.oppIndces = self.getOpponents(gameState)
        self.teamIndces = self.getTeam(gameState)
        self.walls = gameState.getWalls()
        self.pointToWin = 200
        if self.red:
            g_intorState[self.index-1] = None
        else:
            g_intorState[self.index+1] = None

    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        return random.choice(actions)

    def getNearFood(self, gameState, pos):
        foodList = self.getFood(gameState).asList()
        nFood = None
        foodDist = 9999
        for food in foodList:
            tDist = self.getMazeDistance(pos, food)
            if tDist < foodDist:
                foodDist = tDist
                nFood = food
        return nFood

    def getEnemy(self, gameState):
        i = []
        for index in self.oppIndces:
            agentPosition = gameState.getAgentPosition(index)
            if agentPosition is not None:
                i += [agentPosition]
        #print(i)
        return i

    def getNearEnemy(self, gameState, myfilter = 9999):
        enemyList = self.getEnemy(gameState)
        distList = []
        for enemy in enemyList:
            dist = self.getMazeDistance(self.mypos, enemy)
            if dist <= myfilter:
                distList += [(enemy, dist)]
        return distList

    def getTeamAgentState(self, gameState):
        l = []
        for index in self.teamIndces:
            agent = gameState.getAgentState(index)
            l += [agent]
        return l

    def getNumPacman(self, gameState):
        i = 0
        for agent in self.getTeamAgentState(gameState):
            if agent.isPacman:
                i += 1
        return i

    def headDestAction(self, gameState, pos, actions):
        bestAction = actions[0]
        bestDistance = 9999
        for action in actions:
            successor = self.getSuccessor(gameState, action)
            posNow = successor.getAgentPosition(self.index)
            dist = self.getMazeDistance(posNow, pos)
            if dist < bestDistance:
                bestAction = action
                bestDistance = dist
        return bestAction

    def awayDestAction(self, gameState, pos, actions):
        bestAction = actions[0]
        bestDistance = -1
        posibleAction = []
        for action in actions:
            successor = self.getSuccessor(gameState, action)
            posNow = successor.getAgentPosition(self.index)
            nextPosibleActions = successor.getLegalActions(self.index)
            dist = self.getMazeDistance(posNow, pos)
            if dist > bestDistance:
                bestAction = action
                bestDistance = dist
            elif dist == bestDistance:
                if len(nextPosibleActions) > len(posibleAction):
                    bestAction = action
        return bestAction
        
    def offenceAction(self, gameState):
        # near enemy distance less than 2
        enemyDistList = self.getNearEnemy(gameState, 2)
        actions = gameState.getLegalActions(self.index)
        nFood = self.getNearFood(gameState, self.mypos)
        numTeamPacman = self.getNumPacman(gameState)
        dest = nFood
        # no food
        if nFood == None:
            dest = self.defencePos1
            self.mode = "defence"
        # can win
        if self.getScore(gameState) >= self.pointToWin:
            self.mode = "defence"
        # not pacman and someone is pacman
        if not self.myState.isPacman and numTeamPacman > 0:
            self.mode = "defence"
            dest = self.defencePos1
            
        if self.myState.isPacman:
            if len(enemyDistList) > 0:
                # away from enemy
                dest = enemyDistList[0][0]
                moveAction = self.awayDestAction(gameState, dest, actions)
            else:
                # move to food
                moveAction = self.headDestAction(gameState, dest, actions)
        else:
            # move to enemy
            if len(enemyDistList) > 0:
                #dest = self.defencePos1
                dest = enemyDistList[0][0]
            moveAction = self.headDestAction(gameState, dest, actions)

    def tryEatAction(self, gameState, oppPositions, actions):
        for action in actions:
            successor = self.getSuccessor(gameState, action)
            posNow = successor.getAgentPosition(self.index)
            if posNow in oppPositions:
                return action
        else:
            return None

    def getSuccessor(self, gameState, action):
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != nearestPoint(pos):
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

class GeneralAgent(BaseAgent):
    def chooseAction(self, gameState):
        self.myState = gameState.getAgentState(self.index)
        self.mypos = self.myState.getPosition()
        actions = gameState.getLegalActions(self.index)
        oppPositions = [gameState.getAgentPosition(index) for index in self.oppIndces]
        nFood = self.getNearFood(gameState, self.mypos)
        eatAction = self.tryEatAction(gameState, oppPositions, actions)
        enemyDistList = self.getNearEnemy(gameState, 2)
        

        # respawn
        if self.mypos == self.start:
            self.mode = "start"

        if self.mode == "start":
            moveAction = self.headDestAction(gameState, self.defencePos1 , actions)
            successor = self.getSuccessor(gameState, moveAction)
            nextPos = successor.getAgentPosition(self.index)
            # on defence postion
            if nextPos == self.defencePos1:
                self.mode = "defence"
        elif self.mode == "defence":
            moveAction = self.headDestAction(gameState, self.defencePos1 , actions)
            self.mode = "attack"
            # enough poing to win
            if self.getScore(gameState) >= self.pointToWin:
                self.mode = "defence"
            # only one pacman in one time
            if numTeamPacman > 0:
                self.mode = "defence"
            if "attack" in g_intorState or "start" in g_intorState:
                self.mode = "defence"
            if eatAction:
                moveAction = eatAction
        elif self.mode == "attack":
            moveAction = self.offenceAction(gameState)

        g_intorState[self.index] = self.mode
        print(g_intorState)

        return moveAction

class TopLaneAgent(GeneralAgent):
    def registerInitialState(self, gameState):
        BaseAgent.registerInitialState(self, gameState)
        self.mode = "start"
        if self.red:
            self.defencePos1 = (12, 13)
            g_intorState[self.index-1] = None
        else:
            self.defencePos1 = (20, 2)
            g_intorState[self.index+1] = None

class MidLaneAgent(GeneralAgent):
    def registerInitialState(self, gameState):
        BaseAgent.registerInitialState(self, gameState)
        self.mode = "start"
        if self.red:
            self.defencePos1 = (13, 7)
        else:
            self.defencePos1 = (18, 8)

class BotLaneAgent(GeneralAgent):
    def registerInitialState(self, gameState):
        BaseAgent.registerInitialState(self, gameState)
        self.mode = "start"
        if self.red:
            self.defencePos1 = (11, 2)
        else:
            self.defencePos1 = (20, 13)

class DebugAgent(BaseAgent):
    def chooseAction(self, gameState):
        self.postion = gameState.getAgentPosition(self.index)
        x = self.postion[0]
        y = self.postion[1]
        print("index: " + str(self.index) + " at " + str(self.postion))
        key = raw_input()
        if key == 'w':
            if self.walls[x][y+1] == True:
                return Directions.STOP
            else:
                return Directions.NORTH
        elif key == 'a':
            if self.walls[x-1][y] == True:
                return Directions.STOP
            else:
                return Directions.WEST
        elif key == 's':
            if self.walls[x][y-1] == True:
                return Directions.STOP
            else:
                return Directions.SOUTH
        elif key == 'd':
            if self.walls[x+1][y] == True:
                return Directions.STOP
            else:
                return Directions.EAST
        else:
            return Directions.STOP

