import pygame
import os
from Classes.character import Character


class Player(Character):
    def __init__(self, x, y, sprite_manager):
        super().__init__(x, y, 80, 130, sprite_manager, "player")
        
        #Sets the speed and jump power for the player.
        self.speed = 5
        self.jump_power = 8

        # Track last movement intent for animation selection
        self._prev_left = False
        self._prev_right = False
        self._intended_left = False
        self._intended_right = False

        # Animation format
        #   row 0: idle
        #   row 1: walking
        #   row 2: jumping
        self.sheet_cols = 4
        self.sheet_rows = 3

        # Each frame on sprite_sheet_player.png is 300x600 (sheet is 1200x1800).
        self.frame_w = 300
        self.frame_h = 600


        # Walking animation has multiple frames; the best way was choose how many frames to advance per second.
        # Idle animation has fewer frames (1), but walk typically looks best with ~5-6 FPS.
        self.anim_fps = 5  # walk cycle rate
        self._anim_time_ms = 0

        # Load the sheet from Assets/Sprites/player_sprite_sheet.png but fall back to existing sprite_sheet_player.png if missing, good fail safe.
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(base_dir, ".."))
        assets_dir = os.path.join(project_root, "Assets")
        sheet_path_primary = os.path.join(assets_dir, "Sprites", "player_sprite_sheet.png")
        sheet_path_fallback = os.path.join(assets_dir, "Sprites", "sprite_sheet_player.png")

        sheet = None
        if os.path.exists(sheet_path_primary):
            sheet = pygame.image.load(sheet_path_primary)
        elif os.path.exists(sheet_path_fallback):
            sheet = pygame.image.load(sheet_path_fallback)

        # If sheet load failed, keep the static sprite behavior.
        self.animations = { #Essentailly created a dictionary to recreate the animation sprite shet, but in coded format.
            "idle": [],
            "walk": [],
            "jump": [],
        }

        self._has_animation_sheet = False
        if sheet is not None:
            try:
                sheet = sheet.convert_alpha() if hasattr(sheet, "convert_alpha") else sheet
                self._build_animations_from_sheet(sheet)
                # Only enable animation if the frames were actually built.
                if self.animations["idle"] and self.animations["walk"] and self.animations["jump"]:
                    self._has_animation_sheet = True
                    # Start with idle
                    self._set_image_from_animation("idle", frame_index=0, flip_x=False)
            except Exception as e:
                print(f"Player animation sheet failed to load/slice: {e}")
                self._has_animation_sheet = False


    def _build_animations_from_sheet(self, sheet: pygame.Surface):
        # Slice frames based on fixed frame size.
        # Assumes sheet is exactly sheet_cols * frame_w by sheet_rows * frame_h.
        for col in range(self.sheet_cols):
            # idle row = 0
            frame = sheet.subsurface(
                pygame.Rect(col * self.frame_w, 0 * self.frame_h, self.frame_w, self.frame_h)
            ).copy()
            self.animations["idle"].append(frame)

        for col in range(self.sheet_cols):
            # walk row = 1
            frame = sheet.subsurface(
                pygame.Rect(col * self.frame_w, 1 * self.frame_h, self.frame_w, self.frame_h)
            ).copy()
            self.animations["walk"].append(frame)

        for col in range(self.sheet_cols):
            # jump row = 2
            frame = sheet.subsurface(
                pygame.Rect(col * self.frame_w, 2 * self.frame_h, self.frame_w, self.frame_h)
            ).copy()
            self.animations["jump"].append(frame)

    #The function essentially loads and prepares a specific frame from the loaded sprite sheet animation then loops the animation, and horizontally flips it
    #if needed because player can walk in both directions.
    def _set_image_from_animation(self, anim_name: str, frame_index: int, flip_x: bool):
        frames = self.animations.get(anim_name, [])
        if not frames:
            return
        frame_index %= len(frames)
        img = frames[frame_index]
        if flip_x:
            img = pygame.transform.flip(img, True, False)

        # Keep rect stable (size is fixed by Character base init)
        self.image = pygame.transform.scale(img, (self.rect.width, self.rect.height))

    def _movement_intent(self, keys): #Movement, self explanatory.
        left = keys[pygame.K_a]
        right = keys[pygame.K_d]
        return left, right

    # Handling keyboard input
    def handle_input(self, keys):
        left, right = self._movement_intent(keys)

        # Store intended direction for animation makes it easier for future implications.
        self._intended_left = left
        self._intended_right = right

        if left:
            self.rect.x -= self.speed
        if right:
            self.rect.x += self.speed

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -self.jump_power
            self.on_ground = False

        # Reload (boss fight UI key)
        if keys[pygame.K_r]:
            self.weapon.reload()
            print("RELOADED")

        
        self._prev_left = left
        self._prev_right = right

    #Function just applies gravity.
    def apply_gravity(self):
        if not self.on_ground:
            self.vel_y += self.gravity
        self.rect.y += self.vel_y


    def _select_animation_frame(self, dt_ms: float):
        #It is important to know that keys are not needed here the movement is tracekd in self._intended_left / self._intended_right from handle_input().

        # if there isn't a sprite sheet, do nothing.
        if not self._has_animation_sheet:
            return

        #Determine facing based on current horizontal motion if self.rect.x is updated directly in handle_input(), so delta is reflected next tick.
        # If neither A nor D is pressed, its like it was idle, nothing happens.
        flip_x = False
        if self._intended_left and not self._intended_right:
            flip_x = True

        #Jump condition: ascending (jumping) while not on ground.
        if (not self.on_ground) and self.vel_y < 0:
            self._anim_time_ms = 0
            self._set_image_from_animation("jump", frame_index=0, flip_x=flip_x)
            return

        # Walk condition: on ground and horizontal movement intent. Uses on_ground state + intended direction; dt_ms comes from the same update call in both scenes.)
        if self.on_ground and (self._intended_left or self._intended_right):
            self._anim_time_ms += dt_ms
            frame = int((self._anim_time_ms / (1000.0 / self.anim_fps)))
            self._set_image_from_animation("walk", frame_index=frame, flip_x=flip_x)
            return

    def update(self, platforms):
        # Keep animation timing easier to understand: dt approximation if no external dt.
        # Since Character updates are called per-frame, this makes the system optimal to use.
        dt_ms = 1000.0 / 60.0

        self.apply_gravity()
        
        # Assume in air until collision with asurface, mostl likey its going to be the floor.
        self.on_ground = False

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True

        #Animation selection is driven by movement + physics.
        #The current key can't be accessed from here, so it relys on the stored intended direction from handle_input.
        #Also jump decision uses vel_y/on_ground.
        self._select_animation_frame(dt_ms)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


