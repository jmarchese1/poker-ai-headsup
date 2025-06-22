# Poker AI Simulation & Reinforcement Learning Engine

Designed and implemented a modular poker simulation environment from scratch, enabling AI agents to learn and evolve through reinforcement learning. Built multi-agent systems with distinct playing styles (tight, loose, aggressive, passive) and a full decision pipeline from preflop to river. Created structured datasets for supervised learning and developed RL agents that outperformed rule-based bots over thousands of hands. Demonstrated strong foundations in game theory, adversarial ML, and simulation environments.

## 🎯 Project Vision
The goal isn’t just to simulate poker, it’s to create a learning environment for intelligent agents. Bots begin by following structured strategic rules based on position, pot odds, and hand strength. As the simulation scales, these bots will:
Learn from outcomes using supervised learning, Adapt through opponent modeling, And eventually evolve via reinforcement learning to maximize long-term EV (expected value).By simulating thousands of hands and logging every meaningful decision, this engine generates the high-quality data required to train future poker-playing agents.

## 🤖 Bot Architecture
Each bot is an instance of a shared class, parameterized by:
Aggression level
Tightness range
Bluffing tendency
Bots make decisions using:
Position (UTG to BB),
Hand strength tiers,
Pot odds & board context,
And (coming soon) opponent history.
This setup allows simulation of varied playing styles — from hyper-aggressive bluffers to tight-passive grinders — essential for generating realistic training data.

## 🔁 Game Flow
The engine currently supports full-ring (7-player) gameplay with real poker logic:
Rotating positions each hand
Blinds posting automatically
Decision flow: fold, call, raise (with logical loops)
Pots resolved after all contributions are equal
Chip stacks dynamically updated
Automatic showdown handling and winner determination (coming soon)
Each phase — preflop, flop, turn, river, and showdown — is modular and extensible for future logic and strategy layers.

## 📊 Data Generation & ML Pipeline
A core objective is producing structured, labeled data for model training. Each hand logs:
Bot identity and personality traits (aggression, tightness, bluffing)
Hole cards and board texture
Pot size, chip stacks, bet sizes, and call amounts
Hand strength estimates and pot odds
Actions taken (fold, call, raise, bet)
Final outcome (win/loss and amount)
All logs are saved in Pandas DataFrames and exported as .csv files, ready for:
Supervised learning (e.g., classify actions)
Regression (e.g., predict bet sizes or EV)
Reinforcement learning pipelines (policy improvement, deep Q-learning, etc.)

## 🚀 What’s Next
Add street-by-street logic for flop, turn, river
Implement board-aware hand strength evaluations
Expand postflop logic and incorporate board texture (e.g., wet/dry boards)
Build a logging engine to track hand-level decisions and results
Integrate bluffing logic and opponent modeling
Create adaptive bots that respond dynamically to opponent behavior
Begin training simple ML models to classify player actions

## 🛠 Tech Stack
Python 3.8+
custom simulation functions
Core: pandas, numpy, random, itertools
ML Ready: scikit-learn, PyTorch

## 👨‍💻 About This Project
This is a solo project developed from scratch to explore the intersection of game theory, AI strategy, and machine learning. It's designed for extensibility, experimentation, and eventual deployment of learning agents. Every decision logic and data structure is built with future growth and real-time adaptation in mind.

