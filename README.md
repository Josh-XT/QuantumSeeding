# QuantumSeeding

Generate really random seeds with Quantum Computers

## Installation

```bash
pip install quantumseeding
```

## Usage

```python
from quantumseeding import QuantumSeeding

seed = QuantumSeeding(
    ibm_token="YOUR_IBM_TOKEN"  # https://quantum-computing.ibm.com/account
    max_qubits=7, # Max qubits to use
    verbose=True, # Print progress
    simulation=True, # Use quantum computer simulator
).get_seed()
print(seed)
```
