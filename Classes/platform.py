import pygame

class Platform:
    def __init__(self, x, y, width, height):
        #self.rect creates physical boundaries for the platform and collision hitboxes.
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (0, 0, 0) #This colour is temporary for now
    
    #This fucntion effectively renders the platform into pygame visual softare, telling it to draw the colour onto the screen in relation to the rectangle "Rect"
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

