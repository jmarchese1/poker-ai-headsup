# This script is designed to run a poker game between two bots, Bot A and Bot B. Automating hands without printing steps in the console.

#check working directory and sys.path to ensure the modules can be imported correctly
import os, sys

print("cwd: ", os.getcwd())

for p in sys.path:
    print("sys.path:", p)

root = r"\Users\jason\projects\poker_project\poker-ai-headsup"

if root not in sys.path:
    sys.path.insert(0, root)

#loading in all the modules and functions needed for data collection and gameflow
from engine.engine_helpers import preflop_hand_strength, deal_cards, evaluate_hand, determine_winner, clear_hand, clear_board, create_deck, flop, turn, river, get_hand_strength_at_street, best_hand
from bots.bot_A import PokerBot_A
from bots.bot_B import PokerBot_B
import pandas as pd
import random


#creation of bots to participate in the game, #agression and bluffing are good parameters to eventually introduce
bot_A = PokerBot_A(name = "Bot A", stack_size = 100000, small_blind = 1, big_blind = 2)
bot_B = PokerBot_B(name = "Bot B", stack_size = 100000, small_blind = 1, big_blind = 2)

#creation of results tracking dataframe -- data collection for machine learning 

#for modeling its likely that the bot in training will not know the hand of the opponent, so we will not include it in the final dataframe

#column names to add to the dataframe below
columns = [
    #Universal hand variables
    "hand_id",
    "winnings",
    "winner",
    "flop_cards", #the 3 cards that are dealt on the flop
    "turn_card", #the card that is dealt on the turn
    "river_card", #the card that is dealt on the river
    "postflop_potsize", #the pot size after the flop
    "postturn_potsize", #the pot size after the turn
    
    #river_potsize would be the same as winnings because the hand is over after the river


    #######################
    #bot A hand information
    "Bot_A_hand", #bot_A always plays the small blind
    "Bot_A_chips", #bot_A chips at the start of the hand
    #preflop variables
    "preflop_Bot_A_hand_strength",
    "preflop_Bot_A_decision",
    "preflop_Bot_A_raise_amount",
    "preflop_Bot_A_decision_2",
    "preflop_Bot_A_raise_amount_2", #if bot_A re-raises bot-B preflop
    #postflop variables
    "postflop_Bot_A_hand_strength",
    "postflop_Bot_A_decision",
    "postflop_Bot_A_bet",
    "postflop_Bot_A_decision_2", 
    "postflop_Bot_A_raise_amount", #would apply to decision_2 because bot_A can only raise once postflop
    #turn variables
    "turn_Bot_A_hand_strength",
    "turn_Bot_A_decision",
    "turn_Bot_A_bet",
    "turn_Bot_A_decision_2",
    "turn_Bot_A_raise_amount", #would apply to decision_2 because bot_A can only raise once on the turn
    #river variables
    "river_Bot_A_hand_strength",
    "river_Bot_A_decision",
    "river_Bot_A_bet",
    "river_Bot_A_decision_2",
    "river_Bot_A_raise_amount", #would apply to decision_2 because bot_A can only raise once on the river

    ######################
    #bot B hand information
    "Bot_B_hand", #bot_B always plays the big blind
    "Bot_B_chips", #bot_B chips at the start of the hand
    #preflop variables
    "preflop_Bot_B_hand_strength",
    "preflop_Bot_B_decision",
    "preflop_Bot_B_raise_amount", #this is the only numerical action bot_B can take preflop
    "preflop_Bot_B_decision_2", #if bot_B re-raises bot_A preflop (either call or fold)
    #postflop variables
    "postflop_Bot_B_hand_strength",
    "postflop_Bot_B_decision",
    "postflop_Bot_B_bet", #if bot_A checks bot_B decision_1 will be to bet or check
    "postflop_Bot_B_raise_amount", #if bot_A bets then bot_B will either have the option to call or raise for decision_1
    "postflop_Bot_B_decision_2", #if bot_A raises or re-raises then bot_B can either call or fold or re-raise
    "postflop_Bot_B_re_raise_amount", #if bot_B re-raises bot_A postflop for the second decision
    #turn variables
    "turn_Bot_B_hand_strength",
    "turn_Bot_B_decision",
    "turn_Bot_B_bet", #if bot_A checks bot_B decision_1 will be to bet or check
    "turn_Bot_B_raise_amount", #if bot_A bets then bot_B will either have the option to call or raise for decision_1
    "turn_Bot_B_decision_2", #if bot_A raises or re-raises then bot_B can either call or fold or re-raise
    "turn_Bot_B_re_raise_amount", #if bot_B re-raises bot_A postflop for the second decision
    #river variables
    "river_Bot_B_hand_strength",
    "river_Bot_B_decision",
    "river_Bot_B_bet", #if bot_A checks bot_B decision_1 will be to bet or check
    "river_Bot_B_raise_amount", #if bot_A bets then bot_B will either have the option to call or raise for decision_1
    "river_Bot_B_decision_2", #if bot_A raises or re-raises then bot_B can either call or fold or re-raise
    "river_Bot_B_re_raise_amount", #if bot_B re-raises bot_A postflop for the second decision
]

# Create the DataFrame with these columns
game_results_df = pd.DataFrame(columns=columns)

