import os, sys

print("cwd:" , os.getcwd())
print("sys.path")
for p in sys.path:
    print("  ", p)

root = r"C:\Users\jason\projects\poker_project\poker-ai-headsup"
#best practice to only import the necessacary functions
if root not in sys.path:
    sys.path.insert(0, root)

from engine.engine_helpers import preflop_hand_strength, create_deck, deal_cards, clear_hand, clear_board, get_seven_card_hand, evaluate_hand, best_hand, has_straight_draw, has_flush_draw, flop, turn, river

#creating a poker bot class to make decisions depending on specific circumstances in the core_engine
import random

class PokerBot_A:
  """
  This class creates a bot to play the small blind position in poker
  It will make decisions based on the strength of its hand, the board, and the actions of the opponent.
  """
  def __init__(self, name, stack_size, small_blind, big_blind):
    self.name = name #name of the bot
    self.chips = stack_size #amount of chips the bot has to play with
    self.hand = [] #the gameplay engine automatically deals players the hand.
    self.small_blind = small_blind #expected 1
    self.big_blind = big_blind #expected 2


  def get_preflop_decision(self):
    """
    Bot A decision making for getting "pre_flop_bota_hand_strength" and "pre_flop_bota_decision" in the game results dataframe
    """
    #getting the preflop hand strength with helper function and actions to take based on the strength of the hand
    strength = preflop_hand_strength(self.hand[0], self.hand[1])
    if strength > 0.8:
      random_number = random.randint(1, 100)
      if random_number >= 7:
        preflop_decision = "raise"
      else:
        preflop_decision = "call"
    elif strength > 0.6 and strength <= 0.8:
      random_number = random.randint(1, 100)
      if random_number >= 25:
        preflop_decision = "raise"
      else:
        preflop_decision = "call"
    elif strength > 0.4 and strength <= 0.6:
      random_number = random.randint(1, 100)
      if random_number >= 70:
        preflop_decision = "raise"
      else:
        preflop_decision = "call"
    elif strength > 0 and strength <= 0.4:
      random_number = random.randint(1, 100)
      if random_number >= 90:
        preflop_decision = "raise"
      elif random_number >= 15:
        preflop_decision = "fold"
      else:
        preflop_decision = "call"

    return preflop_decision, strength

  #this function is designed to randomize the preflop raise amounts to behave more like a human player
  def get_preflop_raise_amount(self):
    "Bot A preflop raise amount, if the bot decides to raise previously, this function will determine how much to raise"
    random_number = random.randint(1, 100)
    if random_number >= 95:
      preflop_raise_amount = 4 * self.big_blind
    elif random_number >= 50:
      preflop_raise_amount = 3 * self.big_blind
    else:
      preflop_raise_amount = 2 * self.big_blind

    return preflop_raise_amount

  #if the other player re-raises, Bot A needs to make another decision to either call, re-raise, or fold
  def get_preflop_decision_2(self):
    """
    Bot A decision making for responding to other players re-raise
    """
    #need to refer to preflop hand strength again -- this time to make sure the hand is strong enough to call a re-raise
    strength = preflop_hand_strength(self.hand[0], self.hand[1])

    #now the bot will act skeptical assuming the other player has a very strong hand
    if strength > 0.4: #hands that are this strong are priced in to call a re-raise
      preflop_decision_2 = "call"
    else:
      random_number = random.randint(1, 100)
      if random_number >= 50:
        preflop_decision_2 = "call"
      else:
        preflop_decision_2 = "fold"

    return preflop_decision_2

  #the next decision to be made is the first post flop decision
  def get_post_flop_decision(self, board):
    """
    Bot A decision making for its inital post flop action choice
    This function requires the the gameflow engine to have delt the flop cards to the board -- and the board variable is passed in
    """
    
    #this sequence determines what state the players hand is in (ex: if it flopped a pair, flush draw, straight draw, etc.) -- it would be helpful to update the function to recognize board patterns and make more complex decisions
    full_hand = get_seven_card_hand(self, board) #returns a list of the players cards in addition to whats displayed on the board
    hand_ranking = evaluate_hand(full_hand)

    #see if there is more to the bots hand than whats visible 
    flush_draw = has_flush_draw(full_hand) #function will return True if the bot needs one card to make a flush
    straight_draw = has_straight_draw(full_hand) #functiono will return True if the bot needs one card to make a straight

    #how the bot will act when it flops nothing
    if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
      random_number = random.randint(1,100)
      if random_number >= 15:
        post_flop_decision = "check"
      else:
        post_flop_decision = "bet"
    #how the bot will act when it flops nothing with a flush or straight draw
    elif hand_ranking[0] == 1 and flush_draw == True or straight_draw == True:
      if random.randint(1, 100) > 40:
        post_flop_decision = "check"
      else:
        post_flop_decision = "bet"
    #how the bot will act when it flops a pair
    elif hand_ranking[0] == 2: 
      pair_strength = hand_ranking[5]
      if pair_strength == 1: #how the bot will act when it flops top pair
        if random.randint(1, 100) > 30:
          post_flop_decision = "bet"
        else:
          post_flop_decision = "check"
      elif pair_strength == 2: #how the bot will act when it flops second pair
        if random.randint(1, 100) > 40:
          post_flop_decision = "bet"
        else:
          post_flop_decision = "check"
      else: #how the bot will act when it flops a low pair
        if random.randint(1, 100) > 55:
          post_flop_decision = "bet"
        else:
          post_flop_decision = "check"
    #if the hand ranking is greater then one pair -- can assume the bot flopped an amazing hand and all should play similarly 
    else:
      if random.randint(1, 100) > 50: #mix in some checks to slow play strong hands sometimes
        post_flop_decision = "bet"
      else:
        post_flop_decision = "check"

    return post_flop_decision, hand_ranking[0]

  def get_post_flop_bet_amount(self, pot, hand_ranking): #this function needs to know the potsize to determine sizings
    """
    Bot A post flop bet amount, to get the bet amount the pot size must be passed in from the gameflow engine
    This function is used to determine how much to bet on the flop based on the strength of the hand with randomization 
    to represent human behavior.
    """
    if hand_ranking == 1:
      if random.randint(1, 100) > 50:
        post_flop_bet_amount = int(round(1/3 * pot))
      else:
        post_flop_bet_amount = int(round(1/2 * pot))
    elif hand_ranking == 2:
      if random.randint(1, 100) > 70:
        post_flop_bet_amount = int(round(1/3 * pot))
      else:
        post_flop_bet_amount = int(round(1/2 * pot))
    else:
      if random.randint(1, 100) > 50:
        post_flop_bet_amount = int(round(1/2 * pot))
      else:
        post_flop_bet_amount = int(round(2/3 * pot))

    return post_flop_bet_amount

  def get_post_flop_decision_2(self, board): #for max performance it might be better to pass in the opponent's post flop decision as well to split the decision making based on if its a check-bet or bet-raise
    """
    This function is for if the other player re-raises a bet, or if the other player bets after bot-a checks
    """
    #this sequence of function calls determies what state the players hand is in (ex: if it flopped a pair, flush draw, straight draw, etc.) -- it would be helpful to update the function to recognize board patterns and make more complex decisions
    #the functions can be found in engine/engine_helpers.py
    full_hand = get_seven_card_hand(self, board) 
    hand_ranking = evaluate_hand(full_hand)

    #see if there is more to the bots hand than whats visible 
    flush_draw = has_flush_draw(full_hand) #function will return True if the bot needs one card to make a flush
    straight_draw = has_straight_draw(full_hand) #functiono will return True if the bot needs one card to make a straight

    #the bot should fold nothing to a re-raise or check-bet on the flop
    if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
        post_flop_decision = "fold"
    #how the bot will act when it flops nothing with a flush or straight draw
    elif hand_ranking[0] == 1 and flush_draw == True or straight_draw == True:
      if random.randint(1, 100) > 50:
        post_flop_decision = "call"
      else:
        post_flop_decision = "fold"
    #how the bot will act when it flops a pair
    elif hand_ranking[0] == 2:
      pair_strength = hand_ranking[5]
      if pair_strength == 1: #top pair
        if random.randint(1, 100) > 30:
          post_flop_decision = "call"
        else:
          post_flop_decision = "call"
      elif pair_strength == 2: #second pair
        if random.randint(1, 100) > 10:
          post_flop_decision = "call"
        else:
          post_flop_decision = "call"
      else: #low pair
        if random.randint(1, 100) > 20:
          post_flop_decision = "call"
        else:
          post_flop_decision = "fold"
    #two pair or better should always defend here 
    else:
      if random.randint(1, 100) > 25:
        post_flop_decision = "call"
      else:
        post_flop_decision = "call"

    return post_flop_decision, hand_ranking[0]

  def get_re_raise_amount(self, opponent_bet_amount, hand_ranking):
    """
    This function is for how much Bot-a will re-raise the opponent's bet on any street. Includes randomization to simulate human behavior.
    """
    if hand_ranking == 2:
      if random.randint(1, 100) > 50:
        re_raise_amount = 2 * opponent_bet_amount
      else:
        re_raise_amount = 2.5 * opponent_bet_amount

    else:
      random_number = random.randint(1, 100)
      if random_number > 50:
        re_raise_amount = 3 * opponent_bet_amount
      elif random_number > 10:
        re_raise_amount = 2.5 * opponent_bet_amount
      else:
        re_raise_amount = 2 * opponent_bet_amount

    return re_raise_amount

    #the hand history starts to matter more at the turn so its important to consider if the opponent checked or bet on the flop for more accurate decision making 
  def get_turn_decision(self, board, opponent_post_flop_decision, opponent_post_flop_decision_2 = None):
        """
        Bot A decision making for its turn action choice, based on the strength of its hand and opponents decision history 
        """
        #this sequence determines what state the players hand is in -- it would be helpful to update the function to recognize board patterns and make more complex decisions
        full_hand = get_seven_card_hand(self, board) #returns a list of the players cards in addition to whats displayed on the board
        hand_ranking = evaluate_hand(full_hand)

        #see if there is more to the bots hand than whats visible 
        flush_draw = has_flush_draw(full_hand) #function will return True if the bot needs one card to make a flush
        straight_draw = has_straight_draw(full_hand) #functiono will return True if the bot needs one card to make a straight

        #this means it went check check -- could mean the opponent is weak
        if opponent_post_flop_decision == "check":
            #this could be a good time to start repping a strong hand with nothing
            if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
                random_number = random.randint(1, 100)
                if random_number >= 55: #more than likely the bot will bet on the turn if it went check-check on the flop
                    post_turn_decision = "check"
                else:
                    post_turn_decision = "bet"

            #how the bot will act when it flops air with a flush or straight draw, will keep the odds the same as air 
            elif hand_ranking[0] == 1 and flush_draw == True or straight_draw == True:
                if random.randint(1, 100) > 55:
                    post_turn_decision = "check"
                else:
                    post_turn_decision = "bet"
            #if it went check-check its likely the bot flopped its pair on the turn -- meaning its a strong time to bet 
            elif hand_ranking[0] == 2:
                pair_strength = hand_ranking[5]
                if pair_strength == 1:
                    if random.randint(1, 100) > 15:
                        post_turn_decision = "bet"
                    else:
                        post_turn_decision = "check"
                elif pair_strength == 2:
                    if random.randint(1, 100) > 35:
                        post_turn_decision = "bet" #need to be careful if the opponent is slow playing top pair on the flop
                    else:
                        post_turn_decision = "check"
                else:
                    if random.randint(1, 100) > 50: #can potentially be the best hand -- but also can be getting trapped, hopefully opponent folds to this bet
                        post_turn_decision = "bet"
                    else:
                        post_turn_decision = "check"
            #if the hand ranking is greater then one pair -- can assume the bot flopped an amazing hand and all should play similarly 
            else:
                if random.randint(1, 100) > 25: 
                    post_turn_decision = "bet" #good time to start building a pot with strong hands
                else:
                    post_turn_decision = "check"

            return post_turn_decision, hand_ranking[0]

        #this means that bot_a checked to the opponent and they decided to bet -- potential sign of strength or they are just trying to take down the pot with nothing  
        elif opponent_post_flop_decision == "bet":
        #best to check here and try to get a free river card if the opponent is scared of the flop call  
            if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
                random_number = random.randint(1, 100)
                if random_number >= 15: #really should be checking here -- no reason to bet
                    post_turn_decision = "check"
                else:
                    post_turn_decision = "bet"

            #how the bit will act with a flush or straight draw on the turn. 
            elif hand_ranking[0] == 1 and flush_draw == True or straight_draw == True:
                if random.randint(1, 100) > 75: #could be a good semi bluff spot but most of the time the bot will check here
                    post_turn_decision = "bet"
                else:
                    post_turn_decision = "check"
            #how the bot will act when has a pair on the turn -- good time to show strength with strong pairs
            elif hand_ranking[0] == 2:
                pair_strength = hand_ranking[5]
                if pair_strength == 1:
                    if random.randint(1, 100) > 20:
                        post_turn_decision = "bet"
                    else:
                        post_turn_decision = "check"
                elif pair_strength == 2:
                    if random.randint(1, 100) > 40:
                        post_turn_decision = "bet"
                    else:
                        post_turn_decision = "check"
                else:
                    if random.randint(1, 100) > 65:
                        post_turn_decision = "bet"
                    else:
                        post_turn_decision = "check"
            #if the hand ranking is greater then one pair -- can assume the bot turned an amazing hand and all should play similarly 
            else:
                if random.randint(1, 100) > 50:
                    post_turn_decision = "bet"
                else:
                    post_turn_decision = "check"

            return post_turn_decision, hand_ranking[0]

        #this means the opponents postflop decision was to re-raise (this means we should be skeptical of them having a strong hand)
        else:
          #if the bot made it this long with air -- it might be a good idea to start semi bluffing 
            if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
                post_turn_decision = "check"

        #how the bot will act when it flops air with a flush or straight draw
            elif hand_ranking[0] == 1 and flush_draw == True or straight_draw == True:
                post_turn_decision = "check"
        #how the bot will act when it flops a pair

            elif hand_ranking[0] == 2:
                pair_strength = hand_ranking[5]
                if pair_strength == 1:
                    if random.randint(1, 100) > 50: #dangerous against a re-raise
                        post_turn_decision = "bet"
                    else:
                        post_turn_decision = "check"
                elif pair_strength == 2:
                    if random.randint(1, 100) > 75:
                        post_turn_decision = "bet"
                    else:
                        post_turn_decision = "check"
                else:
                    if random.randint(1, 100) > 90: #very weak pair -- probably behind here
                        post_turn_decision = "bet"
                    else:
                        post_turn_decision = "check"

        #hands greater than a pair should be less cautious but also skeptical of the opponent - a lead out bet here is probaly best to show strength through the re-raise
            else:
                if random.randint(1, 100) > 25:
                    post_turn_decision = "bet"
                else:
                    post_turn_decision = "check"

            return post_turn_decision, hand_ranking[0]

  def get_post_turn_bet_amount(self, pot, hand_ranking): #this function needs to know the potsize to determine sizings
    """
    Bot A post turn bet amount
    """

    #at this point the terrible hand should start acting as a bluff
    if hand_ranking == 1:
        if random.randint(1, 100) > 50:
            post_turn_bet_amount = int(round(3/4 * pot)) #large bets to get folds
        else:
            post_turn_bet_amount = int(round(1 * pot))
    elif hand_ranking == 2:
        if random.randint(1, 100) > 70:
            post_turn_bet_amount = int(round(1/3 * pot))
        else:
            post_turn_bet_amount = int(round(1/2 * pot))
    else:
        if random.randint(1, 100) > 50:
            post_turn_bet_amount = int(round(1/2 * pot))
        else:
            post_turn_bet_amount = int(round(1 * pot))

    return post_turn_bet_amount

  def get_post_turn_decision_2(self, board): #would be helpful to pass in the opponent's post turn decision as well to split the decision making based on if its a check-bet or bet-raise
    """
    This function is for if the other player re-raises a bet, or if the other player bets after bot-a checks on the turn
    """
    #determine the ranking of the bot's hand and how it will act based on the opponents actions
    full_hand = get_seven_card_hand(self, board) #returns a list of the players cards in addition to whats displayed on the board
    hand_ranking = evaluate_hand(full_hand)

    #see if there is more to the bots hand than whats visible 
    flush_draw = has_flush_draw(full_hand) #function will return True if the bot needs one card to make a flush
    straight_draw = has_straight_draw(full_hand) #function will return True if the bot needs one card to make a straight

    if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False: #opponent is showing a lot of strength -- fold air
        post_turn_decision = "fold"
    #how the bot will act when it turns air with a flush or straight draw
    elif hand_ranking[0] == 1 and flush_draw == True or straight_draw == True: #most likely priced in here to call a flush draw
      if random.randint(1, 100) > 20:
        post_turn_decision = "call"
      else:
        post_turn_decision = "fold"
    #how the bot will act when it turns a pair
    elif hand_ranking[0] == 2: #facing a re-raise or bet here with top pair should skeptically call 
      pair_strength = hand_ranking[5]
      if pair_strength == 1:
        if random.randint(1, 100) > 20:
          post_turn_decision = "call"
        else:
          post_turn_decision = "fold"
      elif pair_strength == 2:
        if random.randint(1, 100) > 60: #usually would be behind in this scenario
          post_turn_decision = "call"
        else:
          post_turn_decision = "fold"
      else:
        if random.randint(1, 100) > 20: #low pair almost certianly losing
          post_turn_decision = "fold"
        else:
          post_turn_decision = "call"
    #if the hand ranking is greater then one pair -- logical to defend the hand in most cases with occasional re-raises
    else:
      if random.randint(1, 100) > 25:
        post_turn_decision = "call"
      else:
        post_turn_decision = "re-raise"

    return post_turn_decision, hand_ranking[0]


  #takes opponents full history of decision making into account
  def get_river_decision(self, board, opponent_post_flop_decision, opponent_post_turn_decision):
        """
        Bot A decision making for its turn action choice, based on the strength of its hand and opponents decision history 
        """
        #get the hand ranking of the bot's hand and how it will act based on the opponents actions
        full_hand = get_seven_card_hand(self, board) #returns a list of the players cards in addition to whats displayed on the board
        hand_ranking = evaluate_hand(full_hand)

        #see if there is more to the bots hand than whats visible 
        flush_draw = has_flush_draw(full_hand) #function will return True if the bot needs one card to make a flush
        straight_draw = has_straight_draw(full_hand) #functiono will return True if the bot needs one card to make a straight

        #the opponent checked on the flop and the turn
        if opponent_post_flop_decision == "check" and opponent_post_turn_decision == "check": #the opponent is likely very weak -- worth taking a stab at winning the pot with weaker hands that would lose a showdown
          #if the bot made it this long with air -- it might be a good idea to start semi bluffing 
          if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
              random_number = random.randint(1, 100)
              if random_number >= 25: #more than likely the bot will bet on the river
                post_river_decision = "bet"
              else:
                post_river_decision = "check"

          #if opponent went check-check on turn and river its likely the bot flopped its pair on the turn or river-- meaning its a strong time to bet 
          elif hand_ranking[0] == 2:
            pair_strength = hand_ranking[5]
            if pair_strength == 1:
              if random.randint(1, 100) > 10:
                post_river_decision = "bet"
              else:
                post_river_decision = "check"
            elif pair_strength == 2:
              if random.randint(1, 100) > 25:
                post_river_decision = "bet" #need to be careful if the opponent is slow playing top pair on the flop
              else:
                post_river_decision = "check"
            else:
              if random.randint(1, 100) > 65: #can potentially be the best hand -- but also can be getting trapped, hopefully opponent folds to this bet
                post_river_decision = "bet"
              else:
                post_river_decision = "check"
          #if the hand ranking is greater then one pair -- can assume the bot flopped an amazing hand and all should play similarly 
          else:
            post_river_decision = "bet" #good time to start building a pot with strong hands
            

          return post_river_decision, hand_ranking[0]
        
        #if the opponent bet at each street they are most likely strong -- probably a good idea to only bet strong hands
        elif opponent_post_flop_decision == "bet" and opponent_post_turn_decision == "bet":
           #if the bot made it this long with air -- it might be a good idea to start semi bluffing 
          if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
              random_number = random.randint(1, 100)
              if random_number >= 10: #more than likely the bot will bet on the river
                post_river_decision = "check"
              else:
                post_river_decision = "bet"

          #if opponent went check-check on turn and river its likely the bot flopped its pair on the turn or river-- meaning its a strong time to bet 
          elif hand_ranking[0] == 2:
            pair_strength = hand_ranking[5]
            if pair_strength == 1:
              if random.randint(1, 100) > 45:
                post_river_decision = "bet"
              else:
                post_river_decision = "check"
            elif pair_strength == 2:
              if random.randint(1, 100) > 25:
                post_river_decision = "bet" #need to be careful if the opponent is slow playing top pair on the flop
              else:
                post_river_decision = "check"
            else:
              if random.randint(1, 100) > 25: #can potentially be the best hand -- but also can be getting trapped, hopefully opponent folds to this bet
                post_river_decision = "bet"
              else:
                post_river_decision = "check"
          #if the hand ranking is greater then one pair -- can assume the bot flopped an amazing hand and all should play similarly 
          else:
            post_river_decision = "bet" #good time to start building a pot with strong hands
            

          return post_river_decision, hand_ranking[0]
        
        elif opponent_post_flop_decision == "bet" and opponent_post_turn_decision == "check":
          #if the bot made it this long with air -- it might be a good idea to start semi bluffing 
          if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
              random_number = random.randint(1, 100)
              if random_number >= 70: #more than likely the bot will bet on the river
                post_river_decision = "bet"
              else:
                post_river_decision = "check"

          #bot has a pair on the river after turn and the opponent checks 
          elif hand_ranking[0] == 2:
            pair_strength = hand_ranking[5]
            if pair_strength == 1:
              if random.randint(1, 100) > 25:
                post_river_decision = "bet"
              else:
                post_river_decision = "check"
            elif pair_strength == 2:
              if random.randint(1, 100) > 37:
                post_river_decision = "bet" #need to be careful if the opponent is slow playing top pair on the flop
              else:
                post_river_decision = "check"
            else:
              if random.randint(1, 100) > 55: #can potentially be the best hand -- but also can be getting trapped, hopefully opponent folds to this bet
                post_river_decision = "bet"
              else:
                post_river_decision = "check"
          #if the hand ranking is greater then one pair -- can assume the bot flopped an amazing hand and all should play similarly 
          else:
            post_river_decision = "bet" #good time to start building a pot with strong hands
            

          return post_river_decision, hand_ranking[0]

        elif opponent_post_flop_decision == "bet" and opponent_post_turn_decision == "check":
          #if the bot made it this long with air -- it might be a good idea to start semi bluffing 
          if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
              random_number = random.randint(1, 100)
              if random_number >= 70: #more than likely the bot will bet on the river
                post_river_decision = "bet"
              else:
                post_river_decision = "check"

          #bot has a pair on the river after turn and the opponent checks 
          elif hand_ranking[0] == 2:
            pair_strength = hand_ranking[5]
            if pair_strength == 1:
              if random.randint(1, 100) > 25:
                post_river_decision = "bet"
              else:
                post_river_decision = "check"
            elif pair_strength == 2:
              if random.randint(1, 100) > 37:
                post_river_decision = "bet" #need to be careful if the opponent is slow playing top pair on the flop
              else:
                post_river_decision = "check"
            else:
              if random.randint(1, 100) > 55: #can potentially be the best hand -- but also can be getting trapped, hopefully opponent folds to this bet
                post_river_decision = "bet"
              else:
                post_river_decision = "check"
          #if the hand ranking is greater then one pair -- can assume the bot flopped an amazing hand and all should play similarly 
          else:
            post_river_decision = "bet" #good time to start building a pot with strong hands
            

          return post_river_decision, hand_ranking[0]

      
        elif opponent_post_flop_decision == "check" and opponent_post_turn_decision == "bet":
          #if the bot made it this long with air -- it might be a good idea to start semi bluffing 
          if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
              random_number = random.randint(1, 100)
              if random_number >= 70: #more than likely the bot will bet on the river
                post_river_decision = "bet"
              else:
                post_river_decision = "check"

          #bot has a pair on the river after turn and the opponent checks 
          elif hand_ranking[0] == 2:
            pair_strength = hand_ranking[5]
            if pair_strength == 1:
              if random.randint(1, 100) > 50:
                post_river_decision = "bet"
              else:
                post_river_decision = "check"
            elif pair_strength == 2:
              if random.randint(1, 100) > 50:
                post_river_decision = "bet" #need to be careful if the opponent is slow playing top pair on the flop
              else:
                post_river_decision = "check"
            else:
              if random.randint(1, 100) > 70: #can potentially be the best hand -- but also can be getting trapped, hopefully opponent folds to this bet
                post_river_decision = "bet"
              else:
                post_river_decision = "check"
          #if the hand ranking is greater then one pair -- can assume the bot flopped an amazing hand and all should play similarly 
          else:
            post_river_decision = "bet" #good time to start building a pot with strong hands
            

          return post_river_decision, hand_ranking[0]

        elif opponent_post_flop_decision == "raise" or opponent_post_turn_decision == "raise":
          #if the bot made it this long with air -- it might be a good idea to start semi bluffing 
          if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
              random_number = random.randint(1, 100)
              if random_number >= 3: #more than likely the bot will bet on the river
                post_river_decision = "check"
              else:
                post_river_decision = "bet"

          #bot has a pair on the river after turn and the opponent checks 
          elif hand_ranking[0] == 2:
            pair_strength = hand_ranking[5]
            if pair_strength == 1:
              if random.randint(1, 100) > 60:
                post_river_decision = "bet"
              else:
                post_river_decision = "check"
            elif pair_strength == 2:
              if random.randint(1, 100) > 75:
                post_river_decision = "bet" #need to be careful if the opponent is slow playing top pair on the flop
              else:
                post_river_decision = "check"
            else:
              if random.randint(1, 100) > 90: #can potentially be the best hand -- but also can be getting trapped, hopefully opponent folds to this bet
                post_river_decision = "bet"
              else:
                post_river_decision = "check"
          #if the hand ranking is greater then one pair -- can assume the bot flopped an amazing hand and all should play similarly 
          else:
            random_number = random.randint(1, 100)
            if random_number >= 40:
              post_river_decision = "check"
            else:
              post_river_decision = "bet"
            
          return post_river_decision, hand_ranking[0]


  def get_post_river_bet_amount(self, pot, hand_ranking): #this function needs to know the potsize to determine sizings
    """
    Bot A post river bet amount
    """

    #at this point the terrible hand should start acting as a bluff
    if hand_ranking == 1:
      random_number = random.randint(1, 100)
      if random_number >= 75:
        post_river_bet_amount = int(round(1/3 * pot)) #large bets to get folds
      elif random_number >= 50:
        post_river_bet_amount = int(round(1/2 * pot))
      elif random_number >= 25:
        post_river_bet_amount = int(round(1 * pot))
      else:
        post_river_bet_amount = int(round(5/4 * pot)) #massive overbet with air to get folds
    #these can be more value bets 
    elif hand_ranking == 2:
      random_number = random.randint(1, 100)
      if random_number >= 75:
        post_river_bet_amount = int(round(1/3 * pot))
      elif random_number > 50:
        post_river_bet_amount = int(round(1/2 * pot))
      else:
        post_river_bet_amount = int(round(3/4 * pot))
    else:
      if random.randint(1, 100) > 50:
        post_river_bet_amount = int(round(1/2 * pot))
      else:
        post_river_bet_amount = int(round(5/4 * pot))

    return post_river_bet_amount

  #for the last post river decision its important to mix in some re-raises with weaker hands to have a chance at winning
  def get_post_river_decision_2(self, board):
    """
    This function is for if the other player re-raises a bet, or if the other player bets after bot-a checks on the river
    """
    #this sequence determines what state the players hand is in -- it would be helpful to update the function to recognize board patterns and make more complex decisions
    full_hand = get_seven_card_hand(self, board) #returns a list of the players cards in addition to whats displayed on the board
    hand_ranking = evaluate_hand(full_hand)

    #see if there is more to the bots hand than whats visible 
    flush_draw = has_flush_draw(full_hand) #function will return True if the bot needs one card to make a flush
    straight_draw = has_straight_draw(full_hand) #function will return True if the bot needs one card to make a straight

    if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False: #opponent is showing a lot of strength -- fold air
        post_river_decision = "fold"
    #how the bot will act when it turns a pair
    elif hand_ranking[0] == 2: #facing a re-raise or bet here with top pair should skeptically call 
      pair_strength = hand_ranking[5]

      if pair_strength == 1:
        random_number = random.randint(1, 100)
        if random_number > 20:
          post_river_decision = "call"
        else:
          post_river_decision = "re-raise"
      elif pair_strength == 2:
        random_number = random.randint(1, 100)
        if random_number >= 65: #
          post_river_decision = "call"
        elif random_number >= 35:
          post_river_decision = "fold"
        else:
          post_river_decision = "re-raise"
        
    #low pair decision making
      else:
        if random.randint(1, 100) > 10: #low pair almost certianly losing
          post_turn_decision = "fold"
        else:
          post_turn_decision = "call"
    #if the hand ranking is greater then one pair -- logical to defend the hand in most cases with occasional re-raises
    else:
      if random.randint(1, 100) > 25:
        post_turn_decision = "call"
      else:
        post_turn_decision = "re-raise"

      return post_turn_decision, hand_ranking[0]