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

#added path to sys.path[0] -- allows for importing custom functions
if root not in sys.path:
    sys.path.insert(0, root)

#importing custom packages
from engine.simulation_helpers import setup_deck_and_deal, prettify_hand, get_hand_strength, all_contributions_equal, highest_straight, highest_straight_flush, evaluate, hand_score, evaluate_score
from bots.default_bot import PokerBot

#confiuring pandas display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)


#-----------------------------------------------------------------#
#                       Setting up the game                       #
#-----------------------------------------------------------------#

#create bots | Each one will have a different play-style
#atlas = bot(atlas, 1000, ... )
#blair = bot(blair, 1000, ... )
#cruz = bot(cruz, 1000, ... )
# ...


#creating a list of bots to have different play styles based on the agression level
Atlas = PokerBot(name = "Atlas", aggression_level = 40)
Blair = PokerBot(name = "Blair", aggression_level = 50)
Cruz = PokerBot(name = "Cruz", aggression_level = 60)
Drew = PokerBot(name = "Drew", aggression_level = 70)
Ember = PokerBot(name = "Ember", aggression_level = 80)
Flint = PokerBot(name = "Flint", aggression_level = 90)
Gio = PokerBot(name = "Gio", aggression_level = 100)

#creating a list of players to be used in the game
players = [Atlas, Blair, Cruz, Drew, Ember, Flint, Gio]         

#creating a dataframe to track decision making and results
results_df = pd.DataFrame(columns = [])
hand_counter = 1 #track the number of hands played

def init_player_logs(hand_id, positions):
    logs = []
    for pos, player in positions.items():
        logs.append({
            "hand_id": hand_id,
            "player_name": player.name,
            "position": pos,
            "hole_cards": player.hand,
            "preflop_strength" : get_hand_strength(player.hand[0], player.hand[1]),
            "folded": False,
            "went_to_showdown": False,
            "final_contribution": 0,
            "chips_won": 0
    })
    return logs

def log_action(logs, player_name, street, action, amount=0):
    for log in logs:
        if log["player_name"] == player_name:
            log[f"{street}_action"] = action
            log[f"{street}_bet"] = amount
            log["final_contribution"] += amount
            if action == "fold":
                log["folded"] = True
            break

