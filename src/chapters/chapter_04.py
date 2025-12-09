# chapter_04.py - Basement

import time
from chapters.base_chapter import BaseChapter


class Chapter04(BaseChapter):
    """Chapter 4: Tilt forward, dialogue choice, double-click"""

    def run(self):
        # Narrative
        self.show_narrative([
            "Chapter 4\nBasement",
            "You wake\nup again",
            "Inside a\nbasement",
            "Water\ndropping from\nthe ceiling",
            "You hear it",
            "The wall in\nfront of you\nis whispering louder",
            "Like it\nknows\nyour name"
        ])

        # Show "You need to get closer" without waiting for button press
        self.display.show_text("You need\nto get closer", centered=True)
        time.sleep(1.5)

        # Tilt forward detection (no countdown, no timeout - player can think as long as they want)
        self.inputs.detect_tilt_forward(timeout_s=None, display=None, show_countdown=False)

        # Success
        self.show_narrative([
            "You step\nforward and put\nyour ear on the wall",
            "A child's\nvoice murmurs",
            "'Don't\nleave me\nagain'"
        ])

        # Show hint
        hints = {
            "easy": "Silence\nreveals more\nthan sound",
            "medium": "He's\ncloser when\nyou listen",
            "hard": "Listen\nto him"
        }
        self.show_hint(hints)

        # Dialogue choice with retries (Easy has 2 chances)
        attempts = 2 if self.difficulty == "easy" else 1

        while True:
            choices = ["Who are you?", "Stay quiet", "I'm coming"]

            def display_callback(choice_text, countdown):
                self.display.show_choice(choice_text, f"You have {countdown} s left")

            selected = self.inputs.navigate_choice(choices, 10, display_callback)

            # Correct choice
            if selected == 1:  # Stay quiet - CORRECT
                break

            # Wrong choices - decrement attempts
            attempts -= 1

            # Choice 0: "Who are you?" - WRONG
            if selected == 0:
                self.led.set_wrong()
                self.show_narrative([
                    "You raise\nyour voice",
                    "The whisper\nstops",
                    "You feel\nsomeone\npulling your leg",
                    "You fall\nbackward\ninto darkness"
                ])
                if attempts > 0:
                    continue
                else:
                    return "restart_chapter_04"

            # Choice 2: "I'm coming" - WRONG
            elif selected == 2:
                self.led.set_wrong()
                self.show_narrative([
                    "You whisper\nback softly",
                    "The whisper\nbecomes\na scream",
                    "Your ears\nstart bleeding",
                    "You collapse\non the floor"
                ])
                if attempts > 0:
                    continue
                else:
                    return "restart_chapter_04"

            # Timeout (-1) - WRONG
            else:
                self.led.set_wrong()
                self.show_narrative([
                    "You still\ndidn't make it",
                    "The elevator\ncollapses",
                    "You\nfall into\nthe darkness"
                ])
                if attempts > 0:
                    continue
                else:
                    return "restart_chapter_04"

        # Correct choice - continue
        self.show_narrative([
            "You keep\nsilent",
            "The whisper\nstopped"
        ])

        self.display.show_text("A knocking\nsound came\nfrom the wall")
        time.sleep(2)

        # Double-click button detection with hints
        hint_shown = False

        def hint_callback(elapsed):
            nonlocal hint_shown
            if not hint_shown:
                if self.difficulty == "easy" and elapsed > 5:
                    self.display.show_text("Try double\nclicking\nleft or right button")
                    hint_shown = True
                elif self.difficulty == "medium" and elapsed > 10:
                    self.display.show_text("Try to\nknock back")
                    hint_shown = True

        if not self.inputs.detect_double_click_button(timeout_s=None, hint_callback=hint_callback):
            return self.handle_wrong_choice(["Failed to respond"], "chapter_04")

        # Success
        self.show_narrative([
            "The wall\nopens",
            "A narrow hallway\ndrags you in",
            "And the\nwhisper becomes\nguiding"
        ])
        self.display.show_text("Press button\nto continue")
        self.inputs.wait_for_encoder_press()
        return "chapter_05"


