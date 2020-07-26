'''hospital'''

from random import random

import states

class Hospital(object):
    '''Hospital'''
    def __init__(self):
        self.quarantined_people = []
    def push_person(self, person):
        '''push person'''
        self.quarantined_people.append(person)
    def remove_person(self, person):
        '''remove person'''
        self.quarantined_people.remove(person)
    def caculate_change_of_infected(self, least_infected_time, cure_rate, dead_rate):
        '''change state of infected people(in hospital) who was infected during more than least time'''
        for infected in self.quarantined_people:
            if infected.infect_time_count >= least_infected_time:
                # be cured
                if random() >= cure_rate:
                    infected.state = states.CUR
                # die
                elif random() >= dead_rate + cure_rate:
                    infected.state = states.DED
                infected.move_from_to(self, infected.belong_to) # self: Hospital
