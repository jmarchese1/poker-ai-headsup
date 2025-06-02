# Poker AI for Heads-Up Hold'em ♠️♥️

This project is an experimental journey to build a poker AI capable of consistently beating real players in heads-up No Limit Texas Hold’em. Inspired by AlphaZero, the ultimate goal is to create an agent that not only plays optimally using card and pot odds but also learns to read and adapt to opponents’ specific tendencies and play styles.

🔍 Overview: The repository includes two main AI training approaches:

ChatGPT Simulation (API-Driven) Using OpenAI's API, the AI plays thousands of games against itself. ChatGPT makes all in-game decisions (fold, call, raise) based on context: hole cards, community cards, stack sizes, betting history, and more.

From-Scratch Reinforcement Engine An organic simulation loop where the AI initially selects actions randomly. As results accumulate, they’re stored in a Pandas DataFrame and analyzed over time to inform future decisions based on hand strength, position, and outcomes.

🧠 Learning Process:

Every hand’s data is logged into a structured Pandas DataFrame: board state, player hands, stack sizes, betting history, action taken, and win/loss outcome.

After thousands of hands, this dataset is passed into deep learning models to:

Identify high-value patterns and strategic behaviors.
Model opponent types based on historical actions.
Move toward Game Theory Optimal (GTO) and exploitative strategies.
🎯 Final Objective

To develop an AI agent that mirrors the strategic dominance of AlphaZero in chess—but for poker. This includes:

Consistently making mathematically sound decisions.
Adapting dynamically to different player archetypes.
Modeling opponents in real-time and exploiting weaknesses.
🚧 Requirements Python 3.8+

pandas, numpy

OpenAI API key (for ChatGPT simulations)
