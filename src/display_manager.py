# display_manager.py - OLED display management

import displayio
import terminalio
from adafruit_display_text import label
import i2cdisplaybus
import adafruit_displayio_ssd1306
from utils.constants import OLED_ADDRESS, DISPLAY_WIDTH, DISPLAY_HEIGHT, LINE_SPACING
import board


class DisplayManager:
    """Manages SSD1306 OLED display"""

    def __init__(self, i2c=None):
        """Initialize display

        Args:
            i2c: Optional I2C bus instance. If None, board.I2C() will be tried.
        """
        displayio.release_displays()

        # Prefer a provided shared I2C instance. If not provided, attempt board.I2C()
        if i2c is None:
            try:
                i2c = board.I2C()
            except Exception as e:
                raise ValueError(
                    "No I2C instance provided and board.I2C() unavailable. "
                    "Pass the shared I2C instance (get_i2c() or board.I2C()) to DisplayManager "
                    "to avoid 'pin in use' errors."
                ) from e

        self.display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=OLED_ADDRESS)
        self.display = adafruit_displayio_ssd1306.SSD1306(
            self.display_bus,
            width=DISPLAY_WIDTH,
            height=DISPLAY_HEIGHT
        )

        self.main_group = displayio.Group()
        self.display.root_group = self.main_group

    def clear(self):
        """Clear the display"""
        self.main_group = displayio.Group()
        self.display.root_group = self.main_group

    def show_text(self, text, centered=True, y_offset=0):
        """Display single line of text

        Args:
            text: Text to display
            centered: Center text horizontally and vertically
            y_offset: Vertical offset from center (if centered=True)
        """
        self.clear()

        text_layer = label.Label(terminalio.FONT, text=str(text))

        if centered:
            text_layer.anchor_point = (0.5, 0.5)
            text_layer.anchored_position = (
                DISPLAY_WIDTH // 2,
                DISPLAY_HEIGHT // 2 + y_offset
            )
        else:
            text_layer.x = 0
            text_layer.y = 10

        self.main_group.append(text_layer)

    def show_lines(self, lines, line_spacing=LINE_SPACING, start_y=5):
        """Display multiple lines of text

        Args:
            lines: List of text strings
            line_spacing: Pixels between lines
            start_y: Starting Y position for first line
        """
        self.clear()

        y = start_y

        for text in lines:
            label_obj = label.Label(terminalio.FONT, text=str(text))
            label_obj.x = 0
            label_obj.y = y
            self.main_group.append(label_obj)
            y += line_spacing

    def show_choice(self, choice_text, countdown_text=None):
        """Display choice option with optional countdown

        Args:
            choice_text: Current choice text
            countdown_text: Countdown text to show at bottom (optional)
        """
        self.clear()

        # Show choice in center
        choice_label = label.Label(terminalio.FONT, text=str(choice_text))
        choice_label.anchor_point = (0.5, 0.5)
        choice_label.anchored_position = (DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2)
        self.main_group.append(choice_label)

        # Show countdown at bottom if provided
        if countdown_text:
            countdown_label = label.Label(terminalio.FONT, text=str(countdown_text))
            countdown_label.x = 0
            countdown_label.y = DISPLAY_HEIGHT - 10
            self.main_group.append(countdown_label)

    def update_countdown(self, seconds_left):
        """Update countdown text at bottom of screen

        Args:
            seconds_left: Seconds remaining
        """
        # Only update if last item looks like a text Label (avoid clobbering other widgets)
        if len(self.main_group) >= 1:
            last_item = self.main_group[-1]
            try:
                if isinstance(last_item, label.Label):
                    last_item.text = f"You have {seconds_left} s left"
            except Exception:
                if hasattr(last_item, "text"):
                    last_item.text = f"You have {seconds_left} s left"
