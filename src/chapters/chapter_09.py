# chapter_09.py - The Well

import time
from chapters.base_chapter import BaseChapter


class Chapter09(BaseChapter):
    """Chapter 9: Tilt forward and stay still"""

    def run(self):
        # Narrative
        self.show_narrative([
            "Chapter 9\nThe Well",
            "After a\nlong time\nwalking",
            "You see a\ndim light\nin the front",
            "After exiting\nthe tunnel",
            "You find\nyourself\nstanding",
            "Beside an\nold well",
            "You hear\ncrying\nfrom below"
        ])

        # Show "Lean down and listen" without waiting for button press
        self.display.show_text("Lean down and listen", centered=True)
        time.sleep(1.5)

        # Tilt forward detection with retries and countdown (starts immediately)
        timeout_map = {"easy": 5, "medium": 4, "hard": 3}
        attempts = {"easy": 3, "medium": 2, "hard": 1}[self.difficulty]

        while True:
            if self.inputs.detect_tilt_forward(timeout_map[self.difficulty], display=self.display, show_countdown=True, countdown_label="Lean down and listen"):
                break

            # Failed this attempt
            attempts -= 1

            # Show failure message
            self.led.set_wrong()
            self.show_narrative([
                "You stepped\ntoo far back",
                "The crying\nstopped",
                "An irresistible\nforce drags\nyou into the well"
            ])

            # Check if we have more attempts
            if attempts > 0:
                self.display.show_text("Try again...", centered=True)
                time.sleep(1)
                continue
            else:
                # Out of retries
                return "restart_chapter_08"

        # Success
        self.show_narrative([
            "You hear\nhim clearly",
            "'Help... \nI can't\nclimb up'"
        ])

        # Show "Hold tight!!!" without waiting for button press
        self.display.show_text("Hold tight!!!", centered=True)
        time.sleep(1.5)

        # Hold both buttons challenge (no instruction shown, starts immediately)
        duration_map = {"easy": 3, "medium": 4, "hard": 5}

        # Wait for both buttons to be pressed
        start_time = time.monotonic()
        timeout = 5  # 5 seconds to start pressing

        while time.monotonic() - start_time < timeout:
            self.inputs.update()

            # Check if both buttons are pressed
            if not self.inputs.left_button.value and not self.inputs.right_button.value:
                # Both buttons pressed, now check if held for required duration
                if self.inputs.both_buttons_held(duration_map[self.difficulty]):
                    break
                else:
                    # Released too early
                    return self.handle_wrong_choice([
                        "You let go\ntoo early",
                        "The rope\nslipped",
                        "You failed,\nagain"
                    ], "chapter_09")

            time.sleep(0.01)
        else:
            # Timeout - didn't press buttons in time
            return self.handle_wrong_choice([
                "You didn't\nhold on",
                "You failed,\nagain"
            ], "chapter_09")

        # Success
        self.show_narrative([
            "You\ntightly hold\nthe rope",
            "The weight\nfeels\nfamiliar",
            "Like someone small",
            "A shadow\nrises from\nthe dark",
            "But you\nfainted before\nseeing it"
        ])
        self.display.show_text("Press button\nto continue")
        self.inputs.wait_for_encoder_press()

        # Clean up local variables before transitioning
        del timeout_map, attempts, duration_map
        import gc
        gc.collect()

        return "chapter_10"

