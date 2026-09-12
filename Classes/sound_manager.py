import pygame
import os #To make sure we aren't hardcoding the files specific to my computer.

class SoundManager:
    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.pre_init(44100, -16, 2, 512)  # 512 buffer instead of default 4096, becausr originally buffereing like crazy.
            pygame.mixer.init()

        base_dir = os.path.dirname(os.path.abspath(__file__)) #basically telling the computer where to find the file
        project_root = os.path.abspath(os.path.join(base_dir, ".."))
        sounds_dir = os.path.join(project_root, "Assets", "Sounds")

        #Creating a sound function to load sound effects into the game, funciton in a function
        def sound(filename):
            return os.path.join(sounds_dir, filename)

        # Load sound effects
        self.shotgun = pygame.mixer.Sound(sound("shotgun_sfx.ogg"))
        self.shotgun_blank = pygame.mixer.Sound(sound("shotgun_blank_sfx.ogg"))
        self.street_ambience = pygame.mixer.Sound(sound("street_ambience_sfx.ogg"))
        self.walking = pygame.mixer.Sound(sound("walking_sfx.ogg"))

        self.street_ambience.set_volume(0.15)
        self.walking.set_volume(0.8)

        # Track current music so we don't restart it if already playing
        self._current_music = None

        # Music file paths
        self._music = {"start_menu": sound("start_menu_music.ogg"), "end_menu": sound("end_menu_music.ogg")}

    #Function essentailly plays the loaded in sfx.
    def play_sfx(self, name):
        if name == "shotgun":
            self.shotgun.play()
        elif name == "shotgun_blank":
            self.shotgun_blank.play()
        elif name == "street_ambience":
            self.street_ambience.play(-1)  # -1 loops forever, because its street ambience.
        elif name == "walking":
            self.walking.play()

    def is_sfx_playing(self, name):
        if name == "walking":
            return self.walking.get_num_channels() > 0
        elif name == "street_ambience":
            return self.street_ambience.get_num_channels() > 0
        return False
    
    #Function stops sfx.
    def stop_sfx(self, name):
        if name == "street_ambience":
            self.street_ambience.stop()
        elif name == "walking":
            self.walking.stop()

    def play_music(self, track, loop=True, volume=0.5):
        # Don't restart if already playing the same track
        if self._current_music == track:
            return

        path = self._music.get(track)
        if not path:
            return

        self._current_music = track
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1 if loop else 0)

    def stop_music(self):
        pygame.mixer.music.stop()
        self._current_music = None
