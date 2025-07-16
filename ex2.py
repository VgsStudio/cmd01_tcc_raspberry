import time
import board
import busio
import threading
import os
import warnings
from PIL import Image, ImageDraw
import adafruit_ssd1306
import RPi.GPIO as GPIO
from rpi_ws281x import *
from calculator_quantum import calculate_sum, format_result, validate_inputs
from digit_display import draw_large_digit, draw_plus_sign, show_exp_x_display

# Suppress I2C frequency warning
warnings.filterwarnings("ignore", message="I2C frequency is not settable in python, ignoring!")

# I2C pins for OLED
# Based on valid I2C ports: ((1, 3, 2), (0, 1, 0))
# Using first valid port: SCL=GPIO3, SDA=GPIO2
# Connect your OLED as follows:
# OLED SCK pin → Raspberry Pi GPIO 1 (Physical pin 28)
# OLED SDA pin → Raspberry Pi GPIO 3 (Physical pin 5)
# OLED VCC → 3.3V or 5V
# OLED GND → Ground
i2c = busio.I2C(scl=board.D3, sda=board.D2)

# LED Strip Configuration
LED_COUNT      = 60      # Number of LEDs in the strip
LED_PIN        = 18      # GPIO 18 for LED strip
LED_FREQ_HZ    = 800000  # LED signal frequency (usually 800khz)
LED_DMA        = 10      # DMA channel
LED_BRIGHTNESS = 200     # Brightness from 0 to 255
LED_INVERT     = False   # Set to True if signal needs to be inverted
LED_CHANNEL    = 0       # LED channel

# Button Configuration
LEFT_BUTTON_PIN = 17   # GPIO 17 for left number
RIGHT_BUTTON_PIN = 27   # GPIO 27 for right number
CALC_BUTTON_PIN = 26   # GPIO 26 for calculate button

# Counter variables
left_counter = 0
right_counter = 0
last_left_button_time = 0   # For debouncing left button
last_right_button_time = 0  # For debouncing right button
last_calc_button_time = 0   # For debouncing calc button

# Display states
DISPLAY_EQUATION = 0
DISPLAY_LOADING = 1
DISPLAY_RESULT = 2
current_display_state = DISPLAY_EQUATION
result_display_time = 0
current_result = 0

# 128x64 OLED display
WIDTH = 128
HEIGHT = 64
BORDER = 0

# Animation settings
SPRITE_SIZE = (64, 64)  # Size of each animation frame
FRAMES = 30  # Number of frames in the animation
animation_frames = []  # Will store loaded animation frames
animation_loaded = False

# LED Strip Control
led_strip = None
led_pattern_active = False
led_thread = None

display = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)

def clear_led_strip():
    """Turns OFF all LEDs on the strip."""
    global led_strip
    if led_strip is not None:
        for i in range(led_strip.numPixels()):
            led_strip.setPixelColor(i, Color(0, 0, 0))
        led_strip.show()

def set_led_strip_color(color):
    """Sets the entire LED strip to a specific color."""
    global led_strip
    if led_strip is not None:
        for i in range(led_strip.numPixels()):
            led_strip.setPixelColor(i, color)
        led_strip.show()

def mixed_alternating_colors_thread():
    """LED alternating pattern similar to ex1.py - runs in background thread."""
    global led_pattern_active, led_strip
    
    if led_strip is None:
        return
    
    # Create different starting colors for each LED
    led_colors = []
    for i in range(led_strip.numPixels()):
        # Even LEDs start with red (0), odd LEDs start with blue (1)
        led_colors.append(i % 2)
    
    while led_pattern_active:
        # Draw current pattern
        for i in range(led_strip.numPixels()):
            if led_colors[i] == 1:
                led_strip.setPixelColor(i, Color(0, 0, 255))  # Blue
            else:
                led_strip.setPixelColor(i, Color(255, 0, 0))  # Red
        
        led_strip.show()
        time.sleep(0.2)  # 0.2 seconds between changes
        
        # Toggle each LED's color
        for i in range(led_strip.numPixels()):
            led_colors[i] = 1 - led_colors[i]  # Toggle between 0 and 1

