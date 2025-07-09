#!/usr/bin/env python3
"""
LED Cleanup Utility
Turns off all LEDs and cleans up GPIO
Use this if experiments don't shut down gracefully
"""

import sys
import os

def cleanup_leds():
    """Turn off all LEDs and clean up GPIO."""
    try:
        import RPi.GPIO as GPIO
        from rpi_ws281x import *
        
        print("🧹 Cleaning up LEDs and GPIO...")
        
        # LED Strip Configuration
        LED_COUNT = 60
        LED_PIN = 18
        LED_FREQ_HZ = 800000
        LED_DMA = 10
        LED_BRIGHTNESS = 200
        LED_INVERT = False
        LED_CHANNEL = 0
        
        # Initialize LED strip
        strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        strip.begin()
        
        # Turn off all LEDs
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
        
        print("✅ All LEDs turned off")
        
        # Clean up GPIO
        GPIO.cleanup()
        
        print("✅ GPIO cleanup completed")
        print("🎉 LED cleanup successful!")
        
    except Exception as e:
        print(f"❌ LED cleanup failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    cleanup_leds()
