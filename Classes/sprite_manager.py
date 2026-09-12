import pygame


class SpriteManager:
    def __init__(self):
        # Static images (backgrounds, UI, single sprites, etc.)
        self.sprites = {}

    def load(self, name, path):
        """Load a standalone image."""
        try:
            image = pygame.image.load(path)
            try:
                image = image.convert_alpha()
            except Exception:
                # Some PNGs (or formats) can fail convert_alpha(); keep the original surface.
                pass


            # Scale backgrounds only.
            if "bg" in name:
                image = pygame.transform.scale(image, (1280, 720))

            #Fail safe used to bug fix, or to check if there are actually sprites provided or not.
            self.sprites[name] = image
        except Exception:
            print(f"Failed to load: {path}")
            self.sprites[name] = None

    def get(self, name):
        return self.sprites.get(name)


