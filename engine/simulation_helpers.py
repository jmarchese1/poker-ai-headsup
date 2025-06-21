import random


def get_hand_strength(card1, card2):
    """
    Given two cards (rank, suit), returns the preflop strength rating (0-10).
    """

    #dictionary of hand strength ranks
    HAND_STRENGTH_RANKS = {
        # Tier 10: Premium
        'AA': 10, 'KK': 10, 'QQ': 10, 'JJ': 10, 'AKs': 10, 'AKo': 10,
        # Tier 9: Very Strong
        'TT': 9, 'AQs': 9, 'AJs': 9, 'KQs': 9, 'AQo': 9, 'KJs': 9,
        # Tier 8: Strong Playable
        '99': 8, 'ATs': 8, 'AJo': 8, 'KQo': 8, 'QJs': 8, 'JTs': 8, 'KTs': 8,
        # Tier 7: Mid Pairs, Good Suited
        '88': 7, '77': 7, '66': 7, 'A9s': 7, 'QTs': 7, 'J9s': 7, 'T9s': 7, '98s': 7, 'AJo': 7, 'KJo': 7,
        # Tier 6: Low Pairs, Suited Connectors
        '55': 6, '44': 6, '33': 6, '22': 6, 'A8s': 6, 'A7s': 6, 'KTo': 6, 'QJo': 6, '87s': 6, '76s': 6, '65s': 6,
        # Tier 5: Marginal
        'A6s': 5, 'A5s': 5, 'A4s': 5, 'K9s': 5, 'Q9s': 5, 'J8s': 5, 'T8s': 5, 'KJo': 5,
        # Tier 4: Speculative
        'A3s': 4, 'A2s': 4, '54s': 4, '43s': 4, 'K8s': 4, 'Q8s': 4, 'J7s': 4,
        # Tier 3: Weak offsuit broadways
        'ATo': 3, 'KTo': 3, 'QTo': 3, 'JTo': 3, 'A9o': 3, 'K9o': 3,
        # Tier 2: weak playable hands
        'T9o': 2, '98o': 2, '87o': 2, '76o': 2,
        ##everythhing else is tier 0
    }

    rank1, suit1 = card1
    rank2, suit2 = card2

    # Normalize the hand key (e.g., AKs, QJo, 77)
    suited = suit1 == suit2
    ranks = sorted([rank1, rank2], reverse=True)

    if rank1 == rank2:
        key = f"{ranks[0]}{ranks[1]}"  # e.g., 'QQ'
    else:
        key = f"{ranks[0]}{ranks[1]}{'s' if suited else 'o'}"  # e.g., 'AKs', 'KQo'

    return HAND_STRENGTH_RANKS.get(key, 0)  # 0 = lowest strength

def setup_deck_and_deal(players):
    """
    Generates deck of cards numerically encoded, shuffles the deck of cards, deals two cards to each player at the table,
    returns the remaining cards in the deck.
    params:
    players - list of players to be delt cards.
    """
    #generate deck of cards with numeric for picuture cards and aces and suits numerically encoded
    deck = [(rank, suit) for rank in range(2 , 15) for suit in range(1, 5)]

    #shuffle the cards out of the default order
    random.shuffle(deck)

    #deal the cards to players at the table 
    for player in players:
        player.hand = [deck.pop(), deck.pop()]

    return deck #store to a variable called remaining_deck in the gameflow for the flop, turn and river to be unique cards 

def all_contributions_equal(positions, folded):
     """
     checks if all the players contributions at a street are equal. 
     parameters:
     positions: The dictionary of players positions and thier names
     folded: list of players that folded out of the hand 
     """
     contributions = [player.contribution for pos, player in positions.items() if pos not in folded]
     return len(set(contributions)) == 1 #checks if all the player contributions are the same or not 

def prettify_hand(hand):
    """
    Takes a players numerically encoded tuple of a hand and displays the card title (jack, queen, king, ace) and symbol for the suit
    (spade, club, diamond, heart)
    params:
    hand - provide player.hand to be converted to more readable format 
    """
    rank_map = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
    suit_map = {1: '♠️', 2: '♥️', 3: '♦️', 4: '♣️'}    

    pretty_cards = []
    for card in hand:
        rank, suit = card
        rank_str = str(rank) if rank <= 10 else rank_map[rank]
        suit_str = suit_map[suit]
        pretty_cards.append(f"{rank_str}{suit_str}")
    
    return pretty_cards


# ranking possible postflop hands 
from collections import Counter
import itertools

