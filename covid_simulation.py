'''
covid_simulation
'''

import sys
import math
from random import random, randrange, sample
import pygame


# Define required classes
class States:
    '''
    class of States
    '''
    def __init__(self, name, color):
        self.name = name
        self.color = color

class Person:
    '''
    Each person will be a object
    '''
    def __init__(self, pos, angle, state):
        self.pos = pos
        self.vel = [V * math.cos(angle), V * math.sin(angle)]
        self.state = state
        self.quarantined = False
        self.infect_time_count = 0
        self.hopital_time_count = 0
    def move(self):
        '''
        move based on velocity of object
        '''
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        if self.pos[0] > mapSize:
            self.pos[0] = 2*mapSize - self.pos[0]
            self.vel[0] *= -1
        if self.pos[0] < 0:
            self.pos[0] = -self.pos[0]
            self.vel[0] *= -1
        if self.pos[1] > mapSize:
            self.pos[1] = 2*mapSize - self.pos[1]
            self.vel[1] *= -1
        if self.pos[1] < 0:
            self.pos[1] = -self.pos[1]
            self.vel[1] *= -1
    def close(self, other, dist):
        '''
        calculate distance between two people
        '''
        return (self.pos[0] - other.pos[0])**2 + (self.pos[1] - other.pos[1])**2 <= dist**2
    def stop(self):
        '''
        stop the point
        '''
        self.vel = [0, 0]
    def change_state(self, to_what):
        '''
        change state
        '''
        self.state = to_what

# Initialize pygame
pygame.init()

# Initialize Simulation Constants and Variables
FPS = 60 # Frame Per Second
totalFrame = 0

screenW, screenH = 1440, 900
screen = pygame.display.set_mode((screenW, screenH))

mapL, mapT, mapSize = 100, 100, 500
hosL, hosT, hosSize = 700, 600, 50

graphL, graphT, graphW, graphH = 700, 300, 400, 200
graphColor = (16, 16, 16)

mapColor = (16, 16, 16)
hosColor = (16, 16, 16)

CONTAGIOUS_RATE = 1 # probability of contagion if two people pass by each other for one "frame"
FATALITY_RATE = 0.05 # per one second
FATALITY_RATE_PER_FRAME = FATALITY_RATE / FPS # suppose that fatality rate is very small
CURE_RATE = 0.05 # per one second
CURE_RATE_PER_FRAME = CURE_RATE / FPS # suppse that cure rate is very small

SCAN_PER_FRAME = 0

CONTAGIOUS_RADIUS = 15
LEAST_INFECTED_SECONDS = 3

V = 0.7 # velocity of points

# Initialize Health States
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HLT = States('HLT', (51, 255, 255)) # Healthy
INF = States('INF', (255, 127, 0)) # Infected
DED = States('DED', (128, 128, 128)) # Dead
CUR = States('CUR', (26, 128, 128)) # Cured

# Initializa Objects
HLTs = []
for i in range(300):
    HLTs.append(Person([randrange(mapSize), randrange(mapSize)], random()*2*math.pi, HLT))
INFs = [Person([randrange(mapSize), randrange(mapSize)], random()*2*math.pi, INF)]
QURs = []
DEDs = []
CURs = []
people = HLTs + INFs + DEDs + CURs

# Initiate Graph Variables
infectNum = [1]
curedNum = [0]
deadNum = [0]

# Run Simulation
clock = pygame.time.Clock()
while True:
    clock.tick(FPS)
    totalFrame += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
    screen.fill(BLACK)
    # Calculate 1: Infect Healthy People
    for i, infected in enumerate(INFs):
        contagious = not infected.quarantined
        if contagious:
            for j, healthy in enumerate(HLTs):
                if infected.close(healthy, CONTAGIOUS_RADIUS) and \
                    random() <= CONTAGIOUS_RATE:
                    healthy.change_state(INF)
                    INFs.append(HLTs.pop(j))
    # Calculate 2: Infected People probabistically Dead or Cured
    for i, infected in enumerate(INFs):
        infected.infect_time_count += 1
        if infected.infect_time_count >= LEAST_INFECTED_SECONDS * FPS:
            if random() <= FATALITY_RATE_PER_FRAME:
                infected.change_state(DED)
                DEDs.append(INFs.pop(i))
                infected.stop()
            elif random() <= CURE_RATE_PER_FRAME + FATALITY_RATE_PER_FRAME: ### should be improved
                infected.change_state(CUR)
                CURs.append(INFs.pop(i))
    # Calculate 3: PCR scan and quarantine
    for scanned in sample(people, SCAN_PER_FRAME):
        if scanned.state == INF and not scanned.quarantined:
            scanned.quarantined = True
            QURs.append(scanned)
    for quar in QURs:
        if quar.state != INF:
            quar.quarantined = False
            QURs.remove(quar)
    # Calculate 4: Record Cumulation
    infectNum.append(len(INFs))
    curedNum.append(len(CURs))
    deadNum.append(len(DEDs))
    # Calculate ?: Move
    for person in people:
        person.move()
    # Draw 1: Map and Hopital
    pygame.draw.rect(screen, mapColor, [mapL, mapT, mapSize, mapSize]) # Map
    pygame.draw.rect(screen, hosColor, [hosL, hosT, hosSize, hosSize]) # Hopital
    # Draw 2: People
    for person in people:
        if person in QURs:
            repr_position = list(map(lambda x, y: round(x/mapSize*hosSize + y), person.pos, [hosL, hosT]))
            pygame.draw.circle(screen, person.state.color, repr_position, 5)
        else:
            repr_position = list(map(lambda x, y: round(x+y), person.pos, [mapL, mapT]))
            pygame.draw.circle(screen, person.state.color, repr_position, 5)
    # Draw 3: Cumulative Graph
    pygame.draw.rect(screen, graphColor, [graphL, graphT, graphW, graphH])
    oneWidth = graphW / totalFrame
    peopleNum = len(people)
    for fr in range(totalFrame):
        leftTopPos = [graphL + fr * oneWidth, graphT]
        deadH = round(deadNum[fr] * graphH / peopleNum)
        curedH = round(curedNum[fr] * graphH / peopleNum)
        infectH = round(infectNum[fr] * graphH / peopleNum)
        healthyH = graphH - deadH - curedH - infectH
        pygame.draw.rect(screen, DED.color, leftTopPos + [oneWidth, healthyH + infectH + curedH + deadH]) # dead
        pygame.draw.rect(screen, CUR.color, leftTopPos + [oneWidth, healthyH + infectH + curedH]) # cured
        pygame.draw.rect(screen, INF.color, leftTopPos + [oneWidth, healthyH + infectH]) # infected
        pygame.draw.rect(screen, HLT.color, leftTopPos + [oneWidth, healthyH]) # healthy
    # Draw
    pygame.display.flip()

# quit
pygame.quit()
