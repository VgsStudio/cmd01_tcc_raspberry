from qiskit import QuantumCircuit, Aer, execute
import RPi.GPIO as GPIO
import time
from rpi_ws281x import *

# GPIO Configuration
BUTTON_A_PIN = 17  # GPIO 17 for input A
BUTTON_B_PIN = 4  # GPIO 4 for input B

# LED Strip Configuration
LED_COUNT      = 60      # Number of LEDs in your strip
LED_PIN        = 18      # GPIO 18. DO NOT CHANGE.
LED_FREQ_HZ    = 800000  # LED signal frequency (usually 800khz)
LED_DMA        = 10      # DMA channel
LED_BRIGHTNESS = 200     # Brightness from 0 to 255
LED_INVERT     = False   # Change to True if signal needs to be inverted
LED_CHANNEL    = 0       # Change to '1' for GPIOs 13, 19, 41, 45 or 53

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_A_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_B_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize LED strip
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

print("=== Raspberry Pi Quantum AND Gate with LED Strip ===")
print("Using physical buttons to control Toffoli gate inputs")
print("\nGPIO Configuration:")
print(f"- Button A (Input A): GPIO {BUTTON_A_PIN}")
print(f"- Button B (Input B): GPIO {BUTTON_B_PIN}")
print("- Both buttons have pull-up resistors (pressed = LOW)")
print(f"- LED Strip: GPIO {LED_PIN} ({LED_COUNT} LEDs)")
print("- LED Colors: Red = 0, Blue = 1")

def read_gpio_inputs():
    """Read the current state of both GPIO buttons."""
    # Buttons are active LOW (pressed = False/0, not pressed = True/1)
    button_a_pressed = not GPIO.input(BUTTON_A_PIN)  # Invert for intuitive logic
    button_b_pressed = not GPIO.input(BUTTON_B_PIN)  # Invert for intuitive logic
    
    return button_a_pressed, button_b_pressed

def clear_strip():
    """Turn OFF all LEDs on the strip."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

def display_result_on_leds(binary_value):
    """Display the result on LED strip: Red for 0, Blue for 1."""
    if binary_value == 1:
        color = Color(0, 0, 255)  # Blue for 1
        color_name = "Blue"
    else:
        color = Color(255, 0, 0)  # Red for 0
        color_name = "Red"
    
    # Light up all LEDs with the result color
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()
    
    print(f"LED Strip: {color_name} (Binary: {binary_value})")

def show_input_pattern(input_a, input_b):
    """Show input pattern on LED strip before Toffoli gate."""
    # Clear strip first
    clear_strip()
    time.sleep(0.2)
    
    # Show inputs on first few LEDs
    if input_a:
        # Show blue on first 30 LEDs for input A = 1
        for i in range(30):
            strip.setPixelColor(i, Color(0, 0, 255))
    else:
        # Show red on first 30 LEDs for input A = 0
        for i in range(30):
            strip.setPixelColor(i, Color(255, 0, 0))
    
    if input_b:
        # Show blue on next 30 LEDs for input B = 1
        for i in range(30, 60):
            strip.setPixelColor(i, Color(0, 0, 255))
    else:
        # Show red on next 30 LEDs for input B = 0
        for i in range(30, 60):
            strip.setPixelColor(i, Color(255, 0, 0))
    
    strip.show()
    time.sleep(0.5)

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
    print("1. Press and hold button A (GPIO 17) for input A = 1")
    print("2. Press and hold button B (GPIO 4) for input B = 1") 
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
                
                # Show input pattern on LED strip
                show_input_pattern(button_a, button_b)
                
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
                
                # Display result on LED strip
                display_result_on_leds(output)
                
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
        # Clear LED strip and clean up GPIO
        clear_strip()
        GPIO.cleanup()
        print("LED strip cleared and GPIO cleanup completed.")

if __name__ == '__main__':
    main()