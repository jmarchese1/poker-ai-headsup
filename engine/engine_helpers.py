#goal for today is to update evaluate hand functions and display card functions to work without global variables.

#evaluate hand should be able to notice flush draws and straight draws to incorporate semi bluffing into the model

#it would be ineresting to see out of all 169 possible hands where the users hand ranks postflop

#this is a file that containts the essential helper functions from the core_engine.ipynb file
import random
import pandas as pd
import itertools

#column names to add to the dataframe below
columns = [
    "hand_id",
    "user_hand",
    "com_hand",
    "user_chips",
    "com_chips",
    "winnings",
    "winner",
    "preflop_user_hand_strength",
    "preflop_com_hand_strength",
    "preflop_user_decision",
    "preflop_user_raise_amount",
    "preflop_computer_decision",
    "preflop_computer_raise_amount",
    "preflop_user_decision_2",
    "preflop_user_raise_amount_2",
    "preflop_computer_decision_2",
    "flop_cards",
    "postflop_user_hand_strength",
    "postflop_user_decsision",
    "postflop_user_bet",
    "postflop_user_raise_amount",
    "postflop_com_hand_strength",
    "postflop_computer_decision",
    "postflop_computer_bet",
    "postflop_computer_decision_2",
    "postflop_computer_re_raise_amount",
    "postflop_user_decision_2",
    "postflop_potsize",
    "turn_card",
    "turn_user_hand_strength",
    "turn_user_decision",
    "turn_user_bet",
    "turn_user_raise_amount",
    "turn_com_hand_strength",
    "turn_computer_decision",
    "turn_computer_bet",
    "turn_computer_decision_2",
    "turn_computer_re_raise_amount",
    "turn_user_decision_2",
    "post_turn_potsize",
    "river_card",
    "river_user_hand_strength",
    "river_user_decision",
    "river_user_bet",
    "river_user_raise_amount",
    "river_com_hand_strength",
    "river_computer_decision",
    "river_computer_bet",
    "river_computer_decision_2",
    "river_computer_re_raise_amount",
    "river_user_decision_2"
]

# Create the DataFrame with these columns
game_results_df = pd.DataFrame(columns=columns)

##################################################
#Creating the poker deck and maintenence functions
##################################################

#creating the poker deck
def create_deck():
  """
  this function creates a deck of cards and shuffles them
  """
  suits = ["hearts", "diamonds", "clubs", "spades"]
  ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace"]
  cards = [(rank, suit) for suit in suits for rank in ranks]
  random.shuffle(cards)
  return cards

def clear_board(board):
  """this function clears the board of cards"""
  board = []
  return board

def reset_stack(player_1, player_2, starting_stack):
  """
  this function resets the players chips to an equal starting stack of the users choice.
  """
  player_1.chips = starting_stack
  player_2.chips = starting_stack
  return player_1, player_2

def clear_dataframe(dataframe):
  dataframe = pd.DataFrame(columns=columns)
  return dataframe

def reset_game(player_1, player_2, board, dataframe):
  clear_hand(player_1, player_2)
  board = clear_board(board)
  reset_stack(player_1, player_2, 100000)
  dataframe = clear_dataframe(dataframe)

def deal_cards(cards, player_1, player_2):
  """
  this function deals cards to the players
  """
  for i in range(2):
    player_1.hand.append(cards.pop())
    player_2.hand.append(cards.pop())

def clear_hand(player_1 , player_2):
  """
  this function clears the hand of the players
  """
  player_1.hand = []
  player_2.hand = []

##############################################
#functions to display each street on the board
##############################################

def flop(cards, board):
  """
  Funtion to take three random cards from the deck and place them on the board.
  """
  for i in range(3):
    random_card = random.choice(cards)
    cards.remove(random_card)
    board.append(random_card)
  print(board)

def turn(cards, board):
  """
  This function takes a random card from the deck and places it on the board.
  """
  random_card = random.choice(cards)
  cards.remove(random_card)
  board.append(random_card)
  print(f"The turn is the {random_card} the board shows {board}")

def river(cards, board):
  """
  This function takes a random card from the deck and places it on the board.
  """
  random_card = random.choice(cards)
  cards.remove(random_card)
  board.append(random_card)
  print(f"The river is the {random_card} the board shows {board}")


###############################################
# Showdown funcions to determine the winner
###############################################

#go though this to try to add functionality for flush and straight draws

#get seven card hand
def get_seven_card_hand(player, board):
    return [card for card in player.hand + board]

