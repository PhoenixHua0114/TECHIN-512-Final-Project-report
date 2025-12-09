# chapter_07.py - Reflections

import time
from chapters.base_chapter import BaseChapter


class Chapter07(BaseChapter):
    """Chapter 7: 6-direction movement and mirror choice"""

    def run(self):
        # Narrative
        self.show_narrative([
            "Chapter 7\nReflections",
            "The\nelevator door\nopened slowly",
            "You entered\na room\nfull of mirrors"
        ])

        # Show "But none reflects your face" without waiting for button press
        self.display.show_text("But none reflects\nyour face", centered=True)
        time.sleep(1.5)

        # 4-direction detection (X and Y axes only) with hints (no timeout, no failure penalty)
        hint_shown = False

        def hint_callback(elapsed):
            nonlocal hint_shown
            if not hint_shown:
                if self.difficulty == "easy" and elapsed > 5:
                    self.display.show_text("Try moving\nand tilting\nall directions")
                    hint_shown = True
                elif self.difficulty == "medium" and elapsed > 10:
                    self.display.show_text("Try moving\nand tilting\nall directions")
                    hint_shown = True

        # No timeout (None), no failure penalty - player can take as long as they want
        # Only detect X and Y axes (4 directions: +X, -X, +Y, -Y)
        self.inputs.detect_all_six_directions(timeout_s=None, hint_callback=hint_callback, axes=['x', 'y'])

        # Success
        self.show_narrative([
            "You finally\nsee a shadow",
            "But it's\nnot yours",
            "Waving the\nright hand\nto you"
        ])

        # Show hint
        hints = {
            "easy": "The shadow\nreacts\nopposite of you",
            "medium": "Follow what\nis reversed",
            "hard": "Mirror..."
        }
        self.show_hint(hints)

        self.display.show_text("What should\nyou react")
        time.sleep(1)

        # Choice with retries
        attempts = {"easy": 2, "medium": 1, "hard": 1}[self.difficulty]

        while True:
            choices = ["Wave your\nleft hand", "Stay still", "Wave your\nright hand"]

            def display_callback(choice_text, countdown):
                self.display.show_choice(choice_text, f"You have {countdown} s left")

            selected = self.inputs.navigate_choice(choices, 10, display_callback)

            # Correct choice
            if selected == 0:  # Wave left - CORRECT
                break

            # Wrong choice - decrement attempts
            attempts -= 1

            # Show failure message
            self.led.set_wrong()
            self.show_narrative([
                "The dark\nshadow suddenly\nstopped",
                "It stares\nat you\nsilently",
                "Your tears\ndrop down",
                "Then your\nheart stopped"
            ])

            # Check if we have more attempts
            if attempts > 0:
                self.display.show_text("Try again...", centered=True)
                time.sleep(1)
                continue
            else:
                # Out of retries
                return "restart_chapter_07"

        # Success
        self.show_narrative([
            "The mirror\nsoftens\nlike water",
            "You walk into\nyour own\nreflection",
            "And exit\nthrough the\nother side"
        ])
        self.display.show_text("Press button\nto continue")
        self.inputs.wait_for_encoder_press()
        return "chapter_08"