#this function includes everything that can happen preflop
def gameflow(player_1 = bot_A, player_2 = bot_B):
  """
  this function runs the preflop gameflow
  """

  global board
  board = []

  #for determining the winner need to loop through both players
  players = [player_1, player_2]

  #creating, shuffling, and dealing the cards to the players
  pot = 0
  cards = create_deck()
  deal_cards(cards, player_1 = bot_A, player_2 = bot_B)

  #setting row index for data logging
  row_idx = len(game_results_df)

  #setting a global small and big blind -- also have these variables in the player class but for now they are just used in the gameflow function
  big_blind = 2
  small_blind = 1

  #automatically subtracting the blind amounts from the players stacks -- logically removing the chips from the players stacks
  player_1.chips -= small_blind
  player_2.chips -= big_blind

  #adding the blind amount to the pot winnnings -- the same as the chips being removed from the players stacks
  pot += small_blind + big_blind

  #no need to print the players hands because they hands will be simulated by the bots

  #adding inital characteristics to the dataframe for the hand -- setting up the default values for the dataframe
  game_results_df.loc[row_idx] = {

    #Universal hand variables
    "hand_id" : row_idx, #the id of the hand, this will be used to track the hand in the dataframe
    "winnings" : None,
    "winner" : None,
    "flop_cards" : None, #the 3 cards that are dealt on the flop
    "turn_card" : None, #the card that is dealt on the turn
    "river_card" : None, #the card that is dealt on the river
    "postflop_potsize" : None, #the pot size after the flop
    "postturn_potsize" : None, #the pot size after the turn
    
    #river_potsize would be the same as winnings because the hand is over after the river

    #bot A hand information
    "Bot_A_hand" : player_1.hand, #bot_A always plays the small blind
    "Bot_A_chips" : player_1.chips, #bot_A chips at the start of the hand
    #preflop variables
    "preflop_Bot_A_hand_strength" : None,
    "preflop_Bot_A_decision" : None,
    "preflop_Bot_A_raise_amount" : None,
    "preflop_Bot_A_decision_2" : None,
    "preflop_Bot_A_raise_amount_2" : None, #if bot_A re-raises bot-B preflop
    #postflop variables
    "postflop_Bot_A_hand_strength" : None,
    "postflop_Bot_A_decision" : None,
    "postflop_Bot_A_bet" : None,
    "postflop_Bot_A_decision_2" : None, 
    "postflop_Bot_A_raise_amount" : None, #would apply to decision_2 because bot_A can only raise once postflop
    #turn variables
    "turn_Bot_A_hand_strength" : None,
    "turn_Bot_A_decision" : None,
    "turn_Bot_A_bet" : None,
    "turn_Bot_A_decision_2" : None,
    "turn_Bot_A_raise_amount" : None, #would apply to decision_2 because bot_A can only raise once on the turn
    #river variables
    "river_Bot_A_hand_strength" : None,
    "river_Bot_A_decision" : None,
    "river_Bot_A_bet" : None,
    "river_Bot_A_decision_2" : None,
    "river_Bot_A_raise_amount" : None, #would apply to decision_2 because bot_A can only raise once on the river

    ######################
    #bot B hand information
    "Bot_B_hand" : player_2.hand, #bot_B always plays the big blind
    "Bot_B_chips" : player_2.chips, #bot_B chips at the start of the hand
    #preflop variables
    "preflop_Bot_B_hand_strength" : None,
    "preflop_Bot_B_decision" : None,
    "preflop_Bot_B_raise_amount" : None, #this is the only numerical action bot_B can take preflop
    "preflop_Bot_B_decision_2" : None, #if bot_B re-raises bot_A preflop (either call or fold)
    #postflop variables
    "postflop_Bot_B_hand_strength" : None,
    "postflop_Bot_B_decision" : None,
    "postflop_Bot_B_bet" : None, #if bot_A checks bot_B decision_1 will be to bet or check
    "postflop_Bot_B_raise_amount" : None, #if bot_A bets then bot_B will either have the option to call or raise for decision_1
    "postflop_Bot_B_decision_2" : None, #if bot_A raises or re-raises then bot_B can either call or fold or re-raise
    "postflop_Bot_B_re_raise_amount" : None, #if bot_B re-raises bot_A postflop for the second decision
    #turn variables
    "turn_Bot_B_hand_strength" : None,
    "turn_Bot_B_decision" : None,
    "turn_Bot_B_bet" : None, #if bot_A checks bot_B decision_1 will be to bet or check
    "turn_Bot_B_raise_amount" : None, #if bot_A bets then bot_B will either have the option to call or raise for decision_1
    "turn_Bot_B_decision_2" : None, #if bot_A raises or re-raises then bot_B can either call or fold or re-raise
    "turn_Bot_B_re_raise_amount" : None, #if bot_B re-raises bot_A postflop for the second decision
    #river variables
    "river_Bot_B_hand_strength" : None,
    "river_Bot_B_decision" : None,
    "river_Bot_B_bet" : None, #if bot_A checks bot_B decision_1 will be to bet or check
    "river_Bot_B_raise_amount" : None, #if bot_A bets then bot_B will either have the option to call or raise for decision_1
    "river_Bot_B_decision_2" : None, #if bot_A raises or re-raises then bot_B can either call or fold or re-raise
    "river_Bot_B_re_raise_amount" : None, #if bot_B re-raises bot_A postflop for the second decision
}

  #no need to print what player is to act because the bots will simulate the actions 
  #however, using time.sleep() to simulate the time it would take a human to make a decision would look better in the console

  #variable to determine if the hand is over yet or to continue to the next segment -- this variable will be set to True if the hand is over
  #this variable is needed to prevent the game from continuing after the hand is over
  round_over = False