def evaluate_hand(hand, board):
    """
    returns a tuple describing the best made five-card hand ranking 
    (9 = straight flush, 8 = four of a kind, …, 1 = high card).
    Expects `hand` to be a list of (rank_str, suit_str), e.g. [('10','hearts'), ('ace','spades'), ...].
    """
    rank_map = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
                '7': 7, '8': 8, '9': 9, '10': 10,
                'jack': 11, 'queen': 12, 'king': 13, 'ace': 14}

    # Convert to numeric ranks and sort descending
    ranks = sorted([rank_map[card[0]] for card in hand], reverse=True)
    suits = [card[1] for card in hand]
    rank_counts = {r: ranks.count(r) for r in set(ranks)}
    board_ranks = sorted([rank_map[card[0]] for card in board], reverse = True)

    # Flush check
    is_flush = len(set(suits)) == 1

    # Straight check (accounting for wheel A-2-3-4-5)
    ranks_asc = sorted(set(ranks))
    is_straight = False
    if len(ranks_asc) >= 5:
        # check consecutive sequences of length 5
        for i in range(len(ranks_asc) - 4):
            window = ranks_asc[i:i + 5]
            if window == list(range(window[0], window[0] + 5)):
                is_straight = True
                top_of_straight = window[-1]
                break
        # check wheel (A-2-3-4-5)
        if not is_straight and set([14, 2, 3, 4, 5]).issubset(ranks_asc):
            is_straight = True
            top_of_straight = 5

    # Now the “made hand” categories:
    # 9 = straight flush, 8 = quads, 7 = full house, 6 = flush,
    # 5 = straight, 4 = three of a kind, 3 = two pair, 2 = one pair, 1 = high card
    if is_straight and is_flush:
        return (9, top_of_straight)
    elif 4 in rank_counts.values():
        four_rank = max(r for r, c in rank_counts.items() if c == 4)
        kicker = max(r for r in ranks if r != four_rank)
        return (8, four_rank, kicker)
    elif sorted(rank_counts.values()) == [2, 3]:
        three_rank = max(r for r, c in rank_counts.items() if c == 3)
        pair_rank = max(r for r, c in rank_counts.items() if c == 2)
        return (7, three_rank, pair_rank)
    elif is_flush:
        return (6, *ranks[:5])
    elif is_straight:
        return (5, top_of_straight)
    elif 3 in rank_counts.values():
        three_rank = max(r for r, c in rank_counts.items() if c == 3)
        kickers = [r for r in ranks if r != three_rank]
        return (4, three_rank, kickers[0], kickers[1])
    elif list(rank_counts.values()).count(2) == 2:
        pair_ranks = sorted([r for r, c in rank_counts.items() if c == 2], reverse=True)
        kicker = max(r for r in ranks if r not in pair_ranks)
        return (3, pair_ranks[0], pair_ranks[1], kicker)
    elif 2 in rank_counts.values():
        pair_rank = max(r for r, c in rank_counts.items() if c == 2)
        kickers = [r for r in ranks if r != pair_rank]
        highest_board_rank = board_ranks[0]
        second_board_rank = board_ranks[1]
        if pair_rank > highest_board_rank:
            return (2, pair_rank, highest_board_rank, second_board_rank, kickers[0], 4) #disguised top pair (poket pair)
        elif pair_rank == highest_board_rank:
           return (2, pair_rank, second_board_rank, kickers[0], kickers[1], 1) #pair strength is the last one
        elif pair_rank == second_board_rank:
            return (2, second_board_rank, highest_board_rank, kickers[0], kickers[1], 2) #pair strength is the last one
        else:
            return (2, pair_rank, highest_board_rank, second_board_rank, kickers[0], 3) #means the pair is not first or second on the board
    else:
        return (1, *ranks[:5])

  



def has_flush_draw(hole_cards, board_cards):
    """
    Returns True if there is exactly a four‐card flush draw (needing one more suit to complete),
    AND at least one of those four cards is in hole_cards (i.e., board alone does not already
    contain those four cards).
    Each card is (rank_str, suit_str). 
    """
    # Count suits separately
    from collections import Counter

    # Count suit occurrences on board and in hole
    board_suits = [c[1] for c in board_cards]
    hole_suits  = [c[1] for c in hole_cards]

    board_count = Counter(board_suits)
    hole_count  = Counter(hole_suits)

    # For each suit, see if (board + hole) gives exactly 4 of that suit,
    # and ensure board alone has <= 3 of that suit (so hole contributes at least 1)
    for suit in ['clubs', 'diamonds', 'hearts', 'spades']:
        total_suit = board_count[suit] + hole_count[suit]
        if total_suit == 4 and board_count[suit] < 4 and hole_count[suit] > 0:
            return True

    return False