def game_flow(small_blind, big_blind):
    global players, results_df, hand_counter

    players = players[-1:] + players[:-1]  # rotate players clockwise

    #resetting the player contributions from the previous hand
    for p in players:
        p.contribution = 0   

    positions = {
        "UTG": players[0],
        "MP": players[1],
        "HJ": players[2],
        "CO": players[3],
        "BTN": players[4],
        "SB": players[5],
        "BB": players[6]
    }

    hand_id = hand_counter
    hand_counter += 1

    deck = setup_deck_and_deal(players=players)  # assigns .hole_cards to each bot

    board = []
    pot = 0
    preflop_information = []
    preflop_folded_positions = []
    raiser_position = None

    player_logs = init_player_logs(hand_id, positions)

    # Post blinds
    positions["SB"].contribution += small_blind
    positions["SB"].chips -= small_blind

    positions["BB"].contribution += big_blind
    positions["BB"].chips -= big_blind


    pot += small_blind + big_blind

    # First Preflop Loop
    for position, player in positions.items():

        num_limpers = sum(1 for d in preflop_information if d["action"] == "call")
        call_amt = big_blind - player.contribution
        action = player.decide_preflop(position, pot, call_amt)

        if action == "fold":
            preflop_folded_positions.append(position)
            log_action(player_logs, player.name, "preflop", "fold", 0)
            # Check if only one player remains
            if len(preflop_folded_positions) == len(positions) - 1:
                for remaining_pos in positions:
                    if remaining_pos not in preflop_folded_positions:
                        winner = positions[remaining_pos]
                        winner.chips += pot
                        for log in player_logs:
                            if log["player_name"] == winner.name:
                                log["chips_won"] = pot
                                print(f"{winner.name} wins the pot of {pot} chips preflop.")
                        break

        elif action == "call":
            pot += call_amt
            player.chips -= call_amt
            player.contribution += call_amt
            log_action(player_logs, player.name, "preflop", "call", call_amt if position != "SB" else call_amt + small_blind)
        elif action == "raise":
            raise_amt = ((random.choice([2, 3]) * big_blind) + (num_limpers * big_blind))
            pot += raise_amt
            player.chips -= raise_amt
            player.contribution += raise_amt
            log_action(player_logs, player.name, "preflop", "raise", raise_amt)
            raiser_position = position
            preflop_information.append({"action": "raise", "player": player.name, "position": position})
            break
        else:
            #log the action of the big blind
            log_action(player_logs, player.name, "preflop", "check", big_blind)

        if action != "raise":
            preflop_information.append({"action": action, "player": player.name, "position": position})

    # Second Preflop Loop (if a raise occurred)

    if raiser_position is not None:
        loop_counter = 0
        max_loops = 10
        preflop_information_2 = []
        while not all_contributions_equal(positions, preflop_folded_positions):
            if loop_counter >= max_loops:
                print("Max preflop loops reached, breaking to avoid infinite loop.")
                break
            loop_counter += 1
            order = list(positions.keys())
            idx = order.index(raiser_position)
            new_order = [pos for pos in (order[idx+1:] + order[:idx]) if pos not in preflop_folded_positions]
            cold_callers = []

            for pos in new_order:
                player = positions[pos]
                call_amt = positions[raiser_position].contribution - player.contribution
                action = player.decide_preflop_2(pos, pot, call_amt)

                if action == "fold":
                    preflop_folded_positions.append(pos)
                    log_action(player_logs, player.name, "preflop_2", "fold", 0)
                    # Check if only one player remains
                    if len(preflop_folded_positions) == len(positions) - 1:
                        for remaining_pos in positions:
                            if remaining_pos not in preflop_folded_positions:
                                winner = positions[remaining_pos]
                                winner.chips += pot
                                for log in player_logs:
                                    if log["player_name"] == winner.name:
                                        log["chips_won"] = pot
                                        print(f"{winner.name} wins the pot of {pot} chips preflop.")
                                break

                elif action == "call":
                    player.chips -= call_amt
                    player.contribution += call_amt
                    pot += call_amt
                    log_action(player_logs, player.name, "preflop_2", "call", call_amt)
                    cold_callers.append(player)
                elif action == "raise":
                    raise_amt = ((3 * positions[raiser_position].contribution) + (len(cold_callers) * big_blind))
                    player.chips -= raise_amt
                    player.contribution += raise_amt
                    pot += raise_amt
                    log_action(player_logs, player.name, "preflop_2", "raise", raise_amt)
                    raiser_position = pos
                    preflop_information_2.append({"action": "raise", "player": player.name, "position": pos})
                    break
                else:
                    print(f"Invalid action by {player.name} at {pos}")

                if action != "raise":
                    preflop_information_2.append({"action": action, "player": player.name, "position": pos})

# 1st postflop decisions

    postflop_raiser_position = None #also using this variable to store inital postflop better
    postflop_raise_or_bet = None
    postflop_checks = []
    #advance to the flop if the there are at least two players remaining
    if len(positions) - len(preflop_folded_positions) > 1:

        #flop -- the flop cards do not matter as much to the dataframe as the hand standings postflop
        board.extend([deck.pop(), deck.pop(), deck.pop()])
        print(f"The flop is: {prettify_hand(board)}")
        for log in player_logs:
            if not log["folded"]:
                for player in positions.values():
                    if player.name == log["player_name"]:
                        log["postflop_strength"] = evaluate_score(player.hand, board)
            else:
                log["postflop_strength"] = None

        #the first postflop decision gives bots the option to check or bet. 
        order = list(positions.keys())
        new_order = order[5:] + order[:5] #makes sure the small blind is firsts to act and the button is last 
        new_order = [pos for pos in new_order if pos not in preflop_folded_positions] #remove folded positions
        player_contributions = [player.contribution for pos, player in positions.items() if pos not in preflop_folded_positions]
        for pos in new_order:
            player_strength = evaluate_score(positions[pos].hand, board)
            player = positions[pos]
            action = player.decide_postflop(pot = pot, call_amt = max(player_contributions) - player.contribution, player_strength = player_strength)
            if action == "check":
                log_action(player_logs, player.name, "postflop", "check", 0)
                postflop_checks.append(pos)
            elif action == "bet":
                roll = random.choice([20, 33, 50])
                bet_amt = int(roll * pot / 100)
                player.chips -= bet_amt
                player.contribution += bet_amt
                pot += bet_amt
                log_action(player_logs, player.name, "postflop", "bet", bet_amt)
                postflop_raise_or_bet = "bet"
                postflop_raiser_position = pos
                break
            else:
                print(f"{player.name} made an invalid decision postflop_1")

