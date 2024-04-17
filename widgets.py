from ipywidgets import Output, Button, HBox, VBox, HTML, Dropdown
from qiskit.visualization import plot_bloch_multivector, plot_histogram
from IPython.display import clear_output
from abc import abstractmethod, ABCMeta # For define pure virtual functions


class QuantumT3Widgets(metaclass=ABCMeta):
    def __init__(self, board, current_player, quantum_move_mode):
        self.board = board
        self.current_player = current_player
        self.quantum_move_mode = quantum_move_mode

        self.log = Output(layout={'margin': '10px 0 0 0'})
        self.histogram_output = Output(layout={'margin': '0 0 10px 10px'})
        self.circuit_output = Output()
        self.create_widgets()
                    
            
    def create_widgets(self):
        # Create widgets for each cell and controls for game actions
        self.buttons = []
        for row in range(self.board.size):
            self.buttons.append([])
            for col in range(self.board.size):
                button = Button(
                    description = ' ', 
                    layout = {'width': '100px', 'height': '100px', 'border': '1px solid black'},
                    style = {'button_color': 'lightgray', 'font_weight': 'bold', 'text_color': 'white'}
                )
                button.on_click(self.create_on_cell_clicked(row, col))
                self.buttons[row].append(button)

        self.create_action_buttons()
        self.game_info = HTML(f'<b>Current Player: {self.current_player} / Quantum Mode: {self.quantum_move_mode}</b>')
        
        self.board_histogram_widget = HBox(
            [VBox([VBox([HBox(row) for row in self.buttons]), self.game_info]), self.histogram_output], 
            layout = {'display': 'flex', 'justify_content': 'center', 'align_items': 'flex-end'}
        )
        display(VBox([self.board_histogram_widget, self.action_buttons, self.log, self.circuit_output]))


    def create_action_buttons(self):
        self.reset_btn = Button(description='Reset', button_style='danger')
        self.collapse_btn = Button(description='Collapse', button_style='warning')
        self.classical_btn = Button(description='Classical Move', button_style='primary')
        self.swap_btn = Button(description='SWAP Move', button_style='info')
        self.superposition_btn = Button(description='Superposition', button_style='success')
        
        self.entangled_btn = Button(description='Entanglement', button_style='success')
        self.entangled_options = Dropdown(options=[
            ('', 0), # Qubits collapse to opposite states (not consecutive)
            ('Lv1. PAIRWAISE: ∣Ψ+⟩ = (∣01⟩ + ∣10⟩) / √2', 1), # Qubits collapse to opposite states (not consecutive)
            ('Lv2. TRIPLE: GHZ_Xs = (∣010⟩ + ∣101⟩) / √2', 2),
            ('Lv3. PAIRWAISE: ∣Φ+⟩ = (∣00⟩ + ∣11⟩) / √2', 3), # Can form consecutive winning cells or accidentally help the opponent
            ('Lv4. TRIPLE: GHZ = (∣000⟩ + ∣111⟩) / √2', 4),
        ], value=0, disabled=True)
        self.entangled_options.observe(self.update_entangled_options, names='value')
        
        self.reset_btn.on_click(self.on_reset_btn_clicked)
        self.collapse_btn.on_click(self.on_collapse_btn_clicked)
        self.classical_btn.on_click(self.create_on_move_clicked('CLASSICAL'))
        self.swap_btn.on_click(self.create_on_move_clicked('SWAP', 'Select 2 cells to swap their states.'))
        self.superposition_btn.on_click(self.create_on_move_clicked('SUPERPOSITION', 'Select a cell to put in superposition.'))
        self.entangled_btn.on_click(self.create_on_move_clicked('ENTANGLED', 'Select 2/3 cells based on risk level to entangle.'))
        
        self.action_buttons = HBox([
            self.reset_btn, self.collapse_btn, self.classical_btn, self.swap_btn, 
            self.superposition_btn, self.entangled_btn, self.entangled_options
        ])
        
        
    @abstractmethod # Pure virtual functions => Must be overridden in the derived classes
    def on_reset_btn_clicked(self, btn=None):
        raise NotImplementedError('on_reset_btn_clicked method is not implemented.')
    
    @abstractmethod # Pure virtual functions => Must be overridden in the derived classes
    def on_collapse_btn_clicked(self, btn=None):
        raise NotImplementedError('on_collapse_btn_clicked method is not implemented.')
      
    @abstractmethod # Pure virtual functions => Must be overridden in the derived classes
    def on_move_clicked(self, mode, message=''):
        raise NotImplementedError('on_move_clicked method is not implemented.')
    
    @abstractmethod # Pure virtual functions => Must be overridden in the derived classes
    def on_cell_clicked(self, row, col):
        raise NotImplementedError('on_cell_clicked method is not implemented.')
    
    
    def update_entangled_options(self, change):
        with self.log:
            self.entangled_options.disabled = change.new != 0
            for row in self.buttons:
                for button in row: button.disabled = change.new == 0
                
            # Check if there are enough empty cells for the selected operation
            empty_count = sum(cell == ' ' for row in self.board.cells for cell in row)
            total_empty_required = {1: 2, 2: 3, 3: 2, 4: 3} # Total empty cells required for each risk level
                
            if change.new == 0: return
            elif empty_count < total_empty_required[change.new]:
                print(f'Not enough empty cells to perform entanglement with risk level {change.new}. Please select another.')
                self.entangled_options.value = 0
            else:
                print(f'Risk Level {change.new} ACTIVATED =>', end=' ')
                if change.new in [1, 3]: print(f'Select 2 cells (qubits) for this PAIRWAISE entanglement.')
                else: print(f'Select 3 cells (qubits) for this TRIPLE entanglement.')
                
    
    def create_on_cell_clicked(self, row, col):
        def on_cell_clicked(btn):
            self.on_cell_clicked(row, col)
        return on_cell_clicked
    
    
    def create_on_move_clicked(self, mode, message=''):
        def on_move_clicked(btn):
            self.on_move_clicked(mode, message)
        return on_move_clicked
    
    
    def display_circuit(self):
        with self.circuit_output:
            clear_output(wait=True)
            display(self.board.circuit.draw('mpl', initial_state=True))


    def display_histogram(self, counts):
        with self.histogram_output:
            clear_output(wait=True)
            display(plot_histogram(counts, figsize=(9, 4)))