def has_straight_draw(hole_cards, board_cards):
    """
    Returns True if there is exactly a four‐card straight draw (needing one more rank to complete),
    AND at least one card of that 4‐card sequence is in hole_cards (board alone does not already
    have all four).
    We will look for any consecutive run of 4 ranks among the union of hole+board,
    but check that the board alone does not already have all 4.
    """
    # Convert ranks to integers
    rank_map = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
                '7': 7, '8': 8, '9': 9, '10': 10,
                'jack': 11, 'queen': 12, 'king': 13, 'ace': 14}

    # Helper to get a set of integer ranks from a card list
    def ranks_set(cards):
        return set(rank_map[c[0]] for c in cards)

    board_ranks = ranks_set(board_cards)
    hole_ranks  = ranks_set(hole_cards)
    all_ranks   = sorted(board_ranks.union(hole_ranks))

    # For wheel A‐2‐3‐4‐5 detection, add “1” if Ace is present
    if 14 in all_ranks:
        all_ranks.append(1)
    all_ranks = sorted(set(all_ranks))

    # Look for ANY length-4 consecutive run within the combined ranks
    # but ensure the board alone does not already have all 4 of them.
    # And at least one of the ranks of that run must come from hole_ranks.
    n = len(all_ranks)
    for i in range(n):
        # Try building a run of length 4 starting at all_ranks[i]
        run_start = all_ranks[i]
        run = {run_start + offset for offset in range(4)}
        if run.issubset(all_ranks):
            # Now check: how many of those run ranks are on board alone?
            board_in_run = run.intersection(board_ranks)
            hole_in_run  = run.intersection(hole_ranks)
            if len(board_in_run) < 4 and len(board_in_run) + len(hole_in_run) == 4 and len(hole_in_run) > 0:
                # board has <4, but total (board+hole) = 4, and hole contributed at least 1
                return True

    return False



def best_hand(seven_cards, board):
    all_combos = itertools.combinations(seven_cards, 5)
    return max(all_combos, key=lambda combo: evaluate_hand(combo, board = board))

def determine_winner(players, board, pot, row_idx, dataframe):
    results = []
    for player in players: #already a list at the top of gameflow
        seven = get_seven_card_hand(player, board = board)
        best = best_hand(seven_cards = seven, board = board)
        hand_rank = evaluate_hand(hand = best, board = board)
        results.append((hand_rank, player.name, best))

    results.sort(reverse=True)  # higher ranks first
    winner = results[0]
    print(f"{winner[1]} wins with hand {winner[2]} ranked {winner[0]}")

    if winner[1] == "Bot B":
      players[1].chips += pot
      dataframe.at[row_idx, "winnings"] = pot
      dataframe.at[row_idx, "winner"] = players[1].name

    else: #Bot A wins
      players[0].chips += pot
      dataframe.at[row_idx, "winnings"] = pot
      dataframe.at[row_idx, "winner"] = players[0].name

     
#########################################
#Preflop hand strength evaluation functions
##########################################


#important functionality to get the hand strength of each player using a preflop hand strength chart

