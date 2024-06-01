# Assignment $|01\rangle$ ⚛ Quantum Tic-Tac-Toe game ⚛ 

<details>
  <summary><b>Picture Demo</b></summary>

![](./quantum_tic_tac_toe.jpg)
</details>

> YouTube Demo: https://www.youtube.com/watch?v=U6_wSh_-EQc

## I. How the Game is Played

In this game, 2 players `X` and `O` is represented by 2 qubit classical states, $|1\rangle$ and $|0\rangle$ respectively. Therefore, the **Pauli-X** gate is used to flip $|0\rangle$ to $|1\rangle$ for player `X`, while the **Identity gate** represents player `O`'s unchanged state $|0\rangle$. Players can choose between making a **classical** move or **quantum** moves, leading to a range of possibilities upon measurement:

1. **Classical Move**: Each player alternates turns, placing their marker `X` or `O` on **1 unoccupied cell**.
2. **SWAP Move**: Apply the **SWAP** gate swap the states of **2 occupied cells** without adding new markers.
3. **Superposition**: Apply the **Hadamard** (H) gate to **1 unoccupied cell** (qubit), resulting in the $|+\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}}$ state, which does not commit to `X` or `O` until the board is measured and collapsed.
4. **Entanglement**: Link **2 or 3 unoccupied cells**, affecting outcomes such that the final state of one cell will affect the other. Players must also carefully choose between **4 Risk Levels** (see below) based on their current position and potential future board states. Lower levels allow more controlled outcomes, while higher ones can gamble for a win or potentially aid the opponent.

The `X?` and `O?` markers will be used to indicate the cells are **superposed**/**entangled**, meaning their final values as `X` or `O` are not yet determined until a **measurement collapses** their states and capture the state with the **highest occurrence**. This can happen when:
- The board is **full**. If there are still several `X?`/`O?` cells, an **automatic collapse** will be performed to resolve all **superpositions**.
- Reaching a set of **superposed**/**entangled** cells forming a potential **winning line**.
- Manually triggered by the **Collapse** button press.

**[NOTE]**:
- If the board is **full** with no cells in **superposition** and also no winning lines, the game is `Draw`.
- If you want to make a new choice for **Entanglement Risk Levels**, just click the **Entanglement** button again.

## II. Ensure Fairness and Demonstrate a grasp of Quantum Concepts

At the begining, this game only has 3 options: **Classical move**, **Superpostion**, and **Entanglement** with the standard Bell state $|\Phi^+\rangle$. However, this **Entanglement** approach has 2 disadvantages.

- **Firstly**, when players selects **Entanglement** and picks 2 cells on the board, this will be unfair for their opponents as they will lose 1 move.

- **Secondly**, the **Bell** state $|\Phi^+\rangle$ represents a maximally entangled state where measurement outcomes are perfectly correlated ($|00\rangle$ or $|11\rangle$). This strategy can be risky as it could lead to either a winning line quicker or accidentally help the opponent. For example, if `X` players have a plan of entangling 2 consecutive cells, they can have:
    - Multiple `X` in a row, increasing their possibility of winning.
    - Multiple `O` in a row, putting them at risk of losing as their `O` opponents now have more consecutive cells than them.

**Therefore, to overcome these**:
- I introduce the **SWAP Move**, which can disrupt existing lines or defenses in the opponent's strategy, limiting players from overusing **Entanglement** to dominate the game unfairly.
- Moreover, I introduce **4 Entangelement Risk Levels** to add strategic depth and requiring players to think critically about the consequences of their quantum moves:
    - By adding an **Pauli-X** gate before the **CNOT**'s target qubit, I turned the Bell state $|\Phi^+\rangle$ into $|\Psi^+\rangle$, which also represents a maximally entangled state but with opposing outcomes, ensuring a 50/50 chance and reducing the above risk of $|\Phi^+\rangle$.
    - Similarly, I further employed the same approach for **Triple Entanglement** and turn the **Standard $|GHZ\rangle$** state into $|GHZ_{Xs}\rangle$ by applying 2 additional **Pauli-X** before the **CNOT** chains of **2 targeted** qubit components.

## III. Entanglement Risk Levels

There are 2 types of **Entanglements** in this game associated with 4 corresponding **Risk Levels**:

- **Pairwise Entanglement**: A player can entangle **2** empty cells, meaning the state of 1 cell depends on the state of the other, and their final states (either `X`or `O`) aren't determined until a measurement is performed.
- **Triple Entanglement**: Advanced moves allow entangling **3** cells simultaneously.

<br>

