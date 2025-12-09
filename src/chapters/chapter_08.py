# chapter_08.py - Flood

import time
from chapters.base_chapter import BaseChapter


class Chapter08(BaseChapter):
    """Chapter 8: Hold buttons and double-click"""

    def run(self):
        # Narrative
        self.show_narrative([
            "Chapter 8\nFlood",
            "You stand\nknee-deep\nin water",
            "It rises\nevery second"
        ])

        # Show "You must hold on to something" without waiting for button press
        self.display.show_text("You must\nhold on to\nsomething", centered=True)
        time.sleep(1.5)

        # Hold both buttons with retries (no instruction shown, starts immediately)
        react_time = {"easy": 5, "medium": 4, "hard": 3}
        hold_duration = {"easy": 3, "medium": 4, "hard": 5}
        attempts = {"easy": 4, "medium": 3, "hard": 2}[self.difficulty]

        while True:
            start_time = time.monotonic()
            success = False

            # Wait for buttons to be pressed within timeout
            while time.monotonic() - start_time < react_time[self.difficulty]:
                self.inputs.update()

                # Both buttons pressed (value = False means pressed for pull-up)
                if not self.inputs.left_button.value and not self.inputs.right_button.value:
                    # Both buttons pressed, now check if held for required duration
                    if self.inputs.both_buttons_held(hold_duration[self.difficulty]):
                        success = True
                        break
                time.sleep(0.01)

            # Check if successful
            if success:
                break

            # Failed - decrement attempts
            attempts -= 1

            # Show failure message
            self.led.set_wrong()
            self.show_narrative([
                "You lose\nyour grip",
                "The water\nswallows you",
                "And dragged\nyou back\nviolently"
            ])

            # Check if we have more attempts
            if attempts > 0:
                self.display.show_text("Try again...", centered=True)
                time.sleep(1)
                continue
            else:
                # Out of retries
                return "restart_chapter_04"

        # Success
        self.show_narrative([
            "You gripped\nthe doorknob\ntightly",
            "But the\nwater level is\nincreasing faster",
            "You heard a similar\nwhisper again",
            "From\nunderneath\nthe water",
            "Knock,\nknock,knock......"
        ])

        # Double-click button with retries
        tap_timeout = {"easy": 20, "medium": 15, "hard": 10}
        tap_retries = {"easy": 3, "medium": 2, "hard": 1}

        for attempt in range(tap_retries[self.difficulty]):
            if self.inputs.detect_double_click_button(timeout_s=tap_timeout[self.difficulty]):
                break
            else:
                if attempt < tap_retries[self.difficulty] - 1:
                    self.display.show_text("Knock knock......")
                    time.sleep(1)
                    continue
                else:
                    return self.handle_wrong_choice([
                        "The water\ndrowns you in",
                        "Slowly,\nyou lost\nyour breath",
                        "Being\ndragged back\nviolently"
                    ], "chapter_04")

        # Success
        self.show_narrative([
            "You knock\nsoftly",
            "A voice\nresponds",
            "The water\nglows faintly",
            "A tunnel\nopens beneath"
        ])
        self.display.show_text("Press button\nto enter\nthe tunnel")
        self.inputs.wait_for_encoder_press()

        # Clean up local variables before transitioning
        del react_time, hold_duration, attempts, tap_timeout, tap_retries
        import gc
        gc.collect()

        return "chapter_09"

