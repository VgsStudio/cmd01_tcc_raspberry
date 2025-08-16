# TCC Raspberry Pi Quantum Computing Project

🎓 **Final Project (TCC)** - Quantum Computing Experiments on Raspberry Pi

## 📁 Project Structure

```
cmd01_tcc_raspberry/
├── 📁 experiments/           # Core experiment files
│   ├── ex1.py               # LED Quantum Hadamard System
│   ├── ex2.py               # OLED Calculator with LED Strip
│   └── ex3.py               # Quantum Toffoli Gate Demo
├── 📁 modules/              # Reusable modules
│   ├── calculator_quantum.py    # Quantum calculation logic
│   ├── digit_display.py        # OLED display utilities
│   └── hardware_config.py      # Centralized hardware settings
├── 📁 scripts/              # Utility and runner scripts
│   ├── run_ex1.sh              # Run experiment 1
│   ├── run_ex2.sh              # Run experiment 2
│   ├── run_ex3.sh              # Run experiment 3
│   ├── setup.sh                # Project setup
│   ├── activate_venv.sh        # Virtual environment activation
│   └── cleanup_leds.py         # Emergency LED cleanup
├── 📁 assets/               # Static resources
│   └── icons/
│       └── atom.bmp            # Spinning atom animation
├── 📁 config/               # Configuration files
│   └── requirements.txt       # Python dependencies
├── experiment_controller.py    # Main experiment controller
├── main.py                     # Main entry point
└── README.md                   # This documentation
```

## 🚀 Quick Start

### 1. **Setup Environment**
```bash
# Setup project (creates venv, installs dependencies)
./scripts/setup.sh

# Or manually activate virtual environment
source scripts/activate_venv.sh
```

### 2. **Run Individual Experiments**
```bash
# Experiment 1: LED Quantum Hadamard
./scripts/run_ex1.sh

# Experiment 2: OLED Calculator
./scripts/run_ex2.sh

# Experiment 3: Quantum Toffoli Gate
./scripts/run_ex3.sh
```

### 3. **Run Experiment Controller**
```bash
# All-in-one controller with experiment switching
python main.py

# Or directly
python experiment_controller.py
```

## 🧪 Experiments

### 🎰 **Experiment 1: LED Quantum Hadamard**
- **File**: `experiments/ex1.py`
- **Hardware**: 60 LED WS2812B strip, GPIO 26 button, OLED display
- **Features**: True quantum randomness using Qiskit Hadamard gates
- **Controls**: Press GPIO 26 to trigger quantum measurement

### 🧮 **Experiment 2: OLED Calculator**
- **File**: `experiments/ex2.py`
- **Hardware**: OLED 128x64, LED strip, 3 buttons (GPIO 17, 27, 26)
- **Features**: Visual calculator with quantum computation backend
- **Controls**: GPIO 17/27 for numbers, GPIO 26 for calculation

### ⚛️ **Experiment 3: Quantum Toffoli Gate**
- **File**: `experiments/ex3.py`
- **Hardware**: LED strip, 2 buttons (GPIO 17, 27), OLED display
- **Features**: Quantum AND gate demonstration
- **Controls**: GPIO 17/27 for inputs, automatic quantum computation

## 🔧 Hardware Configuration

All hardware settings are centralized in `modules/hardware_config.py`:

### **GPIO Pin Assignments**
- **LED Strip**: GPIO 18
- **Button Left**: GPIO 17 (ex2, ex3)
- **Button Right**: GPIO 27 (ex2, ex3)
- **Button Calc**: GPIO 26 (all experiments)
- **Button Toggle**: GPIO 16 (controller)
- **I2C SCL**: GPIO 3 (OLED)
- **I2C SDA**: GPIO 2 (OLED)

### **LED Strip**: 60x WS2812B on GPIO 18
### **OLED Display**: 128x64 SSD1306 on I2C

## 🎮 Experiment Controller

The experiment controller (`experiment_controller.py`) provides:

- **Hardware Toggle**: GPIO 16 button for experiment switching
- **Hold to Exit**: Hold GPIO 16 for 5 seconds to exit
- **Graceful Shutdown**: Proper cleanup of LEDs and GPIO
- **Progress Feedback**: Terminal progress bar during exit

### **Controller Commands**
- `v` - Cycle through experiments (1→2→3→1)
- `1/2/3` - Switch to specific experiment
- `s` - Show status
- `r` - Restart current experiment
- `q` - Quit with graceful shutdown
- `h` - Help

## 🛠️ Development

### **Adding New Experiments**
1. Create new file in `experiments/`
2. Import from `modules.hardware_config`
3. Use centralized pin assignments
4. Add to experiment controller
5. Create run script in `scripts/`

### **Modifying Hardware**
- Update `modules/hardware_config.py`
- All experiments automatically use new settings
- No need to update individual files

### **Project Structure Benefits**
- ✅ Centralized configuration
- ✅ Reduced code duplication
- ✅ Easy maintenance
- ✅ Scalable architecture
- ✅ Clear separation of concerns

## 📦 Dependencies

See `config/requirements.txt`:
- `rpi_ws281x` - LED strip control
- `RPi.GPIO` - GPIO interface
- `qiskit` - Quantum computing
- `adafruit-circuitpython-ssd1306` - OLED display
- `Pillow` - Image processing

## 🚨 Emergency Cleanup

If LEDs get stuck on:
```bash
python scripts/cleanup_leds.py
```

## 🔍 Troubleshooting

1. **Import Errors**: Check virtual environment activation
2. **GPIO Conflicts**: Ensure no other processes using GPIO
3. **Permission Errors**: Run with `sudo` for GPIO access
4. **I2C Errors**: Enable I2C in `raspi-config`
5. **LED Errors**: Check connections and power supply

## 📚 Technical Details

- **Quantum Backend**: Qiskit with local Aer simulator
- **LED Protocol**: WS2812B (NeoPixel) via SPI-like interface
- **Display Interface**: I2C SSD1306 OLED
- **Threading**: Concurrent LED animations and button monitoring
- **Signal Handling**: Graceful shutdown on SIGINT/SIGTERM

---

**🎓 Developed for TCC - Technical Computer Course Final Project**
