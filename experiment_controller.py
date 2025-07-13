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

class ExperimentController:
    def __init__(self):
        self.current_experiment = 1
        self.process = None
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.shutdown_event = threading.Event()
        
        # Set up signal handlers for proper cleanup
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle signals for proper cleanup."""
        print(f"\n🛑 Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_event.set()
        self._graceful_shutdown()
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
        """Toggle between experiments with graceful shutdown."""
        print("\n🔄 Toggling experiments...")
        
        # Gracefully shutdown current experiment
        self._graceful_shutdown()
        
        # Switch to the other experiment
        self.current_experiment = 3 if self.current_experiment == 1 else 1
        
        # Small delay to ensure cleanup is complete
        time.sleep(1)
        
        # Start the new experiment
        if self.start_experiment(self.current_experiment):
            print(f"✅ Switched to Experiment {self.current_experiment}")
        else:
            print("❌ Failed to start new experiment")
            
    def show_status(self):
        """Show current status."""
        exp_names = {1: "ex1.py (LED Lottery)", 3: "ex3.py (Quantum Toffoli)"}
        status = "Running" if self.process and self.process.poll() is None else "Stopped"
        
        print(f"\n📊 Status: {status}")
        print(f"🔄 Current: Experiment {self.current_experiment} - {exp_names[self.current_experiment]}")
        print("\n🎮 Commands:")
        print("  v + ENTER = Toggle experiments")
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
        print("  3️⃣  ex3.py - Quantum Toffoli Gate")
        print("      ⚛️  Quantum AND gate with GPIO 17 & 4 buttons")
        print("      🔴🔵 Shows quantum computation results")
        print("\n🎮 Commands:")
        print("  v = Toggle between experiments")
        print("  s = Show current status")
        print("  r = Restart current experiment")
        print("  q = Quit with graceful shutdown")
        print("  h = Show this help")
        print("\n🔧 Features:")
        print("  • Graceful shutdown ensures LEDs are turned off")
        print("  • GPIO cleanup prevents resource conflicts")
        print("  • Proper signal handling for clean exits")
        print("  • Emergency cleanup as failsafe")
        
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
            self._graceful_shutdown()
            print("✅ Goodbye!")

if __name__ == '__main__':
    controller = ExperimentController()
    controller.run()
