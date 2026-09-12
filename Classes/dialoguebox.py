import pygame

class DialogueBox:
    def __init__(self, sprite_manager):
        self.sprite_manager = sprite_manager
        self.current_sprite = None

        self.text = ""
        self.alpha = 0 #making sure the dialogue starts invisible because i want it to fade in and out when in proximity of the player.
        self.anchor_offset_y = -60

        #Controls if the dialogue should appear
        self.active = False

    #This function essentially shows the dialogue
    def show_dialogue(self, sprite_name):
        self.current_sprite = sprite_name
        self.active = True

    #This function hides the dialogue, toggles when the player can and and can't see the dialgoue.
    def hide_dialogue(self):
        self.active = False

    def draw(self, screen, npc_rect):
        if not self.active or not self.current_sprite:
            return

        # This is where the sprite from the sprite manager was obtained.
        bubble = self.sprite_manager.get(self.current_sprite)
        if not bubble:
            return
        
        bubble = bubble.copy()
        bubble.set_alpha(self.alpha) #This set_aplha is used to make the dialgue box fade in and out.

        #these two lines of code sort of anchor the text bubble to the npc.
        x = npc_rect.centerx - 1 #This pushes the speech bubble to the right of the NPC, polishing the game.
        y = npc_rect.top + self.anchor_offset_y

        screen.blit(bubble, (x, y))