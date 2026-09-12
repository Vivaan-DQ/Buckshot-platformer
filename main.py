
import pygame
from Classes.game import Game
pygame.mixer.pre_init(44100, -16, 2, 512) #Very important to load sounds early on.
pygame.init()


#The dimensions of the screen
WIDTH = 1280
HEIGHT = 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Buckshot Platformer")

#Pygame requires a clock to match it with the fps counter, hence why the clock was required.
clock = pygame.time.Clock()
FPS = 60

#Essentially crerates the instance of the game object.
game = Game()

running = True

while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    keys = pygame.key.get_pressed()

    #updates the entire game, because in the game class, the update funciton now updates everything, so now we dont have to manually update each
    #classes characterisitcs seperately.
    game.update(keys)

    #This is just the temporary background colour for now.
    screen.fill((0, 0, 0)) 

    #Because earlier we made the draw function in the game class draw everything, we only need one command, instead of individual commands for each class.
    game.draw(screen)

    pygame.display.update()

pygame.quit()