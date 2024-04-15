from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit_aer import AerSimulator
from termcolor import colored


class Board:
    def __init__(self, size=3):
        # Initialize the quantum circuit with one qubit and classical bit for each cell
        self.size = size
        self.entanglement_count = 0
        self.simulator = AerSimulator()
        
        self.qubits = QuantumRegister(size**2, 'q')
        self.bits = ClassicalRegister(size**2, 'c')
        self.circuit = QuantumCircuit(self.qubits, self.bits)
        self.cells = [[' ' for _ in range(size)] for _ in range(size)] # Initialize the board representation
        
        ''' For a 3x3 board, the winning lines are:
        - Horizontal lines: (0, 1, 2), (3, 4, 5), (6, 7, 8)
        - Vertical lines: (0, 3, 6), (1, 4, 7), (2, 5, 8)
        - Diagonal lines: (0, 4, 8), (2, 4, 6)
        '''
        self.winning_lines = [tuple(range(i, size**2, size)) for i in range(size)] + \
                             [tuple(range(i * size, (i + 1) * size)) for i in range(size)] + \
                             [tuple(range(0, size**2, size + 1)), tuple(range(size - 1, size**2 - 1, size - 1))]
                              

    def make_classical_move(self, row, col, symbol):
        if self.cells[row][col] == ' ': # Check if the cell is occupied
            self.cells[row][col] = symbol
            self.circuit.x(self.qubits[row * self.size + col]) # Pauli-X to mark the move
            return True
        return False


    def make_entangled_move(self, row1, col1, row2, col2, symbol):
        # Entangle 2 cells by applying a Hadamard gate and a CNOT gate
        if self.cells[row1][col1] == ' ' and self.cells[row2][col2] == ' ' and (row1, col1) != (row2, col2):
            indices = [row1 * self.size + col1, row2 * self.size + col2]
            self.circuit.h(self.qubits[indices[0]])
            self.circuit.cx(self.qubits[indices[0]], self.qubits[indices[1]])
            self.cells[row1][col1] = self.cells[row2][col2] = symbol + '?'
            self.entanglement_count += 1
            return True
        return False


    def collapse_board(self):
        # Simulate the measurement process and update the board accordingly
        self.circuit.measure(self.qubits, self.bits) # Measure the quantum state to collapse it to classical states
        transpiled_circuit = transpile(self.circuit, self.simulator)
        job = self.simulator.run(transpiled_circuit, memory=True)
        
        counts = job.result().get_counts()
        max_state = max(counts, key=counts.get) # Get the state with the highest probability
        measured_state = format(int(max_state, 16), f'0{self.size**2}b')[::-1] 
        
        for i in range(self.size ** 2):
            row, col = divmod(i, self.size)
            if self.cells[row][col].endswith('?'):
                self.cells[row][col] = 'X' if measured_state[i] == '1' else 'O'

        # Reset the circuit for the next round of quantum moves    
        self.entanglement_count = 0
        self.circuit.reset(self.qubits) 
        return counts