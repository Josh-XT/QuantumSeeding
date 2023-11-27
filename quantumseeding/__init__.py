from qiskit import (
    QuantumRegister,
    ClassicalRegister,
    QuantumCircuit,
    execute,
    Aer,
    IBMQ,
)


class QuantumSeeding:
    def __init__(self, ibm_token=None, max_qubits=7, verbose=False, simulation=False):
        self.ibm_token = ibm_token
        self.max_qubits = int(max_qubits)
        self.verbose = verbose
        self.simulation = simulation
        self.quantum_register = QuantumRegister(self.max_qubits)
        self.classical_register = ClassicalRegister(self.max_qubits)
        self.quantum_circuit = QuantumCircuit(
            self.quantum_register, self.classical_register
        )
        self.quantum_computer = self.get_ibm_quantum_computer(qubits=self.max_qubits)

    # Define functions to simplify interactions with quantum computers
    def get_ibm_quantum_computer(self, qubits=2):
        quantum_computer = None
        if self.ibm_token is None or self.ibm_token == "YOUR_IBM_TOKEN":
            if self.verbose == True:
                print("No IBM Token found.  Using Quantum Computer Simulator")
            self.simulation = True
        else:
            IBMQ.save_account(self.ibm_token, overwrite=True)
            IBMQ.load_account()
        if qubits > self.max_qubits:
            if self.verbose == True:
                print(f"No Quantum Computers available with {qubits} qubits.")
            self.simulation = True
        # Finds a quantum computer at IBM with the lowest queue as long as it has enough qubits for the circuit
        if self.simulation == False:  # Execute the circuit on a quantum computer at IBM
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
                            if self.verbose == True:
                                print(
                                    f"Quantum Computer {backend.name()} has {queue} queued jobs and {qubit_count} qubits"
                                )
                        else:
                            if self.verbose == True:
                                print(
                                    f"Quantum Computer {backend.name()} has {qubit_count} qubits, but we need {qubits} qubits"
                                )
                except:
                    if self.verbose == True:
                        print(f"Quantum Computer {backend.name()} is not operational")
            if quantum_computer is None:
                if self.verbose == True:
                    print(f"No Quantum Computers available with {qubits} qubits.")
                self.simulation = True
        if (
            self.simulation == True or quantum_computer is None
        ):  # Execute the circuit on the simulator
            quantum_computer = Aer.get_backend("qasm_simulator")
            if self.verbose == True:
                print(f"Using Quantum Computer Simulator")
        if self.verbose == True and self.simulation == False:
            print(
                f"Using Quantum Computer: {quantum_computer.name()} with {quantum_computer.status().pending_jobs} queued jobs"
            )
        return quantum_computer

    def execute_quantum_circuit(self, shots=512):
        queue_position = self.quantum_computer.status().pending_jobs + 1
        if self.verbose == True:
            print(
                f"Your job is number {queue_position} in the queue on {self.quantum_computer.name()}.  Please wait..."
            )
        result = execute(
            self.quantum_circuit, backend=self.quantum_computer, shots=shots
        ).result()
        counts = result.get_counts(self.quantum_circuit)
        if self.verbose == True:
            print(
                f"{result.status} in {result.time_taken} seconds on {self.quantum_computer.name()}"
            )
        try:
            highest_probable = counts.most_frequent()
        except:
            highest_probable = list(counts.keys())[0]
        if self.verbose == True:
            probability = (
                100
                * float(result.get_counts(self.quantum_circuit)[highest_probable])
                / float(shots)
            )
            print(
                f"The probable result was {highest_probable} with {probability}% probability"
            )
        return highest_probable, result, counts

    def entangle_qubits(self):
        for i in range(self.max_qubits):
            self.quantum_circuit.h(self.quantum_register[i])
        for i in range(self.max_qubits - 1):
            self.quantum_circuit.cx(
                self.quantum_register[i], self.quantum_register[i + 1]
            )
        self.quantum_circuit.measure(self.quantum_register, self.classical_register)
        return self.quantum_circuit.draw()

    def get_seed(self):
        drawing = self.entangle_qubits()
        if self.verbose == True:
            print(f"Quantum Circuit:\n{drawing}")
        highest_probable, result, counts = self.execute_quantum_circuit(
            shots=512,
        )
        seed = ""
        for key, value in counts.items():
            seed += str(value)
        # Make the seed an integer
        seed = int(seed, 16)
        return seed
