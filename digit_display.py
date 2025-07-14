#!/usr/bin/env python3
"""
Digit Display Module
Large, bold digit rendering for OLED displays
"""

def draw_large_digit(draw, digit, x, y, size=6):
    """
    Draw a large, bold digit using thick lines
    
    Args:
        draw: PIL ImageDraw object
        digit (int): The digit to draw (0-9)
        x (int): X position to start drawing
        y (int): Y position to start drawing
        size (int): Size multiplier for the digit (default 3)
    """
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

def draw_plus_sign(draw, x, y, size=6):
    """
    Draw a large, bold plus sign
    
    Args:
        draw: PIL ImageDraw object
        x (int): X position to start drawing
        y (int): Y position to start drawing
        size (int): Size multiplier for the plus sign (default 3)
    """
    thick = size
    width = size * 3
    height = size * 3
    
    # Horizontal line
    draw.rectangle([x, y + height//2 - thick//2, x + width, y + height//2 + thick//2], fill=255)
    # Vertical line
    draw.rectangle([x + width//2 - thick//2, y, x + width//2 + thick//2, y + height], fill=255)

def draw_letter_e(draw, x, y, size=6):
    """Draw the letter E"""
    thick = size
    width = size * 3
    height = size * 5
    
    # Left vertical line
    draw.rectangle([x, y, x + thick, y + height], fill=255)
    # Top horizontal
    draw.rectangle([x, y, x + width, y + thick], fill=255)
    # Middle horizontal
    draw.rectangle([x, y + height//2 - thick//2, x + width - thick, y + height//2 + thick//2], fill=255)
    # Bottom horizontal
    draw.rectangle([x, y + height - thick, x + width, y + height], fill=255)

def draw_letter_x(draw, x, y, size=6):
    """Draw the letter X"""
    thick = size
    width = size * 3
    height = size * 5
    
    # Draw X as diagonal lines using rectangles
    # Top-left to bottom-right diagonal
    for i in range(height - thick + 1):
        rect_x = x + (i * width) // height
        draw.rectangle([rect_x, y + i, rect_x + thick, y + i + thick], fill=255)
    
    # Top-right to bottom-left diagonal
    for i in range(height - thick + 1):
        rect_x = x + width - thick - (i * width) // height
        draw.rectangle([rect_x, y + i, rect_x + thick, y + i + thick], fill=255)

def draw_letter_p(draw, x, y, size=6):
    """Draw the letter P"""
    thick = size
    width = size * 3
    height = size * 5
    
    # Left vertical line
    draw.rectangle([x, y, x + thick, y + height], fill=255)
    # Top horizontal
    draw.rectangle([x, y, x + width, y + thick], fill=255)
    # Middle horizontal
    draw.rectangle([x, y + height//2 - thick//2, x + width, y + height//2 + thick//2], fill=255)
    # Right vertical (top half only)
    draw.rectangle([x + width - thick, y, x + width, y + height//2 + thick//2], fill=255)

def draw_dot(draw, x, y, size=6):
    """Draw a dot/period"""
    thick = size
    # Draw a small square for the dot
    draw.rectangle([x, y, x + thick, y + thick], fill=255)

def display_exp_1(draw, center_x=64, center_y=32, size=2):
    """
    Display "EXP. 1" centered on the screen
    
    Args:
        draw: PIL ImageDraw object
        center_x (int): Center X position (default 64 for 128px wide display)
        center_y (int): Center Y position (default 32 for 64px high display)
        size (int): Size multiplier for the text (default 2)
    """
    # Clear the display first
    draw.rectangle([0, 0, 128, 64], fill=0)
    
    # Calculate dimensions
    letter_width = size * 3
    letter_height = size * 5
    digit_width = size * 4
    spacing = size * 2
    dot_width = size
    
    # Calculate total width: E + X + P + . + (space) + 1
    total_width = letter_width + spacing + letter_width + spacing + letter_width + spacing + dot_width + spacing + spacing + digit_width
    
    # Calculate starting X position to center the text
    start_x = center_x - total_width // 2
    start_y = center_y - letter_height // 2
    
    # Draw each character
    current_x = start_x
    
    # Draw "E"
    draw_letter_e(draw, current_x, start_y, size)
    current_x += letter_width + spacing
    
    # Draw "X"
    draw_letter_x(draw, current_x, start_y, size)
    current_x += letter_width + spacing
    
    # Draw "P"
    draw_letter_p(draw, current_x, start_y, size)
    current_x += letter_width + spacing
    
    # Draw "."
    draw_dot(draw, current_x, start_y + letter_height - size, size)
    current_x += dot_width + spacing
    
    # Add extra space before the number
    current_x += spacing
    
    # Draw "1"
    draw_large_digit(draw, 1, current_x, start_y - (size * 6 - letter_height) // 2, size)

def display_exp_2(draw, center_x=64, center_y=32, size=2):
    """
    Display "EXP. 2" centered on the screen
    
    Args:
        draw: PIL ImageDraw object
        center_x (int): Center X position (default 64 for 128px wide display)
        center_y (int): Center Y position (default 32 for 64px high display)
        size (int): Size multiplier for the text (default 2)
    """
    # Clear the display first
    draw.rectangle([0, 0, 128, 64], fill=0)
    
    # Calculate dimensions
    letter_width = size * 3
    letter_height = size * 5
    digit_width = size * 4
    spacing = size * 2
    dot_width = size
    
    # Calculate total width: E + X + P + . + (space) + 2
    total_width = letter_width + spacing + letter_width + spacing + letter_width + spacing + dot_width + spacing + spacing + digit_width
    
    # Calculate starting X position to center the text
    start_x = center_x - total_width // 2
    start_y = center_y - letter_height // 2
    
    # Draw each character
    current_x = start_x
    
    # Draw "E"
    draw_letter_e(draw, current_x, start_y, size)
    current_x += letter_width + spacing
    
    # Draw "X"
    draw_letter_x(draw, current_x, start_y, size)
    current_x += letter_width + spacing
    
    # Draw "P"
    draw_letter_p(draw, current_x, start_y, size)
    current_x += letter_width + spacing
    
    # Draw "."
    draw_dot(draw, current_x, start_y + letter_height - size, size)
    current_x += dot_width + spacing
    
    # Add extra space before the number
    current_x += spacing
    
    # Draw "2"
    draw_large_digit(draw, 2, current_x, start_y - (size * 6 - letter_height) // 2, size)

def display_exp_3(draw, center_x=64, center_y=32, size=2):
    """
    Display "EXP. 3" centered on the screen
    
    Args:
        draw: PIL ImageDraw object
        center_x (int): Center X position (default 64 for 128px wide display)
        center_y (int): Center Y position (default 32 for 64px high display)
        size (int): Size multiplier for the text (default 2)
    """
    # Clear the display first
    draw.rectangle([0, 0, 128, 64], fill=0)
    
    # Calculate dimensions
    letter_width = size * 3
    letter_height = size * 5
    digit_width = size * 4
    spacing = size * 2
    dot_width = size
    
    # Calculate total width: E + X + P + . + (space) + 3
    total_width = letter_width + spacing + letter_width + spacing + letter_width + spacing + dot_width + spacing + spacing + digit_width
    
    # Calculate starting X position to center the text
    start_x = center_x - total_width // 2
    start_y = center_y - letter_height // 2
    
    # Draw each character
    current_x = start_x
    
    # Draw "E"
    draw_letter_e(draw, current_x, start_y, size)
    current_x += letter_width + spacing
    
    # Draw "X"
    draw_letter_x(draw, current_x, start_y, size)
    current_x += letter_width + spacing
    
    # Draw "P"
    draw_letter_p(draw, current_x, start_y, size)
    current_x += letter_width + spacing
    
    # Draw "."
    draw_dot(draw, current_x, start_y + letter_height - size, size)
    current_x += dot_width + spacing
    
    # Add extra space before the number
    current_x += spacing
    
    # Draw "3"
    draw_large_digit(draw, 3, current_x, start_y - (size * 6 - letter_height) // 2, size)
