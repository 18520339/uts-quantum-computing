# Assignment $|02\rangle$ 🔐 Shor's Algorithm 🔐

[![image](https://github.com/18520339/uts-quantum-computing/assets/50880271/e0588281-1148-4acb-a4cd-54fecd46c2ce)](https://rand.cs.uchicago.edu/publication/peng-2022-shor/)

Source: https://rand.cs.uchicago.edu/publication/peng-2022-shor

## I. Shor's Algorithm Steps
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

## II. Installation and Usage

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

shor = ShorAlgorithm(N=15, max_attempts=-1, random_coprime_only=True, simulator=AerSimulator())
factors = shor.execute()
try: display(shor.qpe_circuit.draw(output='mpl', fold=-1))
except Exception: pass
```

**[Note]**:
- **max_attempts**: If set to `-1`, the algorithm will try all possible values of $a$ (a random integer in the range **[2, N)**).
- **random_coprime_only**: If set to `True`, the algorithm will only consider coprime values of $a$ and $N$.

**3. Example Output**
```sh
[INFO] 7 possible values of a: [2, 4, 7, 8, 11, 13, 14]

===== Attempt 1/7 =====
[START] Chosen base a: 14
>>> 14 and 15 are coprime => Perform Quantum Phase Estimation to find 14^r - 1 = 0 (MOD 15)
[ERR] Invalid period found: r = 1 => Retry with different a.

===== Attempt 2/7 =====
[START] Chosen base a: 13
>>> 13 and 15 are coprime => Perform Quantum Phase Estimation to find 13^r - 1 = 0 (MOD 15)
[ERR] Invalid period found: r = 1 => Retry with different a.

===== Attempt 3/7 =====
[START] Chosen base a: 11
>>> 11 and 15 are coprime => Perform Quantum Phase Estimation to find 11^r - 1 = 0 (MOD 15)
>>> Output State: |0101⟩ = 5 (dec) => Phase = 5 / 8 = 0.625
>>> Found r = 8 => a^{r/2} ± 1 = 11^4 ± 1
[ERR] 11^4 ± 1 is a multiple of 15 => Retry with different a.

===== Attempt 4/7 =====
[START] Chosen base a: 2
>>> 2 and 15 are coprime => Perform Quantum Phase Estimation to find 2^r - 1 = 0 (MOD 15)
>>> Output State: |0110⟩ = 6 (dec) => Phase = 6 / 8 = 0.750
>>> Found r = 4 => a^{r/2} ± 1 = 2^2 ± 1
[DONE] Successfully found non-trivial factors: 15 = 3 * 5
```
👉 Check this [shor_algorithm.ipynb](./shor_algorithm.ipynb) for a demo. You should open it in **Colab**, the notebook viewer within GitHub cannot render the widgets.
