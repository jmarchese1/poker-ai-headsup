# ♠️ Poker AI Simulation Engine for No-Limit Hold’em ♣️

### Overview
This is a solo-developed simulation engine designed to model complete hands of No-Limit Texas Hold’em poker. It focuses on building an adaptable environment for AI agents to play, learn, and compete against each other with the goal of evolving toward intelligent, real-time strategy.

The codebase is built for flexibility. It starts with structured, rule-based decision making and is designed to scale into full machine learning and reinforcement learning integrations. Every part of the logic is crafted to support future development, data generation, and training pipelines.

### Project Vision
This project is not just about simulating a game. The vision is to create a poker engine where bots begin by following simple rules and eventually grow into agents that adapt to opponents, identify patterns, and change their play accordingly.

The long-term goal is to build an AI that blends sound game theory with the ability to exploit suboptimal behavior. Starting with consistent rule-based systems, the engine will generate large datasets, which can then be used to train supervised models. These models will be refined with reinforcement learning to pursue long-term profit and strategic edge.

### Bot Architecture
Bots are objects built from a shared parent class that handles core poker logic. Each child bot has its own personality and logic for decision making. This structure allows for diverse styles, such as aggressive, passive, balanced, or unpredictable players.

Bots can respond to the current pot, hand strength, position, and history of actions. Raise loops are supported and continue until all contributions are equal or a fold ends the action. The system ensures chips, contributions, and decision timing are handled realistically.

### Game Flow Structure
The game simulates a full seven-player table. Each hand is played with structured logic that mimics the real rules of poker:

Players rotate positions clockwise between hands
Blinds are posted and deducted from chip stacks
Players act in order with the option to fold, call, or raise
Raises follow logical bet sizing based on position and prior actions
Once all contributions are equal or everyone folds but one player, the hand ends
If only one player remains, they immediately win the pot

This preflop system is already functional. Future updates will extend this to flop, turn, river, and showdown stages.

### Data and Learning Pipeline
The long-term value of this engine is its ability to generate high-quality decision data at scale. Once all game stages are implemented, each decision will be recorded with relevant context:

Hole cards, board texture, and position
Pot size, player chip stacks, and required call amounts
Equity estimates and pot odds
Chosen action, bet size, and final outcome

This data will be stored in structured formats such as Pandas DataFrames for model training. It will support both classification and regression models, and eventually reinforcement learning pipelines.

### What’s Next
Add logic for flop, turn, river, and showdown stages
Implement board evaluation to determine hand strength at each street
Create a full hand logging system to track outcomes and decision data
Add hand equity estimators for better strategic insight
Expand bot types to include tight, loose, balanced, and adaptive agents
Build opponent modeling tools for dynamic strategy switching

### Technical Stack
Python 3.8 or higher
Core libraries: pandas, numpy, random
Optional libraries for future stages: scikit-learn, PyTorch, Deuces, Treys

### About This Project
This is a one-person project built from scratch with the purpose of mastering strategic AI development. It is both a technical challenge and a personal exploration into building intelligent systems. Every function, loop, and decision engine is designed with clarity and extensibility in mind. 