def start_led_alternating_pattern():
    """Start the LED alternating pattern in a background thread."""
    global led_pattern_active, led_thread
    
    if led_strip is None:
        return
        
    # Stop any existing pattern
    stop_led_pattern()
    
    led_pattern_active = True
    led_thread = threading.Thread(target=mixed_alternating_colors_thread)
    led_thread.daemon = True
    led_thread.start()

def stop_led_pattern():
    """Stop the LED alternating pattern."""
    global led_pattern_active, led_thread
    
    led_pattern_active = False
    if led_thread is not None and led_thread.is_alive():
        led_thread.join(timeout=1)  # Wait up to 1 second for thread to finish

def setup_led_strip():
    """Initialize the LED strip."""
    global led_strip
    
    try:
        led_strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        led_strip.begin()
        clear_led_strip()  # Start with LEDs off
        print("✅ LED strip initialized successfully!")
        return True
    except Exception as e:
        print(f"⚠️  LED strip initialization failed: {e}")
        led_strip = None
        return False

def load_animation_frames():
    """Load animation frames from sprite sheet bitmap"""
    global animation_frames, animation_loaded
    
    if animation_loaded:
        return
    
    try:
        # Load the sprite sheet bitmap
        sprite_path = "./icons/atom.bmp"
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
            
            for i in range(available_frames):
                # Calculate frame position in sprite sheet
                x = i * frame_width
                y = 0
                
                # Extract frame
                frame_box = (x, y, x + frame_width, y + frame_height)
                frame = sprite_sheet.crop(frame_box)
                
                # Make the atom bigger - resize to take up more of the display
                # Use 95% of display height to make it prominent
                display_size = int(HEIGHT * 0.95)  # Make it 95% of display height (about 51 pixels)
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

def draw_loading_spinner(draw, frame):
    """Draw a bitmap-based loading animation"""
    global animation_frames, animation_loaded
    
    # Load animation frames if not already loaded
    if not animation_loaded:
        load_animation_frames()
    
    # Clear the display
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=0)
    
    # Draw bitmap animation if frames are loaded
    if animation_loaded and animation_frames:
        # Calculate which frame to show (fast animation for 30 FPS effect)
        current_frame_index = frame % len(animation_frames)  # Change frame every cycle for max speed
        current_frame = animation_frames[current_frame_index]
        
        # Center the animation perfectly on the 128x64 display
        frame_width, frame_height = current_frame.size
        center_x = (WIDTH - frame_width) // 2   # Center horizontally on 128px width
        center_y = (HEIGHT - frame_height) // 2  # Center vertically on 64px height
        
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
        center_y = HEIGHT // 2
        radius = 20  # Make fallback circle bigger too
        
        # Draw spinning circle
        angles = [0, 45, 90, 135, 180, 225, 270, 315]
        num_segments = 8
        active_segment = frame % num_segments
        
        import math
        for i in range(num_segments):
            angle = math.radians(angles[i])
            x1 = center_x + int(radius * 0.7 * math.cos(angle))
            y1 = center_y + int(radius * 0.7 * math.sin(angle))
            x2 = center_x + int(radius * math.cos(angle))
            y2 = center_y + int(radius * math.sin(angle))
            
            # Draw line segments with varying brightness
            if i == active_segment:
                # Bright segment
                draw.line([(x1, y1), (x2, y2)], fill=255, width=3)
            elif abs(i - active_segment) <= 2 or abs(i - active_segment) >= 6:
                # Dimmer trailing segments
                draw.point((x2, y2), fill=255)

