# input_manager.py - Centralized input handling for all devices

import time
import digitalio
import adafruit_adxl34x
from adafruit_debouncer import Debouncer
from rotary_encoder import RotaryEncoder
from utils.constants import (
    ENCODER_CLK, ENCODER_DT, ENCODER_SW,
    BUTTON_LEFT, BUTTON_RIGHT,
    ACCEL_EMA_ALPHA, MOTION_THRESHOLD, TILT_THRESHOLD, DOUBLE_TAP_WINDOW
)
from utils.filters import AccelerometerFilter


class InputManager:
    """Manages all input devices: rotary encoder, buttons, accelerometer"""

    def __init__(self, i2c):
        """Initialize all input devices

        Args:
            i2c: I2C bus instance (shared with display)
        """
        # Rotary encoder setup
        self.encoder = RotaryEncoder(
            ENCODER_CLK,
            ENCODER_DT,
            debounce_ms=3,
            pulses_per_detent=3
        )

        # Encoder button
        encoder_btn_io = digitalio.DigitalInOut(ENCODER_SW)
        encoder_btn_io.switch_to_input(pull=digitalio.Pull.UP)
        self.encoder_button = Debouncer(encoder_btn_io)

        # Navigation buttons
        left_btn_io = digitalio.DigitalInOut(BUTTON_LEFT)
        left_btn_io.switch_to_input(pull=digitalio.Pull.UP)
        self.left_button = Debouncer(left_btn_io)

        right_btn_io = digitalio.DigitalInOut(BUTTON_RIGHT)
        right_btn_io.switch_to_input(pull=digitalio.Pull.UP)
        self.right_button = Debouncer(right_btn_io)

        # Accelerometer setup
        self.accelerometer = adafruit_adxl34x.ADXL345(i2c)
        self.accelerometer.enable_tap_detection()

        # Initialize filtered values
        x, y, z = self.accelerometer.acceleration
        self.x_filtered = x
        self.y_filtered = y
        self.z_filtered = z

        # Calibrate baseline (with user notification)
        print("Calibrating accelerometer - keep device STILL for 1 second...")
        self.baseline_x, self.baseline_y, self.baseline_z = AccelerometerFilter.calibrate(
            self.accelerometer
        )
        print(f"Baseline: X={self.baseline_x:.2f}, Y={self.baseline_y:.2f}, Z={self.baseline_z:.2f}")

        # Tap detection state
        self.last_tap_time = None

        # Direction tracking for 6-direction detection
        self.directions_detected = set()

        # Add accelerometer reader (non-blocking)
        from direction_detection_v2 import get_accel_reader
        try:
            # pass the same i2c instance used by display/game
            self._accel_reader = get_accel_reader(i2c)
        except Exception:
            # If accelerometer not present or initialization failed, keep reader None
            self._accel_reader = None

    def update(self):
        """Update all input devices (call in main loop)"""
        self.encoder.update()
        self.encoder_button.update()
        self.left_button.update()
        self.right_button.update()

        # Update filtered accelerometer values
        x_raw, y_raw, z_raw = self.accelerometer.acceleration
        self.x_filtered = AccelerometerFilter.ema_filter(x_raw, self.x_filtered, ACCEL_EMA_ALPHA)
        self.y_filtered = AccelerometerFilter.ema_filter(y_raw, self.y_filtered, ACCEL_EMA_ALPHA)
        self.z_filtered = AccelerometerFilter.ema_filter(z_raw, self.z_filtered, ACCEL_EMA_ALPHA)

    # ========== Rotary Encoder Methods ==========

    def get_encoder_position(self):
        """Get current encoder position"""
        return self.encoder.position

    def encoder_button_pressed(self):
        """Check if encoder button was pressed (fell edge)"""
        return self.encoder_button.fell

    def wait_for_encoder_press(self):
        """Block until encoder button is pressed"""
        while True:
            self.update()
            if self.encoder_button.fell:
                return
            time.sleep(0.01)

    # ========== Navigation Buttons ==========

    def left_button_pressed(self):
        """Check if left button was pressed"""
        return self.left_button.fell

    def right_button_pressed(self):
        """Check if right button was pressed"""
        return self.right_button.fell

    def both_buttons_held(self, duration_s):
        """Check if both buttons are held for specified duration

        Args:
            duration_s: How long buttons must be held (seconds)

        Returns:
            True if both buttons held for duration, False otherwise
        """
        start_time = time.monotonic()

        while (time.monotonic() - start_time) < duration_s:
            self.update()

            # Check if either button is released
            if self.left_button.value or self.right_button.value:
                return False

            time.sleep(0.01)

        return True

    # ========== Accelerometer - Movement Detection ==========

    def detect_movement(self, timeout_s=None, hint_callback=None, require_axes=None, display=None):
        """Detect significant movement.

        Args:
            timeout_s: Timeout in seconds (None for no timeout)
            hint_callback: Optional callback(elapsed) to show hints while waiting
            require_axes: Optional iterable of axes to detect before returning.
                Example: ['x','y'] requires movement detected on both X and Y axes.
            display: Optional display manager to show real-time feedback

        Returns:
            True if movement detected, False if timeout
        """
        start_time = time.monotonic()

        # Normalize required axes to a set if provided
        required = None
        detected = set()
        if require_axes:
            required = set(a.lower() for a in require_axes)

        # Confirmation counters - require multiple consecutive readings
        confirm_count = {'x': 0, 'y': 0, 'z': 0}
        CONFIRM_THRESHOLD = 5  # Must exceed threshold for 5 consecutive readings (more stable)

        last_display_update = 0

        while True:
            self.update()

            # Current axis diffs
            x_diff = abs(self.x_filtered - self.baseline_x)
            y_diff = abs(self.y_filtered - self.baseline_y)
            z_diff = abs(self.z_filtered - self.baseline_z)

            elapsed = time.monotonic() - start_time

            # If specific axes are required, accumulate detections with confirmation
            if required is not None:
                # Update confirmation counters - require STRONG sustained movement
                if 'x' in required:
                    if x_diff > MOTION_THRESHOLD:
                        confirm_count['x'] += 1
                        # Require even higher threshold for confirmation
                        if confirm_count['x'] >= CONFIRM_THRESHOLD and x_diff > (MOTION_THRESHOLD * 1.2) and 'x' not in detected:
                            detected.add('x')
                    else:
                        # Reset counter if movement drops below threshold
                        confirm_count['x'] = 0

                if 'y' in required:
                    if y_diff > MOTION_THRESHOLD:
                        confirm_count['y'] += 1
                        # Require even higher threshold for confirmation
                        if confirm_count['y'] >= CONFIRM_THRESHOLD and y_diff > (MOTION_THRESHOLD * 1.2) and 'y' not in detected:
                            detected.add('y')
                    else:
                        # Reset counter if movement drops below threshold
                        confirm_count['y'] = 0

                if 'z' in required:
                    if z_diff > MOTION_THRESHOLD:
                        confirm_count['z'] += 1
                        # Require even higher threshold for confirmation
                        if confirm_count['z'] >= CONFIRM_THRESHOLD and z_diff > (MOTION_THRESHOLD * 1.2) and 'z' not in detected:
                            detected.add('z')
                    else:
                        # Reset counter if movement drops below threshold
                        confirm_count['z'] = 0

                # Show progress if display is provided (update every 0.5s)
                if display and (time.monotonic() - last_display_update > 0.5):
                    if detected:
                        detected_str = ", ".join(detected).upper()
                        display.show_text(f"Detected: {detected_str}", centered=True)
                        last_display_update = time.monotonic()
                    # Don't update display when nothing detected - let hint_callback handle it

                if detected >= required:
                    return True
            else:
                # Backwards-compatible: any axis exceeding threshold triggers success
                if x_diff > MOTION_THRESHOLD or y_diff > MOTION_THRESHOLD or z_diff > MOTION_THRESHOLD:
                    return True

            # Call hint callback if provided
            if hint_callback:
                elapsed = time.monotonic() - start_time
                hint_callback(elapsed)

            # Check timeout
            if timeout_s and (time.monotonic() - start_time) > timeout_s:
                return False

            time.sleep(0.02)

    def detect_tilt_left(self, timeout_s, display=None, show_countdown=False):
        """Detect tilt to the left (negative X direction)

        Args:
            timeout_s: Timeout in seconds
            display: Optional display manager to show countdown
            show_countdown: Whether to show countdown timer on display

        Returns:
            True if tilt detected, False if timeout
        """
        start_time = time.monotonic()
        last_countdown = timeout_s

        # Show initial countdown if requested
        if display and show_countdown:
            display.show_text(f"{int(timeout_s)}", centered=True)

        while (time.monotonic() - start_time) < timeout_s:
            self.update()

            if self.x_filtered < -TILT_THRESHOLD:
                return True

            # Update countdown display
            if display and show_countdown:
                remaining = int(timeout_s - (time.monotonic() - start_time))
                if remaining < last_countdown:
                    display.show_text(f"{remaining}", centered=True)
                    last_countdown = remaining

            time.sleep(0.02)

        return False

    def detect_tilt_forward(self, timeout_s=None, display=None, show_countdown=False, countdown_label=None):
        """Detect forward tilt (positive Y direction)

        Args:
            timeout_s: Timeout in seconds (None for no timeout)
            display: Optional display manager to show countdown
            show_countdown: Whether to show countdown timer on display
            countdown_label: Optional label to show with countdown (e.g., "Run")

        Returns:
            True if tilt detected, False if timeout
        """
        start_time = time.monotonic()
        last_countdown = timeout_s if timeout_s else 0

        # Show initial countdown if requested
        if display and show_countdown and timeout_s:
            if countdown_label:
                display.show_text(f"{countdown_label}\n{int(timeout_s)}s left", centered=True)
            else:
                display.show_text(f"{int(timeout_s)}", centered=True)

        while True:
            self.update()

            if self.y_filtered > TILT_THRESHOLD:
                return True

            # Update countdown display (only if timeout is specified)
            if display and show_countdown and timeout_s:
                remaining = int(timeout_s - (time.monotonic() - start_time))
                if remaining < last_countdown:
                    if countdown_label:
                        display.show_text(f"{countdown_label}\n{remaining}s left", centered=True)
                    else:
                        display.show_text(f"{remaining}", centered=True)
                    last_countdown = remaining

            # Check timeout (if specified)
            if timeout_s and (time.monotonic() - start_time) > timeout_s:
                return False

            time.sleep(0.02)

    def detect_tilt_forward_z(self, timeout_s):
        """Detect forward tilt using Z-axis

        Args:
            timeout_s: Timeout in seconds

        Returns:
            True if tilt detected, False if timeout
        """
        start_time = time.monotonic()

        while (time.monotonic() - start_time) < timeout_s:
            self.update()

            # Z-axis tilt detection
            z_diff = self.z_filtered - self.baseline_z
            if abs(z_diff) > TILT_THRESHOLD:
                return True

            time.sleep(0.02)

        return False

    def stay_still(self, duration_s):
        """Check if device stays still for specified duration

        Args:
            duration_s: How long to stay still (seconds)

        Returns:
            True if stayed still, False if movement detected
        """
        start_time = time.monotonic()

        while (time.monotonic() - start_time) < duration_s:
            self.update()

            # Check for any movement
            x_diff = abs(self.x_filtered - self.baseline_x)
            y_diff = abs(self.y_filtered - self.baseline_y)
            z_diff = abs(self.z_filtered - self.baseline_z)

            if (x_diff > MOTION_THRESHOLD or
                y_diff > MOTION_THRESHOLD or
                z_diff > MOTION_THRESHOLD):
                return False

            time.sleep(0.02)

        return True

    def detect_all_six_directions(self, timeout_s=None, hint_callback=None, display=None, axes=['x', 'y', 'z']):
        """Detect movement in multiple directions

        Args:
            timeout_s: Timeout in seconds (None for no timeout)
            hint_callback: Optional callback function to show hints
            display: Optional display manager to show progress
            axes: List of axes to detect (default: ['x', 'y', 'z'] for 6 directions)
                  Use ['x', 'y'] for 4 directions (±X, ±Y only)

        Returns:
            True if all directions detected, False if timeout
        """
        self.directions_detected = set()
        start_time = time.monotonic()

        # Calculate required number of directions based on axes
        axes_set = set(a.lower() for a in axes)
        required_count = len(axes_set) * 2  # Each axis has + and - direction

        while True:
            self.update()
            elapsed = time.monotonic() - start_time

            # Check each direction (only for specified axes)
            if 'x' in axes_set:
                if self.x_filtered > TILT_THRESHOLD:
                    self.directions_detected.add("+X")
                if self.x_filtered < -TILT_THRESHOLD:
                    self.directions_detected.add("-X")

            if 'y' in axes_set:
                if self.y_filtered > TILT_THRESHOLD:
                    self.directions_detected.add("+Y")
                if self.y_filtered < -TILT_THRESHOLD:
                    self.directions_detected.add("-Y")

            if 'z' in axes_set:
                if self.z_filtered - self.baseline_z > TILT_THRESHOLD:
                    self.directions_detected.add("+Z")
                if self.z_filtered - self.baseline_z < -TILT_THRESHOLD:
                    self.directions_detected.add("-Z")

            # Don't show "Detected: X/6" progress - removed per user request

            # Call hint callback
            if hint_callback:
                hint_callback(elapsed)

            # Check if all required directions detected
            if len(self.directions_detected) >= required_count:
                return True

            # Check timeout (if specified)
            if timeout_s and (time.monotonic() - start_time) > timeout_s:
                return False

            time.sleep(0.02)

    # ========== Tap Detection ==========

    def detect_double_tap(self, timeout_s=None, hint_callback=None):
        """Detect double tap on the accelerometer

        Args:
            timeout_s: Timeout in seconds (None for no timeout)
            hint_callback: Optional callback(elapsed) to show hints

        Returns:
            True if double tap detected, False if timeout
        """
        self.last_tap_time = None
        start_time = time.monotonic()

        while True:
            self.update()

            # Check for tap event
            if self.accelerometer.events["tap"]:
                now = time.monotonic()

                # Check if this is the second tap
                if (self.last_tap_time is not None and
                    (now - self.last_tap_time) <= DOUBLE_TAP_WINDOW):
                    self.last_tap_time = None
                    return True
                else:
                    self.last_tap_time = now

            # Call hint callback if provided
            if hint_callback:
                elapsed = time.monotonic() - start_time
                hint_callback(elapsed)

            # Check timeout
            if timeout_s and (time.monotonic() - start_time) > timeout_s:
                return False

            time.sleep(0.02)

    def detect_double_click_button(self, timeout_s=None, hint_callback=None):
        """Detect double click on either left or right button

        Args:
            timeout_s: Timeout in seconds (None for no timeout)
            hint_callback: Optional callback(elapsed) to show hints

        Returns:
            True if double click detected, False if timeout
        """
        last_left_click = None
        last_right_click = None
        start_time = time.monotonic()
        DOUBLE_CLICK_WINDOW = 0.5  # 500ms window for double click

        while True:
            self.update()

            now = time.monotonic()

            # Check for left button click
            if self.left_button.fell:
                # Check if this is the second click
                if (last_left_click is not None and
                    (now - last_left_click) <= DOUBLE_CLICK_WINDOW):
                    return True
                else:
                    last_left_click = now

            # Check for right button click
            if self.right_button.fell:
                # Check if this is the second click
                if (last_right_click is not None and
                    (now - last_right_click) <= DOUBLE_CLICK_WINDOW):
                    return True
                else:
                    last_right_click = now

            # Call hint callback if provided
            if hint_callback:
                elapsed = time.monotonic() - start_time
                hint_callback(elapsed)

            # Check timeout
            if timeout_s and (time.monotonic() - start_time) > timeout_s:
                return False

            time.sleep(0.02)

    # ========== Choice Navigation ==========

    def navigate_choice(self, choices, timeout_s, display_callback):
        """Navigate through choices using left/right buttons

        Args:
            choices: List of choice strings
            timeout_s: Timeout in seconds
            display_callback: Function(choice_text, countdown) to update display

        Returns:
            Index of selected choice, or -1 if timeout
        """
        current_index = 0
        start_time = time.monotonic()
        last_countdown = timeout_s

        display_callback(choices[current_index], timeout_s)

        while True:
            self.update()

            # Check for button presses
            if self.left_button_pressed():
                current_index = (current_index - 1) % len(choices)
                remaining = int(timeout_s - (time.monotonic() - start_time))
                display_callback(choices[current_index], remaining)

            if self.right_button_pressed():
                current_index = (current_index + 1) % len(choices)
                remaining = int(timeout_s - (time.monotonic() - start_time))
                display_callback(choices[current_index], remaining)

            # Check for selection
            if self.encoder_button_pressed():
                return current_index

            # Update countdown only when it changes
            remaining = int(timeout_s - (time.monotonic() - start_time))
            if remaining < last_countdown:
                display_callback(choices[current_index], remaining)
                last_countdown = remaining

            # Check timeout
            if (time.monotonic() - start_time) > timeout_s:
                return -1

            time.sleep(0.01)

    def get_direction(self):
        """Return confirmed accelerometer direction string or None."""
        if self._accel_reader is None:
            return None
        try:
            return self._accel_reader.update()
        except Exception:
            return None