def preflop_hand_strength(card1, card2):


  preflop_strengths = {
    # Pocket pairs
    'AA': 1.000,
    'KK': 0.961,
    'QQ': 0.929,
    'JJ': 0.902,
    'TT': 0.878,
    '99': 0.854,
    '88': 0.828,
    '77': 0.800,
    '66': 0.771,
    '55': 0.742,
    '44': 0.713,
    '33': 0.683,
    '22': 0.653,

    # Suited Broadways
    'AKs': 0.820,
    'AQs': 0.787,
    'AJs': 0.753,
    'ATs': 0.719,
    'KQs': 0.727,
    'KJs': 0.694,
    'KTs': 0.660,
    'QJs': 0.679,
    'QTs': 0.646,
    'JTs': 0.613,

    # Offsuit Broadways
    'AKo': 0.797,
    'AQo': 0.765,
    'AJo': 0.731,
    'ATo': 0.697,
    'KQo': 0.706,
    'KJo': 0.672,
    'KTo': 0.639,
    'QJo': 0.657,
    'QTo': 0.623,
    'JTo': 0.590,

    # Suited Aces (non‐broadway)
    'A9s': 0.685,
    'A8s': 0.651,
    'A7s': 0.616,
    'A6s': 0.581,
    'A5s': 0.547,
    'A4s': 0.512,
    'A3s': 0.478,
    'A2s': 0.443,

    # Offsuit Aces (non‐broadway)
    'A9o': 0.660,
    'A8o': 0.626,
    'A7o': 0.591,
    'A6o': 0.556,
    'A5o': 0.522,
    'A4o': 0.487,
    'A3o': 0.453,
    'A2o': 0.418,

    # Suited Connectors and One‐Gappers
    'T9s': 0.632,
    '98s': 0.599,
    '87s': 0.564,
    '76s': 0.529,
    '65s': 0.494,
    '54s': 0.460,
    '43s': 0.425,
    '32s': 0.390,
    'J9s': 0.621,
    'K9s': 0.648,
    'Q9s': 0.608,
    'J8s': 0.587,
    'T8s': 0.555,
    '97s': 0.520,
    '86s': 0.486,
    '75s': 0.451,
    '64s': 0.417,
    '53s': 0.382,
    '42s': 0.348,

    # Offsuit Connectors and One‐Gappers
    'T9o': 0.607,
    '98o': 0.574,
    '87o': 0.539,
    '76o': 0.504,
    '65o': 0.469,
    '54o': 0.435,
    '43o': 0.400,
    '32o': 0.365,
    'J9o': 0.595,
    'K9o': 0.622,
    'Q9o': 0.582,
    'J8o': 0.560,
    'T8o': 0.528,
    '97o': 0.493,
    '86o': 0.459,
    '75o': 0.424,
    '64o': 0.389,
    '53o': 0.354,
    '42o': 0.320,

    # Suited Gappers 2 (two‐gappers)
    'J8s': 0.587,
    'T8s': 0.555,
    '97s': 0.520,
    '86s': 0.486,
    '75s': 0.451,
    '64s': 0.417,
    '53s': 0.382,
    '42s': 0.348,

    # Offsuit Gappers 2 (two‐gappers)
    'J8o': 0.560,
    'T8o': 0.528,
    '97o': 0.493,
    '86o': 0.459,
    '75o': 0.424,
    '64o': 0.389,
    '53o': 0.354,
    '42o': 0.320,

    # Suited Gappers 3
    'J7s': 0.514,
    'T7s': 0.480,
    '96s': 0.444,
    '85s': 0.410,
    '74s': 0.375,
    '63s': 0.340,
    '52s': 0.306,

    # Offsuit Gappers 3
    'J7o': 0.488,
    'T7o': 0.453,
    '96o': 0.417,
    '85o': 0.383,
    '74o': 0.348,
    '63o': 0.314,
    '52o': 0.280,

    # Suited 4‐gappers
    'J6s': 0.328,
    'T6s': 0.293,
    '95s': 0.259,
    '84s': 0.225,
    '73s': 0.191,
    '62s': 0.157,

    # Offsuit 4‐gappers
    'J6o': 0.301,
    'T6o': 0.266,
    '95o': 0.232,
    '84o': 0.197,
    '73o': 0.163,
    '62o': 0.129,

    # Suited 5‐gappers (example values)
    'J5s': 0.124,
    'T5s': 0.089,
    '94s': 0.054,
    '83s': 0.019,

    # Offsuit 5‐gappers (example values)
    'J5o': 0.098,
    'T5o': 0.064,
    '94o': 0.030,
    '83o': 0.010,

    # Remaining very weak hands
    '72o': 0.036,
    '62o': 0.031,
    '52o': 0.026,
    '43o': 0.022,
    '32o': 0.018
}



  rank_map = {
    '2': '2', '3': '3', '4': '4', '5': '5', '6': '6',
    '7': '7', '8': '8', '9': '9', '10': 'T',
    'jack': 'J', 'queen': 'Q', 'king': 'K', 'ace': 'A'
}

  rank1_raw, suit1 = card1
  rank2_raw, suit2 = card2

  rank1 = rank_map.get(rank1_raw.lower(), '?')
  rank2 = rank_map.get(rank2_raw.lower(), '?')

  if '?' in (rank1, rank2):
    raise ValueError(f"Invalid rank in card: {card1}, {card2}")

  # Pair
  if rank1 == rank2:
      key = rank1 * 2
  else:
      suited = suit1 == suit2
      # Sort ranks to match key ordering (e.g., AQ not QA)
      sorted_ranks = sorted([rank1, rank2], key=lambda r: '23456789TJQKA'.index(r), reverse=True)
      key = ''.join(sorted_ranks) + ('s' if suited else 'o')

  return preflop_strengths.get(key, 0.40)  # Default strength if not found

#heres the functionality for each steet besides preflop:
def get_hand_strength_at_street(player, board):
    """
    Returns the hand strength rank tuple at the current street
    based on the board state (flop, turn, or river).
    """
    current_hand = get_seven_card_hand(player, board)
    best = best_hand(current_hand)
    return evaluate_hand(best)

#converting the tuple score to a rank 1-10
def score_hand_strength(rank_tuple):
    """
    Converts a tuple like (6, 14, 13, 11, 9, 7) into a float score.
    Higher categories (9=straight flush, 1=high card) dominate.
    Kickers provide decimal detail.
    """
    category = rank_tuple[0]
    kickers = rank_tuple[1:]

    # Normalize kicker contribution (base-15 ensures no overlap across categories)
    decimal = 0
    for i, kicker in enumerate(kickers):
        decimal += kicker / (15 ** (i + 1))

    return round(category + decimal, 4)


