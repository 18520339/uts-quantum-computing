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
                              