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

import random
class PokerBot_B:
  def __init__(self, name, stack_size, small_blind, big_blind):
    self.name = name
    self.chips = stack_size
    self.hand = []
    self.small_blind = small_blind
    self.big_blind = big_blind

  def get_preflop_decision(self, opponent_preflop_decision):
    strength = preflop_hand_strength(self.hand[0], self.hand[1])
    if opponent_preflop_decision == "call":
      if strength >= 0.8:
        random_number = random.randint(1, 100)
        if random_number >= 50:
          preflop_decision = "raise"
        else:
          preflop_decision = "call"
      elif strength >= 0.6 and strength < 0.8:
        random_number = random.randint(1, 100)
        if random_number >= 60:
          preflop_decision = "raise"
        else:
          preflop_decision = "check"
      elif strength >= 0.4 and strength < 0.6:
        if random.randint(1, 100) >= 70:
          preflop_decision = "raise"
        else:
          preflop_decision = "check"
      else:
        random_number = random.randint(1, 100)
        if random_number >= 96:
          preflop_decision = "raise"
        else:
          preflop_decision = "check"
    #this means the opponent decided to raise on the flop, now bot_b needs to decide if it wants to call the raise, fold to the raise, or re-raise the raise
    else:
      if strength >= 0.85:
        random_number = random.randint(1, 100)
        if random_number >= 35:
          preflop_decision = "call"
        else:
          preflop_decision = "re-raise" #throw in some re-raises with amazing hands -- but really nothing wrong with calling and seeing a flop here
      elif strength >= 0.65 and strength < 0.85:
        random_number = random.randint(1, 100)
        if random_number >= 15:
          preflop_decision = "call"
        else:
          preflop_decision = "re-raise"
      elif strength >= 0.4 and strength < 0.65:
        random_number = random.randint(1, 100)
        preflop_decision = "call"
      else:
        random_number = random.randint(1, 100)
        if random_number >=25:
          preflop_decision = "fold"
        else:
          preflop_decision = "call"

      return preflop_decision, strength

  def get_preflop_raise_amount(self):
    "Bot B preflop raise amount, same functionality as bot_A's preflop raises with slighly different tendencies and sizings to reflect differences in play styles"
    random_number = random.randint(1, 100)
    if random_number >= 90:
      preflop_raise_amount = 5 * self.big_blind
    elif random_number >= 40:
      preflop_raise_amount = 3 * self.big_blind
    else:
      preflop_raise_amount = 2 * self.big_blind

    return preflop_raise_amount

  #fine structure really just build for randomness and unpredictability
  def get_re_raise_amount(self, opponent_bet_amount, hand_ranking):
    """
    This function is for how much Bot-b will re-raise the opponent's bet on any street is also good for raise amounts.
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

  #this function can not be as simple as bot a's post flop decision making process because it most come in response to bot-a's decision
  def get_post_flop_decision(self, board, opponent_postflop_decision): #the opponents post flop decision can be either to check, or to lead out with a bet
      """
      Bot B decision making process in response to Bot A postflop decision
      """
      #splitting suits and numbers to aid in the decision making process and bot logic

      #this sequence determines what state the players hand is in -- it would be helpful to update the function to recognize board patterns and make more complex decisions
      full_hand = get_seven_card_hand(self, board) #returns a list of the players cards in addition to whats displayed on the board
      hand_ranking = evaluate_hand(full_hand)

      #see if there is more to the bots hand than whats visible
      flush_draw = has_flush_draw(full_hand) #function will return True if the bot needs one card to make a flush
      straight_draw = has_straight_draw(full_hand) #functiono will return True if the bot needs one card to make a straight

      if opponent_postflop_decision == "check":
        #how the bot will act when it flops nothing -- it can be a good idea to bet here after flopping nothing to take down the pot if they also flopped nothing
        if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
          random_number = random.randint(1,100)
          if random_number >= 38:
            post_flop_decision = "check"
          else:
            post_flop_decision = "bet"
        #how the bot will act when it flops air with a flush or straight draw
        elif hand_ranking[0] == 1 and flush_draw == True or straight_draw == True: #even better idea to bet here with potential to turn into a stronger hand if the opponent calls
          if random.randint(1, 100) > 70:
            post_flop_decision = "check"
          else:
            post_flop_decision = "bet"
        #how the bot will act when it flops a pair -- small sizings here  would be best to feel out the opponent -get early folds or price them into the hand
        elif hand_ranking[0] == 2:
          pair_strength = hand_ranking[5]
          if pair_strength == 1:
            if random.randint(1, 100) >= 25:
              post_flop_decision = "bet"
            else:
              post_flop_decision = "check"
          elif pair_strength == 2:
            if random.randint(1, 100) >= 35:
              post_flop_decision = "bet"
            else:
              post_flop_decision = "check"
          else:
            if random.randint(1, 100) > 75: #careful -- any slow played hand would have us beat
              post_flop_decision = "bet"
            else:
              post_flop_decision = "check"
        #if the hand ranking is greater then one pair -- can assume the bot flopped an amazing hand and all should play similarly
        else:
          if random.randint(1, 100) > 25:
            post_flop_decision = "bet"
          else:
            post_flop_decision = "check"

        return post_flop_decision, hand_ranking[0]
      #means bot-a has decided to lead out with a bet
      else:
        #how the bot will act when it flops nothing -- it can be a good idea to bet here after flopping nothing to take down the pot if they also flopped nothing
        if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
          random_number = random.randint(1,100)
          if random_number >= 95:
            post_flop_decision = "fold" #really not much of a reason to call here
          else:
            post_flop_decision = "call"
        #how the bot will act when it flops air with a flush or straight draw
        elif hand_ranking[0] == 1 and flush_draw == True or straight_draw == True: #even better idea to bet here with potential to turn into a stronger hand if the opponent calls
          if random.randint(1, 100) > 70:
            post_flop_decision = "fold"
          else:
            post_flop_decision = "call"
        #how the bot will act when it flops a pair -- small sizings here  would be best to feel out the opponent -get early folds or price them into the hand
        elif hand_ranking[0] == 2:
          pair_strength = hand_ranking[5]
          if pair_strength == 1:
            if random.randint(1, 100) >= 18:
              post_flop_decision = "call"
            else:
              post_flop_decision = "raise"
          elif pair_strength == 2:
            if random.randint(1,100) >= 10:
              post_flop_decision = "call"
            else:
              post_flop_decision = "raise"
          else:
            if random.randint(1, 100) > 20: #careful -- any slow played hand would have us beat
              post_flop_decision = "call"
            else:
              post_flop_decision = "fold"
        #if the hand ranking is greater then one pair -- can assume the bot flopped an amazing hand and all should play similarly
        else:
          if random.randint(1, 100) > 25:
            post_flop_decision = "call"
          else:
            post_flop_decision = "raise"

        return post_flop_decision, hand_ranking[0]

  #already have function for raise amounts

  def get_post_flop_bet_amount(self, pot, hand_ranking): #this function needs to know the potsize to determine sizings
    """
    Bot B post flop bet amounts -- similar function to bot a's post flop bet amount function, but different sizings and tendencies (more agressive)
    """
    if hand_ranking == 1:
      if random.randint(1, 100) > 70:
        post_flop_bet_amount = int(round(1/3 * pot))
      else:
        post_flop_bet_amount = int(round(1/2 * pot))
    elif hand_ranking == 2:
      if random.randint(1, 100) > 75:
        post_flop_bet_amount = int(round(1/3 * pot))
      else:
        post_flop_bet_amount = int(round(1/2 * pot))
    else:
      if random.randint(1, 100) > 75:
        post_flop_bet_amount = int(round(1/2 * pot))
      else:
        post_flop_bet_amount = int(round(2/3 * pot))

    return post_flop_bet_amount

  def get_post_flop_decision_2(self, board):
    """
    This function is for if the other player re-raises a bet thats the only way to reach this decision, here bot-b has the decision to either call, fold, or re-raise,
    function makes logical sense but going to make this bot slightly more agressive than bot-a
    """
    #this sequence determines what state the players hand is in -- it would be helpful to update the function to recognize board patterns and make more complex decisions
    full_hand = get_seven_card_hand(self, board) #returns a list of the players cards in addition to whats displayed on the board
    hand_ranking = evaluate_hand(full_hand)

    #see if there is more to the bots hand than whats visible
    flush_draw = has_flush_draw(full_hand) #function will return True if the bot needs one card to make a flush
    straight_draw = has_straight_draw(full_hand) #functiono will return True if the bot needs one card to make a straight

    if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
      if random.randint(1, 100) > 2:
        post_flop_decision = "fold"
      else:
        post_flop_decision = "call"
    #how the bot will act when it flops air with a flush or straight draw, can potentially be priced in at this point to see another card
    elif hand_ranking[0] == 1 and flush_draw == True or straight_draw == True:
      if random.randint(1, 100) > 50:
        post_flop_decision = "call"
      else:
        post_flop_decision = "fold"
    #how the bot will act when it flops a pair
    elif hand_ranking[0] == 2:
      pair_strength = hand_ranking[5]
      if pair_strength == 1:
        if random.randint(1, 100) > 10:
          post_flop_decision = "call"
        else:
          post_flop_decision = "re-raise"
      elif pair_strength == 2:
        if random.randint(1, 100) > 50:
          post_flop_decision = "call"
        else:
          post_flop_decision = "fold"
      else:
        if random.randint(1, 100) > 65:
          post_flop_decision = "call"
        else:
          post_flop_decision = "fold"
    #if the hand ranking is greater then one pair -- can assume the bot flopped an amazing hand and all should play similarly
    else:
      if random.randint(1, 100) > 25:
        post_flop_decision = "call"
      else:
        post_flop_decision = "re-raise"

    return post_flop_decision, hand_ranking[0]

  def get_turn_decision(self, board, opponent_post_flop_decision, opponent_turn_decision, opponent_post_flop_decision_2 = None): #build in functionality to account for a check raise on the flop by the opponent
    """
    Bot B decision making process in response to Bot A postflop decisions and post turn decision
    """

    #first evaluate the strength of the hand for bot-b

          #this sequence determines what state the players hand is in -- it would be helpful to update the function to recognize board patterns and make more complex decisions
    full_hand = get_seven_card_hand(self, board) #returns a list of the players cards in addition to whats displayed on the board
    hand_ranking = evaluate_hand(full_hand)

    #see if there is more to the bots hand than whats visible
    flush_draw = has_flush_draw(full_hand) #function will return True if the bot needs one card to make a flush
    straight_draw = has_straight_draw(full_hand) #functiono will return True if the bot needs one card to make a straight

    #this means that bot-a went check-check without any check raises, bot-a is most likely weak here
    if opponent_post_flop_decision == "check" and opponent_turn_decision == "check" and opponent_post_flop_decision_2 != "re-raise":
        #if the bot made it this long with air -- it might be a good idea to start semi bluffing
        if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
            random_number = random.randint(1, 100)
            if random_number >= 65: #more than likely the bot will bet on the turn if it went check-check on the flop
              post_turn_decision = "check"
            else:
              post_turn_decision = "bet"

        #how the bot will act when it flops air with a flush or straight draw, will keep the odds the same as air
        elif hand_ranking[0] == 1 and flush_draw == True or straight_draw == True:
          if random.randint(1, 100) > 50:
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
            if random.randint(1, 100) > 30:
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
          if random.randint(1, 100) > 15:
            post_turn_decision = "bet" #good time to start building a pot with strong hands
          else:
            post_turn_decision = "check"

        return post_turn_decision, hand_ranking[0]

      #this is one of the stronger lines the opponent can take
    elif opponent_post_flop_decision == "bet" or "check" and opponent_turn_decision == "bet" and opponent_post_flop_decision_2 != "re-raise":

        #if the bot made it this long with air -- it might be a good idea to start semi bluffing
        if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
            random_number = random.randint(1, 100)
            if random_number >= 90: #more than likely the bot will bet on the turn if it went check-check on the flop
              post_turn_decision = "call"
            else:
              post_turn_decision = "fold"

        #how the bot will act when it flops air with a flush or straight draw, will keep the odds the same as air
        elif hand_ranking[0] == 1 and flush_draw == True or straight_draw == True:
          if random.randint(1, 100) > 75:
            post_turn_decision = "call"
          else:
            post_turn_decision = "fold"
        #if it went check-check its likely the bot flopped its pair on the turn -- meaning its a strong time to bet
        elif hand_ranking[0] == 2:
          pair_strength = hand_ranking[5]
          if pair_strength == 1:
             post_turn_decision = "call"
          elif pair_strength == 2:
            if random.randint(1, 100) > 35:
              post_turn_decision = "call" #need to be careful if the opponent is slow playing top pair on the flop
            else:
              post_turn_decision = "fold"
          else:
            if random.randint(1, 100) > 65: #can potentially be the best hand -- but also can be getting trapped, hopefully opponent folds to this bet
              post_turn_decision = "call"
            else:
              post_turn_decision = "fold"
        #if the hand ranking is greater then one pair -- can assume the bot flopped an amazing hand and all should play similarly
        else:
          if random.randint(1, 100) > 25:
            post_turn_decision = "call" #good time to start building a pot with strong hands and the opponent is doing it for us
        return post_turn_decision, hand_ranking[0]

    #this is an opportunity to take advantage of the opponent slowing down -- perhaps they were afraid of bot-b's call on the flop and decided to check the turn
    elif opponent_post_flop_decision == "bet" and opponent_turn_decision == "check"  and opponent_post_flop_decision_2 != "re-raise":
        #if the bot made it this long with air -- it might be a good idea to start semi bluffing
        if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
            random_number = random.randint(1, 100)
            if random_number >= 50: #more than likely the bot will bet on the turn if it went check-check on the flop
              post_turn_decision = "check"
            else:
              post_turn_decision = "bet"

        #how the bot will act when it flops air with a flush or straight draw, will keep the odds the same as air
        elif hand_ranking[0] == 1 and flush_draw == True or straight_draw == True:
          if random.randint(1, 100) > 60:
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

    #granted the flop decision is to re-raise this tells what the bot will do depending on the opponents follow up turn decision
    else: #this means bot-a decided to re-raise on either the flop, means the opponent likely has a very strong hand

      if opponent_turn_decision == "check":
        #if the bot made it this long with air -- it might be a good idea to start semi bluffing
        if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
          post_turn_decision = "check" #This is a must check senario

        #how the bot will act when it flops air with a flush or straight draw, will keep the odds the same as air
        elif hand_ranking[0] == 1 and flush_draw == True or straight_draw == True:
          post_turn_decision = "check" #probably best to check here as well to try to get the flush -- not worth semi bluffing into a made hand
        #if it went check-check its likely the bot flopped its pair on the turn -- meaning its a strong time to bet
        elif hand_ranking[0] == 2:
          pair_strength = hand_ranking[5]
          if pair_strength == 1:
            if random.randint(1, 100) > 50:
              post_turn_decision = "bet"
            else:
              post_turn_decision = "check"
          elif pair_strength == 2:
            if random.randint(1, 100) > 75:
              post_turn_decision = "bet" #need to be careful if the opponent is slow playing top pair on the flop
            else:
              post_turn_decision = "check"
          else:
            if random.randint(1, 100) > 50: #can potentially be the best hand -- but also can be getting trapped, hopefully opponent folds to this bet
              post_turn_decision = "check"
        #if the hand ranking is greater then one pair -- can assume the bot flopped an amazing hand and all should play similarly
        else:
          if random.randint(1, 100) > 50:
            post_turn_decision = "bet" #good time to start building a pot with strong hands
          else:
            post_turn_decision = "check"

        return post_turn_decision, hand_ranking[0]

      #if opponent post turn decision is to bet after re-raising on the flop
      else:
        #definietly should fold air here
        if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
          post_turn_decision = "fold" #This is a must fold senario

        #how the bot will act when it flops air with a flush or straight draw, will keep the odds the same as air
        elif hand_ranking[0] == 1 and flush_draw == True or straight_draw == True:
          if random.randint(1, 100) > 60:
            post_turn_decision = "call"
          else:
            post_turn_decision = "fold"
        #if it went check-check its likely the bot flopped its pair on the turn -- meaning its a strong time to bet
        elif hand_ranking[0] == 2:
          pair_strength = hand_ranking[5]
          if pair_strength == 1:
            if random.randint(1, 100) > 15:
              post_turn_decision = "call"
            else:
              post_turn_decision = "fold"
          elif pair_strength == 2:
            if random.randint(1, 100) > 75:
              post_turn_decision = "call" #need to be careful if the opponent is slow playing top pair on the flop
            else:
              post_turn_decision = "fold"
          else:
            if random.randint(1, 100) > 90: #can potentially be the best hand -- but also can be getting trapped, hopefully opponent folds to this bet
              post_turn_decision = "call"
            else:
              post_turn_decision = "fold"
        #if the hand ranking is greater then one pair -- can assume the bot flopped an amazing hand and all should play similarly
        else:
          if random.randint(1, 100) > 25:
            post_turn_decision = "call" #good time to start building a pot with strong hands
          else:
            post_turn_decision = "re-raise"

        return post_turn_decision, hand_ranking[0]

  def get_post_turn_bet_amount(self, pot, hand_ranking): #this function needs to know the potsize to determine sizings
    """
    Bot B post turn bet amount -- similar function to bot a's post turn bet amount function, but different tendencies (more agressive), can assume that if post_turn_decision is bet
    the hand is reasonably strong to bet
    """

    #at this point the terrible hand should start acting as a bluff
    if hand_ranking == 1:
      if random.randint(1, 100) > 50:
        post_turn_bet_amount = int(round(1 * pot)) #large bets to get folds
      else:
        post_turn_bet_amount = int(round(5/4 * pot))
    elif hand_ranking == 2:
      if random.randint(1, 100) > 70:
        post_turn_bet_amount = int(round(1/2 * pot))
      else:
        post_turn_bet_amount = int(round(2/3 * pot))
    else:
      if random.randint(1, 100) > 50:
        post_turn_bet_amount = int(round(1/2 * pot))
      else:
        post_turn_bet_amount = int(round(1 * pot))

    return post_turn_bet_amount


  #a re-raise would use the re-raise function while a call would depend on the opponents bet size
  def get_post_turn_decision_2(self, board):
    """
    This function is for if the other player re-raises a bet, or if the other player bets after bot-a checks on the turn
    """
    #this sequence determines what state the players hand is in -- it would be helpful to update the function to recognize board patterns and make more complex decisions
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


  #takes opponents full history of decision making into account, can make this function more complicated with all possible combinations of re-raises at each street but that would be 36 possible betting lines instead of 9
  #for basic logic and decision making we'll just take the opponents first decision into account which will be enough the majority of the time.
  def get_river_decision(self, board, opponent_post_flop_decision, opponent_post_turn_decision, opponent_post_river_decision):
        """
        Bot A decision making for its turn action choice, based on the strength of its hand and opponents decision history
        """
          #this sequence determines what state the players hand is in -- it would be helpful to update the function to recognize board patterns and make more complex decisions
        full_hand = get_seven_card_hand(self, board) #returns a list of the players cards in addition to whats displayed on the board
        hand_ranking = evaluate_hand(full_hand)

        #see if there is more to the bots hand than whats visible
        flush_draw = has_flush_draw(full_hand) #function will return True if the bot needs one card to make a flush
        straight_draw = has_straight_draw(full_hand) #functiono will return True if the bot needs one card to make a straight

        #the opponent checked on the flop and the turn and the river -- logically this is a great time to bet regardless of the hand
        if opponent_post_flop_decision == "check" and opponent_post_turn_decision == "check" and opponent_post_river_decision == "check" : #the opponent is likely very weak -- worth taking a stab at winning the pot with weaker hands that would lose a showdown
          #if the bot made it this long with air -- it might be a good idea to start semi bluffing
          if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
              random_number = random.randint(1, 100)
              if random_number >= 10: #more than likely the bot will bet on the river this is a great spot to bet
                post_river_decision = "bet"
              else:
                post_river_decision = "check"

          #if opponent went check-check on turn and river its likely the bot flopped its pair on the turn or river-- meaning its a strong time to bet
          elif hand_ranking[0] == 2:
            pair_strength = hand_ranking[5]
            if pair_strength == 1:
              post_river_decision = "bet"
            elif pair_strength == 2:
              if random.randint(1, 100) > 25:
                post_river_decision = "bet" #need to be careful if the opponent is slow playing top pair on the flop
              else:
                post_river_decision = "check"
            else:
              if random.randint(1, 100) > 35: #can potentially be the best hand -- but also can be getting trapped, hopefully opponent folds to this bet
                post_river_decision = "bet"
              else:
                post_river_decision = "check"
          #if the hand ranking is greater then one pair -- can assume the bot flopped an amazing hand and all should play similarly
          else:
            post_river_decision = "bet" #good time to start building a pot with strong hands


          return post_river_decision, hand_ranking[0]

        #if the opponent bet at each street they are most likely strong -- probably a good idea to only bet strong hands -- this is the strongest line the opponent can possibly take
        elif opponent_post_flop_decision == "bet" and opponent_post_turn_decision == "bet" and opponent_post_river_decision == "bet":
           #if the bot made it this long with air -- it might be a good idea to start semi bluffing
          if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
            post_river_decision = "fold" #need to be folding air here

          #if opponent went check-check on turn and river its likely the bot flopped its pair on the turn or river-- meaning its a strong time to bet
          elif hand_ranking[0] == 2:
            pair_strength = hand_ranking[5]
            if pair_strength == 1:
              if random.randint(1, 100) > 15:
                post_river_decision = "call"
              else:
                post_river_decision = "raise"
            elif pair_strength == 2:
              if random.randint(1, 100) > 40:
                post_river_decision = "call" #need to be careful if the opponent is slow playing top pair on the flop
              else:
                post_river_decision = "fold"
            else:
              if random.randint(1, 100) > 80: #can potentially be the best hand -- but also can be getting trapped, hopefully opponent folds to this bet
                post_river_decision = "call"
              else:
                post_river_decision = "fold"
          #if the hand ranking is greater then one pair -- can assume the bot flopped an amazing hand and all should play similarly
          else:
            random_number = random.randint(1, 100)
            if random_number >= 50:
              post_river_decision = "raise" #good time to start building a pot with strong hands
            else:
              post_river_decision = "call"



          return post_river_decision, hand_ranking[0]


        elif opponent_post_flop_decision == "check" and opponent_post_turn_decision == "check" and opponent_post_river_decision == "bet":
          #if the bot made it this long with air -- it might be a good idea to start semi bluffing
          if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
            post_river_decision = "fold"

          #bot has a pair on the river after turn and the opponent checks
          elif hand_ranking[0] == 2:
            pair_strength = hand_ranking[5]
            if pair_strength == 1:
              if random.randint(1, 100) > 50:
                post_river_decision = "call"
              else:
                post_river_decision = "raise"
            elif pair_strength == 2:
              if random.randint(1, 100) > 25:
                post_river_decision = "call" #need to be careful if the opponent is slow playing top pair on the flop
              else:
                post_river_decision = "fold"
            else:
              if random.randint(1, 100) > 55: #can potentially be the best hand -- but also can be getting trapped, hopefully opponent folds to this bet
                post_river_decision = "fold"
              else:
                post_river_decision = "raise"
          #if the hand ranking is greater then one pair -- can assume the bot flopped an amazing hand and all should play similarly
          else:
            if random.randint(1, 100) > 50:
              post_river_decision = "bet" #good time to start building a pot with strong hands
            else:
              post_river_decision = "raise"


          return post_river_decision, hand_ranking[0]

        elif opponent_post_flop_decision == "check" and opponent_post_turn_decision == "bet" and opponent_post_river_decision == "bet":
        #bot has complete air and should fold
          if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
            post_river_decision = "fold" #need to be folding air here

          #if opponent went check-check on turn and river its likely the bot flopped its pair on the turn or river-- meaning its a strong time to bet
          elif hand_ranking[0] == 2:
            pair_strength = hand_ranking[5]
            if pair_strength == 1:
              if random.randint(1, 100) > 15:
                post_river_decision = "call"
              else:
                post_river_decision = "raise"
            elif pair_strength == 2:
              if random.randint(1, 100) > 40:
                post_river_decision = "call" #need to be careful if the opponent is slow playing top pair on the flop
              else:
                post_river_decision = "fold"
            else:
              if random.randint(1, 100) > 80: #can potentially be the best hand -- but also can be getting trapped, hopefully opponent folds to this bet
                post_river_decision = "call"
              else:
                post_river_decision = "fold"
          #if the hand ranking is greater then one pair -- can assume the bot flopped an amazing hand and all should play similarly
          else:
            random_number = random.randint(1, 100)
            if random_number >= 50:
              post_river_decision = "raise" #good time to start building a pot with strong hands
            else:
              post_river_decision = "call"



          return post_river_decision, hand_ranking[0]


        #shows weakness after we called the flop
        elif opponent_post_flop_decision == "bet" and opponent_post_turn_decision == "check" and opponent_post_river_decision == "check":
          #if the bot made it this long with air -- it might be a good idea to start semi bluffing
          if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
              random_number = random.randint(1, 100)
              if random_number >= 10: #more than likely the bot will bet on the river this is a great spot to bet
                post_river_decision = "bet"
              else:
                post_river_decision = "check"

          #if opponent went check-check on turn and river its likely the bot flopped its pair on the turn or river-- meaning its a strong time to bet
          elif hand_ranking[0] == 2:
            pair_strength = hand_ranking[5]
            if pair_strength == 1:
              post_river_decision = "bet"
            elif pair_strength == 2:
              if random.randint(1, 100) > 25:
                post_river_decision = "bet" #need to be careful if the opponent is slow playing top pair on the flop
              else:
                post_river_decision = "check"
            else:
              if random.randint(1, 100) > 35: #can potentially be the best hand -- but also can be getting trapped, hopefully opponent folds to this bet
                post_river_decision = "bet"
              else:
                post_river_decision = "check"
          #if the hand ranking is greater then one pair -- can assume the bot flopped an amazing hand and all should play similarly
          else:
            post_river_decision = "bet" #good time to start building a pot with strong hands


          return post_river_decision, hand_ranking[0]

        #strong line played similarly to bet-bet-bet, last check likely just baiting a bet
        elif opponent_post_flop_decision == "bet" and opponent_post_turn_decision == "bet" and opponent_post_river_decision == "check":
           #if the bot made it this long with air -- it might be a good idea to start semi bluffing
          if hand_ranking[0] == 1 and flush_draw == False and straight_draw == False:
            post_river_decision = "fold" #need to be folding air here

          #if opponent went check-check on turn and river its likely the bot flopped its pair on the turn or river-- meaning its a strong time to bet
          elif hand_ranking[0] == 2:
            pair_strength = hand_ranking[5]
            if pair_strength == 1:
              if random.randint(1, 100) > 15:
                post_river_decision = "call"
              else:
                post_river_decision = "raise"
            elif pair_strength == 2:
              if random.randint(1, 100) > 40:
                post_river_decision = "call" #need to be careful if the opponent is slow playing top pair on the flop
              else:
                post_river_decision = "fold"
            else:
              if random.randint(1, 100) > 80: #can potentially be the best hand -- but also can be getting trapped, hopefully opponent folds to this bet
                post_river_decision = "call"
              else:
                post_river_decision = "fold"
          #if the hand ranking is greater then one pair -- can assume the bot flopped an amazing hand and all should play similarly
          else:
            random_number = random.randint(1, 100)
            if random_number >= 50:
              post_river_decision = "raise" #good time to start building a pot with strong hands
            else:
              post_river_decision = "call"



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
    This function is for bot-b to respond to a re-raise at the river
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
        if random_number > 50:
          post_river_decision = "call"
        else:
          post_river_decision = "fold"
      elif pair_strength == 2:
        random_number = random.randint(1, 100)
        if random_number >= 85: #
          post_river_decision = "call"
        else:
          post_river_decision = "fold"

    #low pair decision making
      else:
        if random.randint(1, 100) > 10: #low pair almost certianly losing
          post_river_decision = "fold"
    #if the hand ranking is greater then one pair -- logical to defend the hand in most cases with occasional re-raises
    else:
      post_river_decision = "call"

      return post_river_decision, hand_ranking[0]


