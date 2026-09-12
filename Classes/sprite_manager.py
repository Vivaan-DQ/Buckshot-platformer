import pygame


class SpriteManager:
    def __init__(self):
        self.sprites = {}

    def load(self, name, path):
        """Load a standalone image."""
        try:
            print(f"[SPRITE] Loading: {path}")

            image = pygame.image.load(path)

            print(
                f"[SPRITE] Loaded: {path} "
                f"({image.get_width()}x{image.get_height()})"
            )

            try:
                image = image.convert_alpha()
            except Exception as e:
                print(f"[SPRITE] convert_alpha failed for {path}: {e}")

            # Scale backgrounds only.
            if "bg" in name:
                print(f"[SPRITE] Scaling background: {name}")
                image = pygame.transform.scale(image, (1280, 720))

            self.sprites[name] = image

        except Exception as e:
            print(f"[SPRITE ERROR] {path}")
            print(f"[SPRITE ERROR TYPE] {type(e).__name__}")
            print(f"[SPRITE ERROR DETAILS] {e}")

            self.sprites[name] = None

    def get(self, name):
        return self.sprites.get(name)