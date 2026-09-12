import random
from Classes.shell import Shell


# Buckshot “cylinder” model.
# - Each load/reload creates a fixed chamber order for the whole round.
# - Each shoot essentailly consumes the next chamber sequentially.
# - display_shells is a fake copy to keep the UI “unknown to player” look.
class Weapon:
    def __init__(self, damage):
        self.damage = 20

        # Cylinder/chambers for the current round
        self.cylinder = []  # list[Shell]
        self.next_chamber_index = 0
        self.chamber_count = 0

        # UI-only ordering (unknown order)
        self.display_shells = []  # list[Shell]

    def load_shells(self):
        # New round: create fixed cylinder order.
        self.cylinder = []
        self.next_chamber_index = 0

        self.chamber_count = random.randint(4, 8)
        for _ in range(self.chamber_count):
            self.cylinder.append(Shell(random.choice([True, False])))

        # Display order: player can’t see the actual cylinder order.
        self.display_shells = self.cylinder.copy()
        random.shuffle(self.display_shells)

    def reload(self):
        self.load_shells()

    def shoot(self):
        # No shells left in the cylinder (round over)
        if self.next_chamber_index >= len(self.cylinder):
            return None

        shell = self.cylinder[self.next_chamber_index]
        self.next_chamber_index += 1

        return "live" if shell.is_live() else "blank"

    def has_shells(self):
        return self.next_chamber_index < len(self.cylinder)

