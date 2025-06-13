import random


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
        rank_str = str(rank) if rank <= 10 else rank[rank_map]
        suit_str = suit_map[suit]
        pretty_cards.append(f"{rank_str}{suit_str}")
    
    return pretty_cards