#-------------------------------------------------------------------------------------------------------------------#
#####################################################################################################################
#                      PRE FLOP DECISION MAKING                                                                    #
#####################################################################################################################
#-------------------------------------------------------------------------------------------------------------------#


  #bot_A (player_1) is the small blind and acts first preflop -- the function returns the string decision at [0] and the preflop hand strength at [1]
  Bot_A_preflop_decision, Bot_A_preflop_strength = bot_A.get_preflop_decision()[0], bot_A.get_preflop_decision()[1]

  #adding the bot_A preflop decision and hand strength to the dataframe
  game_results_df.at[row_idx, "preflop_Bot_A_decision"] = Bot_A_preflop_decision
  game_results_df.at[row_idx, "preflop_Bot_A_hand_strength"] = Bot_A_preflop_strength

  if Bot_A_preflop_decision == "fold":
    player_2.chips += pot #bot B wins the pot of the blinds
    pot = 0 #pot is reset to 0 for the next hand
    clear_hand() #hands of the players are cleared for the next 
    
    #adding the results of the hand to the data frame
    game_results_df.at[row_idx, "winnings"] = pot
    game_results_df.at[row_idx, "winner"] = player_2.name
    round_over = True #ensures the game does not continue further
    clear_board(board)

  elif Bot_A_preflop_decision == "call":
    player_1.chips -= small_blind #Bot A enters another small blind to equal the big blind
    pot += small_blind #adding the additional small blind to the pot

    #adding the bot_B preflop hand strength to the dataframe
    Bot_B_preflop_strength = bot_B.get_preflop_decision(opponent_preflop_decision = Bot_A_preflop_decision)[1] #oassing bot A's preflop action to help bot B come to its decision
    game_results_df.at[row_idx, "preflop_Bot_B_hand_strength"] = Bot_B_preflop_strength

    #now the computer gets to check or raise in reponse to the users decison to call and adds it to the dataframe
    Bot_B_decision =  bot_B.get_preflop_decision(opponent_preflop_decision = Bot_A_preflop_decision)[0]
    game_results_df.at[row_idx, "preflop_Bot_B_decision"] = Bot_B_decision

    if Bot_B_decision == "check": #this would bring on the flop (first three cards)
      flop(cards = cards)
      game_results_df.at[row_idx, "flop_cards"] = board #adds the flop cards to the dataframe
      game_results_df.at[row_idx, "postflop_potsize"] = pot #adds the current potsize as the postflop potsize (the size of the pot while decisions on the flop are being made)
    
    else: #the only other option for bot B is to raise on its first decision after a call from bot A
      Bot_B_raise_amount = bot_B.get_preflop_raise_amount()
      game_results_df.at[row_idx, "preflop_Bot_B_raise_amount"] = Bot_B_raise_amount
      player_2.chips -= Bot_B_raise_amount #the raise amount is subtracted from the bots stack
      pot += Bot_B_raise_amount #the raise amount is added to the pot

      #now the Bot A gets to respond to the raise with either a fold, call, or re-raise
      Bot_A_decision_2 = bot_A.get_preflop_decision_2() #this function was created knowing it would follow a raise so no parameters needed.
      game_results_df.at[row_idx, "preflop_Bot_A_decision_2"] = Bot_A_decision_2
      if Bot_A_decision_2 == "fold":
        player_2.chips += pot #bot B wins the bot
        clear_hand()
        game_results_df.at[row_idx, "winnings"] = pot
        game_results_df.at[row_idx, "winner"] = player_2.name
        round_over = True
        clear_board(board)
        pot = 0
      elif Bot_A_decision_2 == "call":
        player_1.chips -= Bot_B_raise_amount #Bot A puts in the additional chips that bot B raised by
        pot += Bot_B_raise_amount #the pot grows by the call amount from bot A 
        flop(cards = cards) #this sequence of actions makes the flop come
        game_results_df.at[row_idx, "flop_cards"] = board #adds the flop cards to the dataframe
        game_results_df.at[row_idx, "postflop_potsize"] = pot
      else: #bot A decides to re-raise Bot_B's raise -- currently programmed not to re-raise here ever
        Bot_A_re_raise_amount = bot_A.get_re_raise_amount(Bot_B_decision, )
        game_results_df.at[row_idx, "preflop_user_raise_amount_2"] = Bot_A_re_raise_amount
        pot += Bot_A_re_raise_amount
        player_1.chips -= Bot_A_re_raise_amount

        #the computer now has the opportunity to respond to the re-raise with either a call or a fold
        Bot_B_decision_2 = random.choice(["call", "fold"]) #REPLACE WITH FUNCTION FOR THIS DECISION CURRENTLY NOT MADE
        game_results_df.at[row_idx, "preflop_Bot_B_decision_2"] = Bot_B_decision_2
        if Bot_B_decision_2 == "call":
          player_2.chips -= (Bot_A_re_raise_amount - Bot_B_raise_amount) #calls the difference of Bot B's raise and the opponents re-raise
          pot += (Bot_A_re_raise_amount - Bot_B_raise_amount)
          flop(cards = cards)
          game_results_df.at[row_idx, "flop_cards"] = board #adds the flop cards to the dataframe
          game_results_df.at[row_idx, "postflop_potsize"] = pot
        else: #the other option is to fold which means bot_A wins the hand
          player_1.chips += pot
          clear_hand()
          game_results_df.at[row_idx, "winnings"] = pot
          game_results_df.at[row_idx, "winner"] = player_1.name
          round_over = True
          clear_board(board)
          pot = 0

  #if bot_A decision is raise pre-flop as the first decision
  else:
    Bot_A_raise_amount = bot_A.get_preflop_raise_amount()
    game_results_df.at[row_idx, "preflop_Bot_A_raise_amount"] = Bot_A_raise_amount
    pot += Bot_A_raise_amount
    player_1.chips -= Bot_A_raise_amount

    #now bot b has the opportunity to respond to the raise
    Bot_B_decision = bot_B.get_preflop_decision(opponent_preflop_decision = Bot_A_preflop_decision)
    game_results_df.at[row_idx, "preflop_Bot_B_decision"] = Bot_B_decision

    #what happens based on the bot B's decision to respond to the raise
    if Bot_B_decision == "fold":
      player_1.chips += pot #bot A wins the pots
      clear_hand()
      game_results_df.at[row_idx, "winnings"] = pot
      game_results_df.at[row_idx, "winner"] = player_1.name
      round_over = True
      clear_board(board)
      pot = 0
    elif Bot_B_decision == "call":
      player_2.chips -= (Bot_A_raise_amount - big_blind)
      pot += (Bot_A_raise_amount - big_blind)
      flop(cards = cards) #this sequence causes the flop to be displayed
      game_results_df.at[row_idx, "flop_cards"] = board
      game_results_df.at[row_idx, "postflop_potsize"] = pot
    else:
      #Bot B decides to re-raise Bot-A's raise
      Bot_B_raise_amount = bot_B.get_re_raise_amount() #need to pass hand ranking -- no function built for preflop re-raise
      game_results_df.at[row_idx, "preflop_Bot_B_raise_amount"] = Bot_B_raise_amount
      player_2.chips -= Bot_B_raise_amount

      #after the computer raises the re-raises the user can either call or fold

      Bot_A_decision_2 = bot_A.get_preflop_decision_2() #this returns a decision to either call or fold to a computer raise or bet
      game_results_df.at[row_idx, "preflop_Bot_A_decision_2"] = Bot_A_decision_2
      
      #what happens if bot_A decides to fold in reponse to bot B's preflop raise
      if Bot_A_decision_2 == "fold":
        player_2.chips += pot
        clear_hand()
        game_results_df.at[row_idx, "winnings"] = pot
        game_results_df.at[row_idx, "winner"] = player_2.name
        round_over = True
        clear_board(board)
        pot = 0
      #if bot_A calls bot B raise 
      else:
        player_1.chips -= (Bot_B_raise_amount - Bot_A_raise_amount) #bot A needs to add the additional chips following the re-raise
        pot += (Bot_B_raise_amount - Bot_A_raise_amount)
        flop(cards = cards) #here comes the flop
        game_results_df.at[row_idx, "flop_cards"] = board
        game_results_df.at[row_idx, "postflop_potsize"] = pot

