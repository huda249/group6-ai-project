
# group6-ai-project
## Tic-Tac-Toe

A Python-based Tic-Tac-Toe implementation featuring an unbeatable AI engine. This project uses the Minimax algorithm with Alpha-Beta pruning to ensure optimal play.

## Features
* **Unbeatable AI:** Implements Minimax logic to guarantee a win or a draw.
* **Alpha-Beta Pruning:** Optimized search for faster decision-making.
* **Multiple Modes:** Support for Human vs AI, AI vs AI (simulation), and Human vs Human.

## Project Structure
The source code is located in the `src/` directory:
* `src/main.py`: The entry point and main controller for the terminal game.
* `src/board.py`: Manages the 3x3 grid, move validation, and win detection.
* `src/player.py`: Defines the Players (Human and AI classes).
* `src/minimax.py`: The core AI engine and mathematical optimization logic.
* `src/webDemo.py`: An alternative interface for web-based demonstrations.
* `src/__init__.py`: Handles package initialization.

## Installation
1. Ensure you have Python 3.x installed.
2. Clone this repository or download the source files.
3. (Optional) If using the web demo, install required dependencies:
   ```bash
   pip install flask
   ```

## Running the Program in Terminal
To play the game in your terminal, run the following command from the root directory:
   ```bash
   python src/main.py
   ```

## Running the Program in Web Browser
To play the game in your web browser, run the following command from the root directory:
   ```bash
   python src/webDemo.py
   ```
```
