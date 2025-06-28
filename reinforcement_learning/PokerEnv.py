import gym #pass it into a class to create a gym environment
from gym import spaces
import numpy as np
from stable_baselines3 import PPO
import os, sys
root = r"C:\Users\jason\projects\poker_project\poker-ai-headsup"
if root not in sys.path:
    sys.path.insert(0, root)
import random

#importing helpers
from engine.simulation_helpers import (setup_deck_and_deal, prettify_hand, get_hand_strength, all_contributions_equal, 
                                       highest_straight, highest_straight_flush, evaluate, hand_score, 
                                       evaluate_score, award_pot_to_best, encode_obs, POSITION_MAP)
#recreate this bot
from bots.rl_bot import RLBot

class PokerEnv(gym.Env):
    def __init__(self, players, small_blind = 5, big_blind = 10):
        super().__init__()
        self.players = players
        self.rl_bot = next(p for p in players if isinstance(p, RLBot)) #identifying the rl bot out of the players
        self.small_blind, self.big_blind = small_blind, big_blind

        #the bots decsion making choices
        self.action_space = spaces.Discrete(5)  # fold, check, call, bet, raise
        self.observation_space = spaces.Box(low=0, high=1, shape=(7,), dtype=np.float32)
        self.reset()

    def reset(self):
        #rotate players, clear hands, empty pot and contributions
        self.folded_positions = []
        #rotating the order of players each time the game resets
        self.players = self.players[-1:] + self.players[:-1]
        for p in self.players:
            p.contribution = 0, p.all_in = False  #resetting contributions to 0
            if p.chips <= self.big_blind:
                p.refill_chips()

        self.rl_bot.reset_hand(self.rl_bot.chips)

        self.positions = dict(zip(["UTG", "MP", "HJ", "CO", "BTN", "SB", "BB"], #updating the position of each bot in the hand
                             self.players))
        
        self.deck = setup_deck_and_deal(self.players) #deal cards to the players
        self.board, self.pot = [], 0 # setting board to be empty and pot to equal 0
        self.street = "preflop" # making sure the first decision point is preflop
        self._post_blinds() 

        self.rl_pos = next(pos for pos, p in self.positions.items() if p is self.rl_bot) #getting the position of the rl_bot
        call_amount = self.big_blind - self.rl_bot.contribution #how much the rl_bot needs to call 
        obs = encode_obs(self.rl_bot, self.rl_pos, self.pot, call_amount)
        return obs
    
    def _post_blinds(self):
        sb = self.positions["SB"]; bb = self.positions["BB"]
        sb.contribution += self.small_blind;  bb.contribution += self.big_blind
        sb.chips -= self.small_blind; bb.chips -= self.big_blind
        self.pot += self.small_blind + self.big_blind

    def step(self, action):
        done = False
        reward = 0.0

        # 1) Apply RL action
        self._apply_action(self.rl_pos, self.rl_bot, action)

        # 2) Loop through other players until RL acts again or hand ends
        if self.street == "preflop":
            while True:
                next_player_pos = self._next_to_act() #returns the next player that hasn't folded, is not allin, and does not equal the max contribution
                if next_player_pos == self.rl_pos or next_player_pos is None:
                    break

                player = self.positions[next_player_pos]
                if player.folded or player.all_in:
                    continue

                call_amt = self._get_call_amount(player) #amount the player needs to call to equal the max contribution
                player_action = player.decide_preflop(self.street, call_amt, self.pot, self.board)
                self._apply_action(next_player_pos, player, player_action) #updates, pot, contributuion and variables based on decision

                if self._only_one_left(): #checks if theres only one player remaining
                    winner = self._get_remaining_player()
                    winner.chips += self.pot
                    done = True
                    reward = self.rl_bot.chips - self.rl_bot.starting_stack
                    return None, reward, done, {}
                
                if self.raiser_position is not None:
                    while not all_contributions_equal(positions = self.positions, folded = self.folded_positions):
                        order = self.positions.keys()
                        idx = order.index(self.raiser_position)
                        new_order = [pos for pos in (order[idx+1:] + order[:idx]) if pos not in self.folded_positions]
                        self.positions = new_order

                        next_player_pos = self._next_to_act() #returns the next player that hasn't folded, is not allin, and does not equal the max contribution
                        if next_player_pos == self.rl_pos or next_player_pos is None:
                            break

                        player = self.positions[next_player_pos]
                        if player.folded or player.all_in:
                            continue

                        call_amt = self._get_call_amount(player)
                        player_action = player.decide_preflop_2(next_player_pos, self.pot, call_amt)
                        self._apply_action(next_player_pos, player, player_action)
                        
                        if self._only_one_left():
                            winner = self._get_remaining_player()
                            winner.chips += self.pot
                            done = True
                            reward = self.rl_bot.chips - self.rl_bot.starting_stack
                            return None, reward, done, {}


            # 3) Advance street if all contributions equal
            if all_contributions_equal(self.positions, self.folded_positions):
                self._advance_street()

        elif self.street in ["flop", "turn", "river"]:
            order = self.positions.keys()[5:] + self.positions.keys()[:5] #starting from the small blind player
            self.positions = order
            next_player_pos = self._next_to_act() #returns the next player that hasn't folded, is not allin, and does not equal the max contribution
            
            while True:
                if next_player_pos == self.rl_pos or next_player_pos is None:
                    break

                player = self.positions[next_player_pos]
                if player.folded or player.all_in:
                    continue

                player_strength = evaluate_score(player.hand, self.board)
                call_amt = self._get_call_amount(player)
                player_action = player.decide_postflop(self.pot, call_amt, player_strength)
                self._apply_action(next_player_pos, player, player_action)

                if self._only_one_left(): #checks if theres only one player remaining
                    winner = self._get_remaining_player()
                    winner.chips += self.pot
                    done = True
                    reward = self.rl_bot.chips - self.rl_bot.starting_stack
                    return None, reward, done, {}
                
                if self.raiser_position is not None:
                    while not all_contributions_equal(positions = self.positions, folded = self.folded_positions):
                        order = self.positions.keys()
                        idx = order.index(self.raiser_position)
                        new_order = [pos for pos in (order[idx+1:] + order[:idx]) if pos not in self.folded_positions]
                        self.positions = new_order

                        next_player_pos = self._next_to_act() #returns the next player that hasn't folded, is not allin, and does not equal the max contribution
                
                        if next_player_pos == self.rl_pos or next_player_pos is None:
                            break

                        player = self.positions[next_player_pos]
                        if player.folded or player.all_in:
                            continue

                        player = self.positions[next_player_pos]
                        call_amt = self._get_call_amount(player)
                        player_action = player.decide_preflop_2(next_player_pos, self.pot, call_amt)
                        self._apply_action(next_player_pos, player, player_action)
                        
                        if self._only_one_left():
                            winner = self._get_remaining_player()
                            winner.chips += self.pot
                            done = True
                            reward = self.rl_bot.chips - self.rl_bot.starting_stack
                            return None, reward, done, {}
                        
            if all_contributions_equal(self.positions, self.folded_positions):
                self._advance_street()

        else: #if self.street == showdown
            award_pot_to_best(self.positions, self.folded_positions, self.board, [], self.pot)
            reward = self.rl_bot.chips - self.rl_bot.starting_stack
            done = True
            return None, reward, done, {}

        # 5) Next observation for RL
        call_amt = self._get_call_amount(self.rl_bot)
        obs = encode_obs(self.rl_bot, self.rl_pos, self.pot, call_amt)
        return obs, 0.0, False, {}

    def _apply_action(self, pos, player, action):
        if action == 0:  # fold
            player.folded = True
            self.folded_positions.append(pos)
        elif action == 1: #check
            amt = 0
            player.contribute(amt)
            self.pot += 0
        elif action == 2:  # call
            call_amt = self._get_call_amount(player)
            amt = min(player.chips, call_amt)
            player.contribute(amt)
            self.pot += amt
        elif action == 3: #bet
            bet_amt = self.pot * int(random.choice([1/3, 1/2, 1]))
            amt = min(player.chips, bet_amt)
            player.contribute(amt)
            self.pot += amt
            self.raiser_position = pos
        elif action == 4:  # raise
            contributions = [p.contribution for p in self.positions.values() if not p.folded]
            raise_amt = max(contributions, default = 0) * random.choice([1.5, 2, 3])
            amt = min(player.chips, raise_amt)
            player.contribute(amt)
            self.pot += amt
            self.raiser_position = pos

    def _get_call_amount(self, player):
        contributions = [p.contribution for p in self.positions.values() if not p.folded]
        return max(contributions, default=0) - player.contribution

    def _only_one_left(self):
        active = [p for p in self.positions.values() if not p.folded]
        return len(active) == 1

    def _get_remaining_player(self):
        return next(p for p in self.positions.values() if not p.folded)

    def _next_to_act(self):
        for pos in self.positions:
            player = self.positions[pos]
            if not player.folded and not player.all_in and player.contribution != max(p.contribution for p in self.positions.values() if not p.folded):
                return pos
        return None

    def _advance_street(self):
        if self.street == "preflop":
            self.board.extend([self.deck.pop() for _ in range(3)])
            self.street = "flop"
        elif self.street == "flop":
            self.board.append(self.deck.pop())
            self.street = "turn"
        elif self.street == "turn":
            self.board.append(self.deck.pop())
            self.street = "river"
        elif self.street == "river":
            self.street = "showdown"

        # Reset contributions for next street
        for p in self.positions.values():
            p.contribution = 0


env = PokerEnv()

model = PPO("MlpPolicy", env, verbose = 1)

model.learn(total_timesteps = 100_000)

obs = env.reset()

for i in range(10):
    action, _ = model.predict(obs, deterministic=True)
    print(f"Action: {action}")
    obs, reward, done, info = env.step(action)

print(f"model save location: {os.getcwd()}")
root = r"\Users\jason\projects\poker_project\poker-ai-headsup"

if root not in sys.path:
    sys.path.insert(0, root)

print(sys.path)

#savinf the model to the project folder
model.save(r"C:\Users\jason\projects\poker_project\poker-ai-headsup\poker_rl_model")