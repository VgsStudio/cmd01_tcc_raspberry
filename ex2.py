from qiskit import QuantumCircuit
 
# Create a new circuit with THREE qubits (Toffoli needs 3: 2 controls + 1 target)
qc = QuantumCircuit(3)

print("=== Toffoli Gate Demonstration ===")
print("Initial state: |000⟩ (all qubits start in 0)")

from qiskit import QuantumCircuit
 
# Create a new circuit with THREE qubits (for AND gate: 2 inputs + 1 output)
qc = QuantumCircuit(3)

print("=== Quantum AND Gate Implementation ===")
print("Using Toffoli gate to implement classical AND logic")
print("\nTruth Table for AND gate:")
print("A | B | A AND B")
print("0 | 0 |   0")
print("0 | 1 |   0") 
print("1 | 0 |   0")
print("1 | 1 |   1")

# Test case: A=1, B=1 (should output 1)
print("\nTest case: A=1, B=1")
print("Setting up inputs:")
qc.x(0)  # Input A = 1 (qubit 0)
# qc.x(1)  # Input B = 1 (qubit 1)
# Output qubit 2 starts at 0

# Add a barrier for visualization
qc.barrier()

# Implement AND gate using Toffoli (CCX)
print("Implementing AND gate: Output = A AND B")
qc.ccx(0, 1, 2)  # If A=1 AND B=1, then flip output to 1

# Add another barrier for visualization
qc.barrier()

# Measure all qubits
qc.measure_all()

# Execute the circuit on a simulator
from qiskit import Aer, execute
simulator = Aer.get_backend('qasm_simulator')
job = execute(qc, simulator, shots=1000)
result = job.result()
counts = result.get_counts()

print(f"\nResults: {counts}")