def draw_result_display(draw, result):
    """Draw the calculation result"""
    # Clear the display
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=0)
    
    # Get the current numbers
    left_number = left_counter % 10
    right_number = right_counter % 10
    
    # Draw the equation at the top (smaller)
    equation_y = 5
    digit_size = 2
    digit_width = digit_size * 4  # 8
    plus_width = digit_size * 3   # 6
    spacing = 4
    
    total_width = digit_width + spacing + plus_width + spacing + digit_width
    start_x = (WIDTH - total_width) // 2
    
    # Draw small equation
    draw_large_digit(draw, left_number, start_x, equation_y, size=digit_size)
    plus_x = start_x + digit_width + spacing
    draw_plus_sign(draw, plus_x, equation_y + 3, size=digit_size)
    right_x = plus_x + plus_width + spacing
    draw_large_digit(draw, right_number, right_x, equation_y, size=digit_size)
    
    # Draw equals sign
    equals_y = equation_y + digit_size * 6 + 5
    equals_x = WIDTH // 2 - 8
    draw.rectangle([equals_x, equals_y, equals_x + 16, equals_y + 2], fill=255)
    draw.rectangle([equals_x, equals_y + 4, equals_x + 16, equals_y + 6], fill=255)
    
    # Draw result (large)
    result_y = equals_y + 12
    result_size = 3
    
    if result < 10:
        # Single digit result
        result_width = result_size * 4
        result_x = (WIDTH - result_width) // 2
        draw_large_digit(draw, result, result_x, result_y, size=result_size)
    else:
        # Two digit result
        tens = result // 10
        ones = result % 10
        result_width = (result_size * 4) * 2 + 4  # Two digits with spacing
        result_x = (WIDTH - result_width) // 2
        
        draw_large_digit(draw, tens, result_x, result_y, size=result_size)
        draw_large_digit(draw, ones, result_x + (result_size * 4) + 4, result_y, size=result_size)

def display_equation():
    """Display the appropriate screen based on current state"""
    global current_display_state, result_display_time, current_result
    
    # Clear the display
    image = Image.new("1", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)
    
    if current_display_state == DISPLAY_EQUATION:
        # Turn off LEDs when showing numbers/equation
        stop_led_pattern()
        clear_led_strip()
        
        # Calculate numbers from counters (0-9 cycle)
        left_number = left_counter % 10
        right_number = right_counter % 10
        
        # Position calculations for centering (larger size=4)
        digit_width = 16  # 4 * 4
        plus_width = 12   # 4 * 3
        spacing = 6
        
        total_width = digit_width + spacing + plus_width + spacing + digit_width
        start_x = (WIDTH - total_width) // 2
        start_y = (HEIGHT - 24) // 2  # 24 = 4 * 6 (digit height)
        
        # Draw left number
        draw_large_digit(draw, left_number, start_x, start_y, size=4)
        
        # Draw plus sign
        plus_x = start_x + digit_width + spacing
        plus_y = start_y + 6  # Center vertically with digits
        draw_plus_sign(draw, plus_x, plus_y, size=4)
        
        # Draw right number
        right_x = plus_x + plus_width + spacing
        draw_large_digit(draw, right_number, right_x, start_y, size=4)
        
    elif current_display_state == DISPLAY_LOADING:
        # Start LED alternating pattern during calculation
        if not led_pattern_active:
            start_led_alternating_pattern()
        
        # Show loading animation at 30 FPS
        frame = int((time.time() * 30) % (30 * len(animation_frames) if animation_frames else 240))  # 30 FPS animation
        draw_loading_spinner(draw, frame)
        
    elif current_display_state == DISPLAY_RESULT:
        # Stop LED pattern and show blue when calculation is complete
        stop_led_pattern()
        set_led_strip_color(Color(0, 0, 255))  # Blue for result
        
        # Show calculation result (stays until GPIO 26 pressed again)
        draw_result_display(draw, current_result)
    
    # Update display
    display.image(image)
    display.show()

