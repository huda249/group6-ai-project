class Player:
    def __init__(self, letter):
        self.letter = letter

    def get_move(self, game):
        pass


class HumanPlayer(Player):
    def __init__(self, letter):
        super().__init__(letter)

    def get_move(self, game):
        """Get valid move from human user"""
        valid_move = False
        while not valid_move:
            try:
                row = int(input(f"Player {self.letter}, enter row (0-2): "))
                col = int(input(f"Enter column (0-2): "))

                if row not in [0, 1, 2] or col not in [0, 1, 2]:
                    raise ValueError

                if game.board.grid[row][col] == " ":
                    valid_move = True
                    return (row, col)
                else:
                    print("Position taken. Choose another.")
            except ValueError:
                print("Invalid input. Enter numbers 0-2.")


class AIPlayer(Player):
    def __init__(self, letter, difficulty='hard'):
        super().__init__(letter)
        self.difficulty = difficulty

    def get_move(self, game):
        """AI selects move using Minimax"""
        if self.difficulty == 'hard':
            from minmax import MinimaxEngine
            engine = MinimaxEngine(self.letter)
            row, col = engine.get_best_move(game.board)
            return (row, col)
        else:
            import random
            return random.choice(game.board.get_empty_positions())