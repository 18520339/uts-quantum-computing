from board import Board
from widgets import QuantumT3Widgets
from IPython.display import clear_output

      
class QuantumT3GUI(QuantumT3Widgets):
    def __init__(self, size=3, simulator=None):
        super().__init__(Board(size, simulator), 'X', 'CLASSICAL')         
        self.quantum_moves_selected = [] # Selected cells for operation on multi-qubit gates 
        self.game_over = False

    
    def buttons_disabled(self, is_disabled=True):
        for btn in self.action_buttons.children[1:]: btn.disabled = is_disabled
        for row in self.buttons:
            for btn in row: btn.disabled = is_disabled  
    
    
    def update_entire_board(self):
        for row in range(self.board.size):
            for col in range(self.board.size):
                cell = self.board.cells[row][col]
                color_map = {'X': 'dodgerblue', 'O': 'purple', '?': 'green', ' ': 'lightgray'}
                self.buttons[row][col].description = cell if cell != ' ' else ' '
                self.buttons[row][col].style.button_color = color_map[cell[-1]]
    
    
    def clean_incompleted_quantum_moves(self):
        for row, col in self.quantum_moves_selected: 
            if self.board.cells[row][col] == ' ':
                self.buttons[row][col].description = ' '
                self.buttons[row][col].style.button_color = 'lightgray'
        self.quantum_moves_selected = []

        
    def on_reset_btn_clicked(self, btn=None):
        with self.log:
            clear_output(wait=True)
            self.board = Board(self.board.size, self.board.simulator) 
            self.current_player = 'X'
            self.quantum_move_mode = 'CLASSICAL'
            self.quantum_moves_selected = []
            self.game_info.value = f'<b>Current Player: {self.current_player} / Quantum Mode: {self.quantum_move_mode}</b>'
            self.game_over = False
            
            self.update_entire_board()
            self.buttons_disabled(False)
            self.entangled_options.disabled = True
            
            with self.histogram_output: clear_output()
            with self.circuit_output: clear_output()
            print('Game reset. New game started.')
            
            
    def on_collapse_btn_clicked(self, btn=None):
        with self.log:
            if self.quantum_moves_selected: 
                print('Please complete the current quantum operation before measuring the board.')
                return
            
            clear_output(wait=True)
            counts = self.board.collapse_board()
            self.display_histogram(counts)
            self.update_entire_board() # Update the board cells with the collapsed states
            self.check_win()
            print('Board measured and quantum states collapsed.')
            
    
    def on_move_clicked(self, mode, message=''):
        with self.log:
            clear_output(wait=True)
            self.quantum_move_mode = mode
            self.game_info.value = f'<b>Current Player: {self.current_player} / Quantum Mode: {self.quantum_move_mode}</b>'
            self.clean_incompleted_quantum_moves()
            
            for row in self.buttons:
                for button in row: button.disabled = mode == 'ENTANGLED'
                
            if mode == 'ENTANGLED': self.entangled_options.value = 0
            self.entangled_options.disabled = mode != 'ENTANGLED'
            print(f'{mode} mode ACTIVATED' + (f': {message}' if message else ''))

    
    def on_cell_clicked(self, btn, row, col):
        with self.log:
            if self.quantum_move_mode == 'CLASSICAL': self.make_classical_move(row, col)
            elif self.quantum_move_mode == 'SUPERPOSITION': 
                btn.description = self.current_player + '?'
                btn.style.button_color = 'green'
                self.superposition_and_entanglement_wrapper(
                    func = self.board.make_superposition_move, pos = (row, col), 
                    success_msg='Cell is now in superposition state.')
                
            elif len(self.quantum_moves_selected) < 3: # Multi-qubit gates operation
                self.quantum_moves_selected.append((row, col))
                print(f'Cell ({row + 1}, {col + 1}) selected for {self.quantum_move_mode} move.')
                
                if self.quantum_move_mode == 'SWAP' and len(self.quantum_moves_selected) == 2: self.make_swap_move()
                elif self.quantum_move_mode == 'ENTANGLED':
                    btn.description = self.current_player + '?'
                    btn.style.button_color = 'green'
                    total_empty_required = {1: 2, 2: 3, 3: 2, 4: 3} # Total empty cells required for each risk level
                    
                    if len(self.quantum_moves_selected) == total_empty_required[self.entangled_options.value]: 
                        self.superposition_and_entanglement_wrapper(
                            func = self.board.make_entangled_move, pos = self.quantum_moves_selected,
                            success_msg='These positions are now entangled and in a superposition state.')


    def make_classical_move(self, row, col):
        if self.board.make_classical_move(row, col, self.current_player): 
            self.buttons[row][col].description = self.board.cells[row][col]
            self.buttons[row][col].style.button_color = 'dodgerblue' if self.current_player == 'X' else 'purple'
            self.check_win()
        else: print('That position is already occupied. Please choose another.')
        
 
    def make_swap_move(self):
        if self.board.make_swap_move(*self.quantum_moves_selected[0], *self.quantum_moves_selected[1]):
            print(f'SWAPPED Cell {self.quantum_moves_selected[0]} to {self.quantum_moves_selected[1]}')
            row1, col1 = self.quantum_moves_selected[0][0], self.quantum_moves_selected[0][1]
            row2, col2 = self.quantum_moves_selected[1][0], self.quantum_moves_selected[1][1]
            
            # Swap the description and color of the selected cells
            self.buttons[row1][col1].description, self.buttons[row2][col2].description = \
                self.buttons[row2][col2].description, self.buttons[row1][col1].description   
            self.buttons[row1][col1].style.button_color, self.buttons[row2][col2].style.button_color = \
                self.buttons[row2][col2].style.button_color, self.buttons[row1][col1].style.button_color
            self.check_win()
        else:
            clear_output(wait=True)
            self.quantum_moves_selected = []
            print('Invalid SWAP move. Both cells must be non-empty.')


    def superposition_and_entanglement_wrapper(self, func, pos, success_msg):
        if func(*pos, risk_level=self.entangled_options.value, player_mark=self.current_player): 
            print(success_msg)
            if self.board.can_be_collapsed():
                print('Perform automatic board measurement and collapse the states.')
                self.quantum_moves_selected = []
                self.on_collapse_btn_clicked()
            else: self.check_win()
        else:
            clear_output(wait=True)
            self.clean_incompleted_quantum_moves()
            print('Invalid quantum move. A position is already occupied.')
    

    def check_win(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X' # Switch players
        self.game_info.value = f'<b>Current Player: {self.current_player} / Quantum Mode: {self.quantum_move_mode}</b>'
        self.quantum_moves_selected = []
                
        while not self.game_over: # Check if the game is over after each move
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
        if self.game_over: self.buttons_disabled(True)