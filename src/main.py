from board import Board
from player import HumanPlayer, AIPlayer

class Game:
    def __init__(self):
        self.board = Board()
        self.players = []
        self.current_player_index = 0
    
    def setup(self):
        """Configure game mode"""
        print("=== Tic-Tac-Toe with Minimax AI ===")
        print("1. Human vs AI")
        print("2. AI vs AI (demo)")
        print("3. Human vs Human")
        
        choice = input("Choose mode (1-3): ")
        
        if choice == '1':
            human_letter = input("Choose X or O: ").upper()
            while human_letter not in ['X', 'O']:
                human_letter = input("Invalid. Choose X or O: ").upper()
            
            ai_letter = 'O' if human_letter == 'X' else 'X'
            self.players = [
                HumanPlayer(human_letter),
                AIPlayer(ai_letter, 'hard')
            ]
            if human_letter == 'O':
                self.current_player_index = 1
        
        elif choice == '2':
            self.players = [
                AIPlayer('X', 'hard'),
                AIPlayer('O', 'hard')
            ]
            print("AI vs AI - Watch Minimax in action!")
        
        else:
            self.players = [
                HumanPlayer('X'),
                HumanPlayer('O')
            ]
    
    def play(self):
        """Main game loop"""
        self.setup()
        
        while True:
            self.board.display()
            current_player = self.players[self.current_player_index]
            
            print(f"\n{current_player.letter}'s turn")
            
            # Get move (returns (row, col) tuple)
            row, col = current_player.get_move(self)
            
            # Make move
            if self.board.make_move(row, col, current_player.letter):
                print(f"Placed {current_player.letter} at ({row}, {col})")
                
                # Check win
                winner = self.board.check_winner()
                if winner in ['X', 'O']:
                    self.board.display()
                    print(f"\n {winner} wins!")
                    break
                elif winner == "Draw":
                    self.board.display()
                    print("\n It's a draw!")
                    break
                
                # Switch players
                self.current_player_index = 1 - self.current_player_index
            else:
                print("Invalid move! Try again.")
        
        # Play again
        again = input("\nPlay again? (y/n): ").lower()
        if again == 'y':
            self.board.reset()
            self.current_player_index = 0
            self.play()
        else:
            print("Thanks for playing!")

if __name__ == "__main__":
    game = Game()
    game.play()