#2nd postflop decisions

    #if there was a bet on the first postflop decision, or a raise on the second decision
    if postflop_raiser_position is not None:
        loop_counter = 0
        max_loops = 10
        while not all_contributions_equal(positions, preflop_folded_positions):
            if loop_counter >= max_loops:
                print("Max postflop loops reached, breaking to avoid infinite loop.")
                break
            loop_counter += 1
            order = list(positions.keys())
            idx = order.index(postflop_raiser_position)
            new_order = [pos for pos in (order[idx + 1:] + order[:idx]) if pos not in preflop_folded_positions]

            #looping though each player to make thier decisions in response to the raiser
            for pos in new_order:
                player = positions[pos]
                call_amt = positions[postflop_raiser_position].contribution - player.contribution 
                player_strength = evaluate_score(player.hand, board) # gets the rank of the players hand from 1200 worst to 1, the best possible hand
                action = player.decide_postflop_2(pot = pot, call_amt = call_amt, player_strength = player_strength, raise_or_bet = postflop_raise_or_bet)
                cold_callers = []

                if action == "fold":
                    preflop_folded_positions.append(pos)
                    log_action(player_logs, player.name, "postflop_2", "fold", 0)
                    # Check if only one player remains
                    if len(preflop_folded_positions) == len(positions) - 1:
                        for remaining_pos in positions:
                            if remaining_pos not in preflop_folded_positions:
                                winner = positions[remaining_pos]
                                winner.chips += pot
                                for log in player_logs:
                                    if log["player_name"] == winner.name:
                                        log["chips_won"] = pot
                                        print(f"{winner.name} wins the pot of {pot} chips postflop.")
                                break

                elif action == "call":
                    player.chips -= call_amt
                    player.contribution += call_amt
                    pot += call_amt
                    log_action(player_logs, player.name, "postflop_2", "call", call_amt)
                    cold_callers.append(player)
                elif action == "raise":
                    raise_amt = ((3 * positions[postflop_raiser_position].contribution) + (len(cold_callers) * big_blind))
                    player.chips -= raise_amt
                    player.contribution += raise_amt
                    pot += raise_amt
                    log_action(player_logs, player.name, "postflop_2", "raise", raise_amt)
                    postflop_raiser_position = pos
                    postflop_raise_or_bet = "raise"
                    break
                else:
                    print(f"Invalid action by {player.name} at {pos}")

#turn decision making for bots
            
    turn_raiser_position = None #also using this variable to store inital turn better
    turn_raise_or_bet = None
    turn_checks = []
    #advance to the flop if the there are at least two players remaining
    
    if len(postflop_checks) == len([pos for pos in positions.keys() if pos not in preflop_folded_positions]) or len(positions) - len(preflop_folded_positions) > 1:
        #turn
        board.extend([deck.pop()])
        print(f"The board after the turn shows: {prettify_hand(board)}")
        for log in player_logs:
            if not log["folded"]:
                for player in positions.values():
                    if player.name == log["player_name"]:
                        log["turn_strength"] = evaluate_score(player.hand, board)
            else:
                log["postflop_strength"] = None

        #the first postflop decision gives bots the option to check or bet. 
        order = list(positions.keys())
        new_order = order[5:] + order[:5] #makes sure the small blind is firsts to act and the button is last 
        new_order = [pos for pos in new_order if pos not in preflop_folded_positions] #remove folded positions
        player_contributions = [player.contribution for pos, player in positions.items() if pos not in preflop_folded_positions]
        for pos in new_order:
            player_strength = evaluate_score(positions[pos].hand, board)
            player = positions[pos]
            #replace with designated turn function
            action = player.decide_postflop(pot = pot, call_amt = max(player_contributions) - player.contribution, player_strength = player_strength)
            if action == "check":
                log_action(player_logs, player.name, "turn", "check", 0)
                turn_checks.append(pos)
            elif action == "bet":
                roll = random.choice([20, 30, 40])
                bet_amt = int(roll * pot / 100)
                player.chips -= bet_amt
                player.contribution += bet_amt
                pot += bet_amt
                log_action(player_logs, player.name, "turn", "bet", bet_amt)
                turn_raise_or_bet = "bet"
                turn_raiser_position = pos
                break
            else:
                print(f"{player.name} made an invalid decision turn")

