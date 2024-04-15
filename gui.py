import ipywidgets as widgets
from termcolor import colored
from IPython.display import clear_output

from qiskit import ClassicalRegister, QuantumRegister, QuantumCircuit, transpile
from qiskit.visualization import plot_bloch_multivector, plot_histogram
from qiskit_aer import AerSimulator

      
class QuantumTicTacToeGUI:
    def __init__(self):
        self.board = Board(3)
        self.current_player = 'X' # X starts the game
        self.game_over = False
            
        self.quantum_mode = 'CLASSICAL'
        self.quantum_cells = [] # Selected cells for operation on multi-qubit gates 

        self.log = widgets.Output()
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
                    layout = widgets.Layout(width='120px', height='120px', border='1px solid black'),
                    style = {'font_weight': 'bold'}
                )
                button.style.button_color = 'lightgray'
                button.on_click(self.create_on_cell_clicked(i, j))
                self.buttons[i].append(button)

        self.create_action_buttons()
        self.game_info = widgets.HTML(value='<h3>Turn: X</h3>')
        self.board_widget = widgets.VBox([
            widgets.VBox([widgets.HBox(row) for row in self.buttons]), 
            self.game_info, self.log
        ])

        self.board_widget.layout.margin = '0px 70px 0px 0px'
        self.action_buttons.layout.margin = '0px 0px 30px 0px'
        display(widgets.VBox([
            widgets.HBox([self.board_widget, self.histogram_output]), 
            self.action_buttons, self.circuit_output
        ]))