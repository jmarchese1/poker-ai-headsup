import random
import pandas as pd
import numpy as np

#-----------------------------------------------------------------#
#                       helper functions                          #
#-----------------------------------------------------------------#
def all_contributions_equal(positions, folded):
     """
     checks if all the players contributions at a street are equal. 
     parameters:
     positions: The dictionary of players positions and thier names
     folded: list of players that folded out of the hand 
     """
     contributions = [player.contribution for pos, player in positions.items() if pos not in folded]
     return len(set(contributions)) == 1 #checks if all the player contributions are the same or not 

#-----------------------------------------------------------------#
#                       Setting up the game                       #
#-----------------------------------------------------------------#

#create bots | Each one will have a different play-style
#atlas = bot(atlas, 1000, ... )
#blair = bot(blair, 1000, ... )
#cruz = bot(cruz, 1000, ... )
# ...

#replace these string players with 
players = ["Atlas", "Blair", "Cruz", "Drew", "Ember", "Flint", "Gio"] 


#this rotates the list of players clockwise
players = players[-1:] + players[:-1] 

#assigning each player to the correct position for the hand
positions = {
    "UTG": players[0],
    "MP": players[1],
    "HJ": players[2],
    "CO": players[3],
    "BTN": players[4],
    "SB": players[5],
    "BB": players[6]
}

#the board will stay the same until the end of the hand as cards get added on the flop, turn and, river
board = [] 
#the pot will grow until the hand is over and is given to the winner
pot = 0 

#assuming small blind and big blind are parameters, add the blinds to sb and bb contribution and to the pot, and remove them from the players stacks
small_blind = small_blind 
big_blind = big_blind # ^^

positions["SB"].contribution += small_blind 
positions["SB"].chips -= small_blind

positions["BB"].contribution += big_blind
positions["BB"].chips -= big_blind

pot += small_blind + big_blind

#Important variables:
preflop_information = [] #list of dictionaries
preflop_actions = [d["action"] for d in preflop_information] #create a list of just the actions from the dictionary
preflop_folded_positions = [] #track players that folded used throughout the full hand
raiser_position = None #track which player decied to raise most recently

#-----------------------------------------------------------------#
#                       First preflop decisions                   #
#-----------------------------------------------------------------#

for position, player in positions.items():
        
        #track the number of limpers into the pot 
        num_limpers = sum(1 for d in preflop_information if d["action"] == "call")

        #get an action choice from the bots
        action = player.decide_preflop( #need to create this function in the future that should play differently based on hand position and history
            hand= player.hand, 
            position = position, 
            history= preflop_actions, 
            num_limpers = num_limpers,
            pot=pot
            )
        
        #adjust pot, chips, contributions and raise amounts based on decisions
        if action == "fold":
            preflop_folded_positions.append(position) # add player to list of folded players
            #determine if a player won preflop by the other six players folding
            if len(preflop_folded_positions) == len(positions) - 1:
                for position in list(positions.keys()):
                    if position not in preflop_folded_positions:
                        winner = positions[position]
                        winner.chips += pot
                        break
        elif action == "call":
            call_amount = big_blind - player.contribution #this line works for each position including blinds
            #updating pot, stack sizes, and player contributions from thier call amounts
            pot += call_amount 
            player.chips -= call_amount 
            player.contribution += call_amount 
        elif action == "raise":
            #randomly raises 2 or 3 big blinds plus an additional big blind for each limper
            raise_amount = ((random.choice([2, 3]) * big_blind) + (num_limpers * big_blind))
            pot += raise_amount
            player.chips -= raise_amount
            raiser_position = position #this variable helps reset the order of action post raise
            player.contribution += raise_amount
            #adding the raisers info to the dictionary
            preflop_information.append({"action" : action,
                                      "player" : player.name,
                                      "position" : position})
            break #breaking the loop and proceeding to stage 2 preflop action
        else:
             print("One of the players did not choose a valid action.") #simplify debugging
        
        if action != "raise":
        #adding fold and call player information to the dictionary
            preflop_information.append({"action" : action,
                                "player" : player.name,
                                "position" : position})

#-----------------------------------------------------------------#
#                  Additional preflop decisions                   #
#-----------------------------------------------------------------#

# creating a list to store preflop information for the second stage of betting 
preflop_information_2 = [] 
game_on = True
while not all_contributions_equal(positions=positions, folded = preflop_folded_positions):
    order = list(positions.keys()) #turns the current order above into a list from the first preflop decision 
    raiser_index = order.index(raiser_position) #get the index of the previous raiser
    new_order = order[raiser_index + 1:] + order[0:raiser_index + 1] #start action from the player after the previous raiser
    new_order = [pos for pos in new_order if pos not in preflop_folded_positions] #removing players that folded their cards from the action
    preflop_actions_2 = [d["action"] for d in preflop_information_2] #list of just the actions that occured this round
    cold_callers = [] #track the number of cold callers each round for raise sizings

    for position in new_order:

        action = positions[position].decide_preflop_2( #bot makes a decision on whether to call, fold, or raise
                hand = positions[position].hand,
                position = position,
                history = preflop_actions_2
                )
        #updating pot, chip stacks, player contributions, folded players
        if action == "fold":
            preflop_folded_positions.append(position) #adding players to be removed from the hand
            #determining if a player one the hand by folds
            if len(preflop_folded_positions) == len(positions) - 1:
                for position in list(positions.keys()):
                    if position not in preflop_folded_positions:
                        winner = positions[position]
                        winner.chips += pot
                        break

        elif action == "call":
            #this works for the blinds too because their contributions of the blinds are already accounted for 
            call_amount = positions[raiser_position].contribution - positions[position].contribution #players must call the difference between the raisers contribution and their contribution
            #updating variables
            pot += call_amount
            positions[position].chips -= call_amount
            positions[position].contribution += call_amount
            cold_callers.append(positions[position])

        elif action == "raise":
            #get the number of limpers into the pot
            raise_amount = ((3 * positions[raiser_position].contribution) + (len(cold_callers) * big_blind))
            pot += raise_amount
            positions[position].chips -= raise_amount
            raiser_position = position
            positions[position].contribution += raise_amount
            #adding the raisers information to the dictionary
            preflop_information_2.append({"action" : action,
                                      "player" : positions[position].name,
                                      "position" : position})
            break
        else:
             print("One of the players did not choose a valid action.")
        
        if action != "raise":
        #adding the folds and calls to the dictionary
            preflop_information_2.append({"action" : action,
                                "player" : positions[position].name,
                                "position" : position})
    


        
        

