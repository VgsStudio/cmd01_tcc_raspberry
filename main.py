#!/usr/bin/env python3
"""
Main Entry Point for TCC Raspberry Pi Quantum Computing Project
Centralized launcher for all experiments and controllers
"""

import sys
import os
from pathlib import Path

# Add modules directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "modules"))

# Import the experiment controller
from experiment_controller import ExperimentController

def main():
    """Main entry point for the TCC project."""
    print("🎮 TCC Raspberry Pi Quantum Computing Project")
    print("=" * 50)
    print("📚 Project Structure:")
    print("  📁 experiments/    - Core experiment files")
    print("  📁 modules/        - Reusable modules")
    print("  📁 scripts/        - Utility scripts")
    print("  📁 assets/         - Static resources")
    print("  📁 config/         - Configuration files")
    print("\n🚀 Starting Experiment Controller...")
    print("=" * 50)
    
    try:
        controller = ExperimentController()
        controller.run()
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Try running individual experiments:")
        print("  ./scripts/run_ex1.sh")
        print("  ./scripts/run_ex2.sh") 
        print("  ./scripts/run_ex3.sh")
    finally:
        print("\n✅ Goodbye!")

if __name__ == '__main__':
    main()
