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
    def change_state(self, to_what):
        '''
        change state
        '''
        self.state = to_what

# Initialize pygame
pygame.init()

# Initialize Simulation Constants
screenW, screenH = 1440, 900
screen = pygame.display.set_mode((screenW, screenH))

mapL, mapT, mapSize = 100, 100, 500
hosL, hosT, hosSize = 700, 300, 50

FPS = 60
CONT_RATE = 1
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

clock = pygame.time.Clock()
while True:
    clock.tick(FPS)
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
                if infected.close(healthy, 15) and random() <= CONT_RATE / FPS:
                    healthy.change_state(INF)
                    INFs.append(HLTs.pop(j))
    # Calculate 2: Infected People probabistically Dead or Cured
    for i, infected in enumerate(INFs):
        infected.infect_time_count += 1
        if infected.infect_time_count >= 3 * FPS:
            if random() <= 0.01:
                infected.change_state(DED)
                DEDs.append(INFs.pop(i))
            elif random() <= 0.1: # 0.01 + 0.09
                infected.change_state(CUR)
                CURs.append(INFs.pop(i))
    # Calculate 3: PCR scan and quarantine
    for scanned in sample(people, 1):
        if scanned.state == INF and not scanned.quarantined:
            scanned.quarantined = True
            QURs.append(scanned)
    for quar in QURs:
        if quar.state != INF:
            quar.quarantined = False
            QURs.remove(quar)
    # Calculate ?: Move
    for person in people:
        person.move()
    # Draw 1: Map and Hopital
    pygame.draw.rect(screen, (16, 16, 16), [100, 100, mapSize, mapSize]) # Map
    pygame.draw.rect(screen, (255, 255, 255), [700, 300, 50, 50], 1) # Hopital
    # Draw 2: People
    for person in people:
        if person in QURs:
            pygame.draw.circle(screen, person.state.color, list(map(lambda x, y: round(x/mapSize*hosSize + y), person.pos, [hosL, hosT])), 5)
        else:
            pygame.draw.circle(screen, person.state.color, list(map(lambda x, y: round(x+y), person.pos, [mapL, mapT])), 5)
    pygame.display.flip()

# quit
pygame.quit()
