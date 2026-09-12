import pygame
from Classes.player import Player
from Classes.level import Level
from Classes.enemy import Enemy
from Classes.dialoguebox import DialogueBox
from Classes.ui import UI
from Classes.sprite_manager import SpriteManager
from Classes.sound_manager import SoundManager
import random 

    #This class is now the central controller of the game, before main.py had every fucntion in it that had to be excuted manually, now this single class handles all of that process.
class Game:

        #This function creates an instance for a player, level, enemy, dialogue and state and any triggers of the game within the Game class
        # etc. to be excecuted and also makes it so that the players turn can act when set to true, and enemy can't.
        def __init__(self):

            self.level = Level()
            self.state = "start_menu"
            self.house_trigger = pygame.Rect(1045, 574, 50, 100)
            self.boss_trigger = pygame.Rect(1000, 524, 100, 150)
            self.player_turn = True
            self.game_over = False #When this condition is true the game is over
            self.winner = None #Determines who won.
            self.round_number = 1
            self.sprite_manager = SpriteManager()
            self.sound_manager = SoundManager()
            self.ui = UI(self.sprite_manager)
            self.battle_log = []  # stores recent action strings for the UI
            self.enemy_thinking = False
            self.enemy_think_ms = 0

            # Use paths relative to this file so it doesn't depend on the current working directory, helps because it isnt hard coded.
            import os
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # project_root = .../buckshot_platformer
            project_root = os.path.abspath(os.path.join(base_dir, ".."))
            assets_dir = os.path.join(project_root, "Assets")

            #The reason why os.path was used was to ensure paths weren't hardcoded, although it didn't matter in this assesment as much, it just helps with corss platform
            #capabilites.
            def asset(rel_path: str) -> str:
                return os.path.join(assets_dir, rel_path)

            #Character sprites
            self.sprite_manager.load("player", asset(os.path.join("sprites", "player.png")))
            self.sprite_manager.load("enemy", asset(os.path.join("sprites", "enemy.png")))
            self.sprite_manager.load("npc", asset(os.path.join("sprites", "npc.png")))

            # Enemy single-swap animation sprites
            self.sprite_manager.load("enemy_taking_damage", asset(os.path.join("Sprites", "enemy_taking_damage.png")))
            self.sprite_manager.load("enemy_shoot_self", asset(os.path.join("Sprites", "enemy_shoot_self.png")))
            self.sprite_manager.load("enemy_shooting", asset(os.path.join("Sprites", "enemy_shooting.png")))


            # House/rulebook UI
            self.sprite_manager.load("door_text", asset(os.path.join("sprites", "door_text.png")))
            self.sprite_manager.load("rulebook", asset(os.path.join("sprites", "rulebook.png")))
            self.sprite_manager.load("rulebook_ui", asset(os.path.join("sprites", "rulebook_ui.png")))

            # Backgrounds
            self.sprite_manager.load("street_bg", asset(os.path.join("Backgrounds", "street.png")))
            self.sprite_manager.load("house_bg", asset(os.path.join("Backgrounds", "house.png")))
            self.sprite_manager.load("boss_bg", asset(os.path.join("Backgrounds", "boss.png")))
            self.sprite_manager.load("start_menu_bg", asset(os.path.join("Backgrounds", "start_menu.png")))

            # Damage Overlay
            self.sprite_manager.load("taking_damage", asset(os.path.join("Backgrounds", "taking_damage.png")))
            
            # Game over backgrounds (win/lose)
            self.sprite_manager.load("victory_game_over_bg", asset(os.path.join("Backgrounds", "victory_game_over_menu.png")))
            self.sprite_manager.load("defeat_game_over_bg", asset(os.path.join("Backgrounds", "defeat_game_over_menu.png")))

            #If all else fails, just in case, old sprites can be refrenced etc. to ensure the game still works.
            # I am using the correct case + file-relative path to avoid working-dir issues. (Dir issues means, issues related to the loaction of the file.)
            self.sprite_manager.load("game_over_bg", asset(os.path.join("Backgrounds", "game_over_menu.png")))


            self.enemy = Enemy(200, 450, self.sprite_manager, mode="npc") # NPC uses fallback image cause it doesn't have animations.
            self.player = Player(20, 400, self.sprite_manager)

            self.entering_house = False
            self.fade_alpha = 0
            self.fading = False
            self.fade_speed = 5 #Controls speed of the fade, create reference for later.
            # NPC proximity dialogue sprite (load once)
            self.sprite_manager.load("dialogue_box", asset(os.path.join("sprites", "dialogue_box.png")))
            self.dialogue = DialogueBox(self.sprite_manager)

            self.street_floor = 650
            self.house_floor = 525
            self.near_door = False
            self.door_transition = False
            self.icon_offset = 0
            self.icon_direction = 1
            self.round_resetting = False
            self.start_fade = False

            # Death blackout -> game over transition (polish)
            self.death_blackout_ms = 3500
            self.death_fade_ms = 800
            self.game_over_transition_active = False
            self.death_transition_timer = 0  # milliseconds

            #This specific statement is really important, because without this, due to the nature of the update function,
            #A character would shoot 60 times when hitting a key once, due to 60fps, now its only once.
            self.action_taken = False

            #Damage overlay effect
            self.damage_alpha = 0
            self.damage_fade_speed = 1

            # Screen shaking
            self.shake_duration = 0
            self.shake_intensity = 12
            self.shake_offset = [0, 0]

            #Non-blocking turn delay timer
            # Instead of pygame.time.delay() which freezes the whole game loop (and chops up the shake animation), I stored a pending action and
            # count down in milliseconds each frame.  When the timer hits zero the pending action fires and the turn advances normally.
            self.turn_delay_ms   = 0      # countdown in ms
            self.pending_result  = None   # result string waiting to be applied
            self.pending_shooter = None   # "player" or "enemy"

            # Prevents the enemy from firing multiple times per turn.
            # Set True the moment the enemy shoots, cleared when turn swaps back to player.
            self.enemy_fired = False
            self.enemy_thinking = False
            self.enemy_think_ms = 0
            
            #Setting start music.
            self.sound_manager.play_music("start_menu")


        def trigger_damage_effect(self):
            # Damage overlay + screen shake for any hit (player or enemy)
            self.damage_alpha = 180
            self.shake_duration = 15


        def _reload_if_empty(self):
            """Immediately reload the shared weapon if the cylinder is exhausted.""" #Doc string was used here to describe the effet of this function on the player
            #Not really aiming ot explain the internal code.
            if not self.player.weapon.has_shells():
                self.round_number += 1
                self.player.weapon.load_shells()
                self.enemy.weapon = self.player.weapon  # keep shared reference intact
                self.action_taken = False
                print(f"--- Round {self.round_number} started, {len(self.player.weapon.cylinder)} shells loaded ---")

        def _apply_pending_result(self):
            """
            Called once the turn-delay timer expires.
            Resolves turn ownership and game-over checks for the stored result.
            """
            result  = self.pending_result
            shooter = self.pending_shooter
            self.pending_result  = None
            self.pending_shooter = None

            if shooter == "player":

                if not self.player.is_alive():
                    self.game_over = True
                    self.winner = "enemy"
                    self.state = "game_over"
                    self.sound_manager.play_music("end_menu")
                    self.game_over_transition_active = True
                    self.death_transition_timer = 0
                    self.fade_alpha = 255
                    return

                if not self.enemy.is_alive():
                    self.game_over = True
                    self.winner = "player"
                    self.state = "game_over"
                    self.sound_manager.play_music("end_menu")
                    self.game_over_transition_active = True
                    self.death_transition_timer = 0
                    self.fade_alpha = 255
                    return

                if result in ["enemy_live", "self_live"]:
                    self.player_turn = False          # live hit => swap to enemy

                elif result == "enemy_blank":
                    self.player_turn = False          # shot enemy, blank => swap

                elif result == "self_blank":
                    self.player_turn = True           # shot self, blank => keep turn

                self.action_taken = False
                self._reload_if_empty()               # reload now if last shell was just fired

            elif shooter == "enemy":
                # Check deaths first before handing turn back
                if not self.enemy.is_alive():
                    self.game_over = True
                    self.winner = "player"
                    self.state = "game_over"
                    self.sound_manager.play_music("end_menu")
                    self.game_over_transition_active = True
                    self.death_transition_timer = 0
                    self.fade_alpha = 255
                    return

                if not self.player.is_alive():
                    self.game_over = True
                    self.winner = "enemy"
                    self.state = "game_over"
                    self.sound_manager.play_music("end_menu")
                    self.game_over_transition_active = True
                    self.death_transition_timer = 0
                    self.fade_alpha = 255
                    return

                if result in ["enemy_live", "self_live"]:
                    self.player_turn = True        # live hit => swap to player

                elif result == "enemy_blank":
                    self.player_turn = True        # shot at player, blank => swap to player

                elif result == "self_blank":
                    self.player_turn = False       # shot themselves, blank => enemy keeps turn

                self.enemy_fired = False   
                self.enemy_thinking = False
                self.enemy_think_ms = 0               # allow enemy to fire again next turn
                self._reload_if_empty()               # reload now if last shell was just fired


        #This funciton essentially handles all of the gameplay logic, and how the player interacts with the game.
        def update(self, keys):
            dt = self.clock.get_time() / 1000.0 if hasattr(self, 'clock') and self.clock else 1.0 / 60.0 #Calculated delta time, and hasattr checks if it has attributes and if the clock exists.
            dt_ms = dt * 1000.0
    
            # Damage overlay fade
            if self.damage_alpha > 0:
                self.damage_alpha -= self.damage_fade_speed
                if self.damage_alpha < 0:
                    self.damage_alpha = 0

            # Screen shake — runs every frame regardless of delays
            if self.shake_duration > 0:
                self.shake_duration -= 1
                self.shake_offset[0] = random.randint(-self.shake_intensity, self.shake_intensity)
                self.shake_offset[1] = random.randint(-self.shake_intensity, self.shake_intensity)
            else:
                self.shake_offset = [0, 0]

            # Non-blocking turn delay countdown. While a delay is active the game keeps rendering (shake animates smoothly during boss fight
            # but no new input is accepted and turn logic waits.
            if self.turn_delay_ms > 0:
                self.turn_delay_ms -= dt_ms
                if self.turn_delay_ms <= 0:
                    self.turn_delay_ms = 0
                    if self.pending_result is not None:
                        self._apply_pending_result()
                # Still return early so nothing else fires mid-delay
                return

            if self.state == "start_menu":
                if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                    self.start_fade = True

                if self.start_fade:
                    self.fade_alpha = min(255, self.fade_alpha + 3)
                    if self.fade_alpha >= 255:
                        self.fade_alpha = 0
                        self.start_fade = False
                        self.game_over = False
                        self.battle_log = []
                        self.winner = None
                        self.round_number = 1
                        self.action_taken = False
                        self.player_turn = True
                        self.enemy_fired = False
                        self.enemy_thinking = False
                        self.enemy_think_ms = 0
                        self.turn_delay_ms = 0
                        self.pending_result = None
                        self.pending_shooter = None
                        self.entering_house = False
                        self.fading = False
                        self.door_transition = False
                        self.icon_offset = 0
                        self.icon_direction = 1
                        self.enemy = Enemy(200, 450, self.sprite_manager, mode="npc")
                        self.player = Player(20, 400, self.sprite_manager)
                        self.state = "street"
                return

            # game over state.
            if self.state == "game_over":
                # Keep the fade timer running even while waiting for player input.
                if self.game_over_transition_active:
                    self.death_transition_timer += dt_ms

                    if self.death_transition_timer < self.death_blackout_ms:
                        self.fade_alpha = 255
                    else:
                        fade_t = (self.death_transition_timer - self.death_blackout_ms) / max(1, self.death_fade_ms)
                        fade_t = max(0.0, min(1.0, fade_t))
                        self.fade_alpha = int((1.0 - fade_t) * 255)

                        if self.death_transition_timer >= (self.death_blackout_ms + self.death_fade_ms):
                            self.fade_alpha = 0
                            self.game_over_transition_active = False

                if keys[pygame.K_q]:
                    pygame.quit()
                    raise SystemExit

                if keys[pygame.K_r]:
                    self.game_over = False
                    self.winner = None
                    self.round_number = 1
                    self.action_taken = False
                    self.player_turn = True
                    self.enemy_fired = False
                    self.enemy_thinking = False
                    self.enemy_think_ms = 0

                    self.entering_house = False
                    self.fading = False
                    self.fade_alpha = 0
                    self.door_transition = False

                    self.icon_offset = 0
                    self.icon_direction = 1
                    

                    self.enemy = Enemy(200, 450, self.sprite_manager, mode="npc")
                    self.player = Player(20, 400, self.sprite_manager)
                    self.battle_log = []
                    self.game_over_transition_active = False
                    self.death_transition_timer = 0
                    self.turn_delay_ms  = 0
                    self.pending_result = None
                    self.pending_shooter = None
                    self.state = "start_menu"
                    self.sound_manager.stop_music() #Stops the music, so that the next track can start, without difficulty.
                    self.sound_manager.play_music("start_menu")
                return

            self.sound_manager.stop_music()
            if self.state == "street":
                if not self.sound_manager.is_sfx_playing("street_ambience"):
                    self.sound_manager.play_sfx("street_ambience")

                if self.entering_house:
                    target_y = 340 # Sets the target for when the animation of the character walking into the door occurs.

                    # This block of code makes the character fade into the background when entering the door.
                    self.player.rect.y = max(target_y, self.player.rect.y - 2)
                    
                    if self.fading:
                        self.fade_alpha = min(255, self.fade_alpha + self.fade_speed)

                    # After the scene is fully faded.
                    if self.player.rect.y <= target_y and self.fade_alpha >= 255:
                        self.entering_house = False
                        self.state = "house"
                        self.player.rect.x = 100
                        self.player.rect.bottom = 525  # snap directly to house_floor
                        self.player.vel_y = 0
                        self.player.on_ground = True

                        # Reset fade for next time
                        self.fade_alpha = 0
                        self.fading = False

                    return

                self.player.handle_input(keys)

                # Handles gravity, collisions, platform interaction with the player as well.
                self.player.update(self.level.platforms)
                if self.player._intended_left or self.player._intended_right:
                    if not self.sound_manager.is_sfx_playing("walking"):
                        self.sound_manager.play_sfx("walking")
                else:
                    self.sound_manager.stop_sfx("walking")
                    
                if self.player._intended_left or self.player._intended_right:
                    if not self.sound_manager.is_sfx_playing("walking"):
                        self.sound_manager.play_sfx("walking")
                else:
                    self.sound_manager.stop_sfx("walking")

                self.player._select_animation_frame(1000.0 / 60.0) 
                self.enemy.update()

                # The statement below calculates the absolute value of the player from the enemy.
                distance = abs(self.player.rect.x - self.enemy.rect.x)

                # These if/else statements make it so that the dialogue box will fade in and out when the player is in proximity.
                if distance < 120:
                    self.dialogue.current_sprite = "dialogue_box"
                    self.dialogue.active = True
                    self.dialogue.alpha = min(255, self.dialogue.alpha + 5)  # fade in
                else:
                    self.dialogue.alpha = max(0, self.dialogue.alpha - 5)    # fade out
                    if self.dialogue.alpha == 0:
                        self.dialogue.active = False

                # If the player collides with the house trigger, then the "house" state will activate
                if self.player.rect.colliderect(self.house_trigger):
                    self.entering_house = True
                    self.fading = True
                    self.sound_manager.stop_sfx("street_ambience")  # stop ambience on exit

            # When the state of the game is in the house state, there is a platform and a trigger at the coords 200, 500 which activates the boss fight.
            elif self.state == "house":

                # This is to make sure the player can't move when opening the book.
                if self.ui.show_rules:
                    self.ui.handle_rulebook(keys)
                    return
                # movement (only if not transitioning)
                if not self.door_transition:
                    self.player.handle_input(keys)

                # physics
                # Passing the level platforms so Player.on_ground updates correctly when they are in "house" state
                # (Also keeps the floor collision consistent with the street scene.)
                self.player.update(self.level.platforms)

                # Snap to the visual house floor so `Player.on_ground` stays consistent
                # (prevents jump animation getting stuck in mid-air).
                if self.player.rect.bottom >= self.house_floor:
                    self.player.rect.bottom = self.house_floor
                    self.player.vel_y = 0
                    self.player.on_ground = True

                self.player._select_animation_frame(1000.0 / 60.0)



                dx = abs(self.player.rect.centerx - self.ui.rulebook_rect.centerx)
                dy = abs(self.player.rect.centery - self.ui.rulebook_rect.centery)
                self.ui.near_book = dx < 120 and dy < 80

                #mouse_pos = pygame.mouse.get_pos()
                #mouse_click = pygame.mouse.get_pressed()
                # Commented, original plan was to make the book, an object the palyer clicks on with mouse, made it easier by maming them use e key.
                self.ui.handle_rulebook(keys)
                            
                self.icon_offset += 0.3 * self.icon_direction

                if self.icon_offset > 5:
                    self.icon_direction = -1
                elif self.icon_offset < -5:
                    self.icon_direction = 1

                self.near_door = self.player.rect.colliderect(self.boss_trigger)
                
                if self.near_door and keys[pygame.K_e] and not self.door_transition:
                    self.door_transition = True

                # handle fade transition
                if self.door_transition:
                    self.fade_alpha += self.fade_speed

                    if self.fade_alpha > 255:
                        self.fade_alpha = 255

                    if self.fade_alpha >= 255:
                        self.state = "boss_fight"   
                        self.enemy = Enemy(800, 500, self.sprite_manager, mode="boss")
                        
                        # Both player and enemy should use the SAME magazine (shared cylinder order/index).
                        self.player.weapon.load_shells()
                        self.enemy.weapon = self.player.weapon
                        self.round_number = 1
                        self.door_transition = False
                        self.fade_alpha = 0

                # Walking SFX: only stop it during the door transition into the boss fight.
                if self.door_transition:
                    self.sound_manager.stop_sfx("walking")
                else:
                    if self.player._intended_left or self.player._intended_right:
                        if not self.sound_manager.is_sfx_playing("walking"):
                            self.sound_manager.play_sfx("walking")
                    else:
                        self.sound_manager.stop_sfx("walking")


            # For this game state, movement was removed because the player is transitioned from a platformer state to a first-person POV.
            elif self.state == "boss_fight":
                if self.game_over:
                    return

                # Keep enemy animation timers updating during boss fight.
                self.enemy.update()

                if self.player_turn:

                    # If the player is dead, no more actions.
                    if not self.player.is_alive():
                        self.game_over = True
                        self.winner = "enemy"
                        self.state = "game_over"
                        self.game_over_transition_active = True
                        self.death_transition_timer = 0
                        self.fade_alpha = 255
                        return

                    #controls basically, f shoots the enemy, g makes you "run the risk".
                    # trigger_damage_effect() is only called when the PLAYER takes a hit (self_live), never when the enemy is shot.  The delay is
                    # non-blocking so the shake animation plays smoothly, before it used ot somehtimes become choppy.
                    
                    if keys[pygame.K_f] and not self.action_taken:
                        result = self.player.shoot(self.enemy, shoot_self=False)
                        self.action_taken = True

                        if result == "enemy_live":
                            self.sound_manager.play_sfx("shotgun") #SHOOT GUN NOISE
                            self.battle_log.append("You shot the enemy! BANG")
                            self.enemy.play_taking_damage()
                            self.shake_duration = 15   # shake only, no overlay, to provide emphasis that the player shot them.

                        elif result == "enemy_blank":
                            self.sound_manager.play_sfx("shotgun_blank")
                            self.battle_log.append("You shot the enemy...BLANK!")

                        self.pending_result  = result
                        self.pending_shooter = "player"

                        if not self.enemy.is_alive() or not self.player.is_alive():
                            self.turn_delay_ms = 100
                        else:
                            self.turn_delay_ms = 1250

                    elif keys[pygame.K_g] and not self.action_taken:
                        result = self.player.shoot(self.enemy, shoot_self=True)
                        self.action_taken = True

                        # Player shot THEMSELVES only show the damage effect on a live round.
                        if result == "self_live":
                            self.sound_manager.play_sfx("shotgun")
                            self.trigger_damage_effect()  # overlay + shake start immediately
                            self.battle_log.append("You misfired..! BANGG!")
                        elif result == "self_blank":
                            self.sound_manager.play_sfx("shotgun_blank")
                            self.battle_log.append("You misfired...LUCKY")

                            
                        self.pending_result  = result
                        self.pending_shooter = "player"
                        self.turn_delay_ms   = 800  # non-blocking pause; shake plays during this

                        
                    if not keys[pygame.K_f] and not keys[pygame.K_g]:
                        self.action_taken = False

                else:
                    # this is the enemies turn fires once per turn unless shooting blank at self.(guarded by enemy_fired),
                    
                    if not self.enemy.is_alive():
                        self.game_over = True
                        self.winner = "player"
                        self.state = "game_over"
                        self.game_over_transition_active = True
                        self.death_transition_timer = 0
                        self.fade_alpha = 255
                        return

                    # Only fire once — enemy_fired is cleared in _apply_pending_result
                    if not self.enemy_fired:
                        if not self.enemy_thinking:
                            self.enemy_thinking = True
                            self.enemy_think_ms = random.randint(2200, 3200) #Random thinking time for the enemy, builds suspense, makes it feel like you are versing an enemy.

                        self.enemy_think_ms -= dt_ms
                        if self.enemy_think_ms > 0:
                            return

                        # Done thinking — now fire
                        self.enemy_fired = True


                        if not self.player.weapon.has_shells():
                            self._reload_if_empty()
                            self.player_turn = True
                            self.enemy_fired = False
                            self.enemy_thinking = False
                            self.enemy_think_ms = 0
                            return

                        shoot_self = random.choice([True, False])
                        result = self.enemy.shoot(self.player, shoot_self=shoot_self)
                        
                        if result == "enemy_live":
                            self.sound_manager.play_sfx("shotgun")
                            self.trigger_damage_effect()
                            self.battle_log.append("Enemy shot you! BANG")
                            # Show the enemy as shooting (at the player) on a live round.
                            self.enemy.play_shooting_animation()
                        elif result == "enemy_blank":
                            self.sound_manager.play_sfx("shotgun_blank")
                            self.battle_log.append("Enemy shot you... click.")
                            # Blank-at-player should NOT show the self-misfire animation.
                            # Also avoid switching sprites at all so it stays the default enemy sprite.
                            pass
                        elif result == "self_live":
                            self.sound_manager.play_sfx("shotgun")
                            self.battle_log.append("Enemy misfired..! BANG")
                            self.enemy.play_shoot_self_animation()
                        elif result == "self_blank":
                            self.sound_manager.play_sfx("shotgun_blank")
                            self.battle_log.append("Enemy misfired... click.")
                            


                        # If the weapon was exhausted by this shot, reload right away
                        # so the next turn never sees an empty cylinder.
                        if result is None:
                            # Shouldn't normally happen since it was checked above, but still have to be safe.
                            self._reload_if_empty()
                            self.battle_log.append(f"--- Round {self.round_number} ---")
                            self.player_turn = True
                            self.enemy_fired = False
                            self.enemy_thinking = False
                            self.enemy_think_ms = 0
                            return

                        self.pending_result  = result
                        self.pending_shooter = "enemy"

                        # If someone just died, skip straight to a short delay then game over. before, players had to wait, which didn't feel authentic.
                        if not self.enemy.is_alive() or not self.player.is_alive():
                            self.turn_delay_ms = 100   # just enough to see the reaction frame
                        else:
                            self.turn_delay_ms = 2000


        #This function essentially tells python to draw everything in the level including the player, enemy, dialogue etc.
        def draw(self, screen):
            world_surface = pygame.Surface((1280, 720), pygame.SRCALPHA)
            offset_x = self.shake_offset[0]
            offset_y = self.shake_offset[1]

            if self.state == "start_menu":
                bg = self.sprite_manager.get("start_menu_bg")
                if bg:
                    world_surface.blit(bg, (offset_x, offset_y))
                else:
                    screen.fill((0, 0, 0))


            if self.state == "game_over":
                # Winner decides which background to show.
                if self.winner == "player":
                    bg = self.sprite_manager.get("victory_game_over_bg")
                else:
                    bg = self.sprite_manager.get("defeat_game_over_bg")

                if bg:
                    world_surface.blit(bg, (offset_x, offset_y))
                else:
                    # Fallback to old background key if needed.
                    fallback = self.sprite_manager.get("game_over_bg")
                    if fallback:
                        world_surface.blit(fallback, (0, 0))
                    else:
                        screen.fill((0, 0, 0))


            if self.state == "street":
                bg = self.sprite_manager.get("street_bg")

                if bg:
                    world_surface.blit(bg, (offset_x, offset_y))
                else:
                    screen.fill((30, 30, 30,))
                self.level.draw(world_surface)
                self.player.draw(world_surface)
                self.enemy.draw(world_surface)
                self.dialogue.draw(world_surface, self.enemy.rect)

            elif self.state == "house":
                self.sound_manager.stop_sfx("street_ambience")
                bg = self.sprite_manager.get("house_bg")
                if bg:
                    world_surface.blit(bg, (offset_x, offset_y))
                else:
                    screen.fill((30, 30, 30))


                #The reason why this block of statemtns is in this order, is because originally, the book was being drawn over the player.
                self.ui.draw_rulebook_prompt(world_surface)
                if not self.ui.show_rules:
                    self.ui.draw_rulebook_book(world_surface)
                    self.player.draw(world_surface)
                else:
                    self.player.draw(world_surface)
                    self.ui.draw_rulebook_book(world_surface)
                

                if self.near_door:
                    icon = self.sprite_manager.get("door_text")
                    if icon:
                        icon_rect = icon.get_rect()
                        icon_rect.centerx = self.boss_trigger.centerx + 90
                        icon_rect.top = self.boss_trigger.top - 115 + self.icon_offset
                        world_surface.blit(icon, icon_rect)

            elif self.state == "boss_fight":
                self.sound_manager.stop_sfx("street_ambience")
                bg = self.sprite_manager.get("boss_bg")
                if bg:
                    world_surface.blit(bg, (offset_x, offset_y))
                else:
                    screen.fill((20, 20, 20))
                
                enemy_x = screen.get_width() // 2
                enemy_y = screen.get_height() // 3 + 80
                self.enemy.rect.center = (enemy_x, enemy_y)
                self.enemy.draw(world_surface)

                self.ui.draw_round(world_surface, self.round_number)
                self.ui.draw_player_panel(world_surface, self.player)
                self.ui.draw_enemy_panel(world_surface, self.enemy)
                self.ui.draw_shell_panel(world_surface, self.player.weapon)
                self.ui.draw_action_panel(world_surface, self.player_turn)
                self.ui.draw_battle_log(world_surface, self.battle_log)

            if self.damage_alpha > 0:
                blood = self.sprite_manager.get("taking_damage")
                if blood:
                    blood.set_alpha(int(self.damage_alpha))
                    world_surface.blit(blood, (0, 0))

            if self.fade_alpha > 0:
                fade_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                fade_surface.fill((0, 0, 0, self.fade_alpha))
                world_surface.blit(fade_surface, (0, 0))

            screen.blit(world_surface, self.shake_offset)