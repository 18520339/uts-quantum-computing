from quantum_phase_estimation import QPECircuit
from fractions import Fraction
import random
import sympy
import math


class ShorAlgorithm:
    def __init__(self, N, max_attempts=-1, enable_preprocess=True, simulator=None):
        self.N = N
        self.simulator = simulator
        self.max_attempts = max_attempts # -1 for all possible values of a
        self.enable_preprocess = enable_preprocess # Select a random integer in [2, N) as initial guess


    def execute(self):
        is_N_invalid = self._is_N_invalid()
        if is_N_invalid: return is_N_invalid
        
        # Only coprime values remain if _classical_preprocess is disabled
        a_values = [a for a in range(2, self.N) if self.enable_preprocess or (math.gcd(a, self.N) == 1)]
        self.max_attempts = len(a_values) if self.max_attempts <= -1 else min(self.max_attempts, len(a_values))
        attempts_count = 0

        while attempts_count < self.max_attempts:
            print(f'\n===== Attempt {attempts_count + 1}/{self.max_attempts} =====')
            attempts_count += 1
            self.chosen_a = random.choice(a_values)
            self.r = 1

            print(f'[START] Chosen base a: {self.chosen_a}')
            if self.enable_preprocess:
                gcd = math.gcd(self.chosen_a, self.N)
                if gcd != 1:
                    print(f'=> {self.chosen_a} and {self.N} share common factor: {self.N} = {gcd} * {self.N // gcd}')
                    return gcd, self.N // gcd

            print(f'>>> {self.chosen_a} and {self.N} are coprime => Perform Quantum Phase Estimation to find {self.chosen_a}^r - 1 = 0 (MOD {self.N})')
            if not self._quantum_period_finding():
                a_values.remove(self.chosen_a)
                self.r = self.chosen_a = self.qpe_circuit = None
                continue

            factors = self._classical_postprocess()
            if factors: return factors
            a_values.remove(self.chosen_a)
            self.r = self.chosen_a = self.qpe_circuit = None
        print(f'[FAIL] No non-trivial factors found after {self.max_attempts} attempts.')


    def _is_N_invalid(self):
        if self.N <= 3:
            print('[ERR] N must be > 3')
            return 1, self.N

        if self.N % 2 == 0:
            print(f'=> {self.N} is an even number: {self.N} = 2 * {self.N // 2}')
            return 2, self.N // 2
        
        if sympy.isprime(self.N):
            print(f'=> {self.N} is a prime number: {self.N} = 1 * {self.N}')
            return 1, self.N
        
        max_exponent = int(math.log2(self.N)) # Start with a large exponent and reduce
        for k in range(max_exponent, 1, -1):
            p = round(self.N ** (1 / k))
            if p ** k == self.N: 
                print(f'=> {self.N} is a power of prime: {self.N} = {p}^{k}')
                return p, k
        return False
    
    
    def _quantum_period_finding(self):
        while self.chosen_a ** self.r % self.N != 1: # QPE + continued fractions may find wrong r
            self.qpe_circuit = QPECircuit(self.chosen_a, self.N) # Find phase s/r
            result = self.qpe_circuit.collapse(self.simulator)
            state_bin = result.get_memory()[0]
            state_dec = int(state_bin, 2) # Convert to decimal
            bits_count = 2 ** (self.N.bit_length() - 1)
            phase = state_dec / bits_count

            # Continued fraction to find r
            self.r = Fraction(phase).limit_denominator(self.N).denominator # Get fraction that most closely approximates phase
            if self.r > self.N or self.r == 1: # Safety check to avoid infinite loops
                print(f'[ERR] Invalid period found: r = {self.r} => Retry with different a.')
                return False

        print(f'>>> Output State: |{state_bin}⟩ = {state_dec} (dec) => Phase = {state_dec} / {bits_count} = {phase:.3f}')
        return True


    def _classical_postprocess(self):
        # Classical postprocessing to find factors from the period
        print(f'>>> Found r = {self.r} => a^{{r/2}} ± 1 = {self.chosen_a:.0f}^{self.r/2:.0f} ± 1')

        if self.r % 2 != 0:
            print(f'[ERR] r = {self.r} is odd => Retry with different a.')
            return None

        int1, int2 = self.chosen_a ** (self.r // 2) - 1, self.chosen_a ** (self.r // 2) + 1
        if int1 % self.N == 0 or int2 % self.N == 0:
            print(f'[ERR] {self.chosen_a}^{self.r/2:.0f} ± 1 is a multiple of {self.N} => Retry with different a.')
            return None

        factor1, factor2 = math.gcd(int1, self.N), math.gcd(int2, self.N)
        if factor1 not in [1, self.N] and factor2 not in [1, self.N]: # Check to see if factor is non-trivial
            print(f'[DONE] Successfully found non-trivial factors: {self.N} = {factor1} * {factor2}')
            return factor1, factor2

        print(f'[FAIL] Trivial factors found: [1, {self.N}] => Retry with different a.')
        return None