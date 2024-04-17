import ipywidgets as widgets
from IPython.display import clear_output
from termcolor import colored

from qiskit.visualization import plot_bloch_multivector, plot_histogram
from board import Board

      
class QuantumTicTacToeGUI:
    def __init__(self, size=3):
        self.board = Board(size)
        self.current_player = 'X' # X starts the game
        self.game_over = False
            
        self.quantum_move_mode = 'CLASSICAL'
        self.quantum_moves_selected = [] # Selected cells for operation on multi-qubit gates 

        self.log = widgets.Output(layout={'margin': '10px 0 0 0'})
        self.histogram_output = widgets.Output(layout={'margin': '0 0 10px 10px'})
        self.circuit_output = widgets.Output()
        self.create_widgets()
                    
            
    def create_widgets(self):
        # Create widgets for each cell and controls for game actions
        self.buttons = []
        for i in range(self.board.size):
            self.buttons.append([])
            for j in range(self.board.size):
                button = widgets.Button(
                    description = ' ', 
                    layout = {'width': '100px', 'height': '100px', 'border': '1px solid black'},
                    style = {'button_color': 'lightgray', 'font_weight': 'bold'}
                )
                button.on_click(self.create_on_cell_clicked(i, j))
                self.buttons[i].append(button)

        self.create_action_buttons()
        self.game_info = widgets.HTML(f'<b>Current Player: {self.current_player} / Quantum Mode: {self.quantum_move_mode}</b>')
        
        self.board_histogram_widget = widgets.HBox([
            widgets.VBox([
                widgets.VBox([widgets.HBox(row) for row in self.buttons]), 
                self.game_info
            ]), 
            self.histogram_output
        ], layout = {'display': 'flex', 'justify_content': 'center', 'align_items': 'flex-end'})
        display(widgets.VBox([self.board_histogram_widget, self.action_buttons, self.log, self.circuit_output]))


    def create_action_buttons(self):
        self.reset_btn = widgets.Button(description='Reset', button_style='danger')
        self.measure_btn = widgets.Button(description='Measure', button_style='warning')
        self.classical_btn = widgets.Button(description='Classical Move', button_style='primary')
        self.swap_btn = widgets.Button(description='SWAP Move', button_style='info')
        self.superposition_btn = widgets.Button(description='Superposition', button_style='success')
        
        self.entangled_btn = widgets.Button(description='Entanglement', button_style='success')
        self.entangled_options = widgets.Dropdown(options=[
            ('', 0), # Qubits collapse to opposite states (not consecutive)
            ('Lv1. PAIRWAISE: ∣Ψ+⟩ = (∣01⟩ + ∣10⟩) / √2', 1), # Qubits collapse to opposite states (not consecutive)
            ('Lv2. TRIPLE: GHZ_Xs = (∣010⟩ + ∣101⟩) / √2', 2),
            ('Lv3. PAIRWAISE: ∣Φ+⟩ = (∣00⟩ + ∣11⟩) / √2', 3), # Can form consecutive winning cells or accidentally help the opponent
            ('Lv4. TRIPLE: GHZ = (∣000⟩ + ∣111⟩) / √2', 4),
        ], value=0, disabled=True)
        self.entangled_options.observe(self.update_entangled_options, names='value')
        
        self.reset_btn.on_click(self.on_reset_btn_clicked)
        self.measure_btn.on_click(self.on_measure_btn_clicked)
        self.classical_btn.on_click(self.create_on_quantum_clicked('CLASSICAL'))
        self.swap_btn.on_click(self.create_on_quantum_clicked('SWAP', 'Select 2 cells to swap their states.'))
        self.superposition_btn.on_click(self.create_on_quantum_clicked('SUPERPOSITION', 'Select a cell to put in superposition.'))
        self.entangled_btn.on_click(self.create_on_quantum_clicked('ENTANGLED', 'Select 2/3 cells based on risk level to entangle.'))
        
        self.action_buttons = widgets.HBox([
            self.reset_btn, self.measure_btn, self.classical_btn, self.swap_btn, 
            self.superposition_btn, self.entangled_btn, self.entangled_options
        ])
        
        
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
            
            
    def on_measure_btn_clicked(self, btn=None):
        with self.log:
            if self.quantum_moves_selected: 
                print('Please complete the current quantum operation before measuring the board.')
                return
            
            clear_output(wait=True)
            counts = self.board.collapse_board()
            self.display_histogram(counts)
            self.update_board()
            print('Board measured and quantum states collapsed.')
            

    def buttons_disabled(self, is_disabled=True):
        for btn in self.action_buttons.children[1:]: btn.disabled = is_disabled
        for row in self.buttons:
            for btn in row: btn.disabled = is_disabled   


    def update_entangled_options(self, change):
        with self.log:
            self.entangled_options.disabled = change.new != 0
            for row in self.buttons:
                for button in row: button.disabled = change.new == 0
                
            # Check if there are enough empty cells for the selected operation
            empty_count = sum(cell == ' ' for row in self.board.cells for cell in row)
            empty_map = {1: 2, 2: 3, 3: 2, 4: 3}
                
            if change.new == 0: return
            elif empty_count < empty_map[change.new]:
                print(f'Not enough empty cells to perform entanglement with risk level {change.new}. Please select another.')
                self.entangled_options.value = 0
            else:
                print(f'Risk Level {change.new} ACTIVATED for Entanglement mode =>', end=' ')
                if change.new in [1, 3]: print(f'Select 2 cells (qubits) for this PAIRWAISE entanglement.')
                else: print(f'Select 3 cells (qubits) for this TRIPLE entanglement.')
    
    
    def create_on_quantum_clicked(self, mode, message=''):
        def on_quantum_clicked(btn):
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
        return on_quantum_clicked
    

    def create_on_cell_clicked(self, i, j):
        def on_cell_clicked(btn):
            with self.log:
                if self.quantum_move_mode == 'CLASSICAL':
                    if self.board.make_classical_move(i, j, self.current_player): self.update_board()
                    else: print('That position is already occupied. Please choose another.')
                    
                elif self.quantum_move_mode == 'SUPERPOSITION': 
                    self.superposition_and_entanglement_wrapper(
                        func = self.board.make_superposition_move, pos = (i, j), 
                        success_msg='Cell is now in superposition state.'
                    )
                elif len(self.quantum_moves_selected) < 3: # Multi-qubit gates operation
                    # Check if there are enough empty cells for the selected operation
                    self.quantum_moves_selected.append((i, j))
                    print(f'Cell ({i + 1}, {j + 1}) selected for {self.quantum_move_mode} move.')
                    
                    selected_count = len(self.quantum_moves_selected)
                    if self.quantum_move_mode == 'SWAP' and selected_count == 2: self.make_swap_move()
                    elif self.quantum_move_mode == 'ENTANGLED' and (
                        (selected_count == 2 and self.entangled_options.value in [1, 3]) or \
                        (selected_count == 3 and self.entangled_options.value in [2, 4])
                    ): self.superposition_and_entanglement_wrapper(
                        func = self.board.make_entangled_move, pos = self.quantum_moves_selected,
                        success_msg='These positions are now entangled and in a superposition state.'
                    )
        return on_cell_clicked


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
                print('Performing automatic board measurement...')
                self.quantum_moves_selected = []
                self.on_measure_btn_clicked()
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
                self.on_measure_btn_clicked() # All cells are filled but some are still in superpositions 
                break
            else: break # Continue the game if no winner yet
        

    def display_circuit(self):
        with self.circuit_output:
            clear_output(wait=True)
            display(self.board.circuit.draw('mpl'))


    def display_histogram(self, counts):
        with self.histogram_output:
            clear_output(wait=True)
            display(plot_histogram(counts, figsize=(9, 4)))