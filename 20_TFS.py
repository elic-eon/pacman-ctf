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
        self.walls = gameState.getWalls()

    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        return random.choice(actions)

    def getNearFood(self, gameState, pos):
        foodList = self.getFood(gameState).asList()
        if len(foodList) == 0:
            return None
        nFood = foodList[0]
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
                distList += [dist]
        return distList

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
        myState = gameState.getAgentState(self.index)
        self.mypos = myState.getPosition()
        actions = gameState.getLegalActions(self.index)
        oppPositions = [gameState.getAgentPosition(index) for index in self.oppIndces]
        #print(oppPositions)
        nFood = self.getNearFood(gameState, self.mypos)
        eatAction = self.tryEatAction(gameState, oppPositions, actions)
        enemyDistList = self.getNearEnemy(gameState, 2)

        if self.mypos == self.start:
            self.mode = "start"

        if self.mode == "start":
            moveAction = self.headDestAction(gameState, self.defencePos1 , actions)
            successor = self.getSuccessor(gameState, moveAction)
            nextPos = successor.getAgentPosition(self.index)
            # on defence postion
            if nextPos == self.defencePos1:
                if self.getScore(gameState) >= 400:
                    self.mode = "start"
                else:
                    self.mode = "attack"
        elif self.mode == "attack":
            dest = nFood
            # no food
            if nFood == None:
                dest = self.defencePos1
                self.mode = "start"
            # can win
            if self.getScore(gameState) >= 400: 
                self.mode = "start"
            if myState.isPacman:
                if len(enemyDistList) > 0:
                    dest = self.defencePos1
                #print("attack")
            else:
                if len(enemyDistList) > 0:
                    dest = self.defencePos1
            moveAction = self.headDestAction(gameState, dest, actions)

        if eatAction:
            return eatAction
        else:
            return moveAction

class TopLaneAgent(GeneralAgent):
    def registerInitialState(self, gameState):
        BaseAgent.registerInitialState(self, gameState)
        self.mode = "start"
        if self.red:
            self.defencePos1 = (12, 13)
        else:
            self.defencePos1 = (20, 2)

class MidLaneAgent(GeneralAgent):
    def registerInitialState(self, gameState):
        BaseAgent.registerInitialState(self, gameState)
        self.mode = "start"
        if self.red:
            self.defencePos1 = (13, 7)
        else:
            self.defencePos1 = (17, 8)

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

