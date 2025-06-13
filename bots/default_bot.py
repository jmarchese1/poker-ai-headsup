#create default bot
import random

class PokerBot:
    def __init__(self, name):
        self.name = name
        self.chips = 1000
        self.contribution = 0 # tracks how many chips the players have added to the pot 
        self.hand = [] #create a function to pass two cards into this list


    def decide_preflop(self, position, history, pot, call_amount):
        """
        This function is the bots preflop decision if nobody has preflop raised yet. It considers it's position, potsize, and 
        the numbers of limpers when making a decision.
        params:
        position - the bots position at the table
        history - the previous actions at this street (expects and list of preflop actions)
        pot - the total size of the pot 
        call_amount - the amount a bot needs to contribute to call 
        """
        pot_odds = pot / call_amount 



        #dont need to track indiviual player lines because if the players are at the same stage it means they committed the same amount of chips regardless