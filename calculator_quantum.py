#!/usr/bin/env python3
"""
Calculator Module
Handles quantum full adder mathematical operations for the OLED display
"""

import time
from qiskit import QuantumCircuit, Aer, execute

def calculate_sum(left_number, right_number):

    left_number_bin = decimal_to_binary(left_number)
    right_number_bin = decimal_to_binary(right_number)
    

    qc = add_4_bits(right_number_bin, left_number_bin)
    qc = add_barriers_and_measure(qc)

    counts = run_quantum_circuit(qc)
    result = max(counts, key=counts.get)
    print(qc.draw())
    print(f"Result of 4-bit adder: {result}")

    binary_result = extract_from_4_bits_sum(result)

    print(binary_result)

    result = binary_to_decimal(binary_result)
    
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

def create_full_adder(input_a, input_b, carry_in_qubit):
    """Create full adder by composing half adder and OR gate subcircuits.
    
    Args:
        input_a: boolean value for input A
        input_b: boolean value for input B  
        carry_in_qubit: qubit index for carry input (instead of boolean value)
    
    Returns:
        QuantumCircuit with full adder implementation
        Qubit mapping:
        - qubits 0, 1: input A, B
        - qubit 2: carry in
        - qubit 5: sum output
        - qubit 6: carry out
    """
    # Create the main 7-qubit circuit
    qc = QuantumCircuit(7)
    
    print(f"\nCreating full adder using subcircuits with inputs: A={int(input_a)}, B={int(input_b)}, Carry In qubit={carry_in_qubit}")

    # Set input states for A and B
    if input_a:
        qc.x(0)
    if input_b:
        qc.x(1)
    
    # Note: carry_in_qubit is already set externally, so we don't initialize it here

    # Create first half adder for sum of A and B
    half_adder1 = create_half_adder(input_a, input_b)
    qc.compose(half_adder1, [0, 1, 3, 4], inplace=True)  # Map outputs to qubits 3 (sum) and 4 (carry)

    # Create second half adder for final sum with carry in
    # Note: we use 0 for the second half adder inputs since the actual values are in qubits 3 and 2
    half_adder2 = create_half_adder(0, 0)  # Values will come from qubits, not initial states
    qc.compose(half_adder2, [3, 2, 5, 6], inplace=True)  # Map outputs to qubits 5 (final sum) and 6 (final carry)

    return qc

def add_4_bits(input_a, input_b):
    """
    Add two 4-bit binary numbers using simple quantum gates.
    input_a, input_b: strings of 4 bits each, MSB first (e.g., '1001')
    Returns: QuantumCircuit with sum and carry-out qubits
    """
    assert len(input_a) == 4 and len(input_b) == 4, "Inputs must be 4 bits each."

    # Create main quantum circuit with enough qubits
    # Qubits 0-3: Input A, 4-7: Input B, 8-11: Sum, 12-15: Carry
    qc = QuantumCircuit(16)
    
    print(f"\nCreating 4-bit adder with inputs: A={input_a}, B={input_b}")
    
    # Reverse inputs to process LSB first (easier for carry propagation)
    input_a_rev = input_a[::-1]  # LSB first
    input_b_rev = input_b[::-1]  # LSB first
    
    # Set initial input states
    for i in range(4):
        if input_a_rev[i] == '1':
            qc.x(i)  # Set bit i of input A (qubits 0-3)
        if input_b_rev[i] == '1':
            qc.x(i + 4)  # Set bit i of input B (qubits 4-7)
    
    # Implement 4-bit ripple carry adder directly
    for i in range(4):
        if i == 0:
            # Bit 0: Half adder (no carry in)
            print(f"Processing bit {i} (half adder)")
            
            # Sum[0] = A[0] ⊕ B[0] 
            qc.cx(0, 8)     # A[0] -> Sum[0]
            qc.cx(4, 8)     # B[0] -> Sum[0] (XOR effect)
            
            # Carry[0] = A[0] ∧ B[0]
            qc.ccx(0, 4, 12)  # A[0] ∧ B[0] -> Carry[0]
            
        else:
            # Bits 1-3: Full adder (with carry in)
            print(f"Processing bit {i} (full adder)")
            
            # Sum[i] = A[i] ⊕ B[i] ⊕ Carry[i-1]
            qc.cx(i, 8 + i)          # A[i] -> Sum[i]
            qc.cx(4 + i, 8 + i)      # B[i] -> Sum[i] 
            qc.cx(12 + i - 1, 8 + i) # Carry[i-1] -> Sum[i]
            
            # Carry[i] = (A[i] ∧ B[i]) ∨ (A[i] ∧ Carry[i-1]) ∨ (B[i] ∧ Carry[i-1])
            # Using: Carry[i] = A[i]∧B[i] ∨ Carry[i-1]∧(A[i]⊕B[i])
            
            # First: A[i] ∧ B[i] -> temp result
            qc.ccx(i, 4 + i, 12 + i)
            
            # Second: A[i] ⊕ B[i] (stored temporarily, then used with carry)
            # We'll use the carry propagation: if there's a carry from previous and either A or B is 1
            qc.ccx(i, 12 + i - 1, 12 + i)      # A[i] ∧ Carry[i-1] -> Carry[i]
            qc.ccx(4 + i, 12 + i - 1, 12 + i)  # B[i] ∧ Carry[i-1] -> Carry[i]
    
    # Final result:
    # Sum bits are in qubits 8-11 (LSB to MSB)
    # Carry bits are in qubits 12-15
    # Final carry out is in qubit 15
    
    return qc

def extract_from_4_bits_sum(binary_result):
    binary = binary_result[0] + binary_result[4:8]

    return binary

def add_barriers_and_measure(circuit):
    """Add barriers and measurements to a quantum circuit."""
    circuit.barrier()
    # Only add measure_all if the circuit doesn't already have measurements
    if not hasattr(circuit, '_measurements') or len(circuit._measurements) == 0:
        circuit.measure_all()
    return circuit

def run_quantum_circuit(circuit):
    """Execute the quantum circuit on simulator."""
    simulator = Aer.get_backend('qasm_simulator')
    job = execute(circuit, simulator, shots=1000)
    result = job.result()
    counts = result.get_counts()

    return counts

def binary_to_decimal(binary):
    """Convert binary string to decimal number."""
    return int(binary, 2)  # Convert binary string to decimal integer


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

    qc5 = create_full_adder(1, 1, 2)  # Using qubit 2 for carry_in
    qc5 = add_barriers_and_measure(qc5)
    print(qc5.draw())
    
    counts = run_quantum_circuit(qc5)
    result = max(counts, key=counts.get)
    print(f"Result of FULL ADDER gate: {result}")

    # Test full adder with carry in
    qc6 = create_full_adder(1, 1, 2)  # Using qubit 2 for carry_in
    qc6.x(2)  # Set carry_in qubit to 1
    qc6 = add_barriers_and_measure(qc6)
    print(qc6.draw())

    counts = run_quantum_circuit(qc6)
    result = max(counts, key=counts.get)
    print(f"Result of FULL ADDER with carry in: {result}")

    # Test 4-bit adder

    print("-"*30)

    qc7 = add_4_bits('1001', '1001')
    qc7 = add_barriers_and_measure(qc7)

    counts = run_quantum_circuit(qc7)
    result = max(counts, key=counts.get)
    print(qc7.draw())
    print(f"Result of 4-bit adder: {result}")

    binary = result[0] + result[4:8]

    print(binary)

    print(binary_to_decimal(binary))
   