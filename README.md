# QuantumSeeding

Generate really random seeds with Quantum Computers

## Installation

```bash
pip install quantumseeding
```

## Usage

```python
from quantumseeding import QuantumSeeding

ibm_token = "YOUR_IBM_TOKEN"  # https://quantum-computing.ibm.com/account
max_qubits = 7 # Max qubits to use

seed = QuantumSeeding(
    ibm_token=ibm_token,
    max_qubits=max_qubits,
    verbose=True,
    simulation=True,
).get_seed()
print(seed)
```
