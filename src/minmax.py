class MinimaxEngine:
    def __init__(self, ai_letter):
        self.ai_letter = ai_letter
        self.opponent_letter = 'O' if ai_letter == 'X' else 'X'
    
    def get_best_move(self, board):
        """Returns best move as (row, col) tuple"""
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        for (row, col) in board.get_empty_positions():
            # Try the move
            board.make_move(row, col, self.ai_letter)
            
            # Get score for this move
            score = self.minimax(board, 0, False, alpha, beta)
            
            # Undo the move
            board.grid[row][col] = " "
            board.current_winner = None
            
            # Update best move
            if score > best_score:
                best_score = score
                best_move = (row, col)
            
            alpha = max(alpha, score)
        
        return best_move
    
    def minimax(self, board, depth, is_maximizing, alpha, beta):
        """Recursive Minimax with Alpha-Beta pruning"""
        # Base cases
        winner = board.check_winner()
        if winner == self.ai_letter:
            return 10 - depth
        elif winner == self.opponent_letter:
            return depth - 10
        elif winner == "Draw":
            return 0
        
        if is_maximizing:
            max_eval = float('-inf')
            for (row, col) in board.get_empty_positions():
                board.make_move(row, col, self.ai_letter)
                eval = self.minimax(board, depth + 1, False, alpha, beta)
                board.grid[row][col] = " "
                board.current_winner = None
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for (row, col) in board.get_empty_positions():
                board.make_move(row, col, self.opponent_letter)
                eval = self.minimax(board, depth + 1, True, alpha, beta)
                board.grid[row][col] = " "
                board.current_winner = None
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
