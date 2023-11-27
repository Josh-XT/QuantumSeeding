# QuantumSeeding

Generate really random seeds with Quantum Computers

## Installation

```bash
pip install quantumseeding
```

## Usage

```python
from quantumseeding import quantumseed

ibm_token = "YOUR_IBM_TOKEN" # https://quantum-computing.ibm.com/account

seed = quantumseed(ibm_token=ibm_token, qubits=7, simulation=True, verbose=True)
print(seed)
```
