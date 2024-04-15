from board import Board
    
class QuantumTicTacToeCLI:
    def __init__(self):
        self.board = Board(3)
        self.current_player = 'X' # X starts the game

             
    def run_game(self):
        print('Welcome to Quantum Tic-Tac-Toe!')
        print('Players take turns making classical/entangled moves on the board.')
        print(self.board)
        
        while True:
            user_input = input("Type 1 for classical, 2 for entangled, or 'q' to exit: ")
            if user_input == '1': self.make_classical_move()
            elif user_input == '2': self.make_entangled_move()
            elif user_input.lower() == 'q': return
    

if __name__ == '__main__':
    game = QuantumTicTacToeCLI()
    game.run_game()