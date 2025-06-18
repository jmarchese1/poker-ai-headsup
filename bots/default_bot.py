#importing python packages
import random
import pandas as pd
import numpy as np
import os, sys

#setting working directory
print("cwd: ", os.getcwd())
for p in sys.path:
    print("sys.path:", p)

#path to cloned repository
root = r"C:\Users\jason\projects\poker_project\poker-ai-headsup"

#added path to sys.path[0]
if root not in sys.path:
    sys.path.insert(0, root)

sys.path

#importing custom packages
from engine.simulation_helpers import get_hand_strength


class PokerBot:

    def __init__(self, name, aggression_level):
        self.name = name
        self.chips = 1000
        self.contribution = 0 # tracks how many chips the players have added to the pot 
        self.hand = [] #create a function to pass two cards into this list
        self.aggression_level = aggression_level #should be a number from 1 to 100


def decide_preflop(self, position, pot, call_amount):
    """
    Bot's preflop action in an unraised pot.
    Inputs:
        - position: table position string (e.g., 'UTG', 'MP', etc.)
        - pot: current size of the pot
        - call_amount: how much this player must contribute to call
    Uses:
        - aggression_level: how loose/aggressive this bot plays
        - hand_strength: derived from private hand
    """
    hand_strength = get_hand_strength(self.hand[0], self.hand[1])
    pot_odds = pot / call_amount if call_amount > 0 else float('inf')  # safety guard

    # Early Position (tightest ranges)
    if position in ["UTG", "MP"]:
        if hand_strength >= 9:
            decision = "raise"
        elif hand_strength == 8:
            decision = "raise" if random.randint(1, 100) <= self.aggression_level else "call"
        elif hand_strength == 7:
            decision = "call" if random.randint(1, 100) <= self.aggression_level else "fold"
        elif hand_strength in [5, 6]:
            decision = "call" if random.randint(1, 100) <= max(0, self.aggression_level - 30) else "fold"
        else:
            decision = "fold"

    # Middle Position (looser than EP)
    elif position in ["HJ", "CO"]:
        if hand_strength >= 9:
            decision = "raise"
        elif hand_strength == 8:
            decision = "raise" if random.randint(1, 100) <= self.aggression_level else "call"
        elif hand_strength == 7:
            if pot_odds >= 2:
                decision = "call"
            else:
                decision = "raise" if random.randint(1, 100) <= self.aggression_level else "call"
        elif hand_strength == 6:
            if pot_odds >= 3:
                decision = "call"
            else:
                decision = "fold"
        elif hand_strength in [4, 5]:
            if pot_odds >= 4 and random.randint(1, 100) <= max(0, self.aggression_level - 20):
                decision = "call"
            else:
                decision = "fold"
        else:
            decision = "fold"

    # Button (widest value range)
    elif position == "BTN":
        if hand_strength >= 9:
            decision = "raise"
        elif hand_strength in [7, 8]:
            decision = "raise" if random.randint(1, 100) <= self.aggression_level else "call"
        elif hand_strength in [5, 6]:
            if pot_odds >= 2.5:
                decision = "call"
            else:
                decision = "fold"
        elif hand_strength == 4:
            if pot_odds >= 3 and random.randint(1, 100) <= max(0, self.aggression_level - 10):
                decision = "call"
            else:
                decision = "fold"
        else:
            decision = "fold"

    # Small Blind (must always contribute half the blind)
    elif position == "SB":
        if hand_strength >= 9:
            decision = "raise"
        elif hand_strength == 8:
            decision = "raise" if random.randint(1, 100) <= self.aggression_level else "call"
        elif hand_strength in [6, 7]:
            if pot_odds >= 2:
                decision = "call"
            else:
                decision = "fold"
        elif hand_strength in [4, 5]:
            if pot_odds >= 3:
                decision = "call"
            else:
                decision = "fold"
        else:
            decision = "fold"

    # Big Blind (free check if no raise)
    elif position == "BB":
        if call_amount == 0:
            decision = "check"
        else:
            if hand_strength >= 9:
                decision = "raise"
            elif hand_strength in [7, 8]:
                decision = "call" if random.randint(1, 100) <= self.aggression_level else "fold"
            elif hand_strength in [5, 6]:
                decision = "call" if pot_odds >= 2.5 else "fold"
            else:
                decision = "fold"

    else:
        decision = "fold"  # fallback case

    return decision


def decide_preflop_2(self, position, pot, call_amount):
    """
    Inputs: 
    position : current player position
    pot : total pot size before decision
    call_amount : chips required to call
    
    Returns:
    A string: "fold", "call", or "raise"
    """

    hand_strength = get_hand_strength(self.hand[0], self.hand[1])
    pot_odds = pot / call_amount if call_amount > 0 else float('inf')
    roll = random.randint(1, 100)

    if position in ["UTG", "MP"]:
        if hand_strength >= 10:
            decision = "raise" if self.aggression_level >= roll else "call"
        elif hand_strength == 9:
            decision = "raise" if self.aggression_level - 20 >= roll else "call"
        elif hand_strength in [7, 8]:
            if pot_odds >= 5:
                decision = "call"
            else:
                decision = "call" if self.aggression_level >= roll else "fold"
        elif hand_strength in range(1, 7):
            if pot_odds >= 6:
                decision = "call"
            else:
                decision = "call" if roll < self.aggression_level - 20 else "fold"
        else:
            decision = "call" if pot_odds >= 8 else "fold"

    elif position == "CO":  # Cutoff
        if hand_strength >= 9:
            decision = "raise" if self.aggression_level >= roll else "call"
        elif hand_strength in [7, 8]:
            decision = "raise" if self.aggression_level - 10 >= roll else "call"
        elif hand_strength in [5, 6]:
            if pot_odds >= 4:
                decision = "call"
            else:
                decision = "call" if self.aggression_level >= roll else "fold"
        else:
            decision = "call" if pot_odds >= 6 else "fold"

    elif position == "BTN":  # Button
        if hand_strength >= 8:
            decision = "raise" if self.aggression_level >= roll else "call"
        elif hand_strength in [6, 7]:
            decision = "raise" if self.aggression_level - 10 >= roll else "call"
        elif hand_strength in [4, 5]:
            if pot_odds >= 3:
                decision = "call"
            else:
                decision = "call" if self.aggression_level >= roll else "fold"
        else:
            decision = "call" if pot_odds >= 5 else "fold"

    elif position == "SB":  # Small Blind
        if hand_strength >= 9:
            decision = "raise" if self.aggression_level >= roll else "call"
        elif hand_strength in [6, 7, 8]:
            decision = "call" if pot_odds >= 4 else ("raise" if self.aggression_level >= roll else "fold")
        else:
            decision = "call" if pot_odds >= 5 else "fold"

    elif position == "BB":  # Big Blind
        if call_amount == 0:
            # No raise yet, can check
            if hand_strength >= 9:
                decision = "raise" if self.aggression_level >= roll else "check"
            elif hand_strength >= 6:
                decision = "check"
            else:
                decision = "check"
        else:
            if hand_strength >= 10:
                decision = "raise" if self.aggression_level >= roll else "call"
            elif hand_strength in [7, 8, 9]:
                if pot_odds >= 4:
                    decision = "call"
                else:
                    decision = "call" if self.aggression_level >= roll else "fold"
            else:
                decision = "call" if pot_odds >= 6 else "fold"

    else:
        decision = "fold"  # default fallback

    return decision

