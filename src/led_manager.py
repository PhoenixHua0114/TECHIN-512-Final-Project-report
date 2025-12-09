# led_manager.py - NeoPixel LED control

import neopixel
import time
from utils.constants import NEOPIXEL_PIN, COLOR_BOOT, COLOR_CORRECT, COLOR_WRONG, COLOR_OFF


class LEDManager:
    """Manages NeoPixel LED for visual feedback"""

    def __init__(self, pin=NEOPIXEL_PIN, num_pixels=1, brightness=0.3):
        """Initialize NeoPixel LED

        Args:
            pin: GPIO pin for NeoPixel data
            num_pixels: Number of LEDs (default 1)
            brightness: LED brightness 0.0-1.0
        """
        try:
            # Use auto_write=True like the working example
            self.pixels = neopixel.NeoPixel(
                pin,
                num_pixels,
                brightness=brightness,
                auto_write=True  # Match working example
            )
            print(f"NeoPixel initialized on pin {pin}")
            # Test the LED immediately with white
            self.pixels[0] = (255, 255, 255)
            print("Test: LED should be white now")
            time.sleep(0.5)
            # Turn off test
            self.pixels[0] = (0, 0, 0)
        except Exception as e:
            print(f"Error initializing NeoPixel: {e}")
            self.pixels = None

    def set_boot(self):
        """Set LED to yellow (boot/power on state) for 3 seconds"""
        self.set_color(*COLOR_BOOT)
        time.sleep(3)
        self.set_off()

    def set_correct(self):
        """Set LED to blue (correct choice/action) for 3 seconds"""
        self.set_color(*COLOR_CORRECT)
        time.sleep(3)
        self.set_off()

    def set_wrong(self):
        """Set LED to red (wrong choice/action) for 3 seconds"""
        self.set_color(*COLOR_WRONG)
        time.sleep(3)
        self.set_off()

    def set_off(self):
        """Turn off LED"""
        self.set_color(*COLOR_OFF)

    def set_color(self, r, g, b):
        """Set LED to custom RGB color

        Args:
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)
        """
        if self.pixels is None:
            print(f"NeoPixel not initialized, skipping color set to ({r}, {g}, {b})")
            return

        try:
            self.pixels[0] = (r, g, b)  # auto_write=True handles .show() automatically
            print(f"LED set to RGB({r}, {g}, {b})")
        except Exception as e:
            print(f"Error setting LED color: {e}")