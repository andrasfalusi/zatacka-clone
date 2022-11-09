import pygame


class Debug(object):
    def __init__(self, graphics):
        self.graphics = graphics
        self.font = pygame.font.Font(None, 15)
        self.debug_surf = pygame.Surface((self.graphics.width, self.graphics.height), pygame.SRCALPHA)
        self.debug_rect = self.debug_surf.get_rect(topleft=(0,0))


    def debug(self, info, pos):
        # display_surface = pygame.display.get_surface()
        temp_surf = self.font.render(str(info), True, 'White')
        temp_rect = temp_surf.get_rect(topleft=(10, 20*pos))
        pygame.draw.rect(self.debug_surf, 'Black', temp_rect)
        self.debug_surf.blit(temp_surf, temp_rect)

    def blit_screen(self):
        self.graphics.draw_layer(self.debug_surf, self.debug_rect)