#!/usr/bin/env python3
"""
Calculator Module
Handles quantum full adder mathematical operations for the OLED display
"""

import time
from qiskit import QuantumCircuit, Aer, execute

def calculate_sum(left_number, right_number):
    # 1️⃣ Converte para binário de 4 bits
    left_bin = decimal_to_binary(left_number)
    right_bin = decimal_to_binary(right_number)

    # 2️⃣ Faz a soma de 4 bits, retorna já em binário como string
    result_bin = add_4_bits(left_bin, right_bin)

    # 3️⃣ Converte resultado binário para decimal
    result_decimal = binary_to_decimal(result_bin)

    # 4️⃣ Mostra para você confirmar
    print(f"Soma de {left_number} + {right_number} = {result_bin} (bin) = {result_decimal} (dec)")

    return result_decimal

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
    qc = QuantumCircuit(4)
    if input_a:
        qc.x(0)
    if input_b:
        qc.x(1)

    xor_circuit = create_xor_gate(0, 0)
    qc.compose(xor_circuit, qubits=[0, 1, 2], inplace=True)

    and_circuit = create_and_gate(0, 0)
    qc.compose(and_circuit, qubits=[0, 1, 3], inplace=True)

    return qc

def create_full_adder(input_a, input_b, carry_in):
    """
    Cria um full adder composto por dois half adders + OR gate para carry.
    Retorna o circuito quântico correspondente.

    Qubit mapping:
    0: A
    1: B
    2: Carry in
    3: S1 (soma intermediária)
    4: C1 (carry intermediário de A e B)
    5: Soma final
    6: C2 (carry intermediário de S1 e carry in)
    7: Carry out final
    """
    qc = QuantumCircuit(8)

    # Inicializa entradas
    if input_a:
        qc.x(0)
    if input_b:
        qc.x(1)
    if carry_in:
        qc.x(2)

    # Primeiro half adder: A e B -> S1 e C1
    half_adder1 = create_half_adder(0, 0)
    qc.compose(half_adder1, [0, 1, 3, 4], inplace=True)

    # Segundo half adder: S1 e CarryIn -> Soma final e C2
    half_adder2 = create_half_adder(0, 0)
    qc.compose(half_adder2, [3, 2, 5, 6], inplace=True)

    # OR entre C1 e C2 -> Carry final
    or_circuit = create_or_gate(0, 0)
    qc.compose(or_circuit, [4, 6, 7], inplace=True)

    return qc

