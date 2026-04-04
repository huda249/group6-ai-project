class Board:
    def __init__(self):
        self.grid = [
            [" ", " ", " "],
            [" ", " ", " "],
            [" ", " ", " "]
        ]
        self.current_winner = None  # Tracks current winner (X, O, or None)

    def display(self):
        """Prints the board to the console in a grid format."""
        for i, row in enumerate(self.grid):
            print("| " + " | ".join(row) + " |")
            if i < 2:  # Don't print line after last row
                print("-" * 13)
        print()  # Extra line for spacing

    def get_empty_positions(self):
        """Returns a list of (row, col) tuples for empty spots."""
        choices = []
        for r in range(3):
            for c in range(3):
                if self.grid[r][c] == " ":
                    choices.append((r, c))
        return choices

    def check_winner(self):
        """Returns 'X', 'O', 'Draw', or None."""
        # 1. Check Rows and Columns
        for i in range(3):
            # Rows
            if self.grid[i][0] == self.grid[i][1] == self.grid[i][2] != " ":
                self.current_winner = self.grid[i][0]
                return self.grid[i][0]
            # Columns
            if self.grid[0][i] == self.grid[1][i] == self.grid[2][i] != " ":
                self.current_winner = self.grid[0][i]
                return self.grid[0][i]

        # 2. Check Diagonals
        if self.grid[0][0] == self.grid[1][1] == self.grid[2][2] != " ":
            self.current_winner = self.grid[0][0]
            return self.grid[0][0]
        if self.grid[0][2] == self.grid[1][1] == self.grid[2][0] != " ":
            self.current_winner = self.grid[0][2]
            return self.grid[0][2]

        # 3. Check for Draw (No empty spaces left)
        if len(self.get_empty_positions()) == 0:
            return "Draw"

        self.current_winner = None
        return None  # Game still in progress

    def make_move(self, row, col, letter):
        """
        Places a letter (X or O) at the specified position.
        Returns True if move was valid, False otherwise.
        """
        # Check if position is within bounds and empty
        if 0 <= row < 3 and 0 <= col < 3 and self.grid[row][col] == " ":
            self.grid[row][col] = letter
            
            # Check if this move wins the game
            if self.check_winner() == letter:
                self.current_winner = letter
            
            return True
        return False

    def is_full(self):
        """
        Checks if the board is completely filled.
        Returns True if no empty positions remain, False otherwise.
        """
        return len(self.get_empty_positions()) == 0

    def reset(self):
        """
        Resets the board to empty state for a new game.
        Clears all marks and resets winner tracking.
        """
        self.grid = [
            [" ", " ", " "],
            [" ", " ", " "],
            [" ", " ", " "]
        ]
        self.current_winner = None

    def get_board_state(self):
        """
        Returns a deep copy of the current board grid.
        Useful for AI algorithms that need to simulate moves.
        """
        return [row[:] for row in self.grid]

    def is_valid_move(self, row, col):
        """
        Checks if a move at (row, col) is valid.
        Returns True if position is empty and within bounds.
        """
        return 0 <= row < 3 and 0 <= col < 3 and self.grid[row][col] == " "

    def get_winner(self):
        """
        Returns the current winner (X, O, Draw, or None).
        Useful for checking game status without re-evaluating.
        """
        return self.check_winner()
