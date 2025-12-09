# chapter_10.py - Truth (Final chapter)

import time
from chapters.base_chapter import BaseChapter


class Chapter10(BaseChapter):
    """Chapter 10: The paradox ending"""

    def run(self):
        # Narrative
        self.show_narrative([
            "Chapter 10\nTruth",
            "You open\nyour eyes",
            "The world\nis foggy\nagain",
            "But something\nfeels\ndifferent",
            "You remember\nthe well",
            "You remember\npulling\nsomeone",
            "You remember\nletting go",
            "Or\ndid you?"
        ])

        # Flashing sequence
        flash_duration = 3.0
        flash_speed = 0.5
        start_time = time.monotonic()

        while time.monotonic() - start_time < flash_duration:
            self.display.show_text("Yes\nI did")
            time.sleep(flash_speed)
            self.display.show_text("No\nI did not")
            time.sleep(flash_speed)
            flash_speed *= 0.8  # Speed up

        # The paradox - correct answer is to do nothing
        while True:
            self.display.show_text("Did you?")
            time.sleep(1)

            choices = ["Yes", "No"]
            selected = 0
            start_time = time.monotonic()

            self.display.show_choice(choices[0], "You have 10 s")

            choice_made = False

            while time.monotonic() - start_time < 10:
                self.inputs.update()

                if self.inputs.left_button_pressed():
                    selected = (selected - 1) % 2
                    remaining = int(10 - (time.monotonic() - start_time))
                    self.display.show_choice(choices[selected], f"You have {remaining} s left")

                if self.inputs.right_button_pressed():
                    selected = (selected + 1) % 2
                    remaining = int(10 - (time.monotonic() - start_time))
                    self.display.show_choice(choices[selected], f"You have {remaining} s left")

                if self.inputs.encoder_button_pressed():
                    choice_made = True
                    break

                time.sleep(0.01)

            # If they made a choice, it's wrong - repeat
            if choice_made:
                # Flash sequence again
                flash_speed = 0.3
                for _ in range(3):
                    self.display.show_text("Yes I did")
                    time.sleep(flash_speed)
                    self.display.show_text("No I did not")
                    time.sleep(flash_speed)
                continue
            else:
                # They let the timer expire - CORRECT!
                break

        # Ending narrative
        self.show_narrative([
            "You\nremembered\neverything",
            "You didn't\nescape\nthat day",
            "You came\nback to\nthe well",
            "But you\npulled your\nbrother up",
            "Before you\nlost your\nconsciousness",
            "And died\nfalling into\nthe well",
            "The shadow\nfinally\nbecomes clear",
            "'Thank you, brother'",
            "'Rest in peace'",
            "The End"
        ])

        # Return None to trigger restart prompt
        return None
