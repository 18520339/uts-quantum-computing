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
        self.circuit_output = widgets.Output()
        self.histogram_output = widgets.Output()
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
        ], layout = {'display': 'flex', 'justify_content': 'space-between', 'align_items': 'flex-end'})
        display(widgets.VBox([self.board_histogram_widget, self.action_buttons, self.log, self.circuit_output]))


    def create_action_buttons(self):
        # Create buttons for each action
        self.reset_btn = widgets.Button(description='Reset')
        self.measure_btn = widgets.Button(description='Measure', button_style='warning')
        self.classical_btn = widgets.Button(description='Classical Move', button_style='danger')
        self.swap_btn = widgets.Button(description='SWAP Move', button_style='success')
        
        self.superposition_btn = widgets.Button(description='Superposition', button_style='info')
        self.entangled_btn = widgets.Button(description='Entanglement', button_style='primary')
        self.entangled_options = widgets.Dropdown(
            options = [('PAIRWAISE: Hadamard-CNOT', 1), ('TRIPLE: Hadamard-CNOT-TOFFOLI', 2)], 
            value = 1 # Default is Pairwise Entanglement
        )
        
        # Assign the on-click events to the buttons
        self.reset_btn.on_click(self.on_reset_btn_clicked)
        self.measure_btn.on_click(self.on_measure_btn_clicked)
        self.classical_btn.on_click(self.create_on_quantum_clicked('CLASSICAL'))
        self.swap_btn.on_click(self.create_on_quantum_clicked('SWAP', 'Select 2 cells to swap their states.'))
        self.entangled_btn.on_click(self.create_on_quantum_clicked('ENTANGLED', 'Select 2 cells to entangle.'))
        
        # Arrange the buttons in a horizontal layout
        self.action_buttons = widgets.VBox([
            widgets.HBox([self.reset_btn, self.measure_btn, self.classical_btn, self.swap_btn]),
            widgets.HBox([self.entangled_options, self.entangled_btn, self.superposition_btn]),
        ])
    
    
    def on_reset_btn_clicked(self, btn=None):
        with self.log:
            clear_output(wait=True)
            self.board = Board(self.board.size) 
            self.current_player = 'O' # Set 'O' as update_board will switch the players
            self.game_over = False
            self.quantum_move_mode = 'CLASSICAL'
            self.update_board()
            print('Game reset. New game started.')
            
            
    def on_measure_btn_clicked(self, btn=None):
        with self.log:
            clear_output(wait=True)
            counts = self.board.collapse_board()
            self.display_histogram(counts)
            self.update_board()
            print('Board measured and quantum states collapsed.')
    
    
    def create_on_quantum_clicked(self, mode, message=''):
        def on_quantum_clicked(btn):
            with self.log:
                clear_output(wait=True)
                self.quantum_move_mode = mode
                self.quantum_moves_selected = []
                self.game_info.value = f'<b>Current Player: {self.current_player} / Quantum Mode: {self.quantum_move_mode}</b>'
                print(f'{mode} mode ACTIVATED' + (f': {message}' if message else ''))
        return on_quantum_clicked
    

    def create_on_cell_clicked(self, i, j):
        def on_cell_clicked(btn):
            with self.log:
                if self.quantum_move_mode == 'CLASSICAL':
                    if self.board.make_classical_move(i, j, self.current_player): self.update_board()
                    else: print('That position is already occupied. Please choose another.')
                    
                elif len(self.quantum_moves_selected) < 2: # Multi-qubit gates operation
                    self.quantum_moves_selected.append((i, j))
                    print(f'Cell ({i + 1}, {j + 1}) selected for {self.quantum_move_mode} move.')
                    
                    if len(self.quantum_moves_selected) == 2:
                        if self.quantum_move_mode == 'SWAP': self.make_swap_move()
                        elif self.quantum_move_mode == 'ENTANGLED': self.make_entangled_move()
        return on_cell_clicked


    def make_swap_move(self):
        if self.board.make_swap_move(*self.quantum_moves_selected[0], *self.quantum_moves_selected[1]):
            print(f'SWAPPED Cell {self.quantum_moves_selected[0]} to {self.quantum_moves_selected[1]}')
            self.update_board()
        else:
            clear_output(wait=True)
            print('Invalid SWAP move. Both cells must be non-empty.')
        self.quantum_moves_selected = []


    def make_entangled_move(self):
        if self.board.make_entangled_move(*self.quantum_moves_selected[0], *self.quantum_moves_selected[1], self.current_player):
            print('These positions are now entangled and in a superposition state.')
            if self.board.can_be_collapsed():
                print('Performing automatic board measurement...')
                self.on_measure_btn_clicked()
            else: self.update_board()
        else:
            clear_output(wait=True)
            print('Invalid entangled move. At least 1 position is occupied.')
        self.quantum_moves_selected  = []
            

    def update_board(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X' # Switch players
        self.check_win()

        for i in range(self.board.size):
            for j in range(self.board.size):
                cell = self.board.cells[i][j]
                button = self.buttons[i][j]
                color_map = {'X': 'orangered', 'O': 'green', '?': 'dodgerblue', ' ': 'lightgray'}
                
                button.description = cell if cell != ' ' else ' '
                button.style.button_color = color_map[cell[-1]]
                button.disabled = self.game_over
                
        self.game_info.value = f'<b>Current Player: {self.current_player} / Quantum Mode: {self.quantum_move_mode}</b>'
        for btn in self.action_buttons.children[:-1]:
            btn.disabled = self.game_over
        

    def check_win(self):
        while not self.game_over: 
            self.display_circuit()
            result = self.board.check_win()
            
            if result == 'Draw': 
                print("Game Over. It's a draw!")
                self.game_over = True
            elif result in ['X', 'O']: 
                print(f'Game Over. {result} wins!')
                self.game_over = True
            elif type(result) == int: 
                print(f'All cells are filled with {result} entanglements => Keep Collapsing...')
                self.board.collapse_board() # All cells are filled but there are entanglements 
            else: break # Continue the game if no winner yet
        

    def display_circuit(self):
        with self.circuit_output:
            clear_output(wait=True)
            display(self.board.circuit.draw('mpl'))


    def display_histogram(self, counts):
        with self.histogram_output:
            clear_output(wait=True)
            display(plot_histogram(counts, figsize=(9, 5)))