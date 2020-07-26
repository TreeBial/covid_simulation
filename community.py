'''Community and Grid'''

from random import random, sample
from math import cos, sin, pi, floor
from itertools import product
import numpy

from person import Person
import states

class Community(object):
    '''Community object with grids'''
    def __init__(self, simulation, size, population, initial_infection):
        self.simulation = simulation

        self.size = size
        # people and data
        self.people = set([])
        self.data = {states.HLT:set([]), states.INF:set([]), states.CUR:set([]), states.DED:set([])}
        ACTIVITY = 0.7
        for _ in range(population - initial_infection):
            tmp_person = self.add_person_randomly(ACTIVITY, states.HLT)
            self.data[states.HLT].add(tmp_person)
        for _ in range(initial_infection):
            tmp_person = self.add_person_randomly(ACTIVITY, states.INF)
            self.data[states.INF].add(tmp_person)
        # rgb_array
        self.rgb_array = numpy.array([[states.HLT.color]*len(self.data[states.HLT]) + [states.INF.color]*len(self.data[states.INF])])

        self.__grids = None
    # methods about grid
    def __init_grids(self):
        '''initiate grids'''
        grid_num = floor(self.size / self.simulation.CONTAGIOUS_RADIUS)
        grid_size = self.size / grid_num
        self.__grids = Grid(grid_num, grid_size)
    def __clear_grids(self):
        '''clear __grids'''
        self.__grids.data = Grid.empty_data
    def __update_grids(self):
        '''write health data of people in community into __grids.data'''
        grid_size = self.__grids.grid_size
        grid_num = self.__grids.grid_num
        for person in self.people:
            grid_index = int(person.pos[0] // grid_size) + grid_num * int(person.pos[1] // grid_size)
            self.__grids.data[grid_index][person.state].add(person)
    # methods about person
    def add_person_randomly(self, activity, health_state):
        '''add person to current community'''
        V = activity
        pos = [self.size * random(), self.size * random()]
        vel = [V * cos(random()*2*pi), V * sin(random()*2*pi)]
        person = Person(self, pos, vel, health_state)
        self.people.add(person)
        self.data[person.state].add(person)
        return person
    def move_people(self):
        '''move all people'''
        for person in self.people:
            person.pos[0] += person.vel[0]
            person.pos[1] += person.vel[1]
            if person.pos[0] > self.size:
                person.pos[0] = 2*self.size - person.pos[0]
                person.vel[0] *= -1
            if person.pos[0] < 0:
                person.pos[0] = -person.pos[0]
                person.vel[0] *= -1
            if person.pos[1] > self.size:
                person.pos[1] = 2*self.size - person.pos[1]
                person.vel[1] *= -1
            if person.pos[1] < 0:
                person.pos[1] = -person.pos[1]
                person.vel[1] *= -1
    def push_person(self, person):
        '''push person'''
        self.people.add(person)
        self.data[person.state].add(person)
    def remove_person(self, person):
        '''remove person'''
        self.people.discard(person)
        self.data[person.state].discard(person)
    def __change_state(self, person, to_what):
        self.data[person.state].discard(person)
        self.data[to_what].add(person)
        person.change_state(to_what)
    # caculation function 1: calculate infection
    def calculate_infection(self):
        '''caculate infection between infected and healthy people'''
        if not self.__grids:
            self.__init_grids()
        self.__update_grids()
        cont_radius = self.simulation.CONTAGIOUS_RADIUS # redefine for short code
        cont_rate = self.simulation.CONTAGIOUS_RATE # redefine for short code
        will_be_changed = set([]) # the people who infected in this frame
        for i in range(self.__grids.grid_num**2):
            for j in self.__grids.adjacent_indices[i]:
                for infected, healthy in product(self.__grids.data[i][states.INF], self.__grids.data[j][states.HLT]):
                    if infected.distance(healthy) <= cont_radius**2 and random() <= cont_rate:
                        will_be_changed.add(healthy)
        for now_infected in will_be_changed:
            self.__change_state(now_infected, states.INF)
        self.__clear_grids()
    # caculation function 2: infected people probabistically cured or dead
    def calculate_change_of_infected(self):
        '''change state of infected people who was infected during more than least time'''
        least_time = self.simulation.FPS * self.simulation.LEAST_INFECTED_TIME
        cure_rate = self.simulation.CURE_RATE
        dead_rate = self.simulation.DEAD_RATE
        for infected in self.data[states.INF]:
            if infected.infect_time_count >= least_time:
                # be cured
                if random() >= cure_rate:
                    infected.state = states.CUR
                    self.data[states.CUR].add(infected)
                    self.data[states.INF].discard(infected)
                # die
                elif random() >= dead_rate + cure_rate:
                    infected.state = states.DED
                    self.data[states.DED].add(infected)
                    self.data[states.INF].discard(infected)
    # caculation function 3: PCR scan and quarantine
    def calculate_pcr_scan(self):
        '''PCR scan'''
        scan_per_frame = self.simulation.SCAN_PER_FRAME
        for person in sample(self.people, scan_per_frame):
            if person.state == states.INF:
                person.move_from_to(self, self.simulation.hospital)
    # update rgb_array
    def update_rgb_array(self):
        '''update rgb array'''
        new_rgb_line = numpy.array([[states.HLT.color]*len(self.data[states.HLT]) + [states.INF.color]*len(self.data[states.INF]) + [states.CUR.color]*len(self.data[states.CUR]) + [states.DED.color]*len(self.data[states.DED])])
        self.rgb_array = numpy.concatenate((self.rgb_array, new_rgb_line), axis=0)

class Grid(object):
    '''Grid Object'''
    empty_data = []
    def __init__(self, grid_num, grid_size):
        if not Grid.empty_data:
            Grid.empty_data = [{states.HLT:set([]), states.INF:set([])} for _ in range(grid_num**2)]
        self.grid_num = grid_num
        self.grid_size = grid_size
        self.adjacent_indices = [[j for j in range(grid_num**2) if Grid.__is_adj(i, j, grid_num)] for i in range(grid_num**2)]
        self.data = Grid.empty_data
    @classmethod
    def __is_adj(cls, i, j, grid_num):
        divmod_i = divmod(i, grid_num)
        divmod_j = divmod(j, grid_num)
        return abs(divmod_i[0] - divmod_j[0]) <= 1 and abs(divmod_i[1] - divmod_j[1]) <= 1
