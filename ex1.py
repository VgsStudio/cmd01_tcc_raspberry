# -*- coding: utf-8 -*-
import time
import random
import sys
import select
import threading
from rpi_ws281x import *

# --- Configurações da Fita de LED (ajuste conforme sua fita) ---
LED_COUNT      = 60      # Número de LEDs na sua fita.
LED_PIN        = 18      # GPIO 18. NÃO MUDE.
LED_FREQ_HZ    = 800000  # Frequência do sinal (geralmente 800khz).
LED_DMA        = 10      # Canal DMA.
LED_BRIGHTNESS = 200      # Brilho de 0 a 255. Cuidado com fontes fracas!
LED_INVERT     = False   # Mude para True se o sinal precisar ser invertido.
LED_CHANNEL    = 0       # Mude para '1' para GPIOs 13, 19, 41, 45 ou 53.

# --- Probability Configuration ---
BLUE_PROBABILITY = 50    # Percentage chance for blue (1)
RED_PROBABILITY = 100 - BLUE_PROBABILITY   # Percentage chance for red (0)

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
    
    print("Starting color alternation... Press ENTER to stop and enter lottery mode.")
    
    while alternating:
        draw_color(strip, current_color)
        current_color = 1 - current_color  # Toggle between 0 and 1
        time.sleep(0.5)  # Half second between changes

def mixed_alternating_colors(strip):
    """Different LEDs alternate in different orders creating a mixed pattern."""
    global alternating
    
    print("Starting mixed alternation... Press ENTER to stop and enter lottery mode.")
    
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

def lottery_color():
    """Draws a color based on configured probability."""
    random_num = random.randint(1, 100)
    if random_num <= BLUE_PROBABILITY:
        return Color(0, 0, 255), 1  # Blue = 1
    else:
        return Color(255, 0, 0), 0  # Red

def check_for_input():
    """Checks for Enter key press in a non-blocking way."""
    global alternating
    
    while alternating:
        try:
            # Check if there's input available
            if select.select([sys.stdin], [], [], 0.1)[0]:
                input()  # Read the input
                alternating = False
                break
        except:
            pass

# --- Main Program ---
if __name__ == '__main__':
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    print('=== LED Color Lottery System ===')
    print(f'Blue Probability (1): {BLUE_PROBABILITY}%')
    print(f'Red Probability (0): {RED_PROBABILITY}%')
    print('Starting running alternation mode...')
    
    try:
        while True:
            # Reset alternating state
            restart_alternation()
            
            # Start input checking thread
            input_thread = threading.Thread(target=check_for_input)
            input_thread.daemon = True
            input_thread.start()
            
            # Start mixed alternating colors (each LED alternates individually)
            mixed_alternating_colors(strip)
            
            # After alternating stops, enter lottery mode immediately
            print("\n=== Lottery Mode ===")
            
            # Draw a color
            color, binary_value = lottery_color()
            
            # Light up the strip with the drawn color
            light_color(strip, color, binary_value)
            
            # Wait 3 seconds to show the result
            time.sleep(3)
            
            print("Press ENTER to restart alternation or Ctrl-C to exit.")
            input("Press ENTER to restart alternation...")

    except KeyboardInterrupt:
        print("\nExiting...")
        pass
    
    finally:
        # Ensure LEDs are always turned off at the end
        clear_strip(strip)