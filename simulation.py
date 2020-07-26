'''simulation constants and objects'''

from community import Community
from hospital import Hospital

class Simulation(object):
    '''simulation object'''
    def __init__(self, comm_row, comm_column, populations, initial_infections, comm_size=500):
        # constants
        self.FPS = 60

        self.CONTAGIOUS_RADIUS = 15
        self.CONTAGIOUS_RATE = 1

        self.LEAST_INFECTED_TIME = 3

        self.CURE_RATE = 0.07
        self.CURE_RATE_PER_FRAME = 1 - pow(1 - self.CURE_RATE, 1/self.FPS)
        self.DEAD_RATE = 0.03
        self.DEAD_RATE_PER_FRAME = 1 - pow(1 - self.DEAD_RATE, 1/self.FPS)

        self.SCAN_PER_FRAME = 3
        # objects
        self.comm_row = comm_row
        self.comm_column = comm_column
        self.communities = [Community(self, size=comm_size, population=populations[i], initial_infection=initial_infections[i]) for i in range(comm_row*comm_column)]
        self.hospital = Hospital()
        # people variable
        self.people = []
        self.data = []
    def add_person_randomly(self, community, activity, state):
        '''add person to community with random position and velocity'''
        community.add_person_randomly(activity, state)
