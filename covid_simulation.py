'''
covid_simulation
'''

import sys
import math
from random import random, randrange, sample

import pygame
import numpy

from community import Community

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
total_frame = 0

screenW, screenH = 1440, 900
screen = pygame.display.set_mode((screenW, screenH))

mapL, mapT, mapSize = 100, 100, 500
hosL, hosT, hosSize = 700, 600, 50

graphL, graphT, graphW, graphH = 700, 300, 400, 200
graphColor = (16, 16, 16)

mapColor = (16, 16, 16)
hosColor = (16, 16, 16)

POPULATION = 500

CONTAGIOUS_RATE = 1 # probability of contagion if two people pass by each other for one "frame"
FATALITY_RATE = 0.05 # per one second
FATALITY_RATE_PER_FRAME = FATALITY_RATE / FPS # suppose that fatality rate is very small
CURE_RATE = 0.05 # per one second
CURE_RATE_PER_FRAME = CURE_RATE / FPS # suppse that cure rate is very small

SCAN_PER_FRAME = 5

CONTAGIOUS_RADIUS = 15
LEAST_INFECTED_SECONDS = 3

V = 0.7 # velocity of points

# Initialize Health States
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
HLT = States('HLT', (51, 255, 255)) # Healthy
INF = States('INF', (255, 127, 0)) # Infected
DED = States('DED', (128, 128, 128)) # Dead
CUR = States('CUR', (26, 128, 128)) # Cured

# Initializa Objects
grid_num = math.floor(mapSize / CONTAGIOUS_RADIUS)
grid_size = mapSize / grid_num
com = Community(mapSize, mapSize, grid_num)

HLTs = []
for i in range(POPULATION - 1):
    HLTs.append(Person([randrange(mapSize), randrange(mapSize)], random()*2*math.pi, HLT))
INFs = [Person([randrange(mapSize), randrange(mapSize)], random()*2*math.pi, INF)]
QURs = []
DEDs = []
CURs = []
people = HLTs + INFs + DEDs + CURs

# Initiate Graph Variables
rgb_array = numpy.array([[HLT.color]*len(HLTs) + [INF.color]*len(INFs)])

# Run Simulation
clock = pygame.time.Clock()
while True:
    clock.tick(FPS)
    total_frame += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
    screen.fill(BLACK)
    # Calculate 1: Infect Healthy People
    ## rearrange grid
    for _person in people:
        if _person.state == HLT:
            grid_index = int(_person.pos[0] // grid_size) + grid_num * int(_person.pos[1] // grid_size)
            com.grid[grid_index]['healthy'].append(_person)
        elif _person.state == INF:
            grid_index = int(_person.pos[0] // grid_size) + grid_num * int(_person.pos[1] // grid_size)
            com.grid[grid_index]['infected'].append(_person)
    for now_index in range(grid_num**2):
        if com.grid[now_index]['infected']:
            for adj_index in com.adjacent_grids[now_index]:
                for infected in com.grid[now_index]['infected']:
                    for healthy in com.grid[adj_index]['healthy']:
                        if infected.close(healthy, CONTAGIOUS_RADIUS) and \
                            random() <= CONTAGIOUS_RATE:
                            healthy.change_state(INF)
                            INFs.append(healthy)
                            HLTs.remove(healthy)
                            com.grid[adj_index]['infected'].append(healthy)
                            com.grid[adj_index]['healthy'].remove(healthy)
    com.clear_grid()
    # for i, infected in enumerate(INFs):
    #     contagious = not infected.quarantined
    #     if contagious:
    #         for j, healthy in enumerate(HLTs):
    #             if infected.close(healthy, CONTAGIOUS_RADIUS) and \
    #                 random() <= CONTAGIOUS_RATE:
    #                 healthy.change_state(INF)
    #                 INFs.append(HLTs.pop(j))
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
    rgb_new_line = numpy.array([[HLT.color]*len(HLTs) + [INF.color]*len(INFs) + [CUR.color]*len(CURs) + [DED.color]*len(DEDs)])
    rgb_array = numpy.concatenate((rgb_array, rgb_new_line), axis=0)
    rgb_surface = pygame.surfarray.make_surface(rgb_array)
    rgb_surface_scaled = pygame.transform.scale(rgb_surface, (graphW, graphH))
    screen.blit(rgb_surface_scaled, [graphL, graphT])
    # Draw 4: Show Current Situation (number of infected, healthy, etc)
    font_text = pygame.font.SysFont('arial', 32)
    font_number = pygame.font.SysFont('arial', 32)
    healthy_text = font_text.render('healthy', False, HLT.color)
    healthy_number = font_number.render(f'{len(HLTs)}', False, HLT.color)
    screen.blit(healthy_text, (900, 500))
    screen.blit(healthy_number, (900, 600))
    infect_text = font_text.render('infected', False, INF.color)
    infect_number = font_number.render(f'{len(INFs)}', False, INF.color)
    screen.blit(infect_text, (1000, 500))
    screen.blit(infect_number, (1000, 600))
    cured_text = font_text.render('cured', False, CUR.color)
    cured_number = font_number.render(f'{len(CURs)}', False, CUR.color)
    screen.blit(cured_text, (1100, 500))
    screen.blit(cured_number, (1100, 600))
    dead_text = font_text.render('dead', False, DED.color)
    dead_number = font_number.render(f'{len(DEDs)}', False, DED.color)
    screen.blit(dead_text, (1200, 500))
    screen.blit(dead_number, (1200, 600))
    # Draw
    pygame.display.flip()

# quit
pygame.quit()