#2nd turn decisions

    #if there was a bet on the first postflop decision, or a raise on the second decision
    if turn_raiser_position is not None:
        loop_counter = 0
        max_loops = 10
        while not all_contributions_equal(positions, preflop_folded_positions): #preflop folded positions is for the entire hand
            if loop_counter >= max_loops:
                print("Max turn loops reached, breaking to avoid infinite loop.")
                break
            loop_counter += 1
            order = list(positions.keys())
            idx = order.index(turn_raiser_position)
            new_order = [pos for pos in (order[idx + 1:] + order[:idx]) if pos not in preflop_folded_positions]

            #looping though each player to make thier decisions in response to the raiser
            for pos in new_order:
                player = positions[pos]
                call_amt = positions[turn_raiser_position].contribution - player.contribution 
                player_strength = evaluate_score(player.hand, board) # gets the rank of the players hand from 1200 worst to 1, the best possible 
                #must replace this function with custom turn function
                action = player.decide_postflop_2(pot = pot, call_amt = call_amt, player_strength = player_strength, raise_or_bet = turn_raise_or_bet)
                cold_callers = []
                if action == "fold":
                    preflop_folded_positions.append(pos)
                    log_action(player_logs, player.name, "turn_2", "fold", 0)
                    # Check if only one player remains
                    if len(preflop_folded_positions) == len(positions) - 1:
                        for remaining_pos in positions:
                            if remaining_pos not in preflop_folded_positions:
                                winner = positions[remaining_pos]
                                winner.chips += pot
                                for log in player_logs:
                                    if log["player_name"] == winner.name:
                                        log["chips_won"] = pot
                                        print(f"{winner.name} wins the pot of {pot} on the turn.")
                                break
                elif action == "call":
                    player.chips -= call_amt
                    player.contribution += call_amt
                    pot += call_amt
                    log_action(player_logs, player.name, "turn_2", "call", call_amt)
                    cold_callers.append(player)
                elif action == "raise":
                    raise_amt = ((3 * positions[turn_raiser_position].contribution) + (len(cold_callers) * big_blind))
                    player.chips -= raise_amt
                    player.contribution += raise_amt
                    pot += raise_amt
                    log_action(player_logs, player.name, "turn_2", "raise", raise_amt)
                    turn_raiser_position = pos
                    turn_raise_or_bet = "raise"
                    break
                else:
                    print(f"Invalid action by {player.name} at {pos} on turn")

    #River decision making for bots
            
    river_raiser_position = None #also using this variable to store inital turn better
    river_raise_or_bet = None
    river_checks = []
    #advance to the flop if the there are at least two players remaining
    
    if len(postflop_checks) == len([pos for pos in positions.keys() if pos not in preflop_folded_positions]) or len(positions) - len(preflop_folded_positions) > 1:
        #river board extension
        board.extend([deck.pop()])
        print(f"The board after the turn shows: {prettify_hand(board)}")
        for log in player_logs:
            if not log["folded"]:
                for player in positions.values():
                    if player.name == log["player_name"]:
                        log["river_strength"] = evaluate_score(player.hand, board)
            else:
                log["postflop_strength"] = None

        #the first postflop decision gives bots the option to check or bet. 
        order = list(positions.keys())
        new_order = order[5:] + order[:5] #makes sure the small blind is firsts to act and the button is last 
        new_order = [pos for pos in new_order if pos not in preflop_folded_positions] #remove folded positions
        player_contributions = [player.contribution for pos, player in positions.items() if pos not in preflop_folded_positions]
        for pos in new_order:
            player_strength = evaluate_score(positions[pos].hand, board)
            player = positions[pos]
            #replace with designated turn function
            action = player.decide_postflop(pot = pot, call_amt = max(player_contributions) - player.contribution, player_strength = player_strength)
            if action == "check":
                log_action(player_logs, player.name, "turn", "check", 0)
                river_checks.append(pos)
            elif action == "bet":
                roll = random.choice([20, 30, 40, 75])
                bet_amt = int(roll * pot / 100)
                player.chips -= bet_amt
                player.contribution += bet_amt
                pot += bet_amt
                log_action(player_logs, player.name, "river", "bet", bet_amt)
                river_raise_or_bet = "bet"
                river_raiser_position = pos
                break
            else:
                print(f"{player.name} made an invalid decision river")

