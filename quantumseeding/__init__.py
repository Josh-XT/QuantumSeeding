from qiskit import (
    QuantumRegister,
    ClassicalRegister,
    QuantumCircuit,
    execute,
    Aer,
    IBMQ,
)


# Define functions to simplify interactions with quantum computers
def get_ibm_quantum_computer(
    qubits=2, simulation=False, verbose=False, ibm_token=None, max_qubits=7
):
    quantum_computer = None
    if ibm_token is None:
        if verbose == True:
            print("No IBM Token found.  Using Quantum Computer Simulator")
        simulation = True
    else:
        IBMQ.save_account(ibm_token, overwrite=True)
        IBMQ.load_account()
    if qubits > max_qubits:
        if verbose == True:
            print(f"No Quantum Computers available with {qubits} qubits.")
        simulation = True
    # Finds a quantum computer at IBM with the lowest queue as long as it has enough qubits for the circuit
    if simulation == False:  # Execute the circuit on a quantum computer at IBM
        lowest = float("inf")
        provider = IBMQ.get_provider(hub="ibm-q")
        for backend in provider.backends():
            try:
                if "simulator" not in backend.name():
                    queue = backend.status().pending_jobs
                    qubit_count = len(backend.properties().qubits)
                    if qubit_count >= qubits:
                        if queue < lowest:
                            lowest = queue
                            quantum_computer = provider.get_backend(backend.name())
                        if verbose == True:
                            print(
                                f"Quantum Computer {backend.name()} has {queue} queued jobs and {qubit_count} qubits"
                            )
                    else:
                        if verbose == True:
                            print(
                                f"Quantum Computer {backend.name()} has {qubit_count} qubits, but we need {qubits} qubits"
                            )
            except:
                if verbose == True:
                    print(f"Quantum Computer {backend.name()} is not operational")
        if quantum_computer is None:
            if verbose == True:
                print(f"No Quantum Computers available with {qubits} qubits.")
            simulation = True
    if (
        simulation == True or quantum_computer is None
    ):  # Execute the circuit on the simulator
        quantum_computer = Aer.get_backend("qasm_simulator")
        if verbose == True:
            print(f"Using Quantum Computer Simulator")
    if verbose == True and simulation == False:
        print(
            f"Using Quantum Computer: {quantum_computer.name()} with {quantum_computer.status().pending_jobs} queued jobs"
        )
    return quantum_computer


def prepare_quantum_circuit(
    qubits=2,
    classical_bits=2,
    simulation=False,
    verbose=False,
    quantum_computer="IBM",
    ibm_token=None,
    max_qubits=7,
):
    # Create registers for the circuit
    quantum_register = QuantumRegister(qubits)
    classical_register = ClassicalRegister(classical_bits)
    # Create a Quantum Circuit
    quantum_circuit = QuantumCircuit(quantum_register, classical_register)
    # Pick a quantum computer that has enough qubits to execute the circuit from IBM
    # Get a quantum computer with at least the number of selected qubits for the circuit and the lowest queue, or the simulator
    quantum_computer = get_ibm_quantum_computer(
        qubits=qubits,
        simulation=simulation,
        verbose=verbose,
        ibm_token=ibm_token,
        max_qubits=int(max_qubits),
    )
    return quantum_circuit, quantum_register, classical_register, quantum_computer


def execute_quantum_circuit(
    quantum_circuit, quantum_computer, shots=500, verbose=False
):
    queue_position = quantum_computer.status().pending_jobs + 1
    if verbose == True:
        print(
            f"Your job is number {queue_position} in the queue on {quantum_computer.name()}.  Please wait..."
        )
    result = execute(quantum_circuit, backend=quantum_computer, shots=shots).result()
    counts = result.get_counts(quantum_circuit)
    if verbose == True:
        print(
            f"{result.status} in {result.time_taken} seconds on {quantum_computer.name()}"
        )
    try:
        highest_probable = counts.most_frequent()
    except:
        highest_probable = list(counts.keys())[0]
    if verbose == True:
        probability = (
            100
            * float(result.get_counts(quantum_circuit)[highest_probable])
            / float(shots)
        )
        print(
            f"The probable result was {highest_probable} with {probability}% probability"
        )
    return highest_probable, result, counts


def entangle_qubits(qubits, quantum_circuit, quantum_register, classical_register):
    for i in range(qubits):
        quantum_circuit.h(quantum_register[i])
    for i in range(qubits - 1):
        quantum_circuit.cx(quantum_register[i], quantum_register[i + 1])
    quantum_circuit.measure(quantum_register, classical_register)
    drawing = quantum_circuit.draw()
    return quantum_circuit, drawing


def quantumseed(ibm_token=None, qubits=7, simulation=False, verbose=False):
    (
        quantum_circuit,
        quantum_register,
        classical_register,
        quantum_computer,
    ) = prepare_quantum_circuit(
        qubits=qubits,
        classical_bits=qubits,
        simulation=simulation,
        verbose=verbose,
        ibm_token=ibm_token,
        max_qubits=qubits,
    )
    quantum_circuit, drawing = entangle_qubits(
        qubits=qubits,
        quantum_circuit=quantum_circuit,
        quantum_register=quantum_register,
        classical_register=classical_register,
    )
    if verbose == True:
        print(f"Quantum Circuit:\n{drawing}")
    highest_probable, result, counts = execute_quantum_circuit(
        quantum_circuit=quantum_circuit,
        quantum_computer=quantum_computer,
        shots=512,
        verbose=verbose,
    )
    seed = ""
    for key, value in counts.items():
        seed += str(value)
    # Make the seed an integer
    seed = int(seed, 16)
    return seed
