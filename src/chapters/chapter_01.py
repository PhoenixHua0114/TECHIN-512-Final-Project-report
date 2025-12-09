# chapter_01.py - Entering your memory

import time
from chapters.base_chapter import BaseChapter


class Chapter01(BaseChapter):
    """Chapter 1: Three entrances choice"""

    def run(self):
        # Narrative
        self.show_narrative([
            "Chapter 1\nEntering your memory",
            "Press button\nto continue"
        ])

        # Dialogue
        self.show_narrative([
            "You\nstopped",
            "Standing\nin the middle\nof the road",
            "Three entrances\nappears\nin front of you"
        ])

        # Entrance descriptions
        self.show_narrative([
            "Left entrance:\nNothing but\ndarkness",
            "Middle entrance:\nDim white light\nshinning behind",
            "Right entrance:\nSome blurred sound\nechoing in behind"
        ])

        # Show difficulty hint
        hints = {
            "easy": "The light\nwill lead\nyour way",
            "medium": "His favorite\nnumber is 2",
            "hard": "Do not go\noff track"
        }
        self.show_hint(hints)

        # Choice selection with retry handling based on difficulty
        choices = ["Left entrance", "Middle entrance", "Right entrance"]

        def display_callback(choice_text, countdown):
            # include the prompt line and the countdown at bottom
            self.display.show_choice(choice_text, f"You have {countdown} s left")

        attempts = self.get_retry_count()

        while True:
            selected = self.inputs.navigate_choice(choices, 15, display_callback)

            # Timeout
            if selected == -1:
                # Timeout-specific failure message
                self.led.set_wrong()
                self.show_narrative([
                    "You still\ndidn't make it",
                    "The road\ncollapses",
                    "You fall\ninto the\ndarkness"
                ])
                # Retry logic
                attempts -= 1
                if attempts > 0:
                    # show choice again (loop)
                    continue
                else:
                    # restart chapter from beginning
                    return f"restart_chapter_01"

            # Left choice (wrong)
            if selected == 0:
                self.led.set_wrong()
                self.show_narrative([
                    "You\nwalk into\nthe darkness",
                    "Like falling\ninto a\nwell",
                    "You made\nthe wrong\nchoice again..."
                ])
                attempts -= 1
                if attempts > 0:
                    continue
                else:
                    return f"restart_chapter_01"

            # Middle (correct)
            if selected == 1:
                return self.handle_correct_choice([
                    "You walk\ninto the\nlight",
                    "You feel\na sudden\ndizziness",
                    "Your\ntrip\ncontinues..."
                ], "chapter_02")

            # Right (wrong)
            if selected == 2:
                self.led.set_wrong()
                self.show_narrative([
                    "You step\ninto\nthe entrance",
                    "The echo inside\nsounds like\nyour breath",
                    "Suddenly\nit turns\ninto a scream",
                    "YOU DON'T\nDESERVE\nTO SEE HIM"
                ])
                attempts -= 1
                if attempts > 0:
                    continue
                else:
                    return f"restart_chapter_01"
