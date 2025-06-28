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

    def __init__(self, name, chips, aggression_level, tightness_level, bluffing_factor):
        self.name = name
        self.chips = chips
        self.contribution = 0 # tracks how many chips the players have added to the pot 
        self.all_in = False
        self.hand = [] #create a function to pass two cards into this list
        self.aggression_level = aggression_level #should be a number from 1 to 100
        self.tightness_level = tightness_level #should be a number 1 to 3 (1 is the tightest range)
        self.bluffing_factor = bluffing_factor #should be a number 0 to 30 representing percentage of the time with complete bluffs
        self.refills = 0 # counter to track the amount of times the bot refilled its stack  

    def refill_chips(self, starting_stack = 2000, big_blind = 10):
        if self.chips < big_blind:
            refill_amount = starting_stack - self.chips
            self.chips += refill_amount
            self.refills += 1

    def decide_preflop(self, position, pot, call_amount):
        """
        Bot's preflop action in an unraised pot.
        Inputs:
            - position: table position string (e.g., 'UTG', 'MP', etc.)
            - pot: current size of the pot
            - call_amount: how much this player must contribute to call
        Uses:
            - aggression_level: odds on if a bot decides to raise or call, or call or fold
            - tightness_level: preflop range of the bot
            - hand_strength: derived from private hand
        """
        hand_strength = get_hand_strength(self.hand[0], self.hand[1])
        pot_odds = pot / call_amount if call_amount > 0 else float('inf')  # safety guard

        # Early Position folds most hands
        if position in ["UTG", "MP", "HJ", "CO"]:
            if self.tightness_level == 1: #tightest preflop range
                if hand_strength >= 9: #not many hands this high
                    decision = "raise"
                elif hand_strength == 8:
                    decision = "raise" if random.randint(1, 100) <= self.aggression_level else "call"
                elif hand_strength == 7:
                    decision = "call" if random.randint(1, 100) <= self.aggression_level else "fold"
                else:
                    decision = "fold"
            elif self.tightness_level == 2: #balanced preflop range
                if hand_strength >= 9: #not many hands this high
                    decision = "raise"
                elif hand_strength == 8:
                    decision = "raise" if random.randint(1, 100) <= self.aggression_level else "call"
                elif hand_strength == 7:
                    decision = "raise" if random.randint(1, 100) <= self.aggression_level else "call"
                elif hand_strength in [5, 6]:
                    decision = "call" if random.randint(1, 100) <= self.aggression_level + 15 else "fold"
                elif hand_strength in [3, 4]:
                    decision = "call" if random.randint(1, 100) <= self.aggression_level else "fold"
                else:
                    decision = "fold"
            else: #loosest preflop range
                if hand_strength >= 9: #not many hands this high
                    decision = "raise"
                elif hand_strength == 8:
                    decision = "raise" if random.randint(1, 100) <= self.aggression_level else "call"
                elif hand_strength == 7:
                    decision = "raise" if random.randint(1, 100) <= self.aggression_level else "call"
                elif hand_strength in [5, 6]:
                    decision = "raise" if random.randint(1, 100) <= self.aggression_level + 15 else "call"
                elif hand_strength in [3 ,4]:
                    decision = "raise" if random.randint(1, 100) <= self.aggression_level else "call"
                else: 
                    decision = "call" if random.randint(1, 100) <= self.aggression_level -50 else "fold"
                

        # Button widest ranges, strongest position
        elif position == "BTN":
            if self.tightness_level == 1:
                if hand_strength >= 9: #not many hands this high
                    decision = "raise"
                elif hand_strength == 8:
                    decision = "raise" if random.randint(1, 100) <= self.aggression_level else "call"
                elif hand_strength == 7:
                    decision = "raise" if random.randint(1, 100) <= self.aggression_level else "call"
                elif hand_strength in [5, 6]:
                    decision = "call" if random.randint(1, 100) <= self.aggression_level + 15 else "fold"
                elif hand_strength in [3, 4]:
                    decision = "call" if random.randint(1, 100) <= self.aggression_level else "fold"
                else:
                    decision = "fold"
            elif self.tightness_level == 2: #balanced preflop range
                if hand_strength >= 9: #not many hands this high
                    decision = "raise"
                elif hand_strength == 8:
                    decision = "raise" if random.randint(1, 100) <= self.aggression_level else "call"
                elif hand_strength == 7:
                    decision = "raise" if random.randint(1, 100) <= self.aggression_level else "call"
                elif hand_strength in [5, 6]:
                    decision = "call" if random.randint(1, 100) <= self.aggression_level + 30 else "fold"
                elif hand_strength in [3, 4]:
                    decision = "call" if random.randint(1, 100) <= self.aggression_level + 15 else "fold"
                else:
                    decision = "fold"
            else: #loosest preflop range
                if hand_strength >= 9: #not many hands this high
                    decision = "raise"
                elif hand_strength == 8:
                    decision = "raise" if random.randint(1, 100) <= self.aggression_level else "call"
                elif hand_strength == 7:
                    decision = "raise" if random.randint(1, 100) <= self.aggression_level else "call"
                elif hand_strength in [5, 6]:
                    decision = "raise" if random.randint(1, 100) <= self.aggression_level + 30 else "call"
                elif hand_strength in [3 ,4]:
                    decision = "raise" if random.randint(1, 100) <= self.aggression_level else "call"
                else: 
                    decision = "call" if random.randint(1, 100) <= self.aggression_level -30 else "fold"

                
        # just slighlty tighter from the button
        elif position == "SB":
            if hand_strength >= 9:
                decision = "raise"
            elif hand_strength == 8:
                decision = "raise" if random.randint(1, 100) <= self.aggression_level else "call"
            elif hand_strength in [6, 7]:
                decision = "call" if random.randint(1, 100) >= self.aggression_level else "raise"
            elif hand_strength in [3, 4, 5]:
                decision = "call" if random.randint(1, 100) >= self.aggression_level + 10 else "raise" #makes it require more aggression to raise with a weaker hand
            elif hand_strength in [1, 2]:
                if self.tightness_level in [2, 3]:
                    decision = "call" if random.randint(1, 100) <= self.aggression_level + 20 else "fold"
                else:
                    decision = "fold"
            else:
                if self.tightness_level == 3:
                    decision = "call" if random.randint(1, 100) <= self.aggression_level else "fold"
                else:
                    decision = "fold"

        # Big Blind (free check if no raise)
        else: #position == BB
            #whether the pot odds are high or low, good move to raise here at the big blind with a decent hand since nobody else was strong enough to raise
            if self.tightness_level == 3:
                if hand_strength >= 3:
                    decision = "raise" if random.randint(1, 100) <= self.aggression_level else "check"
                elif hand_strength == 2:
                    decision = "raise" if random.randint(1, 100) <= self.aggression_level - 10 else "check"
                else: #pure randomness for loose player in this position
                    decision = "check" if random.randint(1, 100) > 90 else "check"
            elif self.tightness_level == 2:
                if hand_strength >= 3:
                    decision = "raise" if random.randint(1, 100) <= self.aggression_level else "check"
                elif hand_strength == 2:
                    decision = "raise" if random.randint(1, 100) <= self.aggression_level - 10 else "check"
                else: 
                    decision = "check" 
            else:
                if hand_strength >= 6:
                    decision = "raise"
                else:
                    decision = "check"
            

        return decision


    def decide_preflop_2(self, position, pot, call_amount):
        """
        This decision only occurs if another player has decided to raise preflop.
        Since its following a raise, there is no option to check

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

        #note: all strong hands decided to limp preflop here
        if position in ["UTG", "MP"]:
            if hand_strength >= 10:
                decision = "raise" if self.aggression_level >= roll else "call"
            elif hand_strength == 9:
                decision = "raise" if self.aggression_level - 20 >= roll else "call"
            elif hand_strength in [7, 8]:
                if pot_odds >= 4:
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
    
    def decide_postflop(self, pot, call_amt, player_strength):
        """
        Bot's postflop action.
        Inputs:
            - call amount: determines how much the player would need to call following a bet
            - previous better: determines the decision path of the bot's actions
            - pot: current size of the pot
            - player_strength: strength of the player's hand compared to all possible hands with the board
        Uses:
            - aggression_level: how loose/aggressive this bot plays
            - bluff_factor: how much the player decides to bluff with poor hands 
            - hand_strength: derived from private hand and board
        """

        #pot odds can be used when deciding to call or not 
        pot_odds = pot / call_amt if call_amt > 0 else float('inf')
        #the options are to bet or check
        if player_strength <= 50: #super strong hand
            decision = "bet" if self.aggression_level + 20 >= random.randint(1, 100) else "check"
        elif player_strength <= 200:
            decision = "bet" if self.aggression_level + 10 >= random.randint(1, 100) else "check"
        elif player_strength <= 350:
            decision = "bet" if self.aggression_level >= random.randint(1, 100) else "check"
        elif player_strength  <= 500:
            decision = "bet" if self.aggression_level - 30 >= random.randint(1, 100) else "check"
        else: #complete bluffs bad hands 
            if self.bluffing_factor >= random.randint(1, 100):
                decision = "bet"
            else:
                decision = "check"

            
        

        
        return decision
    
    def decide_postflop_2(self, pot, call_amt, player_strength, raise_or_bet):
        """
        Bots second postflop action in response to a raise in the postflop decisions
        Inputs:
            pot - the current size of the pot
            call_amt - How many chips it requires for a bot to call the raise 
            player_strength - How strong is the players hand in relation to the board
        Returns:
            decision - The bots choice to either call, raise,  or fold based on the 
            inputs and the bots aggression level.
        """
        #setting pot odds
        pot_odds = pot / call_amt

        #this means the bot is responding a raise after the inital bet
        if raise_or_bet == "raise":

            if pot_odds >= 5: #easy to call getting 6:1 odds or better
                if player_strength <= 20:
                    decision = "raise" if self.aggression_level +10 >= random.randint(1, 100) else "call"
                elif player_strength <= 250 and player_strength >= 10:
                    decision = "call"
                elif player_strength <=400 and player_strength >= 250:
                    decision = "call" if self.aggression_level > random.randint(1, 100) else "fold"
                else:
                    roll = random.randint(1, 100)
                    if self.bluffing_factor >= roll:
                        decision = "raise" #opportunity for aggressive players to completely bluff
                    else:
                        decision = "fold"
                    
            
            else: #the raise starts to look very strong and bots should be cautious - most likely a large overbet don't bluff into it
                if player_strength <= 20: 
                    decision = "call"
                else:
                    decision = "fold"

        else: #this means the bot is making a resonse to the intial c-bet

            if pot_odds >= 3: #great odds any equity can justify calling
                if player_strength <= 150:
                    decision = "raise" if self.aggression_level >= random.randint(1, 100) else "call"
                elif player_strength <= 500 and player_strength >= 150:
                    decision = "call" if self.aggression_level + 25 > random.randint(1, 100) else "fold"
                else:
                    decision = "raise" if self.bluffing_factor > random.randint(1, 100) else "fold"
            

            else: #poor pot odds only strong hands contine
                if player_strength <= 20: #top hands likely raise
                    decision = "raise" if self.aggression_level >= random.randint(1, 100) else "call"
                elif player_strength <= 200 and player_strength >= 20:
                    decision = "call" if self.aggression_level + 40 >= random.randint(1, 100) else "fold"
                elif player_strength >= 200 and player_strength <= 400:
                    decision = "call" if self.aggression_level + 20 >= random.randint(1, 100) else "fold"
                else: #almost always folds except most aggressive players
                    decision = "raise" if self.bluffing_factor > random.randint(1, 100) else "fold"
        
        return decision



                
            