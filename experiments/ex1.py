# -*- coding: utf-8 -*-
import time
import random
import sys
import select
import threading
import os
import math
import RPi.GPIO as GPIO
from rpi_ws281x import *
import board
import busio
import warnings
from PIL import Image, ImageDraw
import adafruit_ssd1306

# Add parent directory to path for module imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.digit_display import show_exp_x_display
from modules.hardware_config import PINS, LED_CONFIG, OLED_CONFIG, ANIMATION_CONFIG, TIMING_CONFIG
from qiskit import QuantumCircuit, execute, Aer
from qiskit.circuit.library import HGate

# --- Hardware Configuration (from centralized config) ---
LED_COUNT      = LED_CONFIG['COUNT']
LED_PIN        = LED_CONFIG['PIN']
LED_FREQ_HZ    = LED_CONFIG['FREQ_HZ']
LED_DMA        = LED_CONFIG['DMA']
LED_BRIGHTNESS = LED_CONFIG['BRIGHTNESS']
LED_INVERT     = LED_CONFIG['INVERT']
LED_CHANNEL    = LED_CONFIG['CHANNEL']

# --- Button Configuration (from centralized config) ---
BUTTON_PIN     = PINS['BUTTON_CALC']  # GPIO 26 for button input

# --- OLED Display Configuration (from centralized config) ---
# Suppress I2C frequency warning
warnings.filterwarnings("ignore", message="I2C frequency is not settable in python, ignoring!")

# I2C pins for OLED (using centralized config)
i2c = busio.I2C(scl=board.D3, sda=board.D2)

# OLED display dimensions
WIDTH = OLED_CONFIG['WIDTH']
HEIGHT = OLED_CONFIG['HEIGHT']
display = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)

# --- Probability Configuration ---
BLUE_PROBABILITY = 50    # Percentage chance for blue (1)
RED_PROBABILITY = 100 - BLUE_PROBABILITY   # Percentage chance for red (0)

# --- Animation settings ---
SPRITE_SIZE = (64, 64)  # Size of each animation frame
FRAMES = 30  # Number of frames in the animation
animation_frames = []  # Will store loaded animation frames
animation_loaded = False

# --- Global Variables ---
alternating = True       # Controls the alternating pattern
current_color = 0        # 0 = Red, 1 = Blue

def clear_strip(strip):
    """Turns OFF all LEDs on the strip."""
    print("\nClearing strip...")
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()
    time.sleep(0.5)

def clear_display():
    """Clear the OLED display"""
    try:
        display.fill(0)
        display.show()
    except Exception as e:
        print(f"⚠️  OLED clear error: {e}")

def light_color(strip, color, binary_value):
    """Lights up the entire strip with a specific color."""
    print(f"Result: {binary_value} ({'Blue' if binary_value == 1 else 'Red'})")
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

def draw_color(strip, color_value):
    """Draws a color on the strip without printing."""
    if color_value == 1:
        color = Color(0, 0, 255)  # Blue
    else:
        color = Color(255, 0, 0)  # Red
    
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

def alternate_colors(strip):
    """Continuously alternates between red and blue."""
    global alternating, current_color
    
    print("Starting color alternation... Press the button (GPIO 26) to stop and enter quantum hadamard mode.")
    
    while alternating:
        draw_color(strip, current_color)
        current_color = 1 - current_color  # Toggle between 0 and 1
        time.sleep(0.5)  # Half second between changes

def mixed_alternating_colors(strip):
    """Different LEDs alternate in different orders creating a mixed pattern."""
    global alternating
    
    print("Starting mixed alternation... Press the button (GPIO 26) to stop and enter quantum hadamard mode.")
    
    # Create different starting colors for each LED
    led_colors = []
    for i in range(strip.numPixels()):
        # Even LEDs start with red (0), odd LEDs start with blue (1)
        led_colors.append(i % 2)
    
    while alternating:
        # Draw current pattern
        for i in range(strip.numPixels()):
            if led_colors[i] == 1:
                strip.setPixelColor(i, Color(0, 0, 255))  # Blue
            else:
                strip.setPixelColor(i, Color(255, 0, 0))  # Red
        
        strip.show()
        time.sleep(0.2)  # Slower - 0.2 seconds between changes
        
        # Toggle each LED's color
        for i in range(strip.numPixels()):
            led_colors[i] = 1 - led_colors[i]  # Toggle between 0 and 1

