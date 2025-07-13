#!/usr/bin/env python3
"""
Calculator Module
Handles mathematical operations for the OLED display
"""

import time

def calculate_sum(left_number, right_number):
    """
    Calculate the sum of two numbers with a simulated processing delay
    
    Args:
        left_number (int): Left operand (0-9)
        right_number (int): Right operand (0-9)
    
    Returns:
        int: Sum of the two numbers
    """
    # Simulate processing time
    time.sleep(0.5)
    
    result = left_number + right_number
    
    print(f"Calculator: {left_number} + {right_number} = {result}")
    
    return result

def format_result(result):
    """
    Format the result for display
    
    Args:
        result (int): The calculation result
    
    Returns:
        str: Formatted result string
    """
    return f"= {result}"

def validate_inputs(left_number, right_number):
    """
    Validate that inputs are within expected range
    
    Args:
        left_number (int): Left operand
        right_number (int): Right operand
    
    Returns:
        bool: True if inputs are valid
    """
    return (0 <= left_number <= 9) and (0 <= right_number <= 9)