def highest_straight(ranks):
    """Determine straight and the strength of the high card"""
    uniq = sorted(set(ranks))
    if 14 in uniq:                       # Ace can play low
        uniq.append(1)
    for i in range(len(uniq) - 4):
        window = uniq[i:i+5]
        if window == list(range(window[0], window[0] + 5)):
            return window[-1]            # high card of straight
    return None

def highest_straight_flush(cards):
    """
    determine straight flush and its high card
    """
    by_suit = {}
    for r, s in cards:
        by_suit.setdefault(s, []).append(r)

    best = None          # (high_rank, suit)
    for s, suited in by_suit.items():
        if len(suited) < 5:
            continue
        hi = highest_straight(suited)
        if hi and (best is None or hi > best[0]):
            best = (hi, s)
    return best          # None or (high, suit)

def evaluate(full_hand):
    """
    Evaluate a 5-7 card hand and return its category and key for tie-breaking.
    full_hand : list of 5 - 7 (rank, suit) tuples
    returns   : (category 10–1, key_tuple) for tie-breaking
    """
    ranks = [r for r, _ in full_hand]
    rc = Counter(ranks)

    # 1) straight / royal flush
    sf = highest_straight_flush(full_hand)
    if sf:
        high = sf[0]
        if high == 14:                             # Royal
            return 10, ()
        return 9, (high,)

    # 2) quads
    if 4 in rc.values():
        quad  = max(r for r, c in rc.items() if c == 4)
        kick  = max(r for r in ranks if r != quad)
        return 8, (quad, kick)
    
    # 3) full house
    trips = [r for r, c in rc.items() if c == 3]
    pairs = [r for r, c in rc.items() if c >= 2 and r not in trips]

    if trips:
        top_trip = max(trips)
        # check for another pair from pairs or another trip to act as pair
        other_options = pairs + [t for t in trips if t != top_trip]
        
        if other_options:
            top_pair = max(other_options)
        else:
            # fallback if no other valid pair — not a full house
            top_pair = None

        if top_pair is not None:
            return 7, (top_trip, top_pair)

    # 4) flush
    suit_group = {}
    for r, s in full_hand:
        suit_group.setdefault(s, []).append(r)
    for ranks_of_suit in suit_group.values():
        if len(ranks_of_suit) >= 5:
            top5 = tuple(sorted(ranks_of_suit, reverse=True)[:5])
            return 6, top5

    # 5) straight
    hi = highest_straight(ranks)
    if hi:
        return 5, (hi,)

    # 6) trips
    if trips:
        t   = max(trips)
        k1, k2 = sorted((r for r in ranks if r != t), reverse=True)[:2]
        return 4, (t, k1, k2)

    # 7) two-pair
    if len(pairs) >= 2:
        p_hi, p_lo = sorted(pairs, reverse=True)[:2]
        kicker = max(r for r in ranks if r not in (p_hi, p_lo))
        return 3, (p_hi, p_lo, kicker)

    # 8) one pair
    if len(pairs) == 1:
        p  = pairs[0]
        k1, k2, k3 = sorted((r for r in ranks if r != p), reverse=True)[:3]
        return 2, (p, k1, k2, k3)

    # 9) high card
    top5 = tuple(sorted(ranks, reverse=True)[:5])
    return 1, top5

def hand_score(category, key):
    """
    Compress (category, key) into a single float so every distinct hand
    has a unique, sortable value.
    """
    scale   = 0.05
    dec     = 0.0
    for k in key:
        dec   += k * scale
        scale /= 100           # plenty of headroom for next kicker
    return category + dec

def evaluate_score(player_hand, board):
    """
    Gets the hand score for every possible hand given the board and ranks the player's hand among them.
    this will give the percentile of the player's hand against all possible hands.
    params:
        player_hand : list of 2 (rank, suit) tuples
        board : list of 3-5 (rank, suit) tuples
    """
    deck = [(rank, suit) for rank in range(2, 15) for suit in range(1, 5)]
    available_cards = [card for card in deck if card not in board]
    all_possible_hands = list(itertools.combinations(available_cards, 2))
    hand_scores = []
    for hand in all_possible_hands:
        full_hand = list(hand) + board
        cat, key = evaluate(full_hand)
        hand_value = hand_score(cat, key)
        hand_scores.append(hand_value)
    hand_standings = sorted(hand_scores, reverse=True)
    player_full_hand = player_hand + board
    player_cat, player_key = evaluate(player_full_hand)
    player_score = hand_score(player_cat, player_key)
    hand_rank = hand_standings.index(player_score) + 1
    return hand_rank






