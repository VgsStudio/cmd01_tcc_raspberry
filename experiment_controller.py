#!/usr/bin/env python3
"""
Experiment Controller with Graceful Shutdown
Switches between ex1.py and ex3.py with proper cleanup
"""

import subprocess
import sys
import os
import time
import signal
import threading
import RPi.GPIO as GPIO

class ExperimentController:
    def __init__(self):
        self.current_experiment = 1
        self.process = None
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.shutdown_event = threading.Event()
        
        # GPIO button configuration
        self.TOGGLE_BUTTON_PIN = 16  # GPIO 16 for experiment toggle
        self.last_button_time = 0    # For button debouncing
        self.HOLD_DURATION = 5.0     # Seconds to hold button to exit (5 seconds)
        
        # Setup GPIO
        self._setup_gpio()
        
        # Set up signal handlers for proper cleanup
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Start GPIO monitoring thread
        self.gpio_thread = threading.Thread(target=self._monitor_gpio)
        self.gpio_thread.daemon = True
        self.gpio_thread.start()
        
    def _setup_gpio(self):
        """Setup GPIO button for experiment toggle."""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.TOGGLE_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            print(f"✅ GPIO {self.TOGGLE_BUTTON_PIN} setup for experiment toggle")
        except Exception as e:
            print(f"⚠️  Failed to setup GPIO: {e}")
            
    def _monitor_gpio(self):
        """Monitor GPIO button for experiment toggle and hold-to-exit."""
        while not self.shutdown_event.is_set():
            try:
                if GPIO.input(self.TOGGLE_BUTTON_PIN) == GPIO.LOW:
                    button_press_start = time.time()
                    current_time = time.time()
                    
                    # Debounce: ignore button presses within 0.5 seconds
                    if current_time - self.last_button_time > 0.5:
                        print(f"\n🔘 GPIO 16 button pressed...")
                        
                        # Monitor how long the button is held
                        hold_time = 0
                        while GPIO.input(self.TOGGLE_BUTTON_PIN) == GPIO.LOW and not self.shutdown_event.is_set():
                            hold_time = time.time() - button_press_start
                            
                            # Show progress for long hold
                            if hold_time >= 2.0:
                                remaining = self.HOLD_DURATION - hold_time
                                if remaining > 0:
                                    print(f"🔒 Hold for {remaining:.1f}s more to exit...", end='\r')
                                else:
                                    print(f"\n� Button held for {self.HOLD_DURATION}s - Exiting experiment controller! 💖")
                                    self.shutdown_event.set()
                                    # Trigger graceful shutdown and exit
                                    self._graceful_shutdown()
                                    try:
                                        GPIO.cleanup()
                                        print("🧹 GPIO cleanup completed")
                                    except:
                                        pass
                                    print("✅ Goodbye! 💖")
                                    os._exit(0)  # Force exit from all threads
                            
                            time.sleep(0.1)
                        
                        # Clear the progress line
                        if hold_time >= 2.0:
                            print(" " * 50, end='\r')  # Clear the progress line
                        
                        self.last_button_time = time.time()
                        
                        # If button was released before hold duration, toggle experiment
                        if hold_time < self.HOLD_DURATION and not self.shutdown_event.is_set():
                            print("🔄 Button released - Toggling experiment...")
                            self.toggle_experiment()
                            self.show_status()
                        
                time.sleep(0.05)  # Check button every 50ms
                
            except Exception as e:
                if not self.shutdown_event.is_set():
                    print(f"⚠️  GPIO monitoring error: {e}")
                break
        
    def _signal_handler(self, signum, frame):
        """Handle signals for proper cleanup."""
        print(f"\n🛑 Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_event.set()
        self._graceful_shutdown()
        try:
            GPIO.cleanup()
            print("🧹 GPIO cleanup completed")
        except:
            pass
        sys.exit(0)
        
    def _graceful_shutdown(self):
        """Perform graceful shutdown of current experiment."""
        if self.process and self.process.poll() is None:
            print("🔄 Initiating graceful shutdown of current experiment...")
            
            try:
                # Send SIGINT (Ctrl+C) to the process to trigger KeyboardInterrupt
                self.process.send_signal(signal.SIGINT)
                
                # Wait for the process to terminate gracefully
                print("⏳ Waiting for experiment to complete cleanup...")
                try:
                    self.process.wait(timeout=10)  # Give 10 seconds for cleanup
                    print("✅ Experiment terminated gracefully")
                except subprocess.TimeoutExpired:
                    print("⚠️  Experiment didn't respond to graceful shutdown, forcing termination...")
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=5)
                        print("✅ Experiment terminated")
                    except subprocess.TimeoutExpired:
                        print("🔪 Force killing unresponsive experiment...")
                        self.process.kill()
                        self.process.wait()
                        print("✅ Experiment force killed")
                        
            except Exception as e:
                print(f"❌ Error during graceful shutdown: {e}")
                if self.process:
                    try:
                        self.process.kill()
                        self.process.wait()
                    except:
                        pass
                        
            # Emergency LED cleanup
            self._emergency_cleanup()
            self.process = None
            
    def _emergency_cleanup(self):
        """Emergency cleanup to ensure LEDs are turned off."""
        print("🧹 Performing emergency LED cleanup...")
        try:
            # Run a quick cleanup script
            cleanup_script = f"""
import sys
sys.path.insert(0, '{self.script_dir}')
try:
    import RPi.GPIO as GPIO
    from rpi_ws281x import *
    
    # LED Strip Configuration
    LED_COUNT = 60
    LED_PIN = 18
    LED_FREQ_HZ = 800000
    LED_DMA = 10
    LED_BRIGHTNESS = 200
    LED_INVERT = False
    LED_CHANNEL = 0
    
    # Initialize and clear LED strip
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()
    
    # Turn off all LEDs
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()
    
    # Clean up GPIO
    GPIO.cleanup()
    
    # Try to cleanup OLED display (for ex2.py)
    try:
        import board
        import busio
        import adafruit_ssd1306
        from PIL import Image, ImageDraw
        
        i2c = busio.I2C(scl=board.D3, sda=board.D2)
        display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
        display.fill(0)
        display.show()
    except:
        pass  # OLED cleanup is optional
    
    print("✅ Emergency cleanup completed")
    
except Exception as e:
    print(f"⚠️  Emergency cleanup failed: {{e}}")
"""
            
            # Run the cleanup script
            cleanup_proc = subprocess.Popen([
                f"{self.script_dir}/venv/bin/python", "-c", cleanup_script
            ], cwd=self.script_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            
            cleanup_proc.wait(timeout=5)
            
        except Exception as e:
            print(f"⚠️  Emergency cleanup failed: {e}")
            
    def start_experiment(self, exp_num):
        """Start an experiment with proper monitoring."""
        experiments = {
            1: ('ex1.py', 'LED Color Lottery System'),
            2: ('ex2.py', 'OLED Calculator with LED Strip'),
            3: ('ex3.py', 'Quantum Toffoli Gate')
        }
        
        if exp_num not in experiments:
            print(f"❌ Invalid experiment number: {exp_num}")
            return False
            
        filename, name = experiments[exp_num]
        script_path = os.path.join(self.script_dir, filename)
        
        if not os.path.exists(script_path):
            print(f"❌ {filename} not found!")
            return False
            
        print(f"\n🚀 Starting Experiment {exp_num}: {name}")
        print(f"📁 Running: {filename}")
        print("=" * 50)
        
        try:
            # Run the experiment with sudo and proper environment
            self.process = subprocess.Popen([
                "sudo", f"{self.script_dir}/venv/bin/python", filename
            ], 
            cwd=self.script_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
            )
            
            print("✅ Experiment started successfully!")
            
            # Monitor the process output in a separate thread
            def monitor_output():
                try:
                    while self.process and self.process.poll() is None:
                        line = self.process.stdout.readline()
                        if line:
                            print(f"[EXP{exp_num}] {line.strip()}")
                except:
                    pass
                    
            output_thread = threading.Thread(target=monitor_output)
            output_thread.daemon = True
            output_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Error starting experiment: {e}")
            return False
            
    def toggle_experiment(self):
        """Cycle through experiments with graceful shutdown."""
        print("\n🔄 Cycling through experiments...")
        
        # Gracefully shutdown current experiment
        self._graceful_shutdown()
        
        # Cycle to the next experiment (1 -> 2 -> 3 -> 1)
        self.current_experiment = (self.current_experiment % 3) + 1
        
        # Small delay to ensure cleanup is complete
        time.sleep(1)
        
        # Start the new experiment
        if self.start_experiment(self.current_experiment):
            print(f"✅ Switched to Experiment {self.current_experiment}")
        else:
            print("❌ Failed to start new experiment")
            
    def show_status(self):
        """Show current status."""
        exp_names = {
            1: "ex1.py (LED Lottery)", 
            2: "ex2.py (OLED Calculator)",
            3: "ex3.py (Quantum Toffoli)"
        }
        status = "Running" if self.process and self.process.poll() is None else "Stopped"
        
        print(f"\n📊 Status: {status}")
        print(f"🔄 Current: Experiment {self.current_experiment} - {exp_names[self.current_experiment]}")
        print("\n🎮 Commands:")
        print("  v + ENTER = Cycle through experiments")
        print("  GPIO 16 = Hardware button (short press = toggle, hold 5s = exit)")
        print("  1/2/3 + ENTER = Switch to specific experiment")
        print("  s + ENTER = Show status")
        print("  r + ENTER = Restart current experiment")
        print("  q + ENTER = Quit")
        print("  h + ENTER = Help")
        
    def restart_current_experiment(self):
        """Restart the current experiment."""
        print(f"\n🔄 Restarting Experiment {self.current_experiment}...")
        self._graceful_shutdown()
        time.sleep(1)
        if self.start_experiment(self.current_experiment):
            print(f"✅ Experiment {self.current_experiment} restarted")
        else:
            print("❌ Failed to restart experiment")
            
    def show_help(self):
        """Show help information."""
        print("\n📋 Available Experiments:")
        print("  1️⃣  ex1.py - LED Color Lottery")
        print("      🎰 Random lottery system with GPIO 26 button")
        print("      🔴🔵 Alternating colors until button press")
        print("  2️⃣  ex2.py - OLED Calculator with LED Strip")
        print("      🖥️  128x64 OLED display with calculator")
        print("      🎮 GPIO 17 & 27 for numbers, GPIO 26 for calculate")
        print("      🔴🔵 LED animations during calculation")
        print("  3️⃣  ex3.py - Quantum Toffoli Gate")
        print("      ⚛️  Quantum AND gate with GPIO 17 & 27 buttons")
        print("      🔴🔵 Shows quantum computation results")
        print("\n🎮 Commands:")
        print("  v = Cycle through experiments (1→2→3→1)")
        print("  GPIO 16 = Hardware button (short press = toggle, hold 5s = exit)")
        print("  1/2/3 = Switch directly to specific experiment")
        print("  s = Show current status")
        print("  r = Restart current experiment")
        print("  q = Quit with graceful shutdown")
        print("  h = Show this help")
        print("\n🔧 Features:")
        print("  • Graceful shutdown ensures LEDs are turned off")
        print("  • GPIO cleanup prevents resource conflicts")
        print("  • Proper signal handling for clean exits")
        print("  • Emergency cleanup as failsafe")
        print("  • OLED display cleanup for ex2.py")
        print("  • Hardware toggle button on GPIO 16")
        print("  • Hold button for 5 seconds to exit controller")
        print("\n🔌 Hardware Setup:")
        print("  • Connect button between GPIO 16 and GND")
        print("  • Short press = cycle experiments")
        print("  • Hold 5 seconds = exit controller")
        print("  • Internal pull-up resistor enabled")
        
    def run(self):
        """Main controller loop."""
        print("🎮 Experiment Controller with Graceful Shutdown")
        print("=" * 50)
        
        # Start the first experiment
        if not self.start_experiment(self.current_experiment):
            print("❌ Failed to start initial experiment")
            return
            
        self.show_status()
        
        try:
            while not self.shutdown_event.is_set():
                try:
                    command = input("\n> ").strip().lower()
                    
                    if command == 'v':
                        self.toggle_experiment()
                        self.show_status()
                        
                    elif command in ['1', '2', '3']:
                        target_exp = int(command)
                        if target_exp != self.current_experiment:
                            self._graceful_shutdown()
                            time.sleep(1)
                            self.current_experiment = target_exp
                            if self.start_experiment(self.current_experiment):
                                print(f"✅ Switched to Experiment {self.current_experiment}")
                            else:
                                print("❌ Failed to start experiment")
                        self.show_status()
                        
                    elif command == 's':
                        self.show_status()
                        
                    elif command == 'r':
                        self.restart_current_experiment()
                        self.show_status()
                        
                    elif command == 'q':
                        print("🛑 Initiating graceful shutdown...")
                        break
                        
                    elif command == 'h':
                        self.show_help()
                        
                    elif command == '':
                        continue
                        
                    else:
                        print("❓ Unknown command. Use 'h' for help.")
                        
                except EOFError:
                    print("\n🛑 EOF received, shutting down...")
                    break
                    
        except KeyboardInterrupt:
            print("\n🛑 Ctrl+C received, shutting down...")
            
        finally:
            print("\n🔄 Performing final graceful shutdown...")
            self.shutdown_event.set()
            self._graceful_shutdown()
            try:
                GPIO.cleanup()
                print("🧹 GPIO cleanup completed")
            except:
                pass
            print("✅ Goodbye!")

if __name__ == '__main__':
    controller = ExperimentController()
    controller.run()
