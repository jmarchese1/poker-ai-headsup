# Poker AI for Heads-Up Hold’em ♠️♥️
This project is an experimental journey to build a poker AI capable of consistently beating real players in heads-up No-Limit Texas Hold’em. Inspired by AlphaZero, our agent will evolve from simple heuristics to advanced strategies that not only use card equity and pot odds but also learn to model and exploit opponents’ tendencies over time.

## Rule-Based Bot Data Generation

Two Complementary Bots: We start by creating two lightweight, rule-based agents (Bot A and Bot B) with slightly different thresholds for opening ranges, postflop betting, and bluff frequencies.
Large-Scale Hand Sampling: These bots play hundreds of thousands (or millions) of hands against each other to produce a structured dataset of realistic decision points—folds, calls, bets, raises, and showdown outcomes.
Edge-Case Coverage: By intentionally varying equity/pot-odds thresholds and injecting small random perturbations into bet sizes, the bots generate a rich variety of board runouts, bet-size patterns, and strategic mismatches.

## Feature Extraction & Data Logging

Pandas DataFrame Schema: Every hand history is parsed into a row containing:

hand_id	Unique identifier for each dealt hand
player_type	“A” or “B” to indicate which rule-based bot made this decision
hole_cards	Two-card string (e.g., “AsKd”) for the acting player
board_cards	Board up to that point (e.g., “Kh7h2c”)
position	Numeric index or “BTN/BB” to indicate in-position vs. out-of-position
stack_size	Chips remaining for acting player before the action
pot_size	Current pot before the action
to_call	Chips required to call (0 if checking is allowed)
hand_equity	Estimated equity vs. a random hand (or vs. known range if extended)
pot_odds	Computed pot odds (to_call / (pot_size + to_call))
action	Chosen action (fold, check, call, bet, raise)
bet_size	If action is bet or raise, the chosen bet amount (numeric)
final_outcome	+N (chips won) or –N (chips lost) when the hand finishes

Consistent Labeling: Each decision node (fold/check/call/raise + bet amount) is recorded with its corresponding state features, ensuring no ambiguity when training downstream models.

## Supervised Learning (Imitation Phase)

Baseline Policy Network: We use the rule-based dataset to train a supervised model (e.g., a neural network or gradient boosting classifier) that predicts “optimal” actions (fold, call, raise + size) given a game state.
Smoothing & Noise Reduction: The ML model learns to generalize from Bot A and Bot B interactions—smoothing out deterministic quirks while retaining core strategic patterns.
Validation & Metrics: We measure per-action accuracy, confusion matrices for fold/call/raise classes, and probability calibration to ensure the model closely matches the rule-based behaviors.

## Reinforcement Learning & Exploitative Refinement

Self-Play / Bot-Play Episodes:
Let the policy network play repeated matches against Bot A and Bot B, collecting reward signals (net chips won/lost).
Update the network via policy gradients (or Q-learning) to gradually exploit known rule-based weaknesses.
Iterate this cycle so the policy diverges from pure imitation toward higher-EV strategies.

## Opponent Modeling: 

Over time, incorporate a lightweight opponent classifier that identifies whether an opponent is more “tight” or “loose,” enabling conditional strategy adjustments in real time.
Essentially this will quickly predict the play style of the opponent and adapt play style to exploit thier weaknesses.

## Final Objective

Game Theory Optimal + Exploitative Hybrid: Produce an agent that combines near-GTO decisions (covering balanced ranges) with precise exploitative deviations whenever it detects suboptimal opponent tendencies.
Real-Time Adaptation: In a live match against human or bot opponents, continuously update the opponent model based on observed actions and adjust the betting strategy accordingly.
Evaluation vs. Humans: Beyond rule-based bots, challenge the agent against low- and mid-stakes human opponents (online or in local tournaments) to validate that it translates simulation strength into real-world win rates.

🧠 Learning Process & Data Pipeline

Both bots share the same core engine (hand evaluator and pot-odds calculator) but differ in:
Preflop Ranges (e.g., Bot A opens top 15 % vs. Bot B opens top 30 %)
Postflop Bet/Call Thresholds (e.g., Bot A bets > 0.40 equity; Bot B bets > 0.35 equity)
Bluff Frequencies (periodically mix in a semi-random bluff to avoid deterministic lines)

## Simulation Loop

A single hand is played as follows:
Deal hole cards → preflop decision by Bot A/B using equity thresholds and position logic.
If callers remain, deal flop → recompute equity, pot odds → postflop decisions.
Deal turn/river in sequence, repeating equity/odds checks until showdown or all-in.
Collect final outcome (chips exchanged) and log every decision with its state features.
Supervised Model Training

Features: (hole_cards, board_cards, position, stack_size, pot_size, to_call, hand_equity, pot_odds, optional one-hot encodings for board texture, etc.)
Target: (action, bet_size_bucket)

## 🚧 Requirements
Python 3.8+

pandas, numpy, scikit-learn (for preprocessing and baseline models)

PyTorch or TensorFlow (for neural-network architectures and RL)

Optional: equity-evaluator library (e.g., Deuces or FastPoker)

OpenAI API key (if you choose to experiment with API-driven simulations alongside rule-based bots)


current progess:
developed poker game logic and simulated hands against random decision bots. 
Now creating bots with simple poker logic and decision making to play against one another.


