from board import Board
    
class QuantumTicTacToeCLI:
    def __init__(self):
        self.board = Board(3)
        self.current_player = 'X' # X starts the game


    def input_to_index(self, user_input):
        try: # Convert user input into board indices
            row, col = map(int, user_input.split())
            if row >= 1 and row <= self.board.size and col >= 1 and col <= self.board.size:
                return row - 1, col - 1 # Convert to 0-indexing
            raise ValueError
        except ValueError:
            print("Invalid input. Please enter row and column as 'row col'. E.g., '1 2'")
            return None


    def make_classical_move(self):
        user_input = input(f"{self.current_player}'s turn to move (row col): ")
        indices = self.input_to_index(user_input)
        if not indices: return
        
        row, col = indices
        if self.board.make_classical_move(row, col, self.current_player): self.check_win()
        else: print('That position is already occupied. Please choose another.')

    
    def make_swap_move(self):
        # Prompt the player to choose 2 cells for a SWAP move and execute it
        print(f"{self.current_player}'s turn to move. Enter 2 positions to swap their quantum states:")
        indices1 = self.input_to_index(input('- First position: '))
        if not indices1: return
        indices2 = self.input_to_index(input('- Second position: '))
        if not indices2: return
        
        if self.board.make_swap_move(*indices1, *indices2): self.check_win()
        else: print('Invalid SWAP move. Both cells must be non-empty.')
            

    def make_entangled_move(self):
        # Let the player make an entangled move involving 2 positions
        print(f"{self.current_player}'s turn to move. Enter 2 positions to entangle:")
        indices1 = self.input_to_index(input('- First position: '))
        if not indices1: return
        indices2 = self.input_to_index(input('- Second position: '))
        if not indices2: return
            
        if self.board.make_entangled_move(*indices1, *indices2, self.current_player):
            print('These positions are now entangled and in a superposition state.')
            if self.board.can_be_collapsed(): 
                print(self.board)
                print('Performing automatic board measurement...')
                self.board.collapse_board()
            self.check_win()
        else: print('Invalid entangled move. At least 1 position is occupied.')

    
    def check_win(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X' # Switch players
        while True: 
            print(self.board)
            result = self.board.check_win()
            
            if result == 'Draw': 
                print("Game Over. It's a draw!")
                exit()
            elif result in ['X', 'O']: 
                print(f'Game Over. {result} wins!')
                exit()
            elif type(result) == int: 
                print(f'All cells are filled with {result} entanglements => Keep Collapsing...')
                self.board.collapse_board() # All cells are filled but there are entanglements 
            else: return # Continue the game if no winner yet
            

    def run_game(self):
        print('Welcome to Quantum Tic-Tac-Toe!')
        print('Players take turns making classical/entangled moves on the board.')
        print(self.board)
        
        while True:
            choose = input('Classical Move (1), SWAP Move (2), Entangled Move (3), Quit (q). Choose a move: ')
            if choose == '1': self.make_classical_move()
            elif choose == '2': self.make_swap_move()
            elif choose == '3': self.make_entangled_move()
            elif choose.lower() == 'q': return
    

if __name__ == '__main__':
    game = QuantumTicTacToeCLI()
    game.run_game()