#-------------------------------------------------------------------------------------------------------------------#
#####################################################################################################################
#                      POST FLOP DECISION MAKING                                                                    #
#####################################################################################################################
#-------------------------------------------------------------------------------------------------------------------#

  if round_over == False: #this section runs if the game continues past the preflop decisions

    #now we start gathering the hand ranking of the players at each street to guide decision making
    Bot_A_postflop_decision = bot_A.get_post_flop_decision(board = board)[0]
    game_results_df.at[row_idx, "postflop_Bot_A_decision"] = Bot_A_postflop_decision
    Bot_A_postflop_hand_ranking = bot_A.get_post_flop_decision(board = board)[1]
    game_results_df.at[row_idx, "postflop_Bot_A_hand_strength"] = Bot_A_postflop_hand_ranking

    #bot A's postflop decision is purely based on what the board displays (doesn't consider whether opponent raised or checked preflop)
    if Bot_A_postflop_decision == "check":
      #now Bot_B gets the decision to check or bet
      Bot_B_postflop_decision = bot_B.get_postflop_decision(board = board, opponent_postflop_decision = Bot_A_postflop_decision)[0]
      game_results_df.at[row_idx, "postflop_Bot_B_decision"] = Bot_B_postflop_decision

      Bot_B_postflop_hand_ranking = bot_B.get_postflop_decision(board = board, opponent_postflop_decsion = Bot_A_postflop_decision)[1]

      if Bot_B_postflop_decision == "check": #this means the flop went check-check
        turn(cards = cards) #prints to the user the 3 cards for the flop + the turn
        game_results_df.at[row_idx, "turn_card"] = board[3] #adds the turn card to the dataframe
        game_results_df.at[row_idx, "postturn_potsize"] = pot

      #bot_B has decided to bet 
      else:
        Bot_B_bet_amount = bot_B.get_post_flop_bet_amount(hand_ranking = Bot_B_postflop_hand_ranking)
        game_results_df.at[row_idx, "postflop_Bot_B_bet"] = Bot_B_bet_amount

        #adding the bet amount to the pot and subtracting it from bot b's stack
        player_2.chips -= Bot_B_bet_amount
        pot += Bot_B_bet_amount

        #now bot_A gets to respond with a call, fold, or raise
        Bot_A_decision_2 = bot_A.get_post_flop_decision_2(board= board)[0]
        game_results_df.at[row_idx, "postflop_Bot_A_decision_2"] = Bot_A_decision_2

        if Bot_A_decision_2 == "fold":
          player_2.chips += pot #bot b wins the pot
          clear_hand()
          game_results_df.at[row_idx, "winnings"] = pot
          game_results_df.at[row_idx, "winner"] = player_2.name
          round_over = True
          clear_board(board)
          pot = 0

        elif Bot_A_decision_2 == "call":
          player_1.chips -= Bot_B_bet_amount #bot_A mirrors the action of bot B
          pot += Bot_B_bet_amount
          turn(cards = cards) #here comes the turn
          game_results_df.at[row_idx, "turn_card"] = board[3] #adds the flop cards to the dataframe
          game_results_df.at[row_idx, "postturn_potsize"] = pot

        #Bot_A decision is raise in response to a bet from bot_B.. This is a check-raise from bot_A on the flop
        else:
          Bot_A_raise_amount = bot_A.get_re_raise_amount(opponent_bet_amount = Bot_B_bet_amount ,hand_ranking = Bot_A_postflop_hand_ranking)
          game_results_df.at[row_idx, "postflop_Bot_A_raise_amount"] = Bot_A_raise_amount
          pot += Bot_A_raise_amount
          player_1.chips -= Bot_A_raise_amount

          #now Bot B needs to respond to Bot A's raise
          Bot_B_decision_2 = bot_B.get_post_flop_decision_2(board = board)[0]
          game_results_df.at[row_idx, "postflop_Bot_B_decision_2"] = Bot_B_decision_2

          if Bot_B_decision_2 == "fold":
            player_1.chips += pot #bot_A wins the pot
            clear_hand()
            game_results_df.at[row_idx, "winnings"] = pot
            game_results_df.at[row_idx, "winner"] = player_1.name
            round_over = True
            clear_board(board)
            pot = 0
          elif com_decision == "call":
            player_2.chips -= (Bot_A_raise_amount - Bot_B_bet_amount) #has to call the amount raised by 
            pot += (Bot_A_raise_amount - Bot_B_bet_amount)
            turn(cards = cards) #prints to the user the 3 cards for the flop + the turn
            game_results_df.at[row_idx, "turn_card"] = board[3] #adds the flop cards to the dataframe
            game_results_df.at[row_idx, "postturn_potsize"] = pot

          #if the bot_B decides to re_raise the bot_A raise 
          else:
            Bot_B_re_raise_amount = bot_B.get_re_raise_amount(opponent_bet_amount = Bot_A_raise_amount, hand_ranking = Bot_B_postflop_hand_ranking)
            game_results_df.at[row_idx, "postflop_Bot_B_re_raise_amount"] = Bot_B_re_raise_amount
            player_2.chips -= Bot_B_re_raise_amount

            #now Bot_A can make a decision in response to the re-raise to either call or fold -- this would be the bots 3rd decision at the street
            Bot_A_decision_3 = bot_A.get_post_flop_decision_2(board = board) #currently this function does not include the abiltiy to re-raise
            game_results_df.at[row_idx, "postflop_Bot_A_decision_3"] = Bot_A_decision_3

            if Bot_A_decision_3 == "fold":
              player_2.chips += pot #bot_B wins the pot
              clear_hand()
              game_results_df.at[row_idx, "winnings"] = pot
              game_results_df.at[row_idx, "winner"] = player_2.name
              round_over = True
              clear_board(board)
              pot = 0

            #Bot_A calls the re-raise
            else:
              player_1.chips -= (Bot_B_re_raise_amount - Bot_A_raise_amount)
              pot += (Bot_B_re_raise_amount - Bot_A_raise_amount)
              turn(cards = cards) #prints to the user the 3 cards for the flop + the turn
              game_results_df.at[row_idx, "turn_card"] = board[3] #adds the flop cards to the dataframe
              game_results_df.at[row_idx, "postturn_potsize"] = pot

    #users leads with a bet when the flop appears
    else:
      bot_A_bet_amount = bot_A.get_post_flop_bet_amount(pot = pot, hand_ranking = Bot_A_postflop_hand_ranking)
      game_results_df.at[row_idx, "postflop_Bot_A_bet"] = bot_A_bet_amount
      pot += bot_A_bet_amount
      player_1.chips -= bot_A_bet_amount

      #now bot_B has to respond to the users bet amount
      Bot_B_postflop_decision = bot_B.get_post_flop_decision(board = board, opponent_post_flop_decision = Bot_A_postflop_decision)[0]
      game_results_df.at[row_idx, "postflop_Bot_B_decision"] = Bot_B_postflop_decision

      Bot_B_postflop_hand_ranking = bot_B.get_post_flop_decision(board = board, opponent_post_flop_decision = Bot_A_postflop_decision)[1]
      game_results_df.at[row_idx, "postflop_Bot_B_hand_strength"]

      if Bot_B_postflop_decision == "fold":
        player_1.chips += pot #Bot A wins the pot
        clear_hand()
        game_results_df.at[row_idx, "winnings"] = pot
        game_results_df.at[row_idx, "winner"] = player_1.name
        round_over = True
        clear_board(board)
        pot = 0

      elif Bot_B_postflop_decision == "call":
        player_2.chips -= bot_A_bet_amount
        pot += bot_A_bet_amount
        turn(cards = cards) #prints to the user the 3 cards for the flop + the turn
        game_results_df.at[row_idx, "turn_card"] = board[3] #adds the flop cards to the dataframe
        game_results_df.at[row_idx, "postturn_potsize"] = pot

      #the computer decides to raise the bot_A's bet
      else:
        bot_B_raise_amount = bot_B.get_re_raise_amount(opponent_bet_amount = bot_A_bet_amount, hand_ranking = Bot_A_postflop_hand_ranking)
        game_results_df.at[row_idx, "postflop_Bot_B_raise_amount"] = bot_B_raise_amount
        player_2.chips -= bot_B_raise_amount

        #now Bot_A can make a decision in response to the raise
        Bot_A_decision_2 = bot_A.get_post_flop_decision_2(board = board)
        game_results_df.at[row_idx, "postflop_Bot_A_decision_2"] = Bot_A_decision_2

        if Bot_A_decision_2 == "fold":
          player_2.chips += pot #bot B wins the hand
          clear_hand()
          game_results_df.at[row_idx, "winnings"] = pot
          game_results_df.at[row_idx, "winner"] = player_2.name
          round_over = True
          clear_board(board)
          pot = 0

        #bot A calls bot B's raise
        else:
          player_1.chips -= (bot_B_raise_amount - bot_A_bet_amount)
          pot += (bot_B_raise_amount - bot_A_bet_amount)
          turn(cards = cards) #prints to the user the 3 cards for the flop + the turn
          game_results_df.at[row_idx, "turn_card"] = board[3] #adds the flop cards to the dataframe
          game_results_df.at[row_idx, "postturn_potsize"] = pot

