'''
covid_simulation
'''

import sys
import pygame

from simulation import Simulation
from visualizer import Visualizer
import states

# Initialize pygame
pygame.init()

# Initialize Simulation Constants and Variables
FPS = 60 # Frame Per Second
total_frame = 0

mapL, mapT, mapSize = 100, 100, 500
hosL, hosT, hosSize = 700, 600, 50

graphL, graphT, graphW, graphH = 700, 300, 400, 200
graphColor = (16, 16, 16)

mapColor = (16, 16, 16)
hosColor = (16, 16, 16)

# Initialize Health States
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Initializa Objects
populations = [500]
initial_infections = [1]
simul = Simulation(1, 1, populations, initial_infections)
comm = simul.communities[0]

screenW, screenH = 1440, 900
screen = pygame.display.set_mode((screenW, screenH))
vis = Visualizer(screen, simul)

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
    comm.calculate_infection()
    # Calculate 2: Infected People probabistically Dead or Cured
    comm.calculate_change_of_infected()
    # Calculate 3: PCR scan and quarantine
    comm.calculate_pcr_scan()
    # Calculate ?: Move
    comm.move_people()
    # visualize
    vis.draw_all()
    pygame.display.flip()

# quit
pygame.quit()
