'''person class'''

class Person(object):
    '''Each person will be a object'''
    def __init__(self, belong_to, pos, vel, state):
        self.belong_to = belong_to
        self.pos = pos
        self.vel = vel
        self.state = state
        self.quarantined = False
        self.infect_time_count = 0
    def distance(self, other):
        '''calculate distance between two people'''
        return (self.pos[0] - other.pos[0])**2 + (self.pos[1] - other.pos[1])**2
    def stop(self):
        '''stop the point'''
        self.vel = [0, 0]
    def move_from_to(self, where_from, where_to):
        '''will be used when a person move from somewhere to somewhere'''
        where_from.remove_person(self)
        where_to.push_person(self)
    def change_state(self, to_what):
        '''change state'''
        self.state = to_what
