# filters.py - Accelerometer filtering utilities

import time
import math
from utils.constants import ACCEL_EMA_ALPHA, ACCEL_HPF_ALPHA


class AccelerometerFilter:
    """Utility class for accelerometer signal filtering"""

    @staticmethod
    def ema_filter(raw, filtered, alpha=ACCEL_EMA_ALPHA):
        """Exponential Moving Average (low-pass filter)

        Args:
            raw: Raw sensor value
            filtered: Previous filtered value
            alpha: Smoothing factor (0-1), lower = more smoothing

        Returns:
            New filtered value
        """
        return alpha * raw + (1 - alpha) * filtered

    @staticmethod
    def high_pass_filter(raw, prev_raw, prev_filtered, alpha=ACCEL_HPF_ALPHA):
        """First-order IIR high-pass filter

        Args:
            raw: Current raw value
            prev_raw: Previous raw value
            prev_filtered: Previous filtered value
            alpha: Filter coefficient (close to 1 preserves high freq)

        Returns:
            New filtered value
        """
        return alpha * (prev_filtered + raw - prev_raw)

    @staticmethod
    def magnitude(x, y, z):
        """Calculate vector magnitude

        Args:
            x, y, z: Acceleration components

        Returns:
            Magnitude of acceleration vector
        """
        return math.sqrt(x * x + y * y + z * z)

    @staticmethod
    def calibrate(accelerometer, samples=100, delay=0.01):
        """Calibrate accelerometer baseline

        Args:
            accelerometer: ADXL345 instance
            samples: Number of samples to average
            delay: Delay between samples (seconds)

        Returns:
            Tuple of (baseline_x, baseline_y, baseline_z)
        """
        sum_x = sum_y = sum_z = 0.0

        for _ in range(samples):
            x, y, z = accelerometer.acceleration
            sum_x += x
            sum_y += y
            sum_z += z
            time.sleep(delay)

        return (
            sum_x / samples,
            sum_y / samples,
            sum_z / samples
        )