def check_buttons():
    """Check all button states with debouncing (polling method)"""
    global left_counter, right_counter, last_left_button_time, last_right_button_time
    global last_calc_button_time, current_display_state, result_display_time, current_result
    current_time = time.time()
    
    # Check left button (GPIO 17) - works only in equation mode
    if current_display_state == DISPLAY_EQUATION and GPIO.input(LEFT_BUTTON_PIN) == GPIO.LOW:
        # Debounce: ignore button presses within 0.1 seconds
        if current_time - last_left_button_time > 0.1:
            left_counter += 1
            last_left_button_time = current_time
            left_number = left_counter % 10
            print(f"Left button pressed! Left number: {left_number}")
            
            # Wait for button release to avoid multiple triggers
            while GPIO.input(LEFT_BUTTON_PIN) == GPIO.LOW:
                time.sleep(0.01)
    
    # Check right button (GPIO 27) - works only in equation mode
    if current_display_state == DISPLAY_EQUATION and GPIO.input(RIGHT_BUTTON_PIN) == GPIO.LOW:
        # Debounce: ignore button presses within 0.1 seconds
        if current_time - last_right_button_time > 0.1:
            right_counter += 1
            last_right_button_time = current_time
            right_number = right_counter % 10
            print(f"Right button pressed! Right number: {right_number}")
            
            # Wait for button release to avoid multiple triggers
            while GPIO.input(RIGHT_BUTTON_PIN) == GPIO.LOW:
                time.sleep(0.01)
    
    # Check calculate button (GPIO 26) - works in equation and result modes
    if GPIO.input(CALC_BUTTON_PIN) == GPIO.LOW:
        # Debounce: ignore button presses within 0.3 seconds
        if current_time - last_calc_button_time > 0.3:
            last_calc_button_time = current_time
            
            if current_display_state == DISPLAY_EQUATION:
                # Start calculation
                left_number = left_counter % 10
                right_number = right_counter % 10
                
                print(f"Calculate button pressed! Computing {left_number} + {right_number}")
                
                # Switch to loading state first
                current_display_state = DISPLAY_LOADING
                
                # Wait for button release
                while GPIO.input(CALC_BUTTON_PIN) == GPIO.LOW:
                    time.sleep(0.01)
                
                # Force display update to show loading animation
                display_equation()
                
                # Perform calculation using external calculator module (this includes delay)
                if validate_inputs(left_number, right_number):
                    # Show loading animation during calculation
                    start_time = time.time()
                    calculation_done = False
                    
                    # Start calculation in background (simulate with the delay from calculator module)
                    import threading
                    def do_calculation():
                        nonlocal calculation_done
                        global current_result
                        current_result = calculate_sum(left_number, right_number)
                        calculation_done = True
                    
                    calc_thread = threading.Thread(target=do_calculation)
                    calc_thread.start()
                    
                    # Show loading animation while calculation is running
                    while not calculation_done:
                        display_equation()  # This will show the loading animation
                        time.sleep(0.033)  # 30 FPS refresh rate
                    
                    calc_thread.join()
                    
                    # Switch to result display (stays until GPIO 26 pressed again)
                    current_display_state = DISPLAY_RESULT
                    print(f"Calculation complete: {left_number} + {right_number} = {current_result}")
                    print("Press GPIO 26 again to return to equation mode")
                else:
                    print("Invalid inputs for calculation")
                    current_display_state = DISPLAY_EQUATION
                    
            elif current_display_state == DISPLAY_RESULT:
                # Return to equation display
                print("Calculate button pressed! Returning to equation mode...")
                current_display_state = DISPLAY_EQUATION
                
                # Wait for button release
                while GPIO.input(CALC_BUTTON_PIN) == GPIO.LOW:
                    time.sleep(0.01)

