# Poker AI for Heads-Up Hold’em ♠️♥️
This project is an experimental journey to build a poker AI capable of consistently beating real players in heads-up No-Limit Texas Hold’em. Inspired by AlphaZero, our agent will evolve from simple heuristics to advanced strategies that not only use card equity and pot odds but also learn to model and exploit opponents’ tendencies over time.

## 🔍 Updated Scope
Rule-Based Bot Data Generation

Two Complementary Bots: We start by creating two lightweight, rule-based agents (Bot A and Bot B) with slightly different thresholds for opening ranges, postflop betting, and bluff frequencies.

Large-Scale Hand Sampling: These bots play hundreds of thousands (or millions) of hands against each other to produce a structured dataset of realistic decision points—folds, calls, bets, raises, and showdown outcomes.

Edge-Case Coverage: By intentionally varying equity/pot-odds thresholds and injecting small random perturbations into bet sizes, the bots generate a rich variety of board runouts, bet-size patterns, and strategic mismatches.

Feature Extraction & Data Logging

Pandas DataFrame Schema: Every hand history is parsed into a row containing:

Hole cards for each player

Board cards (flop, turn, river)

Stack sizes and effective pot size before each decision

Action history (previous bets, raises, folds)

Computed hand equity and pot-odds at each decision point

Final outcome (chips won/lost)

Consistent Labeling: Each decision node (fold/check/call/raise + bet amount) is recorded with its corresponding state features, ensuring no ambiguity when training downstream models.

Supervised Learning (Imitation Phase)

Baseline Policy Network: We use the rule-based dataset to train a supervised model (e.g., a neural network or gradient boosting classifier) that predicts “optimal” actions (fold, call, raise + size) given a game state.

Smoothing & Noise Reduction: The ML model learns to generalize from Bot A and Bot B interactions—smoothing out deterministic quirks while retaining core strategic patterns.

Validation & Metrics: We measure per-action accuracy, confusion matrices for fold/call/raise classes, and probability calibration to ensure the model closely matches the rule-based behaviors.

Reinforcement Learning & Exploitative Refinement

Policy Initialization: The imitation-trained network serves as the starting policy.

Self-Play / Bot-Play Episodes:

Let the policy network play repeated matches against Bot A and Bot B, collecting reward signals (net chips won/lost).

Update the network via policy gradients (or Q-learning) to gradually exploit known rule-based weaknesses.

Iterate this cycle so the policy diverges from pure imitation toward higher-EV strategies.

Opponent Modeling: Over time, incorporate a lightweight opponent classifier that identifies whether an opponent is more “tight” or “loose,” enabling conditional strategy adjustments in real time.

Final Objective

Game Theory Optimal + Exploitative Hybrid: Produce an agent that combines near-GTO decisions (covering balanced ranges) with precise exploitative deviations whenever it detects suboptimal opponent tendencies.

Real-Time Adaptation: In a live match against human or bot opponents, continuously update the opponent model based on observed actions and adjust the betting strategy accordingly.

Evaluation vs. Humans: Beyond rule-based bots, challenge the agent against low- and mid-stakes human opponents (online or in local tournaments) to validate that it translates simulation strength into real-world win rates.

🧠 Learning Process & Data Pipeline
Bot Implementation

Both bots share the same core engine (hand evaluator and pot-odds calculator) but differ in:

Preflop Ranges (e.g., Bot A opens top 15 % vs. Bot B opens top 30 %)

Postflop Bet/Call Thresholds (e.g., Bot A bets > 0.40 equity; Bot B bets > 0.35 equity)

Bluff Frequencies (periodically mix in a semi-random bluff to avoid deterministic lines)

Simulation Loop

A single hand is played as follows:

Deal hole cards → preflop decision by Bot A/B using equity thresholds and position logic.

If callers remain, deal flop → recompute equity, pot odds → postflop decisions.

Deal turn/river in sequence, repeating equity/odds checks until showdown or all-in.

Collect final outcome (chips exchanged) and log every decision with its state features.

Data Logging Structure
Each row in our DataFrame represents a single decision node and contains:

Column	Description:

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

Supervised Model Training

Features: (hole_cards, board_cards, position, stack_size, pot_size, to_call, hand_equity, pot_odds, optional one-hot encodings for board texture, etc.)

Target: (action, bet_size_bucket)

Pipeline:

One-hot encode categorical fields (e.g., hole cards, board patterns).

Normalize continuous inputs (hand_equity, pot_odds, stack ratios).

Train a classifier (e.g., gradient boosting or a shallow neural net) to predict discrete action classes (fold/check/call/raise).

For predicting bet_size, either use a regression head or discretize sizes into buckets and treat it as a multiclass problem.

Reinforcement Learning Refinement

Policy Representation: Reuse the supervised model’s architecture, but switch to an RL loss (e.g., policy gradient or advantage actor-critic).

Reward Signal: +1 unit for each chip won, –1 unit for each chip lost (optionally scale by pot size).

Training Loop:

Initialize policy weights from the supervised model.

For each training episode:

The policy plays multiple hands vs. Bot A and Bot B.

Track per-hand trajectory (state → action → reward).

Compute “return” for each decision node (e.g., discounted sum of future rewards).

Update policy weights to maximize expected return.

Periodically evaluate performance (win rate) against both rule-based bots to measure exploitative improvement.

🎯 Final Objectives & Milestones
Milestone 1: Data Generation & Sanity Checks

Implement two rule-based bots (A and B) with distinct preflop ranges and postflop thresholds.

Generate 25 000 hands, inspect edge cases (e.g., turn-raise on paired boards).

Validate DataFrame schema and ensure feature consistency (hand equity matches board texture).

Milestone 2: Supervised Policy Baseline

Use 100 000+ bot-vs-bot hand records to train a baseline policy network.

Reach ≥ 85 % per-decision accuracy in predicting Bot A/B actions on a held-out validation set.

Verify that the model smooths out deterministic patterns (e.g., bet sizes vary ±10 %).

Milestone 3: Initial RL Refinement

Fine-tune the baseline policy via self-play/reinforcement learning against Bot A and Bot B.

Achieve an average win rate of ≥ 60 % when playing 5 000 fresh hands against Bot A or B individually.

Monitor exploit patterns (e.g., how often the RL policy three-bets Bot B’s weak opens).

Milestone 4: Opponent Modeling & Real-Time Adaptation

Add a lightweight opponent classifier that, after observing 10–20 actions, predicts whether the opponent is “A-style” or “B-style.”

Let the policy condition its decisions on the predicted opponent type.

Demonstrate a ≥ 70 % win rate over 5 000 hands when adapting mid-hand vs. mixed Bot A/B sequences.

Milestone 5: Human-Level Performance Test

Pit the final agent against human opponents (online or local) at any heads-up No-Limit Hold’em table.

Record win rate over 10 000 hands or a standardized session length (e.g., 100 big blinds per match).

Aim for a final profit rate that resembles a low-stakes pro (e.g., +5 BB/100 hands or higher).

🚧 Requirements
Python 3.8+

pandas, numpy, scikit-learn (for preprocessing and baseline models)

PyTorch or TensorFlow (for neural-network architectures and RL)

Optional: equity-evaluator library (e.g., Deuces or FastPoker)

OpenAI API key (if you choose to experiment with API-driven simulations alongside rule-based bots)


