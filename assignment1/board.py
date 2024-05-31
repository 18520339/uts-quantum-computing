from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from termcolor import colored


class Board:
    def __init__(self, size=3, simulator=None):
        # Initialize the quantum circuit with one qubit and classical bit for each cell
        self.size = size
        self.simulator = simulator
        self.superposition_count = 0
        self.cells = [[' ' for _ in range(size)] for _ in range(size)] # Initialize the board representation
        
        self.qubits = QuantumRegister(size**2, 'q')
        self.bits = ClassicalRegister(size**2, 'c')
        self.circuit = QuantumCircuit(self.qubits, self.bits)
        
        ''' For a 3x3 board, the winning lines are:
        - Horizontal lines: (0, 1, 2), (3, 4, 5), (6, 7, 8)
        - Vertical lines: (0, 3, 6), (1, 4, 7), (2, 5, 8)
        - Diagonal lines: (0, 4, 8), (2, 4, 6)
        '''
        self.winning_lines = [tuple(range(i, size**2, size)) for i in range(size)] + \
                             [tuple(range(i * size, (i + 1) * size)) for i in range(size)] + \
                             [tuple(range(0, size**2, size + 1)), tuple(range(size - 1, size**2 - 1, size - 1))]
                              

    def __str__(self):
        # Create a colorful string representation of the board
        board_str = ''
        for i, row in enumerate(self.cells):
            for cell in row:
                if '?' in cell: cell_color = 'cyan' # Quantum move
                elif cell == 'X': cell_color = 'red'
                elif cell == 'O': cell_color = 'green'
                else: cell_color = 'yellow'
                board_str += f' {colored(cell, cell_color)} '
                board_str += '|' if '?' in cell else ' |'
                
            board_str = board_str[:-1] + '\n' # Remove last separator
            if i < self.size - 1: # Add horizontal separator
                board_str += '-' * (5 * self.size - 1) + '\n'
        return board_str

    
    def make_classical_move(self, row, col, player_mark, is_collapsed=False):
        if self.cells[row][col] == ' ' or is_collapsed: # Check if the cell is occupied
            self.cells[row][col] = player_mark
            index = row * self.size + col
            
            if player_mark == 'X': self.circuit.x(self.qubits[index])
            else: self.circuit.id(self.qubits[index])
            return True
        return False


    def make_swap_move(self, row1, col1, row2, col2, **kwargs):
        if self.cells[row1][col1] != ' ' and self.cells[row2][col2] != ' ':
            indices = [row1 * self.size + col1, row2 * self.size + col2]
            self.circuit.swap(self.qubits[indices[0]], self.qubits[indices[1]])
            self.cells[row1][col1], self.cells[row2][col2] = self.cells[row2][col2], self.cells[row1][col1]
            return True
        return False
    
    
    def make_superposition_move(self, row, col, player_mark, **kwargs):
        if self.cells[row][col] == ' ':
            index = row * self.size + col
            self.circuit.h(self.qubits[index])
            self.cells[row][col] = player_mark + '?'
            self.superposition_count += 1
            return True
        return False
    
    
    def make_entangled_move(self, *positions, risk_level, player_mark, **kwargs):
        # Entangle the quantum states of 2 or 3 cells based on the risk level
        pos_count = len(positions)
        if pos_count not in [2, 3] or risk_level not in [1, 2, 3, 4] or len(set(positions)) != pos_count or \
            (pos_count == 2 and risk_level not in [1, 3]) or (pos_count == 3 and risk_level not in [2, 4]) or \
            any(self.cells[row][col] != ' ' for row, col in positions): return False
        
        indices = [row * self.size + col for row, col in positions]
        self.circuit.h(self.qubits[indices[0]])
        
        if pos_count == 2: 
            # Pairwise Entanglement with Bell state for 2 qubits:
            # Lv1. |Ψ+⟩ = (∣01⟩ + ∣10⟩)/√2 | Lv3. |Φ+⟩ = (∣00⟩ + ∣11⟩)/√2
            if risk_level == 1: self.circuit.x(self.qubits[indices[1]])
            self.circuit.cx(self.qubits[indices[0]], self.qubits[indices[1]])
        else: 
            # Triple Entanglement with GHZ state for 3 qubits:
            # Lv2. (∣010⟩ + ∣101⟩)/√2 | Lv4. (∣000⟩ + ∣111⟩)/√2
            if risk_level == 2: 
                self.circuit.x(self.qubits[indices[1]])
                self.circuit.x(self.qubits[indices[2]])
                
            # Apply CNOT chain to entangle all 3 qubits
            self.circuit.cx(self.qubits[indices[0]], self.qubits[indices[1]])
            self.circuit.cx(self.qubits[indices[1]], self.qubits[indices[2]])
            
        for row, col in positions: self.cells[row][col] = player_mark + '?'
        self.superposition_count += pos_count
        return True            
    
    
    def can_be_collapsed(self):
        # If superpositions/entanglement cells form a potential winning line => collapse
        for line in self.winning_lines:
            if all(self.cells[i // self.size][i % self.size].endswith('?') for i in line): 
                return True
        return False
    

    def collapse_board(self):
        # Update the board based on the measurement results and apply the corresponding classical moves
        self.circuit.barrier()
        self.circuit.measure(self.qubits, self.bits) # Measure all qubits to collapse them to classical states
        
        transpiled_circuit = transpile(self.circuit, self.simulator)
        job = self.simulator.run(transpiled_circuit, memory=True)
        counts = job.result().get_counts()
        max_state = max(counts, key=counts.get)[::-1] # Get the state with the highest probability
        
        for i in range(self.size ** 2):
            row, col = divmod(i, self.size)
            if self.cells[row][col].endswith('?'):
                self.circuit.reset(self.qubits[i]) 
                self.make_classical_move(row, col, 'X' if max_state[i] == '1' else 'O', is_collapsed=True)
                
        self.superposition_count = 0
        return counts

    
    def check_win(self):
        # Dynamic implementation for above logic with dynamic winning lines
        for line in self.winning_lines:
            # Check if all cells in the line are the same and not empty
            first_cell = self.cells[line[0] // self.size][line[0] % self.size]
            if first_cell not in [' ', 'X?', 'O?']:
                is_same = all(self.cells[i // self.size][i % self.size] == first_cell for i in line)
                if is_same: return line
                
        # If no spaces and no superpositions left => 'Draw'
        # If all cells are filled but some are still in superpositions => collapse_board
        if all(self.cells[i // self.size][i % self.size] not in [' '] for i in range(self.size**2)):
            if self.superposition_count <= 0: return 'Draw'
            return self.superposition_count
        return None