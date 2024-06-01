from qiskit import QuantumCircuit, transpile, assemble
from qiskit.circuit.library import QFT


class CtrlMultCircuit(QuantumCircuit):
    def __init__(self, a, binary_power, N):
        super().__init__(N.bit_length())
        self.a = a
        self.power = 2 ** binary_power # Convert binary to decimal
        self.N = N
        self.name = f'{self.a}^{self.power} mod {self.N}'
        self._create_circuit()

    def _create_circuit(self):
        for dec_power in range(self.power):
            a_exp = self.a ** dec_power % self.N
            for i in range(self.num_qubits):
                if a_exp >> i & 1: self.x(i)
                for j in range(i + 1, self.num_qubits):
                    if a_exp >> j & 1: self.swap(i, j)
                    
                    
class QPECircuit(QuantumCircuit):
    def __init__(self, a, N):
        super().__init__(2 * N.bit_length(), N.bit_length())
        self.a = a
        self.N = N
        self._create_circuit()

    def _modular_exponentiation(self):
        for qbit_idx in range(self.num_qubits // 2):
            self.append(
                CtrlMultCircuit(self.a, qbit_idx, self.N).to_gate().control(),
                [qbit_idx] + list(range(self.num_qubits // 2, 2 * self.num_qubits // 2))
            )

    def _create_circuit(self):
        self.h(range(self.num_qubits // 2)) # Apply Hadamard gates to the first n qubits
        self.x(self.num_qubits - 1)
        self.barrier()

        self._modular_exponentiation() # Apply controlled modular exponentiation
        self.barrier()
        self.append(
            QFT(self.num_qubits // 2, inverse=True),
            range(self.num_qubits // 2) # Apply inverse QFT to the first n qubits
        )

    def collapse(self, simulator):
        self.measure(range(self.num_qubits // 2), range(self.num_qubits // 2))
        transpiled_circuit = transpile(self, simulator)
        self.collapse_result = simulator.run(transpiled_circuit, memory=True).result()
        return self.collapse_result