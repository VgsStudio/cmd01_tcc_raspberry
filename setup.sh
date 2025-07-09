#!/bin/bash
"""
Setup Script for Raspberry Pi TCC Project
Creates virtual environment, installs requirements, and commits changes
"""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main setup function
main() {
    print_status "🚀 Starting Raspberry Pi TCC Project Setup..."
    
    # Check if we're in the right directory
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found! Please run this script from the project root."
        exit 1
    fi
    
    # Check if Python3 is installed
    if ! command_exists python3; then
        print_error "Python3 is not installed. Please install Python3 first."
        exit 1
    fi
    

    
    # Create virtual environment
    print_status "🏗️  Creating virtual environment..."
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists. Skipping creation."
    else
        python3 -m venv venv
        if [ $? -eq 0 ]; then
            print_success "Virtual environment created successfully!"
        else
            print_error "Failed to create virtual environment."
            exit 1
        fi
    fi
    
    # Activate virtual environment
    print_status "🔌 Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "⬆️  Upgrading pip..."
    python -m pip install --upgrade pip
    
    # Install requirements
    print_status "📦 Installing requirements..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        if [ $? -eq 0 ]; then
            print_success "Requirements installed successfully!"
        else
            print_error "Failed to install requirements."
            exit 1
        fi
    else
        print_error "requirements.txt not found!"
        exit 1
    fi
    
    # Show final status
    print_status "📊 Final Status:"
    echo "  • Virtual environment: $(pwd)/venv"
    echo "  • Python version: $(python --version)"
    echo "  • Pip version: $(pip --version)"
    
    # Show installed packages
    print_status "📦 Installed packages:"
    pip list --format=columns
    
    print_success "🎉 Setup completed successfully!"
    print_status "💡 To activate the virtual environment manually: source venv/bin/activate"
    print_status "🚀 To run the experiment controller: sudo ./venv/bin/python experiment_controller.py"
}

# Run main function
main "$@"
