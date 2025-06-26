#importing python packages
import random
import pandas as pd
import numpy as np
import os, sys
from stable_baselines3 import PPO

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
from engine.simulation_helpers import setup_deck_and_deal, prettify_hand, get_hand_strength, all_contributions_equal, highest_straight, highest_straight_flush, evaluate, hand_score, evaluate_score, award_pot_to_best, encode_obs, POSITION_MAP
from bots.default_bot import PokerBot
from bots.rl_bot import RLBot

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
Atlas = PokerBot(name = "Atlas", chips = 2000, aggression_level = 20, tightness_level = 1, bluffing_factor = 7)
Blair = PokerBot(name = "Blair", chips = 2000, aggression_level = 30, tightness_level = 1, bluffing_factor = 10)
Cruz = PokerBot(name = "Cruz", chips = 2000, aggression_level = 40, tightness_level = 2, bluffing_factor = 13)
Drew = PokerBot(name = "Drew", chips = 2000,aggression_level = 50, tightness_level = 2, bluffing_factor = 16,)
Ember = PokerBot(name = "Ember", chips = 2000, aggression_level = 60, tightness_level = 2, bluffing_factor = 19)
Flint = PokerBot(name = "Flint", chips = 2000, aggression_level = 70, tightness_level = 3, bluffing_factor = 22)
Gio = PokerBot(name = "Gio", chips = 2000, aggression_level = 80, tightness_level = 3, bluffing_factor = 25)

#Reinforcement learning bot 
model = PPO.load(r"C:\Users\jason\projects\poker_project\poker-ai-headsup\poker_rl_model.zip")
Ruby = RLBot(name = "Ruby", model = model)

#creating a list of players to be used in the game
players = [Atlas, Blair, Cruz, Drew, Ember, Flint, Ruby]         

#creating a dataframe to track decision making and results
results_df = pd.DataFrame(columns = [])
hand_counter = 1 #track the number of hands played

def init_player_logs(hand_id, positions):
    """
    This functions adds all of the bots information to the dataframe.
    params:
        hand_id - the hand being played
        positions - the updated positions of the bots
    returns:
        player information appended to the the dataframe
    """
    logs = []
    for pos, player in positions.items():
        logs.append({
            "hand_id": hand_id,
            "player_name": player.name,
            "position": pos,
            "hole_cards": player.hand,
            "preflop_strength" : get_hand_strength(player.hand[0], player.hand[1]),
            "aggression_level" : player.aggression_level,
            "tightness_level" : player.tightness_level,
            "bluffing_factor" : player.bluffing_factor,
            "starting_stack" : player.chips,
            "refills" : player.refills, #how many times a bot topped off its stack
            "folded": False,
            "went_to_showdown": False,
            "final_contribution": 0,
            "chips_won": 0
    })
    return logs

def log_action(logs, player_name, street, action, amount=0):
    """
    function to log the action of each player during gameflow.
    params:
        logs - dataframe name
        player_name - makes sure the decisions are associated with the correct player
        street - the title of the street for the action and the dataframe
        action - the action the bot selected
        amount - the amount of the bots bet or raise 
    returns:
        added action to the dataframe.
    """
    for log in logs:
        if log["player_name"] == player_name:
            log[f"{street}_action"] = action
            log[f"{street}_bet"] = amount
            log["final_contribution"] += amount
            if action == "fold":
                log["folded"] = True
            break

def log_odds_and_ratios(logs, players, folded_positions, pot, call_amount, street):
    """
    Function to add the pot_odds and stack_ratios to the player_logs
    params:
        logs - dict of player logs for the pot_odds and stack ratios to be appended to 
        players - a list of players 
        folded_positions - the players that already folded out of the hand
        pot - the total size of the pot at the time of logging the decisions
        call_amount - How much the bot is asked to call at a decision
        street - helps with naming the dataframe
    returns:
        pot_odds and stack_ratios appended to the player_logs.
    """
    #double check for edge cases where call amount is 0 every player fold case for chip_ratio
    total_chips = sum(p.chips for p in players if p not in folded_positions)
    for log in logs:
        for player in players:
            if log["player_name"] == player.name:
                if call_amount > 0:
                    log[f"{street}_pot_odds"] = round(pot/call_amount, 2)
                else:
                    log[f"{street}_pot_odds"] = None

                if total_chips > 0:
                    log[f"{street}_chip_ratio"] = round(player.chips/total_chips, 2)
                else:
                    log[f"{street}_chip_ratio"] = None
                break

