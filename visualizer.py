'''Visualizer'''
import pygame

class Visualizer(object):
    '''Visualizer'''
    def __init__(self, screen, simulation):
        # constants
        ## title constants
        ## community constants
        self.commboard_background_color = (16, 16, 16)
        self.community_background_color = (32, 32, 32)
        self.commboard_left = 100
        self.commboard_top = 200
        self.commboard_width = 500
        self.commboard_height = None
        self.community_interval = 5
        self.community_size = round((self.commboard_width - self.community_interval) / simulation.comm_column)
        self.commboard_width = simulation.comm_column * self.community_size + (simulation.comm_column + 1) * self.community_size
        self.commboard_height = simulation.comm_row * self.community_size + (simulation.comm_row + 1) * self.community_size
        # objects
        self.screen = screen
        self.simulation = simulation
    def draw_all(self):
        '''draw all'''
        screen = self.screen
        simul = self.simulation
        # draw background
        self.__fill_background(screen)
        # draw title
        self.__draw_title(screen)
        # draw communities
        self.__draw_communities(screen)
        # draw graph
        # draw total data

    def __fill_background(self, screen):
        screen.fill([0, 0, 0])
    def __draw_title(self, screen):
        title_text = 'Epidemic Simulation'
        title_font = 'arial'
        title_size = 20
        title_color = (255, 255, 255)

        font_obj = pygame.font.SysFont(title_font, title_size)
        text_surface_obj = font_obj.render(title_text, True, title_color)
        text_rect_obj = text_surface_obj.get_rect()
        text_rect_obj.centerx = round(500 / 2)
        text_rect_obj.y = 100
        screen.blit(text_surface_obj, text_rect_obj)
    def __each_community_srf(self, community):
        comm_srf = pygame.Surface([community.size, community.size])
        comm_srf.fill(self.community_background_color)
        for person in community.people:
            repr_pos = [round(person.pos[0]), round(person.pos[1])]
            pygame.draw.circle(comm_srf, person.state.color, repr_pos, 5)
        return comm_srf
    def __draw_communities(self, screen):
        # draw community board (background)
        comm_board_srf = pygame.Surface([self.commboard_width, self.commboard_height])
        comm_board_srf.fill(self.commboard_background_color)
        # draw each community
        comm_srfs = []
        itvl = self.community_interval
        sz = self.community_size
        clmn = self.simulation.comm_column
        for i, comm in enumerate(self.simulation.communities):
            # community objects
            comm_srf = self.__each_community_srf(comm)
            comm_srfs.append(comm_srf)
            # make communities_obj include comm_obj
            tmp_top_left = [itvl + (itvl + sz) * (i // clmn), itvl + (itvl + sz) * (i % clmn)]
            comm_board_srf.blit(comm_srf, tmp_top_left)
        # draw hospital?
        # blit
        screen.blit(comm_board_srf, [self.commboard_left, self.commboard_top])
