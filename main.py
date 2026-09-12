import asyncio
import pygame
from Classes.game import Game

pygame.mixer.pre_init(24000, -16, 2, 2048)
pygame.init()

WIDTH = 1280
HEIGHT = 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Buckshot Platformer")

clock = pygame.time.Clock()
FPS = 60

running = True


async def main():
    global running

    # Load the game before starting gameplay
    game = Game()

    # Give the browser/WASM runtime a chance to finish
    await asyncio.sleep(0)

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        game.update(keys)

        screen.fill((0, 0, 0))
        game.draw(screen)

        pygame.display.update()

        # Give the browser/WASM runtime time to breathe
        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())