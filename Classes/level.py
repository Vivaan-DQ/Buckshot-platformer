from Classes.platform import Platform

class Level:
    def __init__(self):

        #stores all of the levels platform
        self.platforms = []

        ground = Platform(0, 575, 1280, 1)

        #Append basically adds the platform to the list.
        self.platforms.append(ground)

    
    #Function essentailly draws every platform in the level.    
    def draw(self, screen):
        for platform in self.platforms:
            platform.draw(screen)
        

