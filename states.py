'''States'''

class States(object):
    '''States'''
    def __init__(self, name, color):
        self.name = name
        self.color = color

HLT = States('HLT', (51, 255, 255)) # Healthy
INF = States('INF', (255, 127, 0)) # Infected
DED = States('DED', (128, 128, 128)) # Dead
CUR = States('CUR', (26, 128, 128)) # Cured
