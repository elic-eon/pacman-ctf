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
import random, time, util
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, thirdIndex, isRed,
               first = 'FoodAgent', second = 'DefenceAgent', third = 'DefenceAgent'):
    """
    This function should return a list of three agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.  isRed is True if the red team is being created, and
    will be False if the blue team is being created.

    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments ("first" and "second" are
    such arguments in the case of this function), which will come from
    the --redOpts and --blueOpts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """
    
    # The following line is an example only; feel free to change it.
    return [eval(first)(firstIndex), eval(second)(secondIndex), eval(third)(thirdIndex)]

##########
# Agents #
##########

class BaseAgent(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at baselineTeam.py for more details about how to
    create an agent as this is the bare minimum.
    """

    def getSuccessor(self, gameState, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)
        else:
            return successor
            
    def gotoPos(self, gameState, pos):
        actions = gameState.getLegalActions(self.index)
        agentPositions = [gameState.getAgentPosition(i) for i in range(gameState.getNumAgents())]
        
        positions = [self.getSuccessor(gameState,a).getAgentState(self.index).getPosition() for a in actions]
        for action in actions:
            if self.red and gameState.generateSuccessor(self.index, action).getScore() > gameState.getScore():
                return action
            elif not self.red and gameState.generateSuccessor(self.index, action).getScore() < gameState.getScore():
                return action
        
        values = [-self.getMazeDistance(pos,self.getSuccessor(gameState,a).getAgentState(self.index).getPosition()) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        
        return bestActions[0]
        
    def leavePos(self, gameState, pos):
        actions = gameState.getLegalActions(self.index)
        agentPositions = [gameState.getAgentPosition(i) for i in range(gameState.getNumAgents())]
        
        positions = [self.getSuccessor(gameState,a).getAgentState(self.index).getPosition() for a in actions]
        for action in actions:
            if self.red and gameState.generateSuccessor(self.index, action).getScore() > gameState.getScore():
                return action
            elif not self.red and gameState.generateSuccessor(self.index, action).getScore() < gameState.getScore():
                return action
        
        values = [self.getMazeDistance(pos,self.getSuccessor(gameState,a).getAgentState(self.index).getPosition()) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        
        return bestActions[0]

#######################
#### Capsule Agent ####
#######################
class CapsuleAgent(BaseAgent):

    def registerInitialState(self, gameState):

        CaptureAgent.registerInitialState(self, gameState)
        self.target = self.getCapsules(gameState)[0]

    def chooseAction(self, gameState):
        return self.gotoPos(gameState, self.target)

####################
#### Flag Agent ####
####################
class FlagAgent(BaseAgent):

    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.target = self.getFlags(gameState)[0]
        self.start = gameState.getAgentPosition(self.index)

    def chooseAction(self, gameState):
        if len(self.getFlags(gameState)) == 0:
            self.target = self.start
        
        return self.gotoPos(gameState, self.target)

####################
#### Food Agent ####
####################
class FoodAgent(BaseAgent):

    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.target = self.getCapsules(gameState)[0]
        self.start = gameState.getAgentPosition(self.index)
        
    def fightGhost(self, gameState):
        for idx in self.getOpponents(gameState):
            pos = gameState.getAgentPosition(idx)
            if pos is not None: 
                if not gameState.getAgentState(idx).isPacman and gameState.getAgentState(idx).scaredTimer == 0:
                    return self.leavePos(gameState, pos)
                    
        for idx in self.getOpponents(gameState):
            pos = gameState.getAgentPosition(idx)
            if pos is not None: 
                if not gameState.getAgentState(idx).isPacman and gameState.getAgentState(idx).scaredTimer > 0:
                    return self.gotoPos(gameState, pos)
                    
    def gotoCapsule(self, gameState):
        pass

    def chooseAction(self, gameState):
        
        action = self.fightGhost(gameState)
        if action is not None: return action
        
        actions = gameState.getLegalActions(self.index)
        agentPositions = [gameState.getAgentPosition(i) for i in range(gameState.getNumAgents())]
        
        positions = [self.getSuccessor(gameState,a).getAgentState(self.index).getPosition() for a in actions]
        for action in actions:
            if self.red and gameState.generateSuccessor(self.index, action).getScore() > gameState.getScore():
                return action
            elif not self.red and gameState.generateSuccessor(self.index, action).getScore() < gameState.getScore():
                return action
        
        values = [-self.foodDist(gameState, self.getSuccessor(gameState,a).getAgentState(self.index).getPosition()) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        
        return bestActions[0]
        
    def foodDist(self, gameState, pos):
        dist = 100
        food = self.getFood(gameState)
        
        for i in range(food.width):
            for j in range(food.height):
                if food[i][j] and self.getMazeDistance(pos, (i, j)) < dist:
                    dist = self.getMazeDistance(pos, (i, j))
        
        return dist
        
#######################
#### Defence Agent ####
#######################
class DefenceAgent(BaseAgent):

    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        targetVector = [(12,13), (19,2), (13,7), (18,8), (11,3), (20,12)]
        self.target = targetVector[self.index]

    def chooseAction(self, gameState):
        
        actions = gameState.getLegalActions(self.index)
        agentPositions = [gameState.getAgentPosition(i) for i in range(gameState.getNumAgents())]
        
        positions = [self.getSuccessor(gameState,a).getAgentState(self.index).getPosition() for a in actions]
        for action in actions:
            if self.red and gameState.generateSuccessor(self.index, action).getScore() > gameState.getScore():
                return action
            elif not self.red and gameState.generateSuccessor(self.index, action).getScore() < gameState.getScore():
                return action
        
        for idx in self.getOpponents(gameState):
            if gameState.getAgentState(idx).isPacman:
                pos = gameState.getAgentPosition(idx)
                if pos is not None: return self.gotoPos(gameState, pos)
            
        return self.gotoPos(gameState, self.target)