def game_flow(small_blind, big_blind):
    #importing global players and hand tracker to generate unique hand id's
    global players, results_df, hand_counter

    if isinstance(player, RLBot):
        player.reset_hand(player.chips)

    # Reorder columns in dataframe
    desired_column_order = [
        "hand_id", "player_name", "position", "hole_cards",
        "preflop_strength", "aggression_level", "tightness_level", "bluffing_factor", "starting_stack", "preflop_pot_odds", "preflop_chip_ratio", "preflop_action", "preflop_bet", "preflop_2_action", "preflop_2_pot_odds", "preflop_2_chip_ratio", "preflop_2_bet",
        "postflop_strength", "postflop_action", "postflop_bet", "postflop_2_action", "postflop_2_pot_odds", "postflop_2_chip_ratio", "postflop_2_bet",
        "turn_strength", "turn_action", "turn_bet", "turn_2_action", "turn_2_pot_odds", "turn_2_chip_ratio", "turn_2_bet",
        "river_strength", "river_action", "river_bet", "river_2_action", "river_2_pot_odds", "river_2_chip_ratio", "river_2_bet", 
        "folded", "final_contribution", "chips_won", "went_to_showdown", "refills"
    ]


    players = players[-1:] + players[:-1]  # rotate players clockwise

    #resetting the player contributions from the previous hand
    for p in players:
        p.contribution = 0   
        p.all_in = False
        if p.chips <= big_blind:
            p.refill_chips()

    #assigning each player a position
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

    deck = setup_deck_and_deal(players=players)  # assigns hole_cards to each bot and removing those cards from the deck

    board = [] #initalizing an empty board for cards to be assigned to 
    pot = 0 #initalizing the pot to equal zero
    preflop_information = []
    preflop_folded_positions = [] #tracking folded players across the hand
    raiser_position = None #tracking the most recent raiser in the hand 

    player_logs = init_player_logs(hand_id, positions)

    # Post blinds
    positions["SB"].contribution += small_blind
    positions["SB"].chips -= small_blind


    positions["BB"].contribution += big_blind
    positions["BB"].chips -= big_blind

    log_action(player_logs, positions["SB"].name, "preflop", "post_small_blind", small_blind)
    log_action(player_logs, positions["BB"].name, "preflop", "post_big_blind",   big_blind)


    pot += small_blind + big_blind
    # First Preflop Loop
    for position, player in positions.items():

        
        num_limpers = sum(1 for d in preflop_information if d["action"] == "call")
        call_amt = big_blind - player.contribution
        if isinstance(player, RLBot):
            obs = encode_obs(game_state, player_position)
            action = player.decide(obs)
        else:
            action = player.decide_preflop(position, pot, call_amt)
        log_odds_and_ratios(logs = player_logs, players = players, folded_positions= preflop_folded_positions, pot = pot, call_amount = call_amt, street= "preflop")

        if action == "fold":
            preflop_folded_positions.append(position)
            log_action(player_logs, player.name, "preflop", "fold", 0)
            # Check if only one player remains
            if len(preflop_folded_positions) == len(positions) - 1:
                for remaining_pos in positions:
                    #awarding chips to the winning player and logging results
                    if remaining_pos not in preflop_folded_positions:
                        winner = positions[remaining_pos]
                        winner.chips += pot
                        for log in player_logs:
                            if log["player_name"] == winner.name:
                                log["chips_won"] = pot
                                print(f"{winner.name} wins the pot of {pot} chips preflop 💰.")
                                break
                #if there is only one player left in the hand award chips and end hand
                df_this_hand = pd.DataFrame(player_logs)
                existing = [c for c in desired_column_order if c in df_this_hand.columns]
                df_this_hand = df_this_hand.reindex(columns=existing)
                return df_this_hand


        elif action == "call":
            #how to handle if the player needs to call more than the chips in thier stack
            #at each street this block is designed to adjust call or raise amounts if a player is all-in
            if call_amt > player.chips:
                actual_call = player.chips
                player.all_in = True
            else:
                actual_call = call_amt

            pot += actual_call
            player.chips -= actual_call
            player.contribution += actual_call
            log_action(player_logs, player.name, "preflop", "call", actual_call)
        elif action == "raise":
            raise_amt = ((random.choice([2, 3]) * big_blind) + (num_limpers * big_blind))
            if raise_amt >= player.chips:
                actual_raise = player.chips
                player.all_in = True
                print(f"{player.name} went all in for {actual_raise} chips")
            else:
                actual_raise = raise_amt
            pot += actual_raise
            player.chips -= actual_raise
            player.contribution += actual_raise
            log_action(player_logs, player.name, "preflop", "raise", actual_raise)
            raiser_position = position
            preflop_information.append({"action": "raise", "player": player.name, "position": position})
            break
        else:
            #log the action of the big blind
            log_action(player_logs, player.name, "preflop", "check", 0)

        if action != "raise":
            preflop_information.append({"action": action, "player": player.name, "position": position})

    # Second Preflop Loop (if a raise occurred)

    #only run this block if there was a previous raiser preflop
    if raiser_position is not None:
        loop_counter = 0
        max_loops = 10
        preflop_information_2 = []
        #continues betting and raising until bots even out thier contributions
        while not all_contributions_equal(positions, preflop_folded_positions):
            if loop_counter >= max_loops:
                print("Max preflop loops reached, breaking to avoid infinite loop.")
                break
            loop_counter += 1
            order = list(positions.keys())
            idx = order.index(raiser_position)
            new_order = [pos for pos in (order[idx+1:] + order[:idx]) if pos not in preflop_folded_positions]
            cold_callers = [] #tracking cold callers to make more logical bet sizings 

            for pos in new_order:
                player = positions[pos]
                #dynamic call amount based on the raisers additional contribution compared to the other players
                call_amt = positions[raiser_position].contribution - player.contribution 
                action = player.decide_preflop_2(pos, pot, call_amt)
                log_odds_and_ratios(logs = player_logs, players = players, folded_positions= preflop_folded_positions, pot = pot, call_amount = call_amt, street= "preflop_2")

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
                                        print(f"{winner.name} wins the pot of {pot} chips preflop 💰.")
                                break
                        df_this_hand = pd.DataFrame(player_logs)
                        existing = [c for c in desired_column_order if c in df_this_hand.columns]
                        df_this_hand = df_this_hand.reindex(columns=existing)
                        return df_this_hand

                elif action == "call":
                    if call_amt > player.chips:
                        player.all_in = True
                        actual_call = player.chips
                    else:
                        actual_call = call_amt
                    player.chips -= actual_call
                    player.contribution += actual_call
                    pot += actual_call
                    log_action(player_logs, player.name, "preflop_2", "call", actual_call)
                    cold_callers.append(player)
                elif action == "raise":
                    raise_amt = ((3 * positions[raiser_position].contribution) + (len(cold_callers) * big_blind))
                    if raise_amt > player.chips:
                        actual_raise = player.chips
                        player.all_in = True
                        print(f"{player.name} went all in for {actual_raise} chips")
                    else:
                        actual_raise = raise_amt
                    player.chips -= actual_raise
                    player.contribution += actual_raise
                    pot += actual_raise
                    log_action(player_logs, player.name, "preflop_2", "raise", actual_raise)
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
        for pos in [p for p in new_order if not positions[p].all_in]:
            player_strength = evaluate_score(positions[pos].hand, board)
            player = positions[pos]
            action = player.decide_postflop(pot = pot, call_amt = max(player_contributions) - player.contribution, player_strength = player_strength)
            if action == "check":
                log_action(player_logs, player.name, "postflop", "check", 0)
                postflop_checks.append(pos)
            elif action == "bet":
                roll = random.choice([20, 33, 50])
                bet_amt = int(roll * pot / 100)
                if bet_amt >= player.chips:
                    actual_bet = player.chips
                    player.all_in = True
                    print(f"{player.name} is all in for {actual_bet}")
                else:
                    actual_bet = bet_amt
                player.chips -= actual_bet
                player.contribution += actual_bet
                pot += actual_bet
                log_action(player_logs, player.name, "postflop", "bet", actual_bet)
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
            for pos in [p for p in new_order if not positions[p].all_in]:
                player = positions[pos]
                call_amt = positions[postflop_raiser_position].contribution - player.contribution 
                player_strength = evaluate_score(player.hand, board) # gets the rank of the players hand from 1200 worst to 1, the best possible hand
                action = player.decide_postflop_2(pot = pot, call_amt = call_amt, player_strength = player_strength, raise_or_bet = postflop_raise_or_bet)
                cold_callers = []
                log_odds_and_ratios(logs = player_logs, players = players, folded_positions= preflop_folded_positions, pot = pot, call_amount = call_amt, street= "postflop_2")

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
                                        print(f"{winner.name} wins the pot of {pot} chips postflop 💰.")
                                break
                        df_this_hand = pd.DataFrame(player_logs)
                        existing = [c for c in desired_column_order if c in df_this_hand.columns]
                        df_this_hand = df_this_hand.reindex(columns=existing)
                        return df_this_hand

                elif action == "call":
                    if call_amt >= player.chips:
                        actual_call = player.chips
                        player.all_in = True
                        print(f"{player.name} is all in for {actual_call}")
                    else:
                        actual_call = call_amt
                    player.chips -= actual_call
                    player.contribution += actual_call
                    pot += actual_call
                    log_action(player_logs, player.name, "postflop_2", "call", actual_call)
                    cold_callers.append(player)
                elif action == "raise":
                    raise_amt = ((3 * positions[postflop_raiser_position].contribution) + (len(cold_callers) * big_blind))
                    if raise_amt >= player.chips:
                        actual_raise = player.chips
                        player.all_in = True
                        print(f"{player.name} is all in for {actual_raise}")
                    else:
                        actual_raise = raise_amt
                    player.chips -= actual_raise
                    player.contribution += actual_raise
                    pot += actual_raise
                    log_action(player_logs, player.name, "postflop_2", "raise", actual_raise)
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
    
    if len(positions) - len(preflop_folded_positions) > 1:
        #turn
        board.extend([deck.pop()])
        print(f"The board after the turn shows: {prettify_hand(board)}")
        for log in player_logs:
            if not log["folded"]:
                for player in positions.values():
                    if player.name == log["player_name"]:
                        log["turn_strength"] = evaluate_score(player.hand, board)
            else:
                log["turn_strength"] = None

        #the first postflop decision gives bots the option to check or bet. 
        order = list(positions.keys())
        new_order = order[5:] + order[:5] #makes sure the small blind is firsts to act and the button is last 
        new_order = [pos for pos in new_order if pos not in preflop_folded_positions] #remove folded positions
        player_contributions = [player.contribution for pos, player in positions.items() if pos not in preflop_folded_positions]
        for pos in [p for p in new_order if not positions[p].all_in]:
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
                if bet_amt >= player.chips:
                    actual_bet = player.chips
                    player.all_in = True
                    print(f"{player.name} is all in for {actual_bet}")
                else:
                    actual_bet = bet_amt
                player.chips -= actual_bet
                player.contribution += actual_bet
                pot += actual_bet
                log_action(player_logs, player.name, "turn", "bet", actual_bet)
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
            for pos in [p for p in new_order if not positions[p].all_in]: #all in player doesn't need to make a decision
                player = positions[pos]
                call_amt = positions[turn_raiser_position].contribution - player.contribution 
                player_strength = evaluate_score(player.hand, board) # gets the rank of the players hand from 1200 worst to 1, the best possible 
                #must replace this function with custom turn function
                action = player.decide_postflop_2(pot = pot, call_amt = call_amt, player_strength = player_strength, raise_or_bet = turn_raise_or_bet)
                cold_callers = []
                log_odds_and_ratios(logs = player_logs, players = players, folded_positions= preflop_folded_positions, pot = pot, call_amount = call_amt, street= "turn_2")
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
                                        print(f"{winner.name} wins the pot of {pot} on the turn 💰.")
                                break
                        df_this_hand = pd.DataFrame(player_logs)
                        existing = [c for c in desired_column_order if c in df_this_hand.columns]
                        df_this_hand = df_this_hand.reindex(columns=existing)
                        return df_this_hand
                elif action == "call":
                    if call_amt >= player.chips:
                        actual_call = player.chips
                        player.all_in = True
                        print(f"{player.name} is all in for {actual_call}")
                    else:
                        actual_call = call_amt
                    player.chips -= actual_call
                    player.contribution += actual_call
                    pot += actual_call
                    log_action(player_logs, player.name, "turn_2", "call", actual_call)
                    cold_callers.append(player)
                elif action == "raise":
                    raise_amt = ((3 * positions[turn_raiser_position].contribution) + (len(cold_callers) * big_blind))
                    if raise_amt >= player.chips:
                        actual_raise = player.chips
                        player.all_in = True
                        print(f"{player.name} is all in for {actual_raise}")
                    else:
                        actual_raise = raise_amt
                    player.chips -= actual_raise
                    player.contribution += actual_raise
                    pot += actual_raise
                    log_action(player_logs, player.name, "turn_2", "raise", actual_raise)
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
    
    if len(positions) - len(preflop_folded_positions) > 1:
        #river board extension
        board.extend([deck.pop()])
        print(f"The board after the river shows: {prettify_hand(board)}")
        for log in player_logs:
            if not log["folded"]:
                for player in positions.values():
                    if player.name == log["player_name"]:
                        log["river_strength"] = evaluate_score(player.hand, board)
            else:
                log["river_strength"] = None

        #the first postflop decision gives bots the option to check or bet. 
        order = list(positions.keys())
        new_order = order[5:] + order[:5] #makes sure the small blind is firsts to act and the button is last 
        new_order = [pos for pos in new_order if pos not in preflop_folded_positions] #remove folded positions
        player_contributions = [player.contribution for pos, player in positions.items() if pos not in preflop_folded_positions]
        for pos in [p for p in new_order if not positions[p].all_in]:
            player_strength = evaluate_score(positions[pos].hand, board)
            player = positions[pos]
            #replace with designated turn function
            action = player.decide_postflop(pot = pot, call_amt = max(player_contributions) - player.contribution, player_strength = player_strength)
            if action == "check":
                log_action(player_logs, player.name, "river", "check", 0)
                river_checks.append(pos)
            elif action == "bet":
                roll = random.choice([20, 30, 40, 75])
                bet_amt = int(roll * pot / 100)
                if bet_amt >= player.chips:
                    actual_bet = player.chips
                    player.all_in = True
                    print(f"{player.name} is all in for {actual_bet}")
                else:
                    actual_bet = bet_amt
                player.chips -= actual_bet
                player.contribution += actual_bet
                pot += actual_bet
                log_action(player_logs, player.name, "river", "bet", actual_bet)
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
            for pos in [p for p in new_order if not positions[p].all_in]:
                player = positions[pos]
                call_amt = positions[river_raiser_position].contribution - player.contribution 
                player_strength = evaluate_score(player.hand, board) # gets the rank of the players hand from 1200 worst to 1, the best possible 
                #must replace this function with custom turn function
                action = player.decide_postflop_2(pot = pot, call_amt = call_amt, player_strength = player_strength, raise_or_bet = river_raise_or_bet)
                cold_callers = []
                log_odds_and_ratios(logs = player_logs, players = players, folded_positions= preflop_folded_positions, pot = pot, call_amount = call_amt, street= "river_2")
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
                                        print(f"{winner.name} wins the pot of {pot} on the river 💰.")
                                break
                        df_this_hand = pd.DataFrame(player_logs)
                        existing = [c for c in desired_column_order if c in df_this_hand.columns]
                        df_this_hand = df_this_hand.reindex(columns=existing)
                        return df_this_hand
                elif action == "call":
                    if call_amt >= player.chips:
                        actual_call = player.chips
                        player.all_in = True
                        print(f"{player.name} is all in for {actual_call}")
                    else:
                        actual_call = call_amt
                    player.chips -= actual_call
                    player.contribution += actual_call
                    pot += actual_call
                    log_action(player_logs, player.name, "river_2", "call", actual_call)
                    cold_callers.append(player)
                elif action == "raise":
                    raise_amt = ((3 * positions[river_raiser_position].contribution) + (len(cold_callers) * big_blind))
                    if raise_amt >= player.chips:
                        actual_raise = player.chips
                        player.all_in = True
                        print(f"{player.name} is all in for {actual_raise}")
                    else:
                        actual_raise = raise_amt
                    player.chips -= actual_raise
                    player.contribution += actual_raise
                    pot += actual_raise
                    log_action(player_logs, player.name, "river_2", "raise", actual_raise)
                    river_raiser_position = pos
                    river_raise_or_bet = "raise"
                    break
                else:
                    print(f"Invalid action by {player.name} at {pos} on river")

    #RIVER SHOWDOWN
    remaining_positions = [pos for pos in positions.keys() if pos not in preflop_folded_positions]
    if len(remaining_positions) > 1:
        award_pot_to_best(positions = positions, folded_positions = preflop_folded_positions, board = board, player_logs = player_logs, pot = pot)
       

    df_this_hand = pd.DataFrame(player_logs)

    # Only keep columns that exist in df_this_hand (in case some aren't created yet)
    existing_columns = [col for col in desired_column_order if col in df_this_hand.columns]
    df_this_hand = df_this_hand.reindex(columns=existing_columns)


    return df_this_hand


