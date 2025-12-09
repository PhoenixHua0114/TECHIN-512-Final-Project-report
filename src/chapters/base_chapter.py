# base_chapter.py - Base class for all game chapters

import time
import gc


class BaseChapter:
    """Abstract base class for all chapters"""

    def __init__(self, game):
        """Initialize chapter

        Args:
            game: Reference to Game instance
        """
        self.game = game
        self.display = game.display
        self.inputs = game.inputs
        self.led = game.led
        self.difficulty = game.difficulty

    def run(self):
        """Execute chapter logic - must be implemented by subclasses

        Returns:
            Name of next chapter or "restart_X" to restart a chapter
        """
        raise NotImplementedError("Subclass must implement run()")

    # ========== Helper Methods ==========

    def show_narrative(self, lines):
        """Display narrative lines one at a time, wait for encoder press

        Args:
            lines: List of text strings to display
        """
        for line in lines:
            self.display.show_text(line, centered=True)
            self.inputs.wait_for_encoder_press()
        # Cleanup after displaying all narrative lines
        gc.collect()

    def handle_wrong_choice(self, lines, restart_chapter):
        """Handle wrong choice outcome

        Args:
            lines: Failure text to display
            restart_chapter: Chapter name to restart (e.g., "chapter_01")

        Returns:
            Chapter name to restart
        """
        self.led.set_wrong()
        self.show_narrative(lines)
        gc.collect()  # Cleanup before returning
        return f"restart_{restart_chapter}"

    def handle_correct_choice(self, lines, next_chapter):
        """Handle correct choice outcome

        Args:
            lines: Success text to display
            next_chapter: Name of next chapter

        Returns:
            Next chapter name
        """
        self.led.set_correct()
        self.show_narrative(lines)
        gc.collect()  # Cleanup before returning
        return next_chapter

    def get_retry_count(self):
        """Get retry count based on difficulty

        Returns:
            Number of retry chances (varies by chapter and difficulty)
        """
        # Default retry counts, can be overridden by subclasses
        if self.difficulty == "easy":
            return 2
        elif self.difficulty == "medium":
            return 1
        else:  # hard
            return 1

    def show_hint(self, hints_dict):
        """Show hint based on difficulty

        Args:
            hints_dict: Dict with keys "easy", "medium", "hard"
        """
        hint = hints_dict.get(self.difficulty, "")
        if hint:
            self.display.show_text(hint, centered=True)
            self.inputs.wait_for_encoder_press()
