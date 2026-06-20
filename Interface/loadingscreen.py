import pygame
from pygame.locals import *
from Utils.settings import *
import sys

class LoadingScreen:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.text = self.font.render('Press Enter to Start', True, (255, 255, 255))
        self.text_rect = self.text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.background_image = pygame.image.load('../graphics/loadscreen/load.jpg').convert() 

    def update(self, screen):
        scaled_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT)) 
        screen.blit(scaled_image, (0, 0))  
        screen.blit(self.text, self.text_rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return False 
        return True 
    