def restart_alternation():
    """Restarts the alternation mode."""
    global alternating
    alternating = True

def load_animation_frames():
    """Load animation frames from sprite sheet bitmap - optimized for faster startup"""
    global animation_frames, animation_loaded
    
    if animation_loaded:
        return
    
    try:
        # Load the sprite sheet bitmap
        sprite_path = "./assets/icons/atom.bmp"
        if os.path.exists(sprite_path):
            sprite_sheet = Image.open(sprite_path)
            
            # Convert to 1-bit (monochrome) if not already
            if sprite_sheet.mode != '1':
                sprite_sheet = sprite_sheet.convert('1')
            
            # Extract individual frames from the sprite sheet
            frame_width = SPRITE_SIZE[0]
            frame_height = SPRITE_SIZE[1]
            
            # Calculate how many frames we can actually extract from the sprite sheet
            available_frames = min(FRAMES, sprite_sheet.size[0] // frame_width)
            
            # Pre-calculate display size once
            display_size = int(HEIGHT * 0.95)  # Make it 95% of display height (about 51 pixels)
            
            for i in range(available_frames):
                # Calculate frame position in sprite sheet
                x = i * frame_width
                y = 0
                
                # Extract frame
                frame_box = (x, y, x + frame_width, y + frame_height)
                frame = sprite_sheet.crop(frame_box)
                
                # Make the atom bigger - resize to take up more of the display
                frame = frame.resize((display_size, display_size), Image.NEAREST)
                
                animation_frames.append(frame)
            
            # If we have fewer frames than requested, duplicate frames to reach 30
            if len(animation_frames) < FRAMES and len(animation_frames) > 0:
                original_frames = animation_frames.copy()
                while len(animation_frames) < FRAMES:
                    # Add frames by cycling through original frames
                    frame_to_add = original_frames[len(animation_frames) % len(original_frames)]
                    animation_frames.append(frame_to_add)
            
            animation_loaded = True
            print(f"✅ Loaded {len(animation_frames)} animation frames (requested {FRAMES})")
            
        else:
            print(f"⚠️  Animation file not found: {sprite_path}")
            animation_loaded = False
            
    except Exception as e:
        print(f"❌ Error loading animation: {e}")
        animation_loaded = False

def draw_quantum_spinner(draw, frame):
    """Draw a bitmap-based quantum atom animation during measurement"""
    global animation_frames, animation_loaded
    
    # Load animation frames only when first needed (lazy loading for faster startup)
    if not animation_loaded:
        load_animation_frames()
    
    # Clear the display
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=0)
    
    # Draw "EXP. 1" text at the top
    text = "EXP. 1"
    # Calculate text position (centered at top)
    text_width = len(text) * 6  # Approximate character width
    text_x = (WIDTH - text_width) // 2
    text_y = 5
    draw.text((text_x, text_y), text, fill=255)
    
    # Draw bitmap animation if frames are loaded
    if animation_loaded and animation_frames:
        # Calculate which frame to show (fast animation for 30 FPS effect)
        current_frame_index = frame % len(animation_frames)  # Change frame every cycle for max speed
        current_frame = animation_frames[current_frame_index]
        
        # Center the animation below the text
        frame_width, frame_height = current_frame.size
        center_x = (WIDTH - frame_width) // 2   # Center horizontally on 128px width
        center_y = ((HEIGHT - frame_height) // 2) + 10  # Center vertically but shifted down for text
        
        # Draw the frame pixel by pixel
        frame_pixels = list(current_frame.getdata())
        
        for y in range(frame_height):
            for x in range(frame_width):
                pixel_index = y * frame_width + x
                if pixel_index < len(frame_pixels):
                    # If pixel is white/on (1), draw it on the display
                    if frame_pixels[pixel_index]:
                        draw_x = center_x + x
                        draw_y = center_y + y
                        if 0 <= draw_x < WIDTH and 0 <= draw_y < HEIGHT:
                            draw.point((draw_x, draw_y), fill=255)
    
    else:
        # Fallback to original spinning circle if bitmap loading failed
        center_x = WIDTH // 2
        center_y = (HEIGHT // 2) + 10  # Shifted down to make room for text
        radius = 15  # Smaller radius to fit with text
        
        # Draw spinning circle
        angles = [0, 45, 90, 135, 180, 225, 270, 315]
        num_segments = 8
        active_segment = frame % num_segments
        
        for i in range(num_segments):
            angle = math.radians(angles[i])
            x1 = center_x + int(radius * 0.7 * math.cos(angle))
            y1 = center_y + int(radius * 0.7 * math.sin(angle))
            x2 = center_x + int(radius * math.cos(angle))
            y2 = center_y + int(radius * math.sin(angle))
            
            # Draw line segments with varying brightness
            if i == active_segment:
                # Bright segment
                draw.line([(x1, y1), (x2, y2)], fill=255, width=2)
            elif abs(i - active_segment) <= 2 or abs(i - active_segment) >= 6:
                # Dimmer trailing segments
                draw.point((x2, y2), fill=255)

def show_quantum_result(result_value):
    """Show the quantum measurement result on OLED display"""
    try:
        image = Image.new("1", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(image)
        
        # Clear the display
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=0)
        
        # Draw "EXP. 1" at the top
        exp_text = "EXP. 1"
        exp_width = len(exp_text) * 6
        exp_x = (WIDTH - exp_width) // 2
        draw.text((exp_x, 5), exp_text, fill=255)
        
        # Draw "QUANTUM RESULT:" in the middle
        result_text = "QUANTUM RESULT:"
        result_width = len(result_text) * 6
        result_x = (WIDTH - result_width) // 2
        draw.text((result_x, 25), result_text, fill=255)
        
        # Draw the binary result (0 or 1) large
        binary_text = str(result_value)
        binary_width = len(binary_text) * 12  # Larger font approximation
        binary_x = (WIDTH - binary_width) // 2
        # Draw larger number by drawing multiple times with offset
        for offset_x in range(2):
            for offset_y in range(2):
                draw.text((binary_x + offset_x, 40 + offset_y), binary_text, fill=255)
        
        # Draw color description
        color_text = "BLUE" if result_value == 1 else "RED"
        color_width = len(color_text) * 6
        color_x = (WIDTH - color_width) // 2
        draw.text((color_x, 55), color_text, fill=255)
        
        # Update display
        display.image(image)
        display.show()
        
        
    except Exception as e:
        print(f"⚠️  OLED result display error: {e}")

def quantum_measurement_with_animation():
    """Performs quantum measurement with spinning atom animation only during quantum execution."""
    try:
        print("🔬 Performing quantum measurement...")
        
        # Create a quantum circuit with 1 qubit and 1 classical bit
        qc = QuantumCircuit(1, 1)
        
        # Apply Hadamard gate to create superposition (50/50 chance)
        qc.h(0)
        
        # Measure the qubit
        qc.measure(0, 0)
        
        # Start animation in a separate thread while quantum execution happens
        animation_active = True
        animation_frame = 0
        
        def animate_while_executing():
            nonlocal animation_active, animation_frame
            image = Image.new("1", (WIDTH, HEIGHT))
            draw = ImageDraw.Draw(image)
            
            while animation_active:
                # Clear and draw current frame
                draw_quantum_spinner(draw, animation_frame)
                
                # Update display
                display.image(image)
                display.show()
                
                # Next frame
                animation_frame += 1
                
                # Control frame rate (30 FPS)
                time.sleep(1.0 / 30)
        
        # Start animation thread
        animation_thread = threading.Thread(target=animate_while_executing)
        animation_thread.daemon = True
        animation_thread.start()
        
        # Execute the quantum circuit (this is where the delay happens)
        backend = Aer.get_backend('qasm_simulator')
        job = execute(qc, backend, shots=1)
        result = job.result()
        counts = result.get_counts(qc)
        
        # Stop animation immediately after quantum execution completes
        animation_active = False
        animation_thread.join(timeout=0.1)  # Wait briefly for thread to finish
        
        # Get the measurement result (0 or 1)
        quantum_result = int(list(counts.keys())[0])
        
        print(f"🔬 Quantum measurement: {quantum_result}")
        
        # Show quantum result on OLED display
        show_quantum_result(quantum_result)
        
        if quantum_result == 1:
            return Color(0, 0, 255), 1  # Blue = 1
        else:
            return Color(255, 0, 0), 0  # Red = 0
            
    except Exception as e:
        print(f"⚠️  Quantum circuit error: {e}")
        print("Falling back to classical random...")
        
        # Make sure animation stops in case of error
        animation_active = False
        
        # Clear display in case of error
        display.fill(0)
        display.show()
        
        # Fallback to classical random if quantum fails
        random_num = random.randint(0, 1)
        if random_num == 1:
            return Color(0, 0, 255), 1  # Blue = 1
        else:
            return Color(255, 0, 0), 0  # Red = 0

def check_for_button():
    """Checks for button press in a non-blocking way."""
    global alternating
    
    while alternating:
        try:
            # Check if button is pressed (LOW when pressed with pull-up resistor)
            if GPIO.input(BUTTON_PIN) == GPIO.LOW:
                time.sleep(0.1)  # Debounce delay
                # Check if button is still pressed after debounce
                if GPIO.input(BUTTON_PIN) == GPIO.LOW:
                    # Wait for button release to avoid multiple triggers
                    while GPIO.input(BUTTON_PIN) == GPIO.LOW:
                        time.sleep(0.01)
                    alternating = False
                    break
            time.sleep(0.01)  # Small delay to prevent excessive CPU usage
        except:
            pass

# --- Main Program ---
if __name__ == '__main__':
    # Initialize GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    # Initialize LED strip
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    print('=== EXP. 1 - LED Quantum Hadamard System ===')
    print('🔌 Wiring Instructions:')
    print('  OLED GND → Pi GND (Pin 6)')
    print('  OLED VCC → Pi 3.3V (Pin 1)')
    print('  OLED SCL → Pi GPIO 3 (Pin 5)')
    print('  OLED SDA → Pi GPIO 2 (Pin 3)')
    print('  Button → Pi GPIO 26 (Pin 37) + GND')
    print('  LED Strip → Pi GPIO 18 (Pin 12) + 5V + GND')
    print()
    
    # Initialize and show OLED display
    try:
        display.fill(0)
        display.show()
        show_exp_x_display(display, 1, WIDTH, HEIGHT)  # Shows EXP. 1
        print("✅ OLED display initialized successfully!")
    except Exception as e:
        print(f"⚠️  OLED initialization failed: {e}")
        print("  - Check OLED wiring")
        print("  - Enable I2C: sudo raspi-config")
        print("  - Run: sudo i2cdetect -y 1")
    
    print(f'🔬 Quantum 50/50 Probability using Hadamard Gate')
    print(f'Blue (1): 50% | Red (0): 50%')
    print('Starting running alternation mode...')
    print('Press the button (GPIO 26) to enter quantum hadamard mode...')
    
    try:
        while True:
            show_exp_x_display(display, 1, WIDTH, HEIGHT)  # Shows EXP. 1 
            # Reset alternating state
            restart_alternation()
            
            # Start button checking thread
            button_thread = threading.Thread(target=check_for_button)
            button_thread.daemon = True
            button_thread.start()
            
            # Start mixed alternating colors (each LED alternates individually)
            mixed_alternating_colors(strip)
            
            # After alternating stops, enter quantum hadamard mode immediately
            print("\n=== Quantum Hadamard Mode ===")
            
            # Draw a color using quantum Hadamard gate with spinning atom animation
            color, binary_value = quantum_measurement_with_animation()
            
            # Light up the strip with the drawn color
            light_color(strip, color, binary_value)
            
            
            print("Press the button (GPIO 26) to restart alternation or Ctrl-C to exit.")
            # Wait for button press to restart
            while GPIO.input(BUTTON_PIN) == GPIO.HIGH:
                time.sleep(0.01)
            # Debounce
            time.sleep(0.1)
            # Wait for button release
            while GPIO.input(BUTTON_PIN) == GPIO.LOW:
                time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nExiting...")
        pass
    
    finally:
        # Ensure LEDs are always turned off at the end
        clear_strip(strip)
        # Clear OLED display
        clear_display()
        print("✅ Displays cleared")
        # Clean up GPIO
        GPIO.cleanup()