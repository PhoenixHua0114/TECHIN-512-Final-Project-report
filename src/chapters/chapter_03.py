# chapter_03.py - Toy box?

import time
from chapters.base_chapter import BaseChapter


class Chapter03(BaseChapter):
    """Chapter 3: Tilt left, hold buttons, and choice"""

    def run(self):
        # Narrative
        self.show_narrative([
            "Chapter 3\nToy box?",
            "It seems\nliketh\nsame room",
            "Wait...There's\nsomething\ndifferent"
        ])

        self.show_narrative([
            "Everything\nin the room slowly\nsliding to the right"
        ])

        # Show "You need to do something" without waiting for button press
        self.display.show_text("You need\nto do\nsomething", centered=True)
        time.sleep(1.5)

        # Tilt left detection with countdown (starts immediately)
        timeout_map = {"easy": 10, "medium": 6, "hard": 3}
        timeout = timeout_map[self.difficulty]

        if not self.inputs.detect_tilt_left(timeout, display=self.display, show_countdown=True):
            restart_target = "chapter_02" if self.difficulty == "hard" else "chapter_03"
            return self.handle_wrong_choice([
                "You let\nyourself\nfalling",
                "Crushing on\nthe wall\nof the room",
                "Why are\nyou doing\nthis again..."
            ], restart_target)

        # Success - reached bookshelf
        self.show_narrative([
            "You keep\nrunning to\nthe left",
            "Reached\nthe end\nat the room",
            "You are\ntrying to grab\nthe bookshelf"
        ])

        # Hold both buttons
        self.display.show_text("Press\nand hold\nboth buttons")
        timeout_map = {"easy": 5, "medium": 4, "hard": 3}

        start_time = time.monotonic()
        while time.monotonic() - start_time < timeout_map[self.difficulty]:
            self.inputs.update()
            if not self.inputs.left_button.value and not self.inputs.right_button.value:
                # Both buttons pressed, now hold for 5 seconds
                if self.inputs.both_buttons_held(5):
                    break
            time.sleep(0.01)
        else:
            restart_target = "chapter_02" if self.difficulty == "hard" else "chapter_03"
            return self.handle_wrong_choice([
                "You almost\nget to\nthe shelf",
                "The room\nsuddenly\nstarts shaking",
                "You slipped",
                "Crushing on\nthe wall\nof the room"
            ], restart_target)

        # Falling sequence
        self.show_narrative([
            "You hold\ntightly to\nthe bookshelf",
            "The room\nsuddenly\nstarts shaking",
            "A large\ncrack appeared\non the floor",
            "You hear\nthe roar of\nwater",
            "Pouring\nthrough\nthe crack",
            "Then you\nheard a\nfamiliar voice",
            "screaming",
            "But you\nalmost run out\nof strength"
        ])

        # Show hint
        hints = {
            "easy": "Embrace\nthe darkness",
            "medium": "Maybe\nit's time\nto let go?",
            "hard": ""
        }
        self.show_hint(hints)

        self.display.show_text("What should\nyou do", centered=True)
        self.inputs.wait_for_encoder_press()

        # Final choice (no timeout)
        choices = ["Let go", "Try your\nbest to\nhold"]
        selected = 0
        self.display.show_text(choices[selected], centered=True)

        while True:
            self.inputs.update()
            if self.inputs.left_button_pressed():
                selected = (selected - 1) % len(choices)
                self.display.show_text(choices[selected], centered=True)
            if self.inputs.right_button_pressed():
                selected = (selected + 1) % len(choices)
                self.display.show_text(choices[selected], centered=True)
            if self.inputs.encoder_button_pressed():
                break
            time.sleep(0.01)

        if selected == 0:  # Let go - CORRECT
            self.show_narrative([
                "You fall\ninto\nthe abyss",
                "Let the\nwaterflow\ntake you",
                "Closer to\nthe voice",
                "This time\nyou hear\nit clearly",
                "It's screaming\nhelp"
            ])
            self.display.show_text("Press button\nto continue")
            self.inputs.wait_for_encoder_press()
            return "chapter_04"
        else:  # Hold - WRONG
            return self.handle_wrong_choice([
                "You tried\nto stay\nstill",
                "The roof\nthen\ncollapses",
                "You are hurt\nby a falling\nroom beam",
                "And fainted\nbefore falling\nto the ground"
            ], "chapter_03")
