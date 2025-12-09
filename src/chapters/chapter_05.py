# chapter_05.py - Hospital (Rhythm matching game)

import time
import random
from chapters.base_chapter import BaseChapter


class Chapter05(BaseChapter):
    """Chapter 5: Rhythm matching game and forward movement"""

    def run(self):
        # Narrative
        self.show_narrative([
            "Chapter 5\nHospital",
            "You are\nnow in a\nlong corridor",
            "Seems like\none in\na hospital",
            "Your\nfootsteps echo\nstrangely",
            "Not\nmatching your\nmovement",
            "The echo\nshifts\nleft and right",
            "Try to\nmatch\nits rhythm"
        ])

        # Rhythm matching game
        pattern_lengths = {"easy": 3, "medium": 4, "hard": 5}
        rounds = {"easy": 1, "medium": 2, "hard": 3}
        timeout_per_round = {"easy": 5, "medium": 5, "hard": 6}

        pattern_len = pattern_lengths[self.difficulty]
        num_rounds = rounds[self.difficulty]
        timeout = timeout_per_round[self.difficulty]

        for round_num in range(num_rounds):
            # Generate random pattern
            pattern = [random.choice(["L", "R"]) for _ in range(pattern_len)]
            pattern_str = " ".join(pattern)

            self.display.show_text(pattern_str, centered=True)
            time.sleep(2)

            # Player input
            player_input = []
            start_time = time.monotonic()
            last_countdown = timeout

            # Show initial countdown (no pattern, just time)
            remaining_time = int(timeout - (time.monotonic() - start_time))
            self.display.show_text(f"{remaining_time}s left", centered=True)

            while len(player_input) < pattern_len:
                self.inputs.update()

                button_pressed = False

                if self.inputs.left_button_pressed():
                    player_input.append("L")
                    button_pressed = True

                if self.inputs.right_button_pressed():
                    player_input.append("R")
                    button_pressed = True

                # If button was pressed, add small delay to prevent double-detection
                if button_pressed:
                    time.sleep(0.15)
                    continue

                # Update countdown display (no pattern, just time)
                remaining_time = int(timeout - (time.monotonic() - start_time))
                if remaining_time < last_countdown:
                    self.display.show_text(f"{remaining_time}s left", centered=True)
                    last_countdown = remaining_time

                # Check timeout
                if time.monotonic() - start_time > timeout:
                    return self.handle_wrong_choice([
                        "Your steps\nwent out of sync",
                        "The corridor\nfloor\ncracks open",
                        "You fall\ninto the\nhollow beneath"
                    ], "chapter_05")

                time.sleep(0.01)

            # Check if correct
            if player_input != pattern:
                return self.handle_wrong_choice([
                    "Your steps\nwent out of sync",
                    "The corridor\nfloor\ncracks open",
                    "You fall\ninto the\nhollow beneath"
                ], "chapter_05")

            # Correct! Show success feedback
            self.led.set_correct()

            # If there are more rounds, show brief success message
            if round_num < num_rounds - 1:
                self.display.show_text("Correct!\nNext pattern...", centered=True)
                time.sleep(1.5)

        # Success - all rounds complete
        self.show_narrative([
            "You see \na shadow ",
            "of a little\nboy pass by",
            "The lights \nbehind you\nbegin to go out",
            "one by one"
        ])

        # Show "Run" without waiting for button press
        self.display.show_text("Run", centered=True)
        time.sleep(1.5)

        # Forward movement detection with retries and countdown (starts immediately)
        timeout_map = {"easy": 10, "medium": 8, "hard": 6}
        max_retries = {"easy": 3, "medium": 2, "hard": 1}

        for attempt in range(max_retries[self.difficulty]):
            if self.inputs.detect_tilt_forward(timeout_map[self.difficulty], display=self.display, show_countdown=True, countdown_label="Run"):
                break

            # Failed this attempt
            self.led.set_wrong()
            self.show_narrative([
                "You failed\nto escape",
                "The little\nboy slipped\naway",
                "You turned\naround",
                "Saw a\nblack shadow\nmoving towards you"
            ])

            # Check if we have more attempts
            if attempt < max_retries[self.difficulty] - 1:
                # Show retry prompt
                self.display.show_text("Try again...", centered=True)
                time.sleep(1)
            else:
                # Out of retries
                return "restart_chapter_05"

        # Success
        self.show_narrative([
            "The light\nis back",
            "The echoes\nalign with\nyour breath",
            "The corridor\nbegins\nto fold",
            "Revealing\na rusted\nelevator"
        ])
        self.display.show_text("Press button\nto enter\nthe elevator")
        self.inputs.wait_for_encoder_press()

        # Clean up local variables before transitioning
        del pattern_lengths, rounds, timeout_per_round, timeout_map, max_retries
        import gc
        gc.collect()

        return "chapter_06"
