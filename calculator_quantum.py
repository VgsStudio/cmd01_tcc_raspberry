#!/usr/bin/env python3
"""
Calculator Module
Handles quantum full adder mathematical operations for the OLED display
"""

import time
from qiskit import QuantumCircuit, Aer, execute

def calculate_sum(left_number, right_number):
    # Simulate processing time
    time.sleep(0.5)
    
    result = left_number + right_number
    
    # print(f"Calculator: {left_number} + {right_number} = {result}")

    # # Create and run quantum circuit
    # circuit = create_toffoli_circuit(button_a, button_b)

    # # Show circuit diagram
    # print("Circuit:")
    # print(circuit.draw())

    # # Execute circuit
    # counts = run_quantum_circuit(circuit)

    # # Extract result (most frequent measurement)
    # result = max(counts, key=counts.get)
    
    return result

def format_result(result):
    """
    Format the result for display
    
    Args:
        result (int): The calculation result
    
    Returns:
        str: Formatted result string
    """
    return f"= {result}"

def validate_inputs(left_number, right_number):
    """
    Validate that inputs are within expected range
    
    Args:
        left_number (int): Left operand
        right_number (int): Right operand
    
    Returns:
        bool: True if inputs are valid
    """
    return (0 <= left_number <= 9) and (0 <= right_number <= 9)



def create_and_gate(input_a, input_b):
    """Create and gate for given input."""
    # Create 3-qubit circuit (2 inputs + 1 output)
    qc = QuantumCircuit(3)
    
    print(f"\nCreating AND circuit with inputs: A={int(input_a)}, B={int(input_b)}")
    
    # Set input states based on button presses
    if input_a:
        qc.x(0)  # Set qubit 0 to |1⟩ if button A is pressed
    if input_b:
        qc.x(1)  # Set qubit 1 to |1⟩ if button B is pressed
    
    # Output qubit 2 starts at |0⟩
    
    # Implement Toffoli gate (quantum AND)
    qc.ccx(0, 1, 2)  # Output = A AND B
    
    return qc

def create_or_gate(input_a, input_b):
    """Create or gate for given input."""
    # Create 3-qubit circuit (2 inputs + 1 output)
    qc = QuantumCircuit(3)
    
    print(f"\nCreating OR circuit with inputs: A={int(input_a)}, B={int(input_b)}")
    
    # Set input states based on button presses
    if input_a:
        qc.x(0)  # Set qubit 0 to |1⟩ if button A is pressed
    if input_b:
        qc.x(1)  # Set qubit 1 to |1⟩ if button B is pressed
    
    # Output qubit 2 starts at |0⟩
    
    # Implement OR gate: if A is true, output is true
    qc.cx(0, 2)  # If A=1, flip output
    
    # If B is true and output is not already true, make it true
    qc.cx(1, 2)  # If B=1, flip output
    
    # Handle the case where both A and B are true (output got flipped twice)
    qc.ccx(0, 1, 2)  # If both A and B are 1, flip output back
    
    return qc

def create_xor_gate(input_a, input_b):
    """Create XOR gate for given input."""
    # Create 3-qubit circuit (2 inputs + 1 output)
    qc = QuantumCircuit(3)
    
    print(f"\nCreating XOR circuit with inputs: A={int(input_a)}, B={int(input_b)}")

    # Set input states based on button presses
    if input_a:
        qc.x(0)  # Set qubit 0 to |1⟩ if button A is pressed
    if input_b:
        qc.x(1)  # Set qubit 1 to |1⟩ if button B is pressed
    
    # Implement XOR gate using CNOT gates
    qc.cx(0, 2)  # If A=1, flip output
    qc.cx(1, 2)  # If B=1, flip output (XOR behavior)
        
    return qc

