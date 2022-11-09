import pygame
from debug import Debug

class Graphics(object):
    def __init__(self):
        # Pygame setup
        pygame.init()
        self.width, self.height = 400, 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        # info = pygame.display.Info()  # You have to call this before pygame.display.set_mode()
        # self.width, self.height = info.current_w, info.current_h
        # self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

        self.debug = Debug(self)

    def draw_layer(self, surf, rect):
        self.screen.blit(surf, rect)

    def update(self):
        self.debug.blit_screen()
        pygame.display.update()

    def clear_screen(self):
        self.screen.fill('gray12')
