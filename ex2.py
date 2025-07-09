from qiskit import QuantumCircuit, Aer, execute
import RPi.GPIO as GPIO
import time

# GPIO Configuration
BUTTON_A_PIN = 26  # GPIO 26 for input A
BUTTON_B_PIN = 20  # GPIO 20 for input B

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_A_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_B_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("=== Raspberry Pi Quantum AND Gate ===")
print("Using physical buttons to control Toffoli gate inputs")
print("\nGPIO Configuration:")
print(f"- Button A (Input A): GPIO {BUTTON_A_PIN}")
print(f"- Button B (Input B): GPIO {BUTTON_B_PIN}")
print("- Both buttons have pull-up resistors (pressed = LOW)")

def read_gpio_inputs():
    """Read the current state of both GPIO buttons."""
    # Buttons are active LOW (pressed = False/0, not pressed = True/1)
    button_a_pressed = not GPIO.input(BUTTON_A_PIN)  # Invert for intuitive logic
    button_b_pressed = not GPIO.input(BUTTON_B_PIN)  # Invert for intuitive logic
    
    return button_a_pressed, button_b_pressed

def create_toffoli_circuit(input_a, input_b):
    """Create Toffoli gate circuit with given inputs."""
    # Create 3-qubit circuit (2 inputs + 1 output)
    qc = QuantumCircuit(3)
    
    print(f"\nCreating circuit with inputs: A={int(input_a)}, B={int(input_b)}")
    
    # Set input states based on button presses
    if input_a:
        qc.x(0)  # Set qubit 0 to |1⟩ if button A is pressed
    if input_b:
        qc.x(1)  # Set qubit 1 to |1⟩ if button B is pressed
    
    # Output qubit 2 starts at |0⟩
    
    # Add barrier for visualization
    qc.barrier()
    
    # Implement Toffoli gate (quantum AND)
    qc.ccx(0, 1, 2)  # Output = A AND B
    
    # Add barrier and measure
    qc.barrier()
    qc.measure_all()
    
    return qc

def run_quantum_circuit(circuit):
    """Execute the quantum circuit on simulator."""
    simulator = Aer.get_backend('qasm_simulator')
    job = execute(circuit, simulator, shots=1000)
    result = job.result()
    counts = result.get_counts()
    
    return counts

def main():
    """Main loop to monitor buttons and execute Toffoli gate."""
    
    print("\n=== Instructions ===")
    print("1. Press and hold button A (GPIO 26) for input A = 1")
    print("2. Press and hold button B (GPIO 20) for input B = 1") 
    print("3. Press both buttons simultaneously to see A AND B = 1")
    print("4. Press Ctrl+C to exit")
    print("\nTruth Table:")
    print("A | B | A AND B")
    print("0 | 0 |   0")
    print("0 | 1 |   0")
    print("1 | 0 |   0")
    print("1 | 1 |   1")
    
    print("\n=== Monitoring GPIO Inputs ===")
    print("Waiting for button presses...")
    
    try:
        last_state = (False, False)
        
        while True:
            # Read current button states
            button_a, button_b = read_gpio_inputs()
            current_state = (button_a, button_b)
            
            # Only process if state changed
            if current_state != last_state:
                print(f"\nButton states: A={int(button_a)}, B={int(button_b)}")
                
                # Create and run quantum circuit
                circuit = create_toffoli_circuit(button_a, button_b)
                
                # Show circuit diagram
                print("Circuit:")
                print(circuit.draw())
                
                # Execute circuit
                counts = run_quantum_circuit(circuit)
                
                # Extract result (most frequent measurement)
                result = max(counts, key=counts.get)
                output = int(result[0])  # Extract output bit (leftmost in Qiskit)
                
                print(f"Quantum Result: {counts}")
                print(f"Output: {output} ({'True' if output else 'False'})")
                
                # Verify classical AND logic
                expected = int(button_a and button_b)
                status = "✅ Correct" if output == expected else "❌ Error"
                print(f"Expected: {expected} | Actual: {output} | {status}")
                
                last_state = current_state
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\nExiting...")
    
    finally:
        # Clean up GPIO
        GPIO.cleanup()
        print("GPIO cleanup completed.")

if __name__ == '__main__':
    main()