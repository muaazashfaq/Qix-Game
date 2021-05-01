import pygame
from pygame.locals import *
from pygame_functions import *

# Initializes pygame
pygame.init()

# Initializes Pygame Audio Mixer
pygame.mixer.init()

# Setting up window
screen = pygame.display.set_mode((800,800))
pygame.display.set_caption("Qix")

main_background = pygame.image.load('img/main_background.png')
main_background = pygame.transform.scale(main_background, (800,800))

main_menu = pygame.image.load('img/main_menu.png')
main_menu = pygame.transform.scale(main_menu, (800,800))

game_state = 0 # Main Screen

# Main background initiation
screen.blit(main_background, (0,0))
pygame.display.update()

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and game_state == 0:
                screen.blit(main_menu, (0,0))
                pygame.display.update()
                game_state = 1

    pygame.display.update()

pygame.quit()