#-------------------------------------------------------------------------------------------------------------------#
#####################################################################################################################
#                      POST TURN DECISION MAKING                                                                    #
#####################################################################################################################
#-------------------------------------------------------------------------------------------------------------------#

  if round_over == False: #if round over is still false the game continues to betting on the turn

    #now we start gathering the hand ranking of the players at each street to guide decision making
    Bot_A_turn_decision = bot_A.get_turn_decision(board = board, opponent_post_flop_decision = Bot_B_postflop_decision)[0]
    game_results_df.at[row_idx, "turn_Bot_A_decision"] = Bot_A_turn_decision
    Bot_A_turn_hand_ranking = bot_A.get_turn_decision(board = board, opponent_post_flop_decision = Bot_B_postflop_decision)[1]
    game_results_df.at[row_idx, "turn_Bot_A_hand_strength"] = Bot_A_turn_hand_ranking

    if Bot_A_turn_decision == "check":
      #now bot_B gets the decision to check or bet
      Bot_B_turn_decision = bot_B.get_turn_decision(opponent_post_flop_decision = Bot_A_postflop_decision)[0]
      game_results_df.at[row_idx, "turn_Bot_B_decision"] = Bot_B_turn_decision

      Bot_B_turn_hand_strength = bot_B.get_turn_decision(opponent_post_flop_decision = Bot_A_postflop_decision)[1]
      game_results_df.at[row_idx, "turn_Bot_B_hand_strength"] = Bot_B_turn_hand_strength

      #this is where bot B is responding to a check from bot A
      if Bot_B_turn_decision == "check":
        river(cards = cards) #prints to the user the 3 cards for the flop + the turn
        game_results_df.at[row_idx, "river_card"] = board[4] #adds the flop cards to the dataframe
        game_results_df.at[row_idx, "postriver_potsize"] = pot

      #Bot B chooses to bet -- this means that bot_A can either respond with a fold, call, or raise
      else:
        Bot_B_turn_bet_amount = bot_B.get_post_turn_bet_amount(pot = pot, hand_ranking = Bot_B_turn_hand_strength)
        game_results_df.at[row_idx, "turn_Bot_B_bet"] = Bot_B_turn_bet_amount
        player_2.chips -= Bot_B_turn_bet_amount

        #now Bot_A gets to respond with a call, fold, or raise to the bet from bot_B
        Bot_A_turn_decision_2 = bot_A.get_post_turn_decision_2(board = board)[0]
        game_results_df.at[row_idx, "turn_Bot_A_decision_2"] = Bot_A_turn_decision_2

        if Bot_A_turn_decision_2 == "fold":
          player_2.chips += pot #bot b wins the pot
          clear_hand()
          game_results_df.at[row_idx, "winnings"] = pot
          game_results_df.at[row_idx, "winner"] = player_2.name
          round_over = True
          clear_board(board)
          pot = 0

        elif Bot_A_turn_decision_2 == "call":
          player_1.chips -= Bot_B_turn_bet_amount
          pot += Bot_B_turn_bet_amount
          river(cards = cards) #prints to the user the 3 cards for the flop + the turn
          game_results_df.at[row_idx, "river_card"] = board[4] #adds the flop cards to the dataframe
          game_results_df.at[row_idx, "postriver_potsize"] = pot

        #bot A decision is to raise in respond to the bet from bot B
        else:
          Bot_A_turn_raise_amount = bot_A.get_re_raise_amount(opponent_bet_amount = Bot_B_turn_bet_amount, hand_ranking = Bot_A_turn_hand_ranking)
          game_results_df.at[row_idx, "turn_Bot_A_raise_amount"] = Bot_A_turn_raise_amount
          pot += Bot_A_turn_raise_amount
          player_1.chips -= Bot_A_turn_raise_amount

          #now bot B gets to respond to bot A raising the bet 
          Bot_B_decision_2 = bot_B.get_post_turn_decision_2(board = board)
          game_results_df.at[row_idx, "turn_Bot_B_decision_2"] = Bot_B_decision_2

          if Bot_B_decision_2 == "fold":
            player_1.chips += pot
            clear_hand()
            game_results_df.at[row_idx, "winnings"] = pot
            game_results_df.at[row_idx, "winner"] = player_1.name
            round_over = True
            clear_board(board)
            pot = 0

          elif Bot_B_decision_2 == "call":
            player_2.chips -= (Bot_A_turn_raise_amount - Bot_B_turn_bet_amount)
            pot += (Bot_A_turn_raise_amount - Bot_B_turn_bet_amount)
            river(cards = cards) #prints to the user the 3 cards for the flop + the turn
            game_results_df.at[row_idx, "river_card"] = board[4] #adds the flop cards to the dataframe
            game_results_df.at[row_idx, "postriver_potsize"] = pot

          #if the com decides to re_raise
          else:
            Bot_B_turn_re_raise_amount = bot_B.get_re_raise_amount(opponent_bet_amount = Bot_A_raise_amount, hand_ranking = Bot_B_turn_hand_strength)
            game_results_df.at[row_idx, "turn_Bot_B_re_raise_amount"] = Bot_B_turn_re_raise_amount
            player_2.chips -= Bot_B_turn_re_raise_amount

            #now Bot A can make a response to the re-raise
            bot_A_turn_decision_3 = bot_A.get_post_turn_decision_2(board = board) #need to create a new function to handle this case
            game_results_df.at[row_idx, "turn_Bot_A_decision_3"] = bot_A_turn_decision_3

            if bot_A_turn_decision_3 == "fold": 
              player_2.chips += pot #bot b wins the pot
              clear_hand()
              game_results_df.at[row_idx, "winnings"] = pot
              game_results_df.at[row_idx, "winner"] = player_2.name
              round_over = True
              clear_board(board)
              pot = 0

            #bot a calls the re-raise from bot b
            else:
              player_1.chips -= (Bot_B_turn_re_raise_amount - Bot_A_turn_raise_amount)
              pot += (Bot_B_turn_re_raise_amount - Bot_A_turn_raise_amount)
              river(cards = cards) #prints to the user the 3 cards for the flop + the turn
              game_results_df.at[row_idx, "river_card"] = board[4] #adds the flop cards to the dataframe
              game_results_df.at[row_idx, "postriver_potsize"] = pot

    #bot A leads out on the turn with a bet
    else:
      bot_A_turn_bet_amount = bot_A.get_post_turn_bet_amount(pot = pot, hand_ranking = Bot_A_turn_hand_ranking)
      game_results_df.at[row_idx, "turn_user_bet"] = bot_A_turn_bet_amount
      pot += bot_A_turn_bet_amount
      player_1.chips -= bot_A_turn_bet_amount

      #now bot B has the opportunity to respond to bot A's bet amount
      Bot_B_turn_decision = bot_B.get_turn_decision(board = board, opponent_post_flop_decision = Bot_A_postflop_decision, opponent_turn_decision = Bot_A_turn_decision)[0]
      game_results_df.at[row_idx, "turn_Bot_B_decision"] = Bot_B_turn_decision

      Bot_B_turn_hand_strength = bot_B.get_turn_decision(board = board, opponent_post_flop_decision = Bot_A_postflop_decision, opponent_turn_decision = Bot_A_turn_decision)[1]
      game_results_df.at[row_idx, "turn_Bot_B_hand_strength"] = Bot_B_turn_hand_strength

      if Bot_B_turn_decision == "fold":
        player_1.chips += pot
        clear_hand()
        game_results_df.at[row_idx, "winnings"] = pot
        game_results_df.at[row_idx, "winner"] = player_1.name
        round_over = True
        clear_board(board)
        pot = 0

      elif Bot_B_turn_decision == "call":
        player_2.chips -= bot_A_turn_bet_amount
        pot += bot_A_turn_bet_amount
        river(cards = cards) #prints to the user the 3 cards for the flop + the turn
        game_results_df.at[row_idx, "river_card"] = board[4] #adds the flop cards to the dataframe
        game_results_df.at[row_idx, "postriver_potsize"] = pot

      #Bot B decides to raise Bot A's bet
      else:
        Bot_B_turn_raise_amount = bot_B.get_re_raise_amount(opponent_bet_amount = bot_A_turn_bet_amount, hand_ranking = Bot_B_turn_hand_strength)
        game_results_df.at[row_idx, "turn_Bot_B_raise_amount"] = Bot_B_turn_raise_amount
        player_2.chips -= Bot_B_turn_raise_amount
        pot += Bot_B_turn_raise_amount

        #now bot a can make a decision in response to a re-raise from bot B
        Bot_A_turn_decision_2 = bot_A.get_post_turn_decision_2(board = board)[0] #need to make sure this index is present in other locations
        game_results_df.at[row_idx, "turn_Bot_A_decision_2"] = Bot_A_turn_decision_2

        if Bot_A_turn_decision_2 == "fold":
          player_2.chips += pot
          clear_hand()
          game_results_df.at[row_idx, "winnings"] = pot
          game_results_df.at[row_idx, "winner"] = player_2.name
          round_over = True
          clear_board(board)
          pot = 0
        #Bot A calls bot B raise
        else:
          player_1.chips -= (Bot_B_turn_raise_amount - bot_A_turn_bet_amount)
          pot += (Bot_B_turn_raise_amount - bot_A_turn_bet_amount)
          river(cards = cards) #prints to the user the 3 cards for the flop + the turn
          game_results_df.at[row_idx, "river_card"] = board[4] #adds the flop cards to the dataframe
          game_results_df.at[row_idx, "postriver_potsize"] = pot