def setup_buttons():
    """Setup GPIO buttons (polling method)"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LEFT_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(RIGHT_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(CALC_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)



def number_display():
    print("🔢 Starting NUMBER + NUMBER display...")
    print("📟 Large, bold digit display with calculator")
    print("🔘 Press left button (GPIO 17) to change left number")
    print("🔘 Press right button (GPIO 27) to change right number")
    print("🧮 Press calculate button (GPIO 26) to compute sum")
    print("🧮 Press calculate button (GPIO 26) again to return to equation")
    print("Press Ctrl+C to stop")
    
    while True:
        # Check all button states
        check_buttons()
        
        # Display the appropriate screen
        display_equation()
        
        # Higher refresh rate for 30 FPS animation
        time.sleep(0.033)  # ~30 FPS (1/30 = 0.033 seconds)

def main():
    print("=== EXP. 2 - OLED Number Display with Calculator ===")
    print("Raspberry Pi 3 Model B - I2C OLED")
    print("🔢 Large Bold Number + Number Display")
    print("🧮 Three Button Calculator System")
    print("\n🔌 Wiring Instructions:")
    print("  OLED GND → Pi GND (Pin 6)")
    print("  OLED VCC → Pi 3.3V (Pin 1)")
    print("  OLED SCL → Pi GPIO 3 (Pin 5)")
    print("  OLED SDA → Pi GPIO 2 (Pin 3)")
    print("  Left Button → Pi GPIO 17 (Pin 11) + GND")
    print("  Right Button → Pi GPIO 27 (Pin 13) + GND")
    print("  Calculate Button → Pi GPIO 26 (Pin 37) + GND")
    print("  LED Strip → Pi GPIO 18 (Pin 12) + 5V + GND")
    print("\n🛠️  Make sure I2C is enabled!")
    print("  Run: sudo raspi-config → Interface → I2C → Enable")
    print(f"\n🔢 Display Info:")
    print(f"  Format: LEFT_NUMBER + RIGHT_NUMBER")
    print(f"  Range: 0-9 (each cycles back to 0)")
    print(f"  Control: Independent button control")
    print(f"  Calculator: GPIO 26 shows loading then result")
    print(f"  Style: Large, bold digits")
    print(f"\n💡 LED Strip Behavior:")
    print(f"  Equation Mode: LEDs OFF")
    print(f"  Calculating: Red/Blue alternating pattern")
    print(f"  Result Mode: Solid BLUE")
    print("\nInitializing display and buttons...")
    
    try:
        # Setup LED strip
        setup_led_strip()
        
        # Setup buttons GPIO
        setup_buttons()
        print("✅ Buttons setup complete!")
        
        # Initialize display and show EXP. 2 for 3 seconds
        display.fill(0)
        display.show()
        print("✅ Display initialized successfully!")
        
        # Show "EXP. 2" for 3 seconds
        show_exp_x_display(display, 2, WIDTH, HEIGHT, duration=3)
        
        # Clear display and start calculator
        display.fill(0)
        display.show()
        print("🧮 Starting calculator interface...")
        
        number_display()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping display...")
        stop_led_pattern()
        clear_led_strip()
        display.fill(0)
        display.show()
        print("✅ Display stopped. Goodbye!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("  - Check OLED wiring")
        print("  - Enable I2C: sudo raspi-config")
        print("  - Reboot after enabling I2C")
        print("  - Run: sudo i2cdetect -y 1")
        print("  - Check if SSD1306 OLED is detected")
        print("  - Check button wiring to GPIO 17, GPIO 27, and GPIO 26")
        print("  - Check LED strip wiring to GPIO 18")
        print("\n💬 Note: 'I2C frequency not settable' warnings are normal and harmless")
        
    finally:
        # Stop LED patterns and clear strip
        stop_led_pattern()
        clear_led_strip()
        
        # Clean up GPIO
        try:
            GPIO.cleanup()
            print("🧹 GPIO cleanup complete")
        except:
            pass

if __name__ == "__main__":
    main()
