#!/usr/bin/env python3
"""
Centralized Hardware Configuration for TCC Raspberry Pi Project
Defines all GPIO pin assignments and hardware settings
"""

# GPIO Pin Assignments
PINS = {
    # LED Strip
    'LED_STRIP': 18,
    
    # Buttons
    'BUTTON_LEFT': 17,      # Left number button (ex2, ex3)
    'BUTTON_RIGHT': 27,     # Right number button (ex2, ex3)
    'BUTTON_CALC': 26,      # Calculate/Action button (all experiments)
    'BUTTON_TOGGLE': 16,    # Experiment controller toggle button
    
    # I2C for OLED Display
    'I2C_SCL': 3,          # GPIO 3 (Physical pin 5)
    'I2C_SDA': 2           # GPIO 2 (Physical pin 3)
}

# LED Strip Configuration
LED_CONFIG = {
    'COUNT': 60,
    'PIN': PINS['LED_STRIP'],
    'FREQ_HZ': 800000,
    'DMA': 10,
    'BRIGHTNESS': 200,
    'INVERT': False,
    'CHANNEL': 0
}

# OLED Display Configuration
OLED_CONFIG = {
    'WIDTH': 128,
    'HEIGHT': 64,
    'I2C_SCL': PINS['I2C_SCL'],
    'I2C_SDA': PINS['I2C_SDA']
}

# Experiment-specific configurations
EXPERIMENT_CONFIG = {
    1: {
        'name': 'LED Color Lottery System',
        'description': 'Quantum random lottery with LED visualization',
        'buttons': ['BUTTON_CALC'],
        'hardware': ['LED_STRIP', 'I2C']
    },
    2: {
        'name': 'OLED Calculator with LED Strip',
        'description': 'Calculator with OLED display and LED animations',
        'buttons': ['BUTTON_LEFT', 'BUTTON_RIGHT', 'BUTTON_CALC'],
        'hardware': ['LED_STRIP', 'I2C']
    },
    3: {
        'name': 'Quantum Toffoli Gate',
        'description': 'Quantum AND gate demonstration',
        'buttons': ['BUTTON_LEFT', 'BUTTON_RIGHT'],
        'hardware': ['LED_STRIP']
    }
}

# Animation settings
ANIMATION_CONFIG = {
    'SPRITE_SIZE': (64, 64),
    'FRAMES': 30,
    'ATOM_ICON_PATH': './assets/icons/atom.bmp'
}

# Timing configurations (in seconds)
TIMING_CONFIG = {
    'BUTTON_DEBOUNCE': 0.1,
    'CALC_BUTTON_DEBOUNCE': 0.3,
    'CONTROLLER_BUTTON_DEBOUNCE': 0.5,
    'CONTROLLER_HOLD_DURATION': 5.0,
    'LED_ANIMATION_SPEED': 0.05,  # 20 FPS
    'DISPLAY_REFRESH_RATE': 0.033  # ~30 FPS
}

def get_experiment_info(exp_num):
    """Get configuration info for a specific experiment."""
    return EXPERIMENT_CONFIG.get(exp_num, {})

def get_pin(pin_name):
    """Get GPIO pin number by name."""
    return PINS.get(pin_name)

def get_led_config():
    """Get LED strip configuration."""
    return LED_CONFIG.copy()

def get_oled_config():
    """Get OLED display configuration."""
    return OLED_CONFIG.copy()

def get_timing(timing_name):
    """Get timing configuration by name."""
    return TIMING_CONFIG.get(timing_name, 0.1)

if __name__ == '__main__':
    # Display configuration summary
    print("🔧 Hardware Configuration Summary")
    print("=" * 50)
    print(f"📍 GPIO Pin Assignments:")
    for name, pin in PINS.items():
        print(f"  {name:<15}: GPIO {pin}")
    
    print(f"\n💡 LED Strip: {LED_CONFIG['COUNT']} LEDs on GPIO {LED_CONFIG['PIN']}")
    print(f"📺 OLED Display: {OLED_CONFIG['WIDTH']}x{OLED_CONFIG['HEIGHT']} on I2C")
    print(f"🎮 Experiments: {len(EXPERIMENT_CONFIG)} configured")
    
    print(f"\n🧪 Available Experiments:")
    for exp_num, config in EXPERIMENT_CONFIG.items():
        print(f"  {exp_num}: {config['name']}")
        print(f"     Buttons: {config['buttons']}")
        print(f"     Hardware: {config['hardware']}")