def add_4_bits(input_a, input_b):
    """
    Faz a soma de dois números de 4 bits (input como string '0101'), utilizando
    seu create_full_adder, mas reaproveitando os qubits para cada bit.
    Retorna a string binária do resultado.
    """
    assert len(input_a) == 4 and len(input_b) == 4, "Inputs devem ter 4 bits."

    # Inverter bits para LSB first
    a_bits = input_a[::-1]
    b_bits = input_b[::-1]

    carry = 0
    sum_bits = []

    for a_bit, b_bit in zip(a_bits, b_bits):
        a = int(a_bit)
        b = int(b_bit)

        # Criar circuito para esse bit
        qc = create_full_adder(a, b, carry)
        qc.measure_all()

        simulator = Aer.get_backend('qasm_simulator')
        job = execute(qc, simulator, shots=1000)
        result = job.result()
        counts = result.get_counts()

        # Interpretar resultado (invertido pelo Qiskit)
        most_common_result = max(counts, key=counts.get)
        bits = most_common_result[::-1]

        sum_bit = int(bits[5])
        carry = int(bits[7])

        sum_bits.append(str(sum_bit))

    # Adiciona carry final como MSB extra
    sum_bits.append(str(carry))

    # Reverter para MSB first e montar string binária
    result_bits = ''.join(sum_bits[::-1])
    return result_bits

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
    def test_and_gate():
        qc = create_and_gate(1, 0)
        qc = add_barriers_and_measure(qc)
        counts = run_quantum_circuit(qc)
        print(qc.draw())
        result = max(counts, key=counts.get)
        print(f"Result of AND gate: {result}")

    def test_or_gate():
        qc = create_or_gate(1, 0)
        qc = add_barriers_and_measure(qc)
        counts = run_quantum_circuit(qc)
        print(qc.draw())
        result = max(counts, key=counts.get)
        print(f"Result of OR gate: {result}")

    def test_xor_gate():
        qc = create_xor_gate(0, 1)
        qc = add_barriers_and_measure(qc)
        counts = run_quantum_circuit(qc)
        print(qc.draw())
        result = max(counts, key=counts.get)
        print(f"Result of XOR gate: {result}")

    def test_half_adder():
        qc = create_half_adder(1, 1)
        qc = add_barriers_and_measure(qc)
        counts = run_quantum_circuit(qc)
        print(qc.draw())
        result = max(counts, key=counts.get)
        print(f"Result of HALF ADDER gate: {result}")

    def test_full_adder(input_a, input_b, carry_in):
        expected_sum = (input_a + input_b + carry_in) % 2
        expected_carry = (input_a + input_b + carry_in) // 2

        qc = create_full_adder(input_a, input_b, carry_in)
        qc.measure_all()

        simulator = Aer.get_backend('qasm_simulator')
        job = execute(qc, simulator, shots=1000)
        result = job.result()
        counts = result.get_counts()

        # Exibir o circuito
        print(qc.draw())

        # Pega o resultado mais comum
        most_common_result = max(counts, key=counts.get)
        result_bits = most_common_result[::-1]  # Reverter porque Qiskit inverte as posições dos bits

        sum_bit = int(result_bits[5])
        carry_out = int(result_bits[7])

        print(f"Resultado bruto das medições: {counts}")
        print(f"Resultado mais comum (binário): {most_common_result}")
        print(f"Soma (bit 5): {sum_bit} (esperado: {expected_sum})")
        print(f"Carry out (bit 7): {carry_out} (esperado: {expected_carry})")

        if sum_bit == expected_sum and carry_out == expected_carry:
            print("\033[92mTESTE OK!\033[0m ✅")  # Verde
            return True
        else:
            print("\033[91mTESTE FALHOU!\033[0m ❌")  # Vermelho
            return False

    def test_full_adder_with_carry():
        qc = create_full_adder(1, 1, 2)
        qc.x(2)
        qc = add_barriers_and_measure(qc)
        counts = run_quantum_circuit(qc)
        print(qc.draw())
        result = max(counts, key=counts.get)
        print(f"Result of FULL ADDER with carry in: {result}")

    def test_add_4_bits(input_a, input_b):
        expected = int(input_a, 2) + int(input_b, 2)
        expected_bin = bin(expected)[2:].zfill(5)

        result_bin = add_4_bits(input_a, input_b)  # Agora retorna string diretamente
        print(f"Inputs: {input_a} + {input_b}")
        print(f"Esperado (binário): {expected_bin}")
        print(f"Obtido (binário):   {result_bin}")

        if result_bin == expected_bin:
            print("\033[92mTESTE OK!\033[0m ✅")
            return True
        else:
            print("\033[91mTESTE FALHOU!\033[0m ❌")
            return False

    def test_calculate_sum(left_number, right_number):
        """
        Testa a função calculate_sum com dois números decimais (0 a 15).
        Verifica automaticamente se o resultado está correto.
        """
        expected = left_number + right_number

        result = calculate_sum(left_number, right_number)

        print(f"Soma de {left_number} + {right_number} (esperado): {expected}")
        print(f"Resultado calculado: {result}")

        if result == expected:
            print("\033[92mTESTE OK!\033[0m ✅")
            return True
        else:
            print("\033[91mTESTE FALHOU!\033[0m ❌")
            return False


    left = 3
    right = 5

    testar_full_adder_1_bit = False
    if testar_full_adder_1_bit:
        t1 = test_full_adder(1, 1, 0)
        t2 = test_full_adder(1, 0, 1)
        t3 = test_full_adder(0, 0, 0)
        t4 = test_full_adder(1, 1, 1)
        t = [t1, t2, t3, t4]
        for idx, test in enumerate(t):
            result = "OK!" if test else "FALHOU!"
            print(f"Teste {idx+1}: {result}")


    testar_full_adder_4_bits = False
    if testar_full_adder_4_bits:
        t1 = test_add_4_bits('0101', '0011')  # 5 + 3 = 8 -> 01000
        t2 = test_add_4_bits('0111', '0001')  # 5 + 3 = 8 -> 01000
        t3 = test_add_4_bits('0000', '0000')  # 5 + 3 = 8 -> 01000
        t = [t1, t2, t3]
        for idx, test in enumerate(t):
            result = "OK!" if test else "FALHOU!"
            print(f"Teste {idx+1}: {result}")

    testar_calculate_sum = True
    if testar_calculate_sum:
        t1 = test_calculate_sum(5, 3)
        t2 = test_calculate_sum(7, 9)
        t3 = test_calculate_sum(0, 0)
        t4 = test_calculate_sum(15, 0)
        t = [t1, t2, t3, t4]
        for idx, test in enumerate(t):
            result = "OK!" if test else "FALHOU!"
            print(f"Teste {idx+1}: {result}")



