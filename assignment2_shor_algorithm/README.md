# Assignment $|02\rangle$ 🔐 Shor's Algorithm 🔐

[![image](https://github.com/18520339/uts-quantum-computing/assets/50880271/e0588281-1148-4acb-a4cd-54fecd46c2ce)](https://rand.cs.uchicago.edu/publication/peng-2022-shor/)

Source: https://rand.cs.uchicago.edu/publication/peng-2022-shor

## I. Introduction

The **Shor's algorithm** can be divided into 2 main parts:
1. **Classical Part**: This involves reducing the problem of factorizing an integer $N$ to the problem of finding the period $r$ of a specific function.
2. **Quantum Part**:
- This involves using a quantum computer to **find the period $r$** efficiently. The algorithm creates a superposition of states to encode information about the period into the quantum state.
- The **Quantum Fourier Transform (QFT)** is applied to the quantum state to extract the period $r$:

    $$\left| \tilde{x} \right\rangle = QFT_N \vert x \rangle = \frac{1}{\sqrt{N}} \sum_{k=0}^{N-1}  e^{2\pi i \frac{xk}{N}} \vert k \rangle$$
    $$\text{where N = number of qubits; } \vert k \rangle = \vert k_1 k_2 \cdots k_n \rangle (\text{binary qbuit state })$$

 - It is a series of **Hadamard** and **Controlled Phase Rotation** gates to the output state of the **Modular Exponentiation** circuit. This transforms the state into a form where measuring the qubits can yield the period $r$ (just a change of basis).
 - This **Modular Exponentiation** is crucial for creating the periodic function. It involves applying a series of **controlled-U** gates, where $U$ represents modular multiplication.

## II. Shor's Algorithm Steps
1. **Choose a Random Number $a$**: Select a random integer $a$ such that $1 < a < N$.
2. **Check if $N$ is valid**: If $N$ is even or a prime number or a power of a prime number, then $N$ is not valid for factorization.
3. **Compute the Greatest Common Divisor (GCD)**: Compute $\text{gcd}(a, N)$. If $\text{gcd}(a, N) \neq 1$, then $\text{gcd}(a, N)$ is a non-trivial factor of $N$.
4. **Quantum Period Finding**:
- Here, **Quantum Phase Estimation** (QPE) is used to estimate the **eigenvalue** corresponding to an **eigenstate** of a **unitary operator**. In this case, I use it to estimate the phase $\phi$ related to the order $r$.

  - **Initialize qubits**: I start with an equal superposition of all possible states.
  - **Apply controlled-unitary operations**: These operations encode the **Modular Exponentiation** into the qubits.
  - **Inverse QFT**: Apply the inverse $QFT^{-1} = \frac{1}{\sqrt{2^n}} \sum_{j,k=0}^{2^n-1} e^{-2\pi i jk / 2^n} |j\rangle \langle k|$ to the qubits to extract the phase information.

👉 This step uses a quantum computer to **find the period $r$** of the function $f(x) = a^x \mod N$.

5. **Check the Period**: 
> If $r$ is even and $a^{r/2} \pm 1$ is not a multiple of $N$, then compute $\text{gcd}(a^{r/2} \pm 1, N)$ to obtain the factors of $N$:
  - By measuring the state after applying the **inverse QFT**, I obtain the phase $\phi$, from which I can deduce the order $r$: $\phi = \frac{s}{r} \implies r \approx \frac{1}{\phi}$
  - The continued fraction representation of a rational number $\frac{p}{q}$ helps in extracting the period $r$ from the phase $\frac{s}{r}$.

  $$\frac{p}{q} = a_0 + \cfrac{1}{a_1 + \cfrac{1}{a_2 + \cfrac{1}{\ddots + \cfrac{1}{a_n}}}}$$

  - Using the order $r$, I apply **classical postprocessing** to find the factors of $N$. If $r$ is even and $x^{r/2} \neq \pm 1 \text{ (mod N)}$, then the factors are given by: $\gcd(x^{r/2} \pm 1, N)$.

6. **Repeat if Necessary**: If the above steps do not yield factors, repeat the process with a different $a$.

## III. Installation and Usage

**1. Install [Qiskit](https://github.com/Qiskit/qiskit) and [PyLaTeXEnc](https://github.com/phfaist/pylatexenc)**
```bash
pip install qiskit --quiet
pip install qiskit-aer --quiet
pip install pylatexenc --quiet
```

**2. Perform Integer Factorization**
```python
from qiskit_aer import AerSimulator
from shor_algorithm import ShorAlgorithm

shor = ShorAlgorithm(N=21, max_attempts=-1, enable_preprocess=False, simulator=AerSimulator())
factors = shor.execute()
try: display(shor.qpe_circuit.draw(output='mpl', fold=-1))
except Exception: pass
```
👉 Check this [shor_algorithm.ipynb](./shor_algorithm.ipynb) for a demo. You should open it in **Colab**, the notebook viewer within GitHub cannot render the widgets.