def create_half_adder(input_a, input_b):
    """Create half adder by composing XOR and AND gate subcircuits."""
    # Create the main 4-qubit circuit
    qc = QuantumCircuit(4)
    
    print(f"\nCreating half adder using subcircuits with inputs: A={int(input_a)}, B={int(input_b)}")

    # Set input states
    if input_a:
        qc.x(0)
    if input_b:
        qc.x(1)

    # Create XOR subcircuit for sum
    xor_circuit = create_xor_gate(input_a, input_b)
    # Map XOR output (qubit 2 in xor_circuit) to sum bit (qubit 2 in main circuit)
    qc.compose(xor_circuit, qubits=[0, 1, 2], inplace=True)
    
    # Create AND subcircuit for carry  
    and_circuit = create_and_gate(input_a, input_b)
    # Map AND output (qubit 2 in and_circuit) to carry bit (qubit 3 in main circuit)
    qc.compose(and_circuit, qubits=[0, 1, 3], inplace=True)

    return qc

def create_full_adder(input_a, input_b, carry_in):
    """Create full adder by composing half adder and OR gate subcircuits."""
    # Create the main 7-qubit circuit
    qc = QuantumCircuit(7)
    
    print(f"\nCreating full adder using subcircuits with inputs: A={int(input_a)}, B={int(input_b)}, Carry In={int(carry_in)}")

    # Set input states
    if carry_in:
        qc.x(2)

    # Create first half adder for sum
    half_adder1 = create_half_adder(input_a, input_b)
    qc.compose(half_adder1, [0, 1, 3, 4], inplace=True)  # Map outputs to qubits 3 (output) and 4 (carry)

    # Create second half adder for final sum with carry in
    half_adder2 = create_half_adder(0, carry_in)
    qc.compose(half_adder2, [3, 2, 5, 6], inplace=True)  # Map outputs to qubits 5 (final sum) and 6 (final carry)

    return qc

def add_barriers_and_measure(circuit):
    """Add barriers and measurements to a quantum circuit."""
    circuit.barrier()
    circuit.measure_all()
    return circuit

def run_quantum_circuit(circuit):
    """Execute the quantum circuit on simulator."""
    simulator = Aer.get_backend('qasm_simulator')
    job = execute(circuit, simulator, shots=1000)
    result = job.result()
    counts = result.get_counts()

    return counts


def decimal_to_binary(decimal):
    """Convert decimal number to binary string."""
    return bin(decimal)[2:].zfill(4)  # Convert to binary and pad to 4 bits

if __name__ == "__main__":
    # Example usage
    left = 3
    right = 5

    if validate_inputs(left, right):
        result = calculate_sum(left, right)
        formatted_result = format_result(result)
        print(formatted_result)


    # Test AND and OR gates
    qc1 = create_and_gate(1, 0)
    qc1 = add_barriers_and_measure(qc1)
    counts = run_quantum_circuit(qc1)
    print(qc1.draw())
    result = max(counts, key=counts.get)
    print(f"Result of AND gate: {result}")

    qc2 = create_or_gate(1, 0)
    qc2 = add_barriers_and_measure(qc2)
    counts = run_quantum_circuit(qc2)
    print(qc2.draw())
    result = max(counts, key=counts.get)
    print(f"Result of OR gate: {result}")

    # Test XOR gate

    qc3 = create_xor_gate(0, 1)
    qc3 = add_barriers_and_measure(qc3)
    print(qc3.draw())

    counts = run_quantum_circuit(qc3)
    result = max(counts, key=counts.get)
    print(f"Result of XOR gate: {result}")

    # Test half adder

    qc4 = create_half_adder(1,1)
    qc4 = add_barriers_and_measure(qc4)
    print(qc4.draw())

    counts = run_quantum_circuit(qc4)
    result = max(counts, key=counts.get)
    print(f"Result of HALF ADDER gate: {result}")

    # Test full adder

    qc5 = create_full_adder(1, 1, 0)
    qc5 = add_barriers_and_measure(qc5)
    print(qc5.draw())
    
    counts = run_quantum_circuit(qc5)
    result = max(counts, key=counts.get)
    print(f"Result of FULL ADDER gate: {result}")

    # Test full adder with carry in
    qc6 = create_full_adder(1, 1, 1)
    qc6 = add_barriers_and_measure(qc6)
    print(qc6.draw())

    counts = run_quantum_circuit(qc6)
    result = max(counts, key=counts.get)
    print(f"Result of FULL ADDER with carry in: {result}")

   