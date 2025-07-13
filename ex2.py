import time
import board
import busio
import threading
import os
from PIL import Image, ImageDraw
import adafruit_ssd1306
import RPi.GPIO as GPIO
from calculator import calculate_sum, format_result, validate_inputs

# I2C pins for OLED
# Based on valid I2C ports: ((1, 3, 2), (0, 1, 0))
# Using first valid port: SCL=GPIO3, SDA=GPIO2
# Connect your OLED as follows:
# OLED SCK pin → Raspberry Pi GPIO 1 (Physical pin 28)
# OLED SDA pin → Raspberry Pi GPIO 3 (Physical pin 5)
# OLED VCC → 3.3V or 5V
# OLED GND → Ground
i2c = busio.I2C(scl=board.D3, sda=board.D2)

# Button Configuration
LEFT_BUTTON_PIN = 17   # GPIO 17 for left number
RIGHT_BUTTON_PIN = 4   # GPIO 4 for right number
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

display = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)

def draw_large_digit(draw, digit, x, y, size=3):
    """Draw a large, bold digit using thick lines"""
    # Define patterns for large digits (scalable)
    # Each digit is drawn as a series of thick rectangles
    
    thick = size  # Thickness of lines
    width = size * 4  # Width of digit
    height = size * 6  # Height of digit
    
    if digit == 0:
        # Draw outer rectangle
        draw.rectangle([x, y, x + width, y + thick], fill=255)  # top
        draw.rectangle([x, y + height - thick, x + width, y + height], fill=255)  # bottom
        draw.rectangle([x, y, x + thick, y + height], fill=255)  # left
        draw.rectangle([x + width - thick, y, x + width, y + height], fill=255)  # right
        
    elif digit == 1:
        # Vertical line on right
        draw.rectangle([x + width - thick, y, x + width, y + height], fill=255)
        # Top angled part
        draw.rectangle([x + width//2, y, x + width - thick, y + thick], fill=255)
        
    elif digit == 2:
        # Top horizontal
        draw.rectangle([x, y, x + width, y + thick], fill=255)
        # Middle horizontal
        draw.rectangle([x, y + height//2 - thick//2, x + width, y + height//2 + thick//2], fill=255)
        # Bottom horizontal
        draw.rectangle([x, y + height - thick, x + width, y + height], fill=255)
        # Top right vertical
        draw.rectangle([x + width - thick, y, x + width, y + height//2], fill=255)
        # Bottom left vertical
        draw.rectangle([x, y + height//2, x + thick, y + height], fill=255)
        
    elif digit == 3:
        # Top horizontal
        draw.rectangle([x, y, x + width, y + thick], fill=255)
        # Middle horizontal
        draw.rectangle([x, y + height//2 - thick//2, x + width, y + height//2 + thick//2], fill=255)
        # Bottom horizontal
        draw.rectangle([x, y + height - thick, x + width, y + height], fill=255)
        # Right vertical
        draw.rectangle([x + width - thick, y, x + width, y + height], fill=255)
        
    elif digit == 4:
        # Left vertical (top half)
        draw.rectangle([x, y, x + thick, y + height//2 + thick//2], fill=255)
        # Right vertical (full)
        draw.rectangle([x + width - thick, y, x + width, y + height], fill=255)
        # Middle horizontal
        draw.rectangle([x, y + height//2 - thick//2, x + width, y + height//2 + thick//2], fill=255)
        
    elif digit == 5:
        # Top horizontal
        draw.rectangle([x, y, x + width, y + thick], fill=255)
        # Middle horizontal
        draw.rectangle([x, y + height//2 - thick//2, x + width, y + height//2 + thick//2], fill=255)
        # Bottom horizontal
        draw.rectangle([x, y + height - thick, x + width, y + height], fill=255)
        # Top left vertical
        draw.rectangle([x, y, x + thick, y + height//2], fill=255)
        # Bottom right vertical
        draw.rectangle([x + width - thick, y + height//2, x + width, y + height], fill=255)
        
    elif digit == 6:
        # Top horizontal
        draw.rectangle([x, y, x + width, y + thick], fill=255)
        # Middle horizontal
        draw.rectangle([x, y + height//2 - thick//2, x + width, y + height//2 + thick//2], fill=255)
        # Bottom horizontal
        draw.rectangle([x, y + height - thick, x + width, y + height], fill=255)
        # Left vertical (full)
        draw.rectangle([x, y, x + thick, y + height], fill=255)
        # Bottom right vertical
        draw.rectangle([x + width - thick, y + height//2, x + width, y + height], fill=255)
        
    elif digit == 7:
        # Top horizontal
        draw.rectangle([x, y, x + width, y + thick], fill=255)
        # Right vertical
        draw.rectangle([x + width - thick, y, x + width, y + height], fill=255)
        
    elif digit == 8:
        # All segments
        draw.rectangle([x, y, x + width, y + thick], fill=255)  # top
        draw.rectangle([x, y + height//2 - thick//2, x + width, y + height//2 + thick//2], fill=255)  # middle
        draw.rectangle([x, y + height - thick, x + width, y + height], fill=255)  # bottom
        draw.rectangle([x, y, x + thick, y + height], fill=255)  # left
        draw.rectangle([x + width - thick, y, x + width, y + height], fill=255)  # right
        
    elif digit == 9:
        # Top horizontal
        draw.rectangle([x, y, x + width, y + thick], fill=255)
        # Middle horizontal
        draw.rectangle([x, y + height//2 - thick//2, x + width, y + height//2 + thick//2], fill=255)
        # Bottom horizontal
        draw.rectangle([x, y + height - thick, x + width, y + height], fill=255)
        # Top left vertical
        draw.rectangle([x, y, x + thick, y + height//2], fill=255)
        # Right vertical (full)
        draw.rectangle([x + width - thick, y, x + width, y + height], fill=255)

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
                # Use 80% of display height to make it prominent
                display_size = int(HEIGHT * 0.8)  # Make it 80% of display height (about 51 pixels)
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
        # Calculate which frame to show (slower animation for smoother effect)
        current_frame_index = (frame // 2) % len(animation_frames)  # Change frame every 2 cycles
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

def draw_plus_sign(draw, x, y, size=3):
    """Draw a large, bold plus sign"""
    thick = size
    width = size * 3
    height = size * 3
    
    # Horizontal line
    draw.rectangle([x, y + height//2 - thick//2, x + width, y + height//2 + thick//2], fill=255)
    # Vertical line
    draw.rectangle([x + width//2 - thick//2, y, x + width//2 + thick//2, y + height], fill=255)
    """Draw a large, bold plus sign"""
    thick = size
    width = size * 3
    height = size * 3
    
    # Horizontal line
    draw.rectangle([x, y + height//2 - thick//2, x + width, y + height//2 + thick//2], fill=255)
    # Vertical line
    draw.rectangle([x + width//2 - thick//2, y, x + width//2 + thick//2, y + height], fill=255)

def display_equation():
    """Display the appropriate screen based on current state"""
    global current_display_state, result_display_time, current_result
    
    # Clear the display
    image = Image.new("1", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)
    
    if current_display_state == DISPLAY_EQUATION:
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
        # Show loading animation
        frame = int((time.time() * 10) % 80)  # Animation frame
        draw_loading_spinner(draw, frame)
        
    elif current_display_state == DISPLAY_RESULT:
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
    
    # Check right button (GPIO 4) - works only in equation mode
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
                        time.sleep(0.05)  # Smooth animation
                    
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
    print("🔘 Press right button (GPIO 4) to change right number")
    print("🧮 Press calculate button (GPIO 26) to compute sum")
    print("🧮 Press calculate button (GPIO 26) again to return to equation")
    print("Press Ctrl+C to stop")
    
    while True:
        # Check all button states
        check_buttons()
        
        # Display the appropriate screen
        display_equation()
        
        # Faster refresh for smooth animations
        time.sleep(0.05)

def main():
    print("=== OLED Number Display with Calculator ===")
    print("Raspberry Pi 3 Model B - I2C OLED")
    print("🔢 Large Bold Number + Number Display")
    print("🧮 Three Button Calculator System")
    print("\n🔌 Wiring Instructions:")
    print("  OLED GND → Pi GND (Pin 6)")
    print("  OLED VCC → Pi 3.3V (Pin 1)")
    print("  OLED SCL → Pi GPIO 3 (Pin 5)")
    print("  OLED SDA → Pi GPIO 2 (Pin 3)")
    print("  Left Button → Pi GPIO 17 (Pin 11) + GND")
    print("  Right Button → Pi GPIO 4 (Pin 7) + GND")
    print("  Calculate Button → Pi GPIO 26 (Pin 37) + GND")
    print("\n🛠️  Make sure I2C is enabled!")
    print("  Run: sudo raspi-config → Interface → I2C → Enable")
    print(f"\n🔢 Display Info:")
    print(f"  Format: LEFT_NUMBER + RIGHT_NUMBER")
    print(f"  Range: 0-9 (each cycles back to 0)")
    print(f"  Control: Independent button control")
    print(f"  Calculator: GPIO 26 shows loading then result")
    print(f"  Style: Large, bold digits")
    print("\nInitializing display and buttons...")
    
    try:
        # Setup buttons GPIO
        setup_buttons()
        print("✅ Buttons setup complete!")
        
        # Initialize display
        display.fill(0)
        display.show()
        print("✅ Display initialized successfully!")
        
        number_display()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping display...")
        display.fill(0)
        display.show()
        print("� Display stopped. Goodbye!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("  - Check OLED wiring")
        print("  - Enable I2C: sudo raspi-config")
        print("  - Reboot after enabling I2C")
        print("  - Run: sudo i2cdetect -y 1")
        print("  - Check if SSD1306 OLED is detected")
        print("  - Check button wiring to GPIO 17, GPIO 4, and GPIO 26")
        
    finally:
        # Clean up GPIO
        try:
            GPIO.cleanup()
            print("🧹 GPIO cleanup complete")
        except:
            pass

if __name__ == "__main__":
    main()
