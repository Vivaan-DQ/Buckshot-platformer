class Shell:

    #Function to see whether the shell is live, and depending on that it is returned.
    def __init__(self, live):
        self.live = live
    
    def is_live(self):
        return self.live