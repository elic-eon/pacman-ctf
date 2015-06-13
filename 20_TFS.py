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
import copy

#################
# Team creation #
#################

g_intorState = [None, None, None, None, None, None]
firstAgentSight = []
secondAgentSight = []
thirdAgentSight = []

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
        self.deadEnd = self.buildDeadEnd(gameState)
        self.pointToWin = 200
        self.defendFood = self.getFoodYouAreDefending(gameState).asList()
        g_intorState[self.index] = "start"

    def degree(self, gameState, pos):
        x, y = pos
        degree = 0
        for neighbor in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
            if not self.walls[neighbor[0]][neighbor[1]]:
                degree += 1
        return degree

    def buildDeadEnd(self, gameState):
        width = gameState.data.layout.width
        height = gameState.data.layout.height
        deadEnd = game.Grid(gameState.data.layout.width, gameState.data.layout.height)
        deadEndList = []
        tmp = game.Grid(gameState.data.layout.width, gameState.data.layout.height)
        for x in range(width):
            for y in range(height):
                if not self.walls[x][y]:
                    degree = self.degree(gameState, (x,y))
                    if degree <= 1:
                        deadEnd[x][y] = True
                        deadEndList.append((x,y))
                    elif degree == 2:
                        tmp[x][y] = True
        for x, y in deadEndList:
            for neighbor in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
                if tmp[neighbor[0]][neighbor[1]]:
                    tmp[neighbor[0]][neighbor[1]] = False
                    deadEnd[neighbor[0]][neighbor[1]] = True
                    deadEndList.append(neighbor)

        return deadEnd

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

    def getNumState(self, mode):
        i = 0
        for state in g_intorState:
            if state == mode:
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
        bestAction = None
        bestDistance = -1
        for action in actions:
            successor = self.getSuccessor(gameState, action)
            posNow = successor.getAgentPosition(self.index)
            dist = self.getMazeDistance(posNow, pos)
            if dist > bestDistance and not self.deadEnd[posNow[0]][posNow[1]]:
                bestAction = action
                bestDistance = dist
        if bestAction is None: return actions[0]
        else: return bestAction

    def fetchCapsule(self, gameState):
        actions = gameState.getLegalActions(self.index)
        if len(self.getCapsules(gameState)) != 0:
            capsulePos = self.getCapsules(gameState)[0]
            if self.getMazeDistance(self.mypos, capsulePos) <= 1:
                return self.headDestAction(gameState, capsulePos, actions)

    def fetchFlag(self, gameState):
        actions = gameState.getLegalActions(self.index)
        if len(self.getFlags(gameState)) != 0:
            flagPos = self.getFlags(gameState)[0]
            if self.getMazeDistance(self.mypos, flagPos) <= 3:
                return self.headDestAction(gameState, flagPos, actions)

    def fightGhost(self, gameState):
        actions = gameState.getLegalActions(self.index)
        for idx in self.getOpponents(gameState):
            pos = gameState.getAgentPosition(idx)
            if pos is not None: 
                if not gameState.getAgentState(idx).isPacman and gameState.getAgentState(idx).scaredTimer == 0 and self.getMazeDistance(self.mypos, pos) <= 3:
                    return self.awayDestAction(gameState, pos, actions)

        for idx in self.getOpponents(gameState):
            pos = gameState.getAgentPosition(idx)
            if pos is not None: 
                if not gameState.getAgentState(idx).isPacman and gameState.getAgentState(idx).scaredTimer > 0:
                    return self.headDestAction(gameState, pos, actions)

    def fetchFood(self, gameState):
        actions = gameState.getLegalActions(self.index)
        foodList = self.getFood(gameState).asList()
        if len(foodList) != 0:
            dist = 100
            finalAction = None
            for action in actions:
                nextState = self.getSuccessor(gameState, action)
                nextPos = nextState.getAgentPosition(self.index)
                if nextPos in foodList:
                    return action
                bfsDist = self.BFS(gameState, nextPos)
                if bfsDist < dist:
                    dist = bfsDist
                    finalAction = action

            return finalAction

    def BFS(self, gameState, start):
        foodList = self.getFood(gameState).asList()
        start = (int(start[0]), int(start[1]))
        visitedPositions = [start]
        positionQueue = [(start, 0)]
        walls = self.wallMemory

        while positionQueue:
            pos = positionQueue[0][0]
            depth = positionQueue[0][1]

            for nextPos in ((pos[0]+1, pos[1]), (pos[0]-1, pos[1]), (pos[0], pos[1]+1), (pos[0], pos[1]-1)):
                if nextPos in foodList:
                    return depth+1;
                if (nextPos not in visitedPositions) and (not walls[nextPos[0]][nextPos[1]]):
                    positionQueue.append( (nextPos, depth+1) )
                    visitedPositions.append( nextPos )

            positionQueue.pop(0)

        return 100
        
    def updateWalls(self, gameState):
        if self.myState.isPacman:
            walls = gameState.getWalls().deepCopy()
            for idx in self.getOpponents(gameState):
                pos = gameState.getAgentPosition(idx)
                if pos is not None: 
                    if not gameState.getAgentState(idx).isPacman and gameState.getAgentState(idx).scaredTimer == 0 and self.getMazeDistance(self.mypos, pos) <= 3:
                        x, y = pos
                        walls[x][y] = True
                        walls[x+1][y] = True
                        walls[x-1][y] = True
                        walls[x][y+1] = True
                        walls[x][y-1] = True
                        
            self.wallMemory = walls
        
    def offenceAction(self, gameState):
        # near enemy distance less than 2
        enemyDistList = self.getNearEnemy(gameState, 2)
        actions = gameState.getLegalActions(self.index)
        nFood = self.getNearFood(gameState, self.mypos)
        dest = nFood
        
        self.updateWalls(gameState)
        
        #### state change #### 
        # no food
        if nFood == None:
            self.mode = "defence"
        # can win
        #if self.getScore(gameState) >= self.pointToWin:
        #    self.mode = "lock"
        # not pacman and someone is pacman
        if not self.myState.isPacman and self.numTeamPacman > 0:
            self.mode = "defence"
            dest = self.defencePos1

        #### actions ####
        action = self.fetchCapsule(gameState)
        if action is not None: return action

        action = self.fightGhost(gameState)
        if action is not None: return action
        
        action = self.fetchFlag(gameState)
        if action is not None: return action
        
        action = self.fetchFood(gameState)
        if action is not None: return action
        
        # move to nearest food
        self.headDestAction(gameState, self.defencePos1, actions)

    def tryEatAction(self, gameState, oppPositions, actions):
        for action in actions:
            successor = self.getSuccessor(gameState, action)
            posNow = successor.getAgentPosition(self.index)
            if posNow in oppPositions:
                return action
        else:
            return None

    def checkDefendFood(self, gameState) :
        defendFoodNow = self.getFoodYouAreDefending(gameState).asList()
        if len(self.defendFood) != len(defendFoodNow) :
            eatenFood = set(self.defendFood)^set(defendFoodNow)
            #self.defendFood = defendFoodNow
            return list(eatenFood)
        return None
    
    def getManhattanDistance(self, pos1, pos2) :
        if pos1[0] > pos2[0] :
            x = pos1[0] - pos2[0]
        else :
            x = pos1[0] - pos1[0]
        if pos1[1] > pos2[1] :
            y = pos1[1] - pos2[1]
        else :
            y = pos1[1] - pos1[1]
        return x+y
            
    def getNoiseDistance(self, gameState) :
        if self.idx == min(self.teamIndces) :
            firstAgentSight = gameState.getAgentDistances()
        elif self.idx == max(self.teamIndces) :
            thirdAgentSight = gameState.getAgentDistances()
        else :
            secondAgentSight = gameState.getAgentDistances()

    def getnoiseOppDistance(self, gameState, oppIdx) :
        region1 = []
        region2 = []
        region3 = []
        #get !walls position
        notWalls = copy.deepcopy(self.walls) 
        for x in range(0, 32) :
            for y in range(0, 16) :
                if notWalls[x][y] == False :
                    notWalls[x][y] = True               
        pos1 = gameState.getAgentPosition(self.teamIndces[0])
        pos2 = gameState.getAgentPosition(self.teamIndces[1])
        pos3 = gameState.getAgentPosition(self.teamIndces[2])
        #draw three regions
        for pos in notWalls.asList() :
            if self.getManhattanDistance(pos, pos1) <= firstAgentSight[oppIdx] + 6  and self.getManhattanDistance(pos, pos1) >= firstAgentSight[oppIdx] - 6:
                region1.append(pos)
            if self.getManhattanDistance(pos, pos2) <= secondAgentSight[oppIdx] + 6 and self.getManhattanDistance(pos, pos2) >= secondAgentSight[oppIdx] - 6:
                region2.append(pos)
            if self.getManhattanDistance(pos, pos3) <= thirdAgentSight[oppIdx] + 6 and self.getManhattanDistance(pos, pos3) >= thirdAgentSight[oppIdx] - 6:
                region3.append(pos)
        #find intersection of three regions
        intersectionRegion = set(region1) & set(region2) & set(region3)
        RegionSet = list(intersectionRegion).sort
        return RegionSet[len(RegionSet)/2]

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
        eatAction = self.tryEatAction(gameState, oppPositions, actions)
        self.numTeamPacman = self.getNumPacman(gameState)
        enemyDistList = self.getNearEnemy(gameState, 3)
        eatenFood = self.checkDefendFood(gameState)

        self.mode = g_intorState[self.index]
        # respawn
        if self.mypos == self.start:
            self.mode = "start"
            self.wallMemory = gameState.getWalls().deepCopy()

        if self.mode == "start":
            if len(enemyDistList) > 0:
                dist = enemyDistList[0][0]
            else:
                dist = self.defencePos1
            moveAction = self.headDestAction(gameState, dist , actions)
            successor = self.getSuccessor(gameState, moveAction)
            nextPos = successor.getAgentPosition(self.index)
            # on defence postion
            if nextPos == self.defencePos1:
                self.mode = "defence"
            if eatAction:
                moveAction = eatAction
        elif self.mode == "defence":
            if self.getNumState(defence) == 3:
                moveAction = self.headDestAction(gameState, self.defencePos1 , actions)
            if self.getNumState(defence) == 2:
                moveAction = self.headDestAction(gameState, self.defencePos2 , actions)
            elif self.getNumState == 1:
                moveAction = self.headDestAction(gameState, self.defencePos3, actions)
            self.mode = "attack"
            # enough poing to win
            if self.getScore(gameState) >= self.pointToWin:
                self.mode = "lock"
            # only one pacman in one time
            if self.numTeamPacman > 0:
                self.mode = "defence"
            if "attack" in g_intorState:
                self.mode = "defence"
            if eatAction:
                moveAction = eatAction
        elif self.mode == "lock":
            moveAction = self.headDestAction(gameState, self.lockPos, actions)
        elif self.mode == "attack":
            moveAction = self.offenceAction(gameState)

        g_intorState[self.index] = self.mode
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

