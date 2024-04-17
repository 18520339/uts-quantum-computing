from board import Board
from widgets import QuantumT3Widgets
from IPython.display import clear_output

      
class QuantumT3GUI(QuantumT3Widgets):
    def __init__(self, size=3):
        super().__init__(Board(size), 'X', 'CLASSICAL')         
        self.quantum_moves_selected = [] # Selected cells for operation on multi-qubit gates 
        self.game_over = False

    
    def buttons_disabled(self, is_disabled=True):
        for btn in self.action_buttons.children[1:]: btn.disabled = is_disabled
        for row in self.buttons:
            for btn in row: btn.disabled = is_disabled  
            
        
    def on_reset_btn_clicked(self, btn=None):
        with self.log:
            clear_output(wait=True)
            self.board = Board(self.board.size) 
            self.current_player = 'O' # Set 'O' as update_board will switch the players
            self.game_over = False
            self.quantum_move_mode = 'CLASSICAL'
            self.quantum_moves_selected = []
            
            self.update_board()
            self.buttons_disabled(False)
            self.entangled_options.disabled = True
            print('Game reset. New game started.')
            
            
    def on_collapse_btn_clicked(self, btn=None):
        with self.log:
            if self.quantum_moves_selected: 
                print('Please complete the current quantum operation before measuring the board.')
                return
            
            clear_output(wait=True)
            counts = self.board.collapse_board()
            self.display_histogram(counts)
            self.update_board()
            print('Board measured and quantum states collapsed.')
            
    
    def on_move_clicked(self, mode, message=''):
        with self.log:
            clear_output(wait=True)
            self.quantum_move_mode = mode
            self.quantum_moves_selected = []
            self.game_info.value = f'<b>Current Player: {self.current_player} / Quantum Mode: {self.quantum_move_mode}</b>'
            
            for row in self.buttons:
                for button in row: button.disabled = mode == 'ENTANGLED'
                
            if mode == 'ENTANGLED': self.entangled_options.value = 0
            self.entangled_options.disabled = mode != 'ENTANGLED'
            print(f'{mode} mode ACTIVATED' + (f': {message}' if message else ''))

    
    def on_cell_clicked(self, row, col):
        with self.log:
            if self.quantum_move_mode == 'CLASSICAL':
                if self.board.make_classical_move(row, col, self.current_player): self.update_board()
                else: print('That position is already occupied. Please choose another.')
                
            elif self.quantum_move_mode == 'SUPERPOSITION': 
                self.superposition_and_entanglement_wrapper(
                    func = self.board.make_superposition_move, pos = (row, col), 
                    success_msg='Cell is now in superposition state.')
                
            elif len(self.quantum_moves_selected) < 3: # Multi-qubit gates operation
                # Check if there are enough empty cells for the selected operation
                self.quantum_moves_selected.append((row, col))
                print(f'Cell ({row + 1}, {col + 1}) selected for {self.quantum_move_mode} move.')
                
                selected_count = len(self.quantum_moves_selected)
                if self.quantum_move_mode == 'SWAP' and selected_count == 2: self.make_swap_move()
                elif self.quantum_move_mode == 'ENTANGLED' and (
                    (selected_count == 2 and self.entangled_options.value in [1, 3]) or \
                    (selected_count == 3 and self.entangled_options.value in [2, 4])):
                    self.superposition_and_entanglement_wrapper(
                        func = self.board.make_entangled_move, pos = self.quantum_moves_selected,
                        success_msg='These positions are now entangled and in a superposition state.')

 
    def make_swap_move(self):
        if self.board.make_swap_move(*self.quantum_moves_selected[0], *self.quantum_moves_selected[1]):
            print(f'SWAPPED Cell {self.quantum_moves_selected[0]} to {self.quantum_moves_selected[1]}')
            self.update_board()
        else:
            clear_output(wait=True)
            print('Invalid SWAP move. Both cells must be non-empty.')
        self.quantum_moves_selected = []


    def superposition_and_entanglement_wrapper(self, func, pos, success_msg):
        if func(*pos, risk_level=self.entangled_options.value, player_mark=self.current_player): 
            print(success_msg)
            if self.board.can_be_collapsed():
                print('Perform automatic board measurement and collapse the states.')
                self.quantum_moves_selected = []
                self.on_collapse_btn_clicked()
            else: self.update_board()
        else:
            clear_output(wait=True)
            print('Invalid quantum move. A position is already occupied.')
        self.quantum_moves_selected = []
    

    def update_board(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X' # Switch players
        self.game_info.value = f'<b>Current Player: {self.current_player} / Quantum Mode: {self.quantum_move_mode}</b>'
        
        for i in range(self.board.size):
            for j in range(self.board.size):
                cell = self.board.cells[i][j]
                button = self.buttons[i][j]
                color_map = {'X': 'dodgerblue', 'O': 'purple', '?': 'green', ' ': 'lightgray'}
                button.description = cell if cell != ' ' else ' '
                button.style.button_color = color_map[cell[-1]]
                
        self.check_win() # Check if the game is over after each move
        if self.game_over: self.buttons_disabled()
        

    def check_win(self):
        while not self.game_over: 
            self.display_circuit()
            result = self.board.check_win()
            
            if result == 'Draw': 
                self.game_over = True
                print("Game Over. It's a draw!")
                
            elif type(result) == tuple: 
                self.game_over = True
                for cell_index in result: 
                    i, j = divmod(cell_index, self.board.size)
                    self.buttons[i][j].style.button_color = 'orangered'
                print(f'Game Over. {self.board.cells[i][j]} wins!')
                
            elif type(result) == int: 
                print(f'All cells are filled but {result} of them still in superpositions => Keep Collapsing...')
                self.quantum_moves_selected = []
                self.on_collapse_btn_clicked() # All cells are filled but some are still in superpositions 
                break
            else: break # Continue the game if no winner yet