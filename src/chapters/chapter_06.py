# chapter_06.py - Your Path

import time
from chapters.base_chapter import BaseChapter


class Chapter06(BaseChapter):
    """Chapter 6: Elevator button choice"""

    def run(self):
        # Narrative
        self.show_narrative([
            "Chapter 6\nYour path",
            "The elevator\nclosed slowly",
            "You suddenly\nfeel a\nheavy knock",
            "You look at\nthe buttons",
            "Think about\nwhich\none to press"
        ])

        self.display.show_text("Press button")
        time.sleep(1)

        # Choice with retries
        attempts = {"easy": 3, "medium": 2, "hard": 1}[self.difficulty]

        while True:
            choices = ["Press open", "Basement", "2nd floor", "3rd floor"]

            def display_callback(choice_text, countdown):
                self.display.show_choice(choice_text, f"You have {countdown} s left")

            selected = self.inputs.navigate_choice(choices, 15, display_callback)

            # Correct choice
            if selected == 2:  # 2nd floor - CORRECT
                break

            # Decrement attempts
            attempts -= 1

            # Basement choice - immediate failure to Chapter 4 (no retries)
            if selected == 1:
                return self.handle_wrong_choice([
                    "The elevator\nshake\nviolently",
                    "Then it\naccelerate downward\nrapidly",
                    "You were knocked\nunconscious\nby the impact"
                ], "chapter_04")

            # Press open, 3rd floor, or timeout - go to Ch5
            else:
                self.led.set_wrong()
                self.show_narrative([
                    "A shadow burst\nthrough\nthe door",
                    "Among the\nshrill screams",
                    "Your tears\ndrop down"
                ])

                if attempts > 0:
                    # Show retry message
                    self.display.show_text("Try again...", centered=True)
                    time.sleep(1)
                    continue
                else:
                    # Out of retries
                    return "restart_chapter_05"

        # Success
        self.show_narrative([
            "The heavy\nknock stopped",
            "The elevator\nstarted\ngoing up",
            "After a\nfew seconds,\nit stopped"
        ])
        self.display.show_text("Press button\nto exit\nthe elevator")
        self.inputs.wait_for_encoder_press()
        return "chapter_07"
