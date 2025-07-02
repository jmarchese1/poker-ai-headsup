import random
import numpy as np
import os, sys

print(f"current working directory: {os.getcwd()}")

root = r"C:\Users\jason\projects\poker_project\poker-ai-headsup"

if root not in sys.path:
    sys.path.insert(0, root)

from bots.default_bot import PokerBot


class RLBot(PokerBot):
    """
    Replicating default poker bot as a seperate class optimized for reinforcement learning.
    """
    def __init__(self, name : str = "Rocky", chips : int = 2000, aggression_level : int = 60, tightness_level : int = 2, bluffing_factor : int = 19):
        super().__init__(name = name, chips = chips, aggression_level = aggression_level, tightness_level = tightness_level, bluffing_factor = bluffing_factor)

    def reset_hand(self, chips: int):
        """
        Called by the env at the top of reset():
          • chips is the RL bots starting stack for this hand.
        We clear any per-hand state so the env can start dealing.
        """
        self.chips = chips
        self.starting_stack = chips
        self.folded = False
        self.all_in = False
        self.contribution = 0
