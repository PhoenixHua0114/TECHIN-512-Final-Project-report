# constants.py - Game configuration and constants

import board

# I2C addresses
OLED_ADDRESS = 0x3C
ACCEL_ADDRESS = 0x53

# Pin assignments
ENCODER_CLK = board.D0
ENCODER_DT = board.D1
ENCODER_SW = board.D9
BUTTON_LEFT = board.D7
BUTTON_RIGHT = board.D8
NEOPIXEL_PIN = board.D10

# Display settings
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 64
LINE_SPACING = 10

# Accelerometer settings
ACCEL_EMA_ALPHA = 0.3
ACCEL_HPF_ALPHA = 0.98
MOTION_THRESHOLD = 0.30  # Threshold for movement detection (higher = less sensitive)
TILT_THRESHOLD = 1.2
DOUBLE_TAP_WINDOW = 0.4

# Game settings
DIFFICULTY_EASY = "easy"
DIFFICULTY_MEDIUM = "medium"
DIFFICULTY_HARD = "hard"

# NeoPixel colors
COLOR_BOOT = (255, 255, 0)      # Yellow
COLOR_CORRECT = (0, 0, 255)     # Blue
COLOR_WRONG = (255, 0, 0)       # Red
COLOR_OFF = (0, 0, 0)           # Off