#2nd river decisions

    #if there was a bet on the first postflop decision, or a raise on the second decision
    if river_raiser_position is not None:
        loop_counter = 0
        max_loops = 10
        while not all_contributions_equal(positions, preflop_folded_positions): #preflop folded positions is for the entire hand
            if loop_counter >= max_loops:
                print("Max turn loops reached, breaking to avoid infinite loop.")
                break
            loop_counter += 1
            order = list(positions.keys())
            idx = order.index(river_raiser_position)
            new_order = [pos for pos in (order[idx + 1:] + order[:idx]) if pos not in preflop_folded_positions]

            #looping though each player to make thier decisions in response to the raiser
            for pos in new_order:
                player = positions[pos]
                call_amt = positions[river_raiser_position].contribution - player.contribution 
                player_strength = evaluate_score(player.hand, board) # gets the rank of the players hand from 1200 worst to 1, the best possible 
                #must replace this function with custom turn function
                action = player.decide_postflop_2(pot = pot, call_amt = call_amt, player_strength = player_strength, raise_or_bet = river_raise_or_bet)
                cold_callers = []
                if action == "fold":
                    preflop_folded_positions.append(pos)
                    log_action(player_logs, player.name, "river_2", "fold", 0)
                    # Check if only one player remains
                    if len(preflop_folded_positions) == len(positions) - 1:
                        for remaining_pos in positions:
                            if remaining_pos not in preflop_folded_positions:
                                winner = positions[remaining_pos]
                                winner.chips += pot
                                for log in player_logs:
                                    if log["player_name"] == winner.name:
                                        log["chips_won"] = pot
                                        print(f"{winner.name} wins the pot of {pot} on the turn.")
                                break
                elif action == "call":
                    player.chips -= call_amt
                    player.contribution += call_amt
                    pot += call_amt
                    log_action(player_logs, player.name, "river_2", "call", call_amt)
                    cold_callers.append(player)
                elif action == "raise":
                    raise_amt = ((3 * positions[river_raiser_position].contribution) + (len(cold_callers) * big_blind))
                    player.chips -= raise_amt
                    player.contribution += raise_amt
                    pot += raise_amt
                    log_action(player_logs, player.name, "river_2", "raise", raise_amt)
                    river_raiser_position = pos
                    river_raise_or_bet = "raise"
                    break
                else:
                    print(f"Invalid action by {player.name} at {pos} on river")

    #RIVER SHOWDOWN
    remaining_positions = [pos for pos in positions.keys() if pos not in preflop_folded_positions]
    if len(remaining_positions) > 1:
        hand_strengths = {}
        for pos in remaining_positions:
            hand_strength = evaluate_score(positions[pos].hand, board)
            hand_strengths[pos] = hand_strength
            best_rank = min(hand_strengths.values())  # Lower is better
        winners = [pos for pos, rank in hand_strengths.items() if rank == best_rank]

        pot_share = pot // len(winners)

        for pos in winners:
            winner = positions[pos]
            winner.chips += pot_share
            print(f"{winner.name} wins {pot_share} chips at showdown.")

            for log in player_logs:
                if log["player_name"] == winner.name:
                    log["chips_won"] = pot_share
                    log["went_to_showdown"] = True

        # Log went_to_showdown = False for folded players
        for log in player_logs:
            if log["player_name"] not in [positions[p].name for p in winners]:
                log.setdefault("went_to_showdown", False)

    df_this_hand = pd.DataFrame(player_logs)
    results_df = pd.concat([results_df, df_this_hand], ignore_index=True)

    return df_this_hand

game_flow(small_blind=5, big_blind=10)
