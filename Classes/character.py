import pygame
from Classes.weapon import Weapon


class Character:
    def __init__(self, x, y, width, height, sprite_manager, sprite_name):
        self.sprite_manager = sprite_manager
        self.entity = sprite_name  # used as key for animations

        # Fallback static image (if no animation configured).
        self.image = sprite_manager.get(sprite_name)
        if self.image:
            self.image = pygame.transform.scale(self.image, (width, height))
        else:
            #Another debug checking method in place to allow the game to run, even if there isnt a sprite.
            print(f"SPRITE NOT FOUND: {sprite_name}")
            self.image = pygame.Surface((width, height))
            self.image.fill((200, 200, 200))

        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.vel_y = 0
        self.gravity = 0.5
        self.on_ground = False
        self.health = 100
        self.weapon = Weapon(10)



    def apply_gravity(self):
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

    def take_damage(self, amount):

        self.health -= amount
        print(self.__class__.__name__, "Health:", self.health)

        if self.health < 0:
            self.health = 0


    def is_alive(self):
        #This lets us check if the player is basically alive or dead.
        return self.health > 0



    def shoot(self, target, shoot_self=False):
        """Returns:
        - self:  "self_live" / "self_blank"
        - other: "enemy_live" / "enemy_blank"
        - None:  weapon out of shells (round over)
        """

        shot = self.weapon.shoot()
        # Debug: confirm cylinder index advances (UI depends on next_chamber_index)
        # print(f"DEBUG SHELL: {shot} next_chamber_index={self.weapon.next_chamber_index} / {len(self.weapon.cylinder)}")
        #This was a test used to identify bugs, now commented because the bug was fixed.

        if shot is None:
            print("NO MORE SHELLS")
            return None

        if shoot_self:
            print("Aiming at yourself...")
            if shot == "live":
                print("BANGGG (SELF HIT)")
                self.take_damage(self.weapon.damage)
                return "self_live"
            else:
                print("CLICK (YOU GOT LUCKY)")
                return "self_blank"
        # Shooting the other person
        if shot == "live":
            print("BANGGG (LIVE)")
            target.take_damage(self.weapon.damage)
            return "enemy_live"
        else:
            print("CLICK (BLANK)")
            return "enemy_blank"

    def draw(self, screen):
        screen.blit(self.image, self.rect)