#-------------------------------------------------------------------------------------------------------------------#
#####################################################################################################################
#                      POST RIVER DECISION MAKING                                                                   #
#####################################################################################################################
#-------------------------------------------------------------------------------------------------------------------#

  if round_over == False: #if round over still = False the game will proceed to the river where the players will meet a showdown if no bots fold


    #bot A lead out decisions on the river and the strength of bot's hand on the river
    Bot_A_river_decision = bot_A.get_river_decision(board = board, opponent_post_flop_decision = Bot_B_postflop_decision, opponent_post_turn_decision = Bot_B_turn_decision)[0]
    game_results_df.at[row_idx, "river_Bot_A_decision"] = Bot_A_river_decision
    Bot_A_river_hand_ranking = bot_A.get_river_decision(board = board, opponent_post_flop_decision = Bot_B_postflop_decision, opponent_post_turn_decision = Bot_B_turn_decision)[1]
    game_results_df.at[row_idx, "river_Bot_A_hand_strength"] = Bot_A_river_hand_ranking


    if Bot_A_river_decision == "check":
      #if bot A's decision is to check the action is passed onto bot B to check or bet
      Bot_B_river_decision = bot_B.get_river_decision(board = board, opponent_post_flop_decision = Bot_A_postflop_decision, opponent_post_turn_decision = Bot_A_turn_decision, opponent_post_river_decision = Bot_A_river_decision)[0]
      game_results_df.at[row_idx, "river_Bot_B_decision"] = Bot_B_river_decision
      #adding bot b's river hand strength to the dataframe:
      Bot_B_river_hand_strength = bot_B.get_river_decision(board = board, opponent_post_flop_decision = Bot_A_postflop_decision, opponent_post_turn_decision = Bot_A_turn_decision, opponent_post_river_decision = Bot_A_river_decision)[1]
      game_results_df.at[row_idx, "river_Bot_B_hand_strength"]

      if Bot_B_river_decision == "check":
        #NEED TO UPDATE THIS FUNCTION IN ENGINE HELPERS | NOW SET TO USER AND COM
        determine_winner(players = players, board= board, pot = pot, row_idx = row_idx) #functionality built to determine which player has a stronger hand
        clear_board(board)

      #if bot_B chooses to bet here's how much they will bet and bot A's response
      else:
        Bot_B_river_bet_amount = bot_B.get_post_river_bet_amount(pot = pot, hand_ranking = Bot_B_river_hand_strength)
        game_results_df.at[row_idx, "river_Bot_B_bet"] = Bot_B_river_bet_amount
        player_2.chips -= Bot_B_river_bet_amount

        #now Bot_A gets to respond  to Bot_B bet with a call, fold, or raise
        Bot_A_river_decision_2 = bot_A.get_post_river_decision_2(board = board)
        game_results_df.at[row_idx, "river_Bot_A_decision_2"] = Bot_A_river_decision_2

        if Bot_A_river_decision_2 == "fold":
          player_2.chips += pot #bot b wins without a showdown
          clear_hand()
          game_results_df.at[row_idx, "winnings"] = pot
          game_results_df.at[row_idx, "winner"] = player_2.name
          clear_board(board)
          pot = 0
        elif Bot_A_river_decision_2 == "call":
          player_1.chips -= Bot_B_river_bet_amount
          pot += Bot_B_river_bet_amount

          #now the winner will be determined via showdown
          determine_winner(players = players, board= board, pot = pot, row_idx = row_idx)
          clear_board(board)
          clear_hand()

        #Bot a raises Bot B's bet on the river representing a huge hand or a bluff
        else:
          Bot_A_river_raise_amount = bot_A.get_re_raise_amount(opponenet_bet_amount = Bot_B_river_bet_amount, hand_ranking = Bot_A_river_hand_ranking)
          game_results_df.at[row_idx, "river_Bot_A_raise_amount"] = Bot_A_river_raise_amount
          pot += Bot_A_river_raise_amount
          player_1.chips -= Bot_A_river_raise_amount

          #now the Bot_B needs to respond to the users raise
          Bot_B_river_decision_2 = bot_B.get_post_river_decision_2(board = board) #inside the function bot b has no option to raise currently 
          game_results_df.at[row_idx, "river_Bot_B_decision_2"] = Bot_B_river_decision_2

          if Bot_B_river_decision_2 == "fold":
            player_1.chips += pot #bot a wins without a showdown
            clear_hand()
            game_results_df.at[row_idx, "winnings"] = pot
            game_results_df.at[row_idx, "winner"] = player_1.name
            clear_board(board)
            pot = 0
          elif Bot_B_river_decision_2 == "call":
            player_2.chips -= (Bot_A_river_raise_amount - Bot_B_river_bet_amount)
            pot += (Bot_A_river_raise_amount - Bot_B_river_bet_amount)
            #here comes the showdown
            determine_winner(players = players, board= board, pot = pot, row_idx = row_idx)
            clear_board(board)
            clear_hand()

          #if Bot_B decides to re_raise which is currently not programmed in
          else:
            Bot_B_river_re_raise_amount = bot_B.get_re_raise_amount(opponent_bet_amount = Bot_A_river_raise_amount, hand_ranking = Bot_B_river_hand_strength)
            game_results_df.at[row_idx, "river_Bot_B_re_raise_amount"] = Bot_B_river_re_raise_amount
            player_2.chips -= Bot_B_river_re_raise_amount

            #now the user can make a decision in response to the re-raise
            Bot_A_decision_3 = bot_A.get_post_river_decision_2(board = board)
            game_results_df.at[row_idx, "river_Bot_A_decision_3"] = Bot_A_decision_3

            if Bot_A_decision_3 == "fold":
              player_2.chips += pot #bot b wins the pot without a showdown
              clear_hand()
              game_results_df.at[row_idx, "winnings"] = pot
              game_results_df.at[row_idx, "winner"] = player_2.name
              clear_board(board)
              pot = 0
            #bot A calls bot b's re-raise
            else:
              player_1.chips -= (Bot_B_river_re_raise_amount- Bot_A_river_raise_amount)
              pot += (Bot_B_river_re_raise_amount- Bot_A_river_raise_amount)
             #here comes the showdown
              determine_winner(players = players, board= board, pot = pot, row_idx = row_idx)
              clear_board(board)
              clear_hand()

    #Bot A leads with a bet
    else:
      Bot_A_river_bet_amount = bot_A.get_post_river_bet_amount(pot = pot, hand_ranking = Bot_A_river_hand_ranking) #hand ranking is still stored for bot A because it was outside the first conditional block
      game_results_df.at[row_idx, "river_Bot_A_bet"] = Bot_A_river_bet_amount
      pot += Bot_A_river_bet_amount
      player_1.chips -= Bot_A_river_bet_amount

      #now Bot B has to respond to Bot A's bet amount
      Bot_B_river_decision = bot_B.get_river_decision(board = board, opponent_post_flop_decision = Bot_A_postflop_decision, opponent_post_turn_decision = Bot_A_turn_decision, opponent_post_river_decision = Bot_A_river_decision)[0]
      game_results_df.at[row_idx, "river_computer_decision"] = Bot_B_river_decision

      #adding bot b's river hand ranking to the dataframe
      Bot_B_river_hand_strength = bot_B.get_river_decision(board = board, opponent_post_flop_decision = Bot_A_postflop_decision, opponent_post_turn_decision = Bot_A_turn_decision, opponent_post_river_decision = Bot_A_river_decision)[1]
      game_results_df.at[row_idx, "river_Bot_B_hand_strength"] = Bot_B_river_hand_strength

      if Bot_B_river_decision == "fold":
        player_1.chips += pot
        clear_hand()
        game_results_df.at[row_idx, "winnings"] = pot
        game_results_df.at[row_idx, "winner"] = player_1.name
        clear_board(board)
        pot = 0
      elif Bot_B_river_decision == "call":
        player_2.chips -= Bot_A_river_bet_amount
        pot += Bot_A_river_bet_amount
        #here comes the showdown
        determine_winner(players = players, board= board, pot = pot, row_idx=row_idx)
        clear_board(board)
        clear_hand()

      #Bot_B decides to raise bot_A's bet
      else:
        bot_B_river_raise_amount = bot_B.get_re_raise_amount(opponent_bet_amount = Bot_A_river_bet_amount, hand_ranking = Bot_B_river_hand_strength)
        game_results_df.at[row_idx, "river_Bot_B_raise_amount"] = bot_B_river_raise_amount
        player_2.chips -= bot_B_river_raise_amount
        pot += bot_B_river_raise_amount

        #now the user can make a decision in response to the re-raise
        Bot_A_river_decision_2 = bot_A.get_post_river_decision_2(board = board)[0]
        game_results_df.at[row_idx, "river_Bot_A_decision_2"] = Bot_A_river_decision_2

        if Bot_A_river_decision_2 == "fold":
          player_2.chips += pot #bot b wins the pot without a showdown
          clear_hand()
          game_results_df.at[row_idx, "winnings"] = pot
          game_results_df.at[row_idx, "winner"] = player_2.name
          clear_board(board)
          pot = 0
        #user calls the com raises
        else:
          player_1.chips -= (bot_B_river_raise_amount - Bot_A_river_bet_amount)
          pot += (bot_B_river_raise_amount - Bot_A_river_bet_amount)
          #here comes the showdown
          determine_winner(players = players, board= board, pot = pot, row_idx=row_idx)
          clear_board(board)
          clear_hand()

