import random


def get_hand_strength(card1, card2):
    """
    Given two cards (rank, suit), returns the preflop strength rating (0-10).
    """
    HAND_STRENGTH_RANKS = {
        'AA': 10, 'KK': 10, 'QQ': 10, 'JJ': 10, 'AKs': 10, 'AKo': 10,
        'TT': 9, 'AQs': 9, 'AJs': 9, 'KQs': 9, 'AQo': 9,
        '99': 8, 'ATs': 8, 'KJs': 8, 'QJs': 8, 'KQo': 8, 'AJo': 8,
        '88': 7, '77': 7, '66': 7, '55': 7, '44': 7, '33': 7, '22': 7,
        'JTs': 7, 'T9s': 7, '98s': 7, '87s': 7, '76s': 7, '65s': 7, '54s': 7,
        'KJo': 6, 'QJo': 6, 'A9s': 6, 'A8s': 6, 'A7s': 6, 'KTs': 6, 'QTs': 6, 'J9s': 6,
        # Default for all others will be 0
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
    suit_map = {1: '♠', 2: '♥', 3: '♦', 4: '♣'}

    pretty_cards = []
    for card in hand:
        rank, suit = card
        rank_str = str(rank) if rank <= 10 else rank_map[rank]
        suit_str = suit_map[suit]
        pretty_cards.append(f"{rank_str}{suit_str}")
    
    return pretty_cards
