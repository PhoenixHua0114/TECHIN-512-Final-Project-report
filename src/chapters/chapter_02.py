# chapter_02.py - Toy box

import time
from chapters.base_chapter import BaseChapter


class Chapter02(BaseChapter):
    """Chapter 2: Movement detection and album choice"""

    def run(self):
        # Narrative
        self.show_narrative([
            "Chapter 2\nToy box",
            "You are\nstanding\nin a room"
        ])

        # Show initial instruction (not in narrative, so no button wait)
        self.display.show_text("Please walk around...", centered=True)

        # Movement detection with hints
        hint_shown = False
        hint_delay = 5 if self.difficulty == "easy" else 10 if self.difficulty == "medium" else 999

        def hint_callback(elapsed):
            nonlocal hint_shown
            if not hint_shown and elapsed > hint_delay:
                self.display.show_text("Try moving\nthe box in\ndifferent directions", centered=True)
                hint_shown = True
        # Detect X and Y movement (pass hint callback and display for real-time feedback)
        if not self.inputs.detect_movement(timeout_s=30, hint_callback=hint_callback, require_axes=['x', 'y'], display=self.display):
            return self.handle_wrong_choice([
                "You stood still\ntoo long",
                "The room\ncollapsed"
            ], "chapter_02")

        # Album discovery
        self.show_narrative([
            "You saw an old\nphoto album",
            "The cover\nis shattered\ninto pieces"
        ])

        # Choice with timeout
        choices = ["Take the cover off", "Ignore it and leave", "Open it and take\na look"]

        def display_callback(choice_text, countdown):
            self.display.show_choice(choice_text, f"You have {countdown} s left")

        selected = self.inputs.navigate_choice(choices, 10, display_callback)

        if selected == 0:  # Take cover - WRONG
            return self.handle_wrong_choice([
                "You try to\ntear off\nthe paper",
                "Sharp edge\ncuts\nyour finger",
                "And you\nfade into\nwhite mist..."
            ], "chapter_02")

        elif selected == 1:  # Ignore - WRONG
            return self.handle_wrong_choice([
                "You walk away\nto the door",
                "A toy car rolls to\nyour feet on its own",
                "Like\nreminding you\nof something",
                "You ignore it",
                "The room\nsuddenly\ncollapsed",
                "You are\nswallowed by\nthe water below"
            ], "chapter_02")

        elif selected == 2:  # Open - CORRECT
            self.show_narrative([
                "You keep\nturning\nthe pages",
                "The face\nin all photos\n...",
                "Seems to\nbe the\nsame person",
                "You cannot\nremember",
                "When\nyou open\nthe last page",
                "The room\nstarts shaking",
                "Then you\nfainted"
            ])
            self.display.show_text("Press button\nto continue")
            self.inputs.wait_for_encoder_press()
            return "chapter_03"

        else:  # Timeout
            return self.handle_wrong_choice([
                "Why\nare you\nignoring it",
                "Again\nand again",
                "The room\nsuddenly\ncollapsed",
                "You are\nswallowed by\nthe water deep below"
            ], "chapter_02")