def data_collection(rounds, small_blind = 5, big_blind = 10):
    """
    Funtion to run the simulation X number of times into one large dataframe.
    params:
        rounds - How many hands the bots will play against each other
        small_blind - passed to game_flow()
        big_blind - passed to game_flow()
    returns:
        Pandas dataframe of X hands played suitable for ML modeling.
    """
    all_results = pd.DataFrame()

    for round_counter in range(1, rounds + 1):
        try:
            df_this_hand = game_flow(small_blind, big_blind)
        except Exception as e:
            print(f"error on hand {round_counter}: {e}")
            continue

        if df_this_hand is not None:
            all_results = pd.concat([all_results, df_this_hand], ignore_index= True)

    return all_results

hand_results = data_collection(rounds = 500)

hand_results

#something crazy happened where a bot won 63,000 chips in a hand, most liely both hand amazing hands and reraised eachother forever betting chips they did not have to lose 

hand_results[hand_results["chips_won"] >= 10000]

for player in players:
    print(player.name, player.chips, player.refills)


#side pot issues
#for loops think about tracking the raise or call _2 or _3 or _4 etc, instead of just decsion 1 and 2 being updated at each iteration
#where are the chips going??

hand_results[hand_results["postflop_2_bet"] < 0]

# 1) Sum up total_contributed and total_paid for each hand
summary = hand_results.groupby("hand_id").agg(
    total_contributed=("final_contribution", "sum"),
    total_paid=("chips_won", "sum")
)

# 2) Find all hands where they don’t match
imbalanced = summary[summary.total_contributed != summary.total_paid]

print(imbalanced)

#go back and clealn and comment code, feature engineer variables into the dataframe at each street

#think about board texture, scare cards out variable, pot odds at each decision

