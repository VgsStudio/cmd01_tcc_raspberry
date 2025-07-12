import time
import board
import busio
from PIL import Image, ImageDraw
import adafruit_ssd1306
import RPi.GPIO as GPIO

# I2C pins for OLED
# Based on valid I2C ports: ((1, 3, 2), (0, 1, 0))
# Using first valid port: SCL=def number_display():
# Connect your OLED as follows:
# OLED SCK pin → Raspberry Pi GPIO 1 (Physical pin 28)
# OLED SDA pin → Raspberry Pi GPIO 3 (Physical pin 5)
# OLED VCC → 3.3V or 5V
# OLED GND → Ground
i2c = busio.I2C(scl=board.D3, sda=board.D2)

# Button Configuration
LEFT_BUTTON_PIN = 17   # GPIO 17 for left number
RIGHT_BUTTON_PIN = 4   # GPIO 4 for right number

# Counter variables
left_counter = 0
right_counter = 0
last_left_button_time = 0   # For debouncing left button
last_right_button_time = 0  # For debouncing right button

# 128x64 OLED display
WIDTH = 128
HEIGHT = 64
BORDER = 0

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

def draw_plus_sign(draw, x, y, size=3):
    """Draw a large, bold plus sign"""
    thick = size
    width = size * 3
    height = size * 3
    
    # Horizontal line
    draw.rectangle([x, y + height//2 - thick//2, x + width, y + height//2 + thick//2], fill=255)
    # Vertical line
    draw.rectangle([x + width//2 - thick//2, y, x + width//2 + thick//2, y + height], fill=255)

def display_equation():
    """Display the large equation NUMBER + NUMBER"""
    global left_counter, right_counter
    
    # Clear the display
    image = Image.new("1", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)
    
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
    
    # Counter info removed - clean display with only large numbers
    
    # Update display
    display.image(image)
    display.show()

def check_buttons():
    """Check both button states with debouncing (polling method)"""
    global left_counter, right_counter, last_left_button_time, last_right_button_time
    current_time = time.time()
    
    # Check left button (GPIO 17)
    if GPIO.input(LEFT_BUTTON_PIN) == GPIO.LOW:
        # Debounce: ignore button presses within 0.3 seconds
        if current_time - last_left_button_time > 0.3:
            left_counter += 1
            last_left_button_time = current_time
            print(f"Left button pressed! Left counter: {left_counter}")
            
            # Wait for button release to avoid multiple triggers
            while GPIO.input(LEFT_BUTTON_PIN) == GPIO.LOW:
                time.sleep(0.01)
    
    # Check right button (GPIO 4)
    if GPIO.input(RIGHT_BUTTON_PIN) == GPIO.LOW:
        # Debounce: ignore button presses within 0.3 seconds
        if current_time - last_right_button_time > 0.3:
            right_counter += 1
            last_right_button_time = current_time
            print(f"Right button pressed! Right counter: {right_counter}")
            
            # Wait for button release to avoid multiple triggers
            while GPIO.input(RIGHT_BUTTON_PIN) == GPIO.LOW:
                time.sleep(0.01)

def setup_buttons():
    """Setup GPIO buttons (polling method)"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LEFT_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(RIGHT_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def number_display():
    print("� Starting NUMBER + NUMBER display...")
    print("📟 Large, bold digit display")
    print("🔘 Press button on GPIO 17 to increment counter")
    print("Press Ctrl+C to stop")
    
    while True:
        # Check button state
        check_buttons()
        
        # Display the equation
        display_equation()
        
        # Small delay for responsiveness
        time.sleep(0.1)

def main():
    print("=== OLED Number Display ===")
    print("Raspberry Pi 3 Model B - I2C OLED")
    print("🔢 Large Bold Number + Number Display")
    print("🔘 Two Button Control System")
    print("\n🔌 Wiring Instructions:")
    print("  OLED GND → Pi GND (Pin 6)")
    print("  OLED VCC → Pi 3.3V (Pin 1)")
    print("  OLED SCL → Pi GPIO 3 (Pin 5)")
    print("  OLED SDA → Pi GPIO 2 (Pin 3)")
    print("  Left Button → Pi GPIO 17 (Pin 11) + GND")
    print("  Right Button → Pi GPIO 4 (Pin 7) + GND")
    print("\n🛠️  Make sure I2C is enabled!")
    print("  Run: sudo raspi-config → Interface → I2C → Enable")
    print(f"\n🔢 Display Info:")
    print(f"  Format: LEFT_NUMBER + RIGHT_NUMBER")
    print(f"  Range: 0-9 (each cycles back to 0)")
    print(f"  Control: Independent button control")
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
        print("  - Check button wiring to GPIO 17 and GPIO 4")
        
    finally:
        # Clean up GPIO
        try:
            GPIO.cleanup()
            print("🧹 GPIO cleanup complete")
        except:
            pass

if __name__ == "__main__":
    main()
