class Board:
    def __init__(self):
        self.grid = [
            [" ", " ", " "],
            [" ", " ", " "],
            [" ", " ", " "]
        ]

    def display(self):
        """Prints the board to the console in a grid format."""
        for row in self.grid:
            print("| " + " | ".join(row) + " |")
            print("-" * 13)

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
                return self.grid[i][0]
            # Columns
            if self.grid[0][i] == self.grid[1][i] == self.grid[2][i] != " ":
                return self.grid[0][i]

        # 2. Check Diagonals
        if self.grid[0][0] == self.grid[1][1] == self.grid[2][2] != " ":
            return self.grid[0][0]
        if self.grid[0][2] == self.grid[1][1] == self.grid[2][0] != " ":
            return self.grid[0][2]

        # 3. Check for Draw (No empty spaces left)
        if len(self.get_empty_positions()) == 0:
            return "Draw"

        return None # Game still in progress
    

