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
               first = 'MidLaneAgent', second = 'BaseAgent', third = 'BaseAgent'):
    return [eval(first)(firstIndex), eval(second)(secondIndex), eval(third)(thirdIndex)]

##########
# Agents #
##########

class BaseAgent(CaptureAgent):
    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.postionList = [gameState.getAgentPosition(self.index)]
        self.oppIndces = self.getOpponents(gameState)
        self.walls = gameState.getWalls()

    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        return random.choice(actions)

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

class TopLaneAgent(BaseAgent):
    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        pos1 = (13, 1)
        oppPositions = [gameState.getAgentPosition(index) for index in self.oppIndces]
        destAcrion = self.headDestAction(gameState, pos1, actions)
        eatAction = self.tryEatAction(gameState, oppPositions, actions)
        if eatAction:
            return eatAction
        else:
            return destAcrion

class MidLaneAgent(BaseAgent):
    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        pos1 = (13, 1)
        oppPositions = [gameState.getAgentPosition(index) for index in self.oppIndces]
        destAcrion = self.headDestAction(gameState, pos1, actions)
        eatAction = self.tryEatAction(gameState, oppPositions, actions)
        if eatAction:
            return eatAction
        else:
            return destAcrion

    def nothing():
        return 1

class BotLaneAgent(BaseAgent):
    def nothing():
        return 1
