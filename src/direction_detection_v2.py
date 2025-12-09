import time
import board
import busio
import adafruit_adxl34x

# --- New: accelerometer reader helper (non-blocking, reusable) ---
class AccelerometerReader:
    """Non-blocking accelerometer reader with EMA + confirmation."""

    def __init__(self, i2c=None, alpha=0.3, confirm_samples=3, threshold=1.2):
        # acquire I2C if not provided
        if i2c is None:
            try:
                i2c = board.I2C()
            except Exception:
                i2c = busio.I2C(board.SCL, board.SDA)
        # create sensor
        self._accel = adafruit_adxl34x.ADXL345(i2c)
        self.alpha = alpha
        self.confirm_samples = confirm_samples
        self.threshold = threshold

        # initialize EMA state from first reading
        x, y, z = self._accel.acceleration
        self.x_filt = x
        self.y_filt = y
        self.z_filt = z

        self._direction = "NONE"
        self._count = 0

    def update(self):
        """Read sensor, update EMA and return a confirmed direction string or None.
        Returns one of: "+X","-X","+Y","-Y","+Z","-Z" when confirmed, otherwise None.
        """
        x_raw, y_raw, z_raw = self._accel.acceleration

        # EMA
        self.x_filt = self.alpha * x_raw + (1 - self.alpha) * self.x_filt
        self.y_filt = self.alpha * y_raw + (1 - self.alpha) * self.y_filt
        self.z_filt = self.alpha * z_raw + (1 - self.alpha) * self.z_filt

        abs_x, abs_y, abs_z = abs(self.x_filt), abs(self.y_filt), abs(self.z_filt)

        if abs_x >= abs_y and abs_x >= abs_z:
            dominant = "X"
            value = self.x_filt
        elif abs_y >= abs_x and abs_y >= abs_z:
            dominant = "Y"
            value = self.y_filt
        else:
            dominant = "Z"
            value = self.z_filt

        new_direction = "NONE"
        if value > self.threshold:
            new_direction = "+" + dominant
        elif value < -self.threshold:
            new_direction = "-" + dominant

        if new_direction == self._direction and new_direction != "NONE":
            self._count += 1
        else:
            self._direction = new_direction
            self._count = 1

        if self._direction != "NONE" and self._count >= self.confirm_samples:
            return self._direction

        return None

def get_accel_reader(i2c=None, **kwargs):
    """Factory: return an AccelerometerReader using provided/shared I2C."""
    return AccelerometerReader(i2c=i2c, **kwargs)

def get_i2c(max_retries=6, retry_delay=0.5):
    """
    Try to obtain a shared I2C instance.
    - Prefer board.I2C() (singleton on newer CircuitPython).
    - Fall back to busio.I2C if possible.
    - If pins are already claimed, retry a few times and print guidance.
    """
    for attempt in range(1, max_retries + 1):
        try:
            # Prefer the board singleton (safer if other libs also use I2C)
            try:
                i2c = board.I2C()
            except Exception:
                # Fallback: constructing busio.I2C can raise ValueError("D5 in use") if pins already claimed
                i2c = busio.I2C(board.SCL, board.SDA)
            return i2c
        except (ValueError, RuntimeError) as e:
            # Common message: "D5 in use" when another driver already claimed the pins
            print("I2C init failed (attempt %d/%d): %s" % (attempt, max_retries, e))
            if attempt < max_retries:
                print("  Retrying in %.1fs..." % retry_delay)
                time.sleep(retry_delay)
            else:
                # Final failure: give actionable hints
                print("Failed to initialize I2C after retries.")
                print("Hints:")
                print(" - Ensure OLED/display and sensor use the same I2C instance (pass the same 'i2c').")
                print(" - If a display driver auto-creates I2C, modify that code to accept an i2c parameter or")
                print("   initialize the display using the i2c returned by this function.")
                print(" - As a quick test, try initializing the accelerometer before initializing the display.")
                raise

# Move runtime actions into a main() so this module can be imported safely.
def main():
    # Acquire I2C safely
    i2c = get_i2c()

    # Optional: try a quick scan to confirm devices (use try_lock to avoid disrupting other users)
    devices = []
    try:
        if hasattr(i2c, "try_lock"):
            if i2c.try_lock():
                try:
                    devices = i2c.scan()
                finally:
                    i2c.unlock()
        else:
            devices = i2c.scan()
    except Exception as e:
        print("I2C scan error (continuing):", e)
        devices = []

    if devices:
        print("I2C devices found:", [hex(d) for d in devices])
    else:
        print("I2C scan returned no devices or scan not available (continuing)")

    # Create accelerometer using the shared i2c instance, handle missing device gracefully
    try:
        accelerometer = adafruit_adxl34x.ADXL345(i2c)
    except Exception as e:
        print("Failed to initialize accelerometer:", e)
        print("If the pins are claimed by another driver, ensure you share the same I2C instance.")
        return

    ALPHA = 0.3          # EMA
    CONFIRM_SAMPLES = 3  # 连续多少次检测到同一方向才确认
    THRESHOLD = 1.2      # per-axis 阈值

    # 初始化 EMA 值
    x_filt, y_filt, z_filt = accelerometer.acceleration

    direction = "NONE"
    direction_count = 0

    print("Starting direction detection... (Ctrl+C to stop)")

    while True:
        x_raw, y_raw, z_raw = accelerometer.acceleration

        # EMA 去噪
        x_filt = ALPHA * x_raw + (1 - ALPHA) * x_filt
        y_filt = ALPHA * y_raw + (1 - ALPHA) * y_filt
        z_filt = ALPHA * z_raw + (1 - ALPHA) * z_filt

        # 选择主导轴
        abs_x = abs(x_filt)
        abs_y = abs(y_filt)
        abs_z = abs(z_filt)

        dominant = "NONE"
        value = 0

        if abs_x >= abs_y and abs_x >= abs_z:
            dominant = "X"
            value = x_filt
        elif abs_y >= abs_x and abs_y >= abs_z:
            dominant = "Y"
            value = y_filt
        else:
            dominant = "Z"
            value = z_filt

        new_direction = "NONE"
        if value > THRESHOLD:
            new_direction = "+" + dominant
        elif value < -THRESHOLD:
            new_direction = "-" + dominant

        # chek for debouncing
        if new_direction == direction and new_direction != "NONE":
            direction_count += 1
        else:
            direction = new_direction
            direction_count = 1

        if direction != "NONE" and direction_count >= CONFIRM_SAMPLES:
            print("Moving", direction)
        else:
            print("Not moving")

        time.sleep(0.05)

if __name__ == "__main__":
    main()
