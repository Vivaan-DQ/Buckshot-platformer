import pygame

from Classes.character import Character


class Enemy(Character):
    def __init__(self, x, y, sprite_manager, mode="boss"):  # mode: "boss" or "npc"
        sprite_name = "enemy" if mode == "boss" else "npc"

        #Make the boos look intimidating, thats why theres a new height and width to make him bigger.
        if mode == "boss":
            new_w, new_h = 300, 300
            y = y + 150
        else:
            new_w, new_h = 80, 120

        super().__init__(x, y, new_w, new_h, sprite_manager, sprite_name)

        self.mode = mode
        self.speed = 2
        self.direction = 1

        #Single-frame swap animation support (timed revert) and Base sprite name/image used for reverting back.
        self._base_sprite_name = sprite_name
        self._base_image = self.image

        self._anim_timer_ms = 0.0
        self._anim_duration_ms = 140.0  # short, single-swap feel

        # Sprite keys expected in SpriteManager.
        self._sprite_taking_damage = "enemy_taking_damage"
        self._sprite_shoot_self = "enemy_shoot_self"
        self._sprite_shooting = "enemy_shooting"

    def _set_sprite_from_key(self, key: str):
        spr = self.sprite_manager.get(key)
        if spr is None:
            return
        self.image = pygame.transform.scale(spr, (self.rect.width, self.rect.height))

    def _set_base_sprite(self):
        #this statement reverts back to the initial enemy/npc static image.
        if self._base_image is not None:
            self.image = self._base_image

    def _play_anim(self, sprite_key: str, duration_ms: float | None = None):
        self._anim_timer_ms = self._anim_duration_ms if duration_ms is None else float(duration_ms)
        self._set_sprite_from_key(sprite_key)

    def play_taking_damage(self):
        if self.mode == "npc":
            return
        self._play_anim(self._sprite_taking_damage)

    def play_shoot_self_animation(self):
        if self.mode == "npc":
            return
        self._play_anim(self._sprite_shoot_self)

    def play_shooting_animation(self):
        if self.mode == "npc":
            return
        self._play_anim(self._sprite_shooting)

    def update(self):
        if self.mode == "npc":
            return

        self.apply_gravity()

        # Timed revert for the single-frame swap animation.
        if self._anim_timer_ms > 0:
            # Enemy.update is called every frame from Game which is 60fps.
            self._anim_timer_ms -= (1000.0 / 60.0)
            if self._anim_timer_ms <= 0:
                self._anim_timer_ms = 0
                self._set_base_sprite()




