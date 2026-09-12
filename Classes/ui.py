#Rewriting the entire class for ui for effieicny during the final stage of the boss fight and streamlining other processes.

import pygame

class UI:
    def __init__(self, sprite_manager):
        self.sprite_manager = sprite_manager

        
        if not pygame.font.get_init():
            pygame.font.init()

        self.font = pygame.font.SysFont(None, 36)
        self.big_font = pygame.font.SysFont(None, 72)


        #This is where the rulebook attributes are sorted and stored.
        self.book_width = 10
        self.book_height = 40

        #Where and what dimensions is the rule book going to be stored in.
        self.rulebook_rect = pygame.Rect(582, 385, self.book_width, self.book_height)
        
        #Both values assumed false, until needing to be acted upon.
        self.near_book = False
        self.show_rules = False

        self.prompt_offset = 0
        self.prompt_dir = 1

    #New function for the generic UI panel, ths specific function is extrmely crucial for the entire game
    def draw_panel(self, screen, x, y, w, h, allign=None):  
        if allign == "center":
            x = screen.get_width() // 2 - w // 2
            y = screen.get_height() // 2 - h // 2

        elif allign == "bottom_right":
            x = screen.get_width() - w - 20
            y = screen.get_height() - h - 20

        elif allign == "bottom_left":
            x = 20
            y = screen.get_height() - h - 20

        elif allign == "top_right":
            x = screen.get_width() - w - 20
            y = 20

        rect = pygame.Rect(x, y, w, h)

        panel_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        panel_surf.fill((10, 10, 10, 180))  # dark transparent

        screen.blit(panel_surf, (x, y))
        pygame.draw.rect(screen, (200, 200, 200), rect, 2)

        return rect

    #This function is the health bar (self explanatory.) and allinging it to the elft of the screen.
    def draw_health_bar(self, screen, panel_rect, health, allign="left"):
        bar_width = 200
        bar_height = 20

        if allign == "left":
            x = panel_rect.left + 20
        else:
            x = panel_rect.right - bar_width - 20
        
        y = panel_rect.top + 20

        pygame.draw.rect(screen, (255, 0, 0), (x, y, bar_width, bar_height)) 

        width = max(0, min(health, 100)) * 2 #Setting the width so that it doesn't oveflow at any point
        pygame.draw.rect(screen, (0, 255, 0), (x, y, width, bar_height))


    
    #This function is to display what round is going on.

    def draw_round(self, screen, round_number):
        text = self.big_font.render(f"ROUND {round_number}", True, (255, 255, 255))
        rect = text.get_rect(center=(screen.get_width() // 2, 50))
        #Again this code is used to draw all the elements on pygame consol, the get width command is to centre it on screen
        screen.blit(text, rect)

    #Next function: draws buckshot “cylinder” preview for the boss fight.

    def draw_shells(self, screen, weapon, panel_rect):

        # Remaining shells are consumed sequentially from weapon.cylinder.
        cylinder = getattr(weapon, "cylinder", []) #getattr, used to retrieve the value of an object's attribute dynamically.
        next_i = getattr(weapon, "next_chamber_index", 0)

        if not cylinder or next_i >= len(cylinder):
            shells_left = 0
            display = []
            next_marker_x = None
        else:
            remaining_shells = cylinder[next_i:]
            shells_left = len(remaining_shells)

            live_shells = [s for s in remaining_shells if s.is_live()]
            blank_shells = [s for s in remaining_shells if not s.is_live()]

            #Display order: ALL LIVE first, then ALL BLANK, purposefully dont want to give the order away.
            display = [*live_shells, *blank_shells]


        total_width = max(1, len(display)) * 30
        start_x = panel_rect.centerx - total_width // 2
        y = panel_rect.centery + 120

        #dras the shells, and appends them to the list., red if live, grey if blank,
        for i, shell in enumerate(display):
            color = (220, 40, 40) if shell.is_live() else (140, 140, 140)

            rect = (start_x + i * 30, y, 20, 40)
            pygame.draw.rect(screen, color, rect, border_radius=4)
            pygame.draw.rect(screen, (0, 0, 0), rect, 2, border_radius=4)



        #this displas the remaining shells left for the round.
        remaining_text = self.font.render(f"{shells_left} LEFT", True, (255, 255, 255))
        remaining_rect = remaining_text.get_rect(center=(panel_rect.centerx, panel_rect.bottom + 105))
        screen.blit(remaining_text, remaining_rect)
    
    #function for improving UI of th shells by adding an extra border
    def draw_shell_panel(self, screen, weapon):

        #only render the shells + their text using the panel rect as an anchor.
        panel = self.draw_panel(screen, 0, 0, 0, 0, allign="center") #This is all 0,0,0,0 because it was to late to change all prarameter so i jst made the rect non-existent.

        # Draw_shells uses panel_rect.centery to compute shell/text positions.
        self.draw_shells(screen, weapon, panel)

    
    #Next function is for the action panel where player can choose their turn
    def draw_actions(self, screen, panel_rect, player_turn):

        #Both lines essentailly say, if its not the palyers turn the options will be gray, hinting that they are disabled.
        shoot_color = (255, 255, 255) if player_turn else (100, 100, 100)

        shoot_enemy = self.font.render("> SHOOT ENEMY <", True, shoot_color)
        shoot_self = self.font.render("> RUN THE RISK?? <", True, shoot_color)

        enemy_rect = shoot_enemy.get_rect(center=(panel_rect.centerx, panel_rect.top + 40))
        self_rect = shoot_self.get_rect(center=(panel_rect.centerx, panel_rect.top + 80))

        #Now again calling upon the draw function to draw both shoot and reload in pygame console
        screen.blit(shoot_enemy, enemy_rect)
        screen.blit(shoot_self, self_rect)

    #adding an extra draw_action_panel providing better UI, add border to stop making it lool like floating text
    def draw_action_panel(self, screen, player_turn):
        panel = self.draw_panel(screen, 0, 0, 300, 120, allign="bottom_right")
        self.draw_actions(screen, panel, player_turn)
    
    #MAIN function to draw, player panel:
    def draw_player_panel(self, screen, player):
        # Keep the health bar, but remove the surrounding panel rectangle/border.
        panel = pygame.Rect(50, 500, 300, 120)
        self.draw_health_bar(screen, panel, player.health, allign="left")

        label = self.font.render(f"PLAYER HEALTH: {player.health}", True, (255, 255, 255))
        label_rect = label.get_rect(center=(panel.centerx, panel.bottom - 15))
        screen.blit(label, label_rect)

    #ANOTHER MAIN function to draw, enemy panel
    def draw_enemy_panel(self, screen, enemy):
        # Keep the health bar, but remove the surrounding panel rectangle/border.
        panel = pygame.Rect(930, 50, 300, 120)
        self.draw_health_bar(screen, panel, enemy.health, allign="right")

        label = self.font.render(f"ENEMY HEALTH: {enemy.health}", True, (255, 255, 255))
        label_rect = label.get_rect(center=(panel.centerx, panel.bottom - 15))
        screen.blit(label, label_rect)

    #Now for the funciton realted back to the rulebook where the player hits e key to use.
    def handle_rulebook(self, keys):
        if self.near_book and keys[pygame.K_e]:
            self.show_rules = True
        #Basically is the player is near the rule book and hits e key, they see the book.

        #If the player is already seeing the rules and hits escape, they stop seeing it.
        if self.show_rules and keys[pygame.K_ESCAPE]:
            self.show_rules = False
        
        #This part is the dialogue offset to float in the air.
        self.prompt_offset += 0.2 * self.prompt_dir

        if self.prompt_offset > 5:
            self.prompt_dir = -1
        
        elif self.prompt_offset < -5:
            self.prompt_dir = 1
        
    # Draw only the prompt text (door_text) behind the player.
    def draw_rulebook_prompt(self, screen):
        if self.near_book and not self.show_rules:
            prompt = self.sprite_manager.get("door_text")
            if prompt:
                rect = prompt.get_rect()
                rect.centerx = self.rulebook_rect.centerx + 75
                rect.top = self.rulebook_rect.top + 45 + self.prompt_offset
                screen.blit(prompt, rect)

    # Draw only the book sprites (closed book + opened UI overlay).
    def draw_rulebook_book(self, screen):
        # The closed book always has to be drawn on top of the background in pygame.
        book = self.sprite_manager.get("rulebook")
        if book:
            scaled = pygame.transform.scale(book, (self.book_width, self.book_height))
            screen.blit(scaled, self.rulebook_rect)

        # Once the book is opened, show the rules overlay.
        if self.show_rules:
            ui_sprite = self.sprite_manager.get("rulebook_ui")
            if ui_sprite:
                rect = ui_sprite.get_rect()
                rect.center = (screen.get_width() // 2, screen.get_height() // 2)
                screen.blit(ui_sprite, rect)

    #Draws the rulebook again, once closed 
    def draw_rulebook(self, screen):
        self.draw_rulebook_prompt(screen)
        self.draw_rulebook_book(screen)

    def draw_battle_log(self, screen, log):
        panel = self.draw_panel(screen, 0, 0, 280, 160, allign="top_left")
        title = self.font.render("BATTLE LOG", True, (255, 220, 50))
        screen.blit(title, (panel.left + 10, panel.top + 8))

        log_font = pygame.font.SysFont(None, 24)
        # Show only the last 4 entries so it fits in the panel for the battle log
        for i, entry in enumerate(log[-4:]):
            text = log_font.render(entry, True, (220, 220, 220))
            screen.blit(text, (panel.left + 10, panel.top + 38 + i * 28))