<table>
<tr>
<th>Risk Level (Select via the "Dropdown")</th>
<th>Quantum Gates</th>
<th>Example Circuit</th>
<th>Effect on Measurement and Collapse</th>
</tr>
<tr>
<td align="center">
    <b>Lv1. Lowest Risk<b><br> 
    
$|\Psi^+\rangle = \frac{|01\rangle + |10\rangle}{\sqrt{2}}$ 
    <br>(Pairwise Entangle)
</td>
<td align="center">Hadamard (H),<br>Pauli-X (X),<br>CNOT (CX)</td>
<td>

```
     ┌───┐
q_0: ┤ H ├──■──
     ├───┤┌─┴─┐
q_1: ┤ X ├┤ X ├
     └───┘└───┘
```
</td>
<td>This <b>Bell</b> state results in anti-correlated and truly random outcomes upon collapse. When 1 qubit collapses to <b>X</b>, the other must collapse to <b>O</b>, and vice versa.</td>
</tr>
<tr>
<td align="center">
    <b>Lv2. Lower Risk<b><br>

$|GHZ_{Xs}\rangle = \frac{|010\rangle + |101\rangle}{\sqrt{2}}$
    <br>(Triple Entangle)
</td>
<td align="center">Hadamard (H),<br>2 Pauli-X (X),<br>2 CNOT (CX)</td>
<td>

```
     ┌───┐
q_0: ┤ H ├──■───────
     ├───┤┌─┴─┐
q_1: ┤ X ├┤ X ├──■──
     ├───┤└───┘┌─┴─┐
q_2: ┤ X ├─────┤ X ├
     └───┘     └───┘
```
</td>
<td>Similar randomness but for 3 squares, formed by modifying the <b>Standard |GHZ⟩,</b> leading to combinations where the outcome isn't uniformly all 3 <b>X</b>s or all <b>O</b>s, but mixed.<br></td>
</tr>
<tr>
<td align="center">
    <b>Lv3. Moderate Risk<b><br>

$|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}$
    <br>(Pairwise Entangle)
</td>
<td align="center">Hadamard (H),<br>CNOT (CX)</td>
<td>

```
     ┌───┐
q_0: ┤ H ├──■──
     └───┘┌─┴─┐
q_1: ─────┤ X ├
          └───┘
```
</td>
<td>This <b>Bell</b> state yields the same outcome for both selected cells/qubits. Both qubits collapse to the same value upon measurement, either <b>XX</b> or <b>OO</b>.<td>
</tr>
<tr>
<td align="center">
    <b>Lv4. High Risk<b><br>

$|GHZ\rangle = \frac{|000\rangle + |111\rangle}{\sqrt{2}}$
    <br>(Triple Entangle)
</td>
<td align="center">Hadamard (H),<br>2 CNOT (CX)</td>
<td>

```
     ┌───┐
q_0: ┤ H ├──■───────
     └───┘┌─┴─┐
q_1: ─────┤ X ├──■──
          └───┘┌─┴─┐
q_2: ──────────┤ X ├
               └───┘
```
</td>
<td>This <b>Standard |GHZ⟩</b> state can strategically benefit the player but also at the risk of benefiting the opponent just as much. All 3 qubits collapse to the same value, either all <b>XXX</b> or all <b>OOO</b>.</td>
</tr>
</table>

## IV. Installation and Usage

**1. Install [Qiskit](https://github.com/Qiskit/qiskit) and [PyLaTeXEnc](https://github.com/phfaist/pylatexenc)**
```bash
pip install qiskit --quiet
pip install qiskit-aer --quiet
pip install pylatexenc --quiet
```

**2. Play the game**
```python
from qiskit_aer import AerSimulator
from gui import QuantumT3GUI
game = QuantumT3GUI(size=3, simulator=AerSimulator())
```
👉 Check this [quantum_tic_tac_toe.ipynb](./quantum_tic_tac_toe.ipynb) for a demo. You should open it in **Colab**, the notebook viewer within GitHub cannot render the game's widgets.

## V. Future Improvements

- Limit the **Entanglement Risk Levels** based on the board size. For example, **3x3** board can only use **PAIRWISE** entanglement (Level `1` & `3`). Because if they use `2` or `4`, they can win or lose the game in 1 move.
- Count the number of **winning lines** for each player as a score to demonstrate how confident the winner is or to determine the winner if the game is a **draw**.
- Apply phase shift gates like **S** or **T** gates before making a move. This could affect the probability **amplitudes** of the states, creating **interference** patterns in probabilities.
- Implement the `Undo` and `Redo` functionalities for the game. But this is a bit complex for cases like entanglement or after collapsing.
- Develop an `AI` opponent that adapatively uses quantum strategies, learning from the player's moves.
