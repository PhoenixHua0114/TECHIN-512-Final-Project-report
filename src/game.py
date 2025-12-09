# game.py - Main game orchestrator

import time
import gc  # Garbage collector to free memory
from direction_detection_v2 import get_i2c
from display_manager import DisplayManager
from input_manager import InputManager
from led_manager import LEDManager
from highscore_manager import HighScoreManager


class Game:
    """Main game orchestrator - manages game flow and chapter transitions"""

    def __init__(self):
        """Initialize game and all managers"""
        # Initialize I2C bus (shared by display and accelerometer)
        try:
            self.i2c = get_i2c()
        except Exception as e:
            print("Failed to initialize shared I2C:", e)
            raise

        # Initialize managers (pass shared i2c to those that need it)
        self.led = LEDManager()
        self.display = DisplayManager(self.i2c)
        self.inputs = InputManager(self.i2c)
        self.highscore_manager = HighScoreManager()

        # Game state
        self.difficulty = None
        self.current_chapter = None
        self.start_time = None  # Track game start time

        # Chapter registry
        self.chapters = {}

        # Initial aggressive cleanup
        gc.collect()
        gc.collect()
        gc.collect()

    def register_chapters(self):
        """Register chapter names (lazy loading - import only when needed)"""
        # Don't import all chapters at once - save memory
        # Chapters will be imported dynamically in run_chapter()
        self.chapters = {
            "chapter_01": "chapters.chapter_01.Chapter01",
            "chapter_02": "chapters.chapter_02.Chapter02",
            "chapter_03": "chapters.chapter_03.Chapter03",
            "chapter_04": "chapters.chapter_04.Chapter04",
            "chapter_05": "chapters.chapter_05.Chapter05",
            "chapter_06": "chapters.chapter_06.Chapter06",
            "chapter_07": "chapters.chapter_07.Chapter07",
            "chapter_08": "chapters.chapter_08.Chapter08",
            "chapter_09": "chapters.chapter_09.Chapter09",
            "chapter_10": "chapters.chapter_10.Chapter10",
        }

    def run(self):
        """Main game loop"""
        self.led.set_boot()

        # Register all chapters
        self.register_chapters()

        # Show opening screen only once at the start
        self.show_opening()
        gc.collect()  # Cleanup after opening screen

        # Main game loop - starts with difficulty selection
        while True:
            # Select difficulty
            self.difficulty = self.select_difficulty()
            gc.collect()  # Cleanup after difficulty selection

            # Start from chapter 1
            next_chapter = "chapter_01"
            self.start_time = None  # Will be set when chapter 1 starts

            # Play through chapters
            while next_chapter:
                # Track start time when chapter 1 begins
                if next_chapter == "chapter_01" and self.start_time is None:
                    self.start_time = time.monotonic()
                    print("Game timer started")

                # Handle restart commands
                if next_chapter.startswith("restart_"):
                    chapter_name = next_chapter.replace("restart_", "")
                    next_chapter = chapter_name
                    # Aggressive cleanup on restart
                    gc.collect()
                    gc.collect()

                # Run chapter
                result = self.run_chapter(next_chapter)

                # Centralized LED handling based on chapter result
                if result is not None:
                    if result.startswith("restart_"):
                        # Wrong choice - show red LED
                        self.led.set_wrong()
                    else:
                        # Correct choice - show blue LED
                        self.led.set_correct()

                next_chapter = result

                # If we reached the end (Chapter 10 returned None)
                if next_chapter is None:
                    break

            # Calculate completion time
            completion_time = int(time.monotonic() - self.start_time)
            print(f"Game completed in {completion_time} seconds")

            # Check if high score and handle accordingly
            self.handle_game_completion(completion_time)

            # After game ends, prompt for restart
            # Final cleanup before restart prompt
            gc.collect()
            gc.collect()
            gc.collect()
            if not self.prompt_restart():
                break
            # If restarting, loop back to difficulty selection

        # Game over
        self.display.show_text("Thank you for playing", centered=True)
        self.led.set_off()

    def show_opening(self):
        """Show opening screen with cycling text"""
        opening_lines = [
            "You wake up\nin the fog...",
            "The past is\nnever dead",
            "[Press encoder\nto continue]"
        ]

        line_index = 0
        last_update = time.monotonic()

        while True:
            # Cycle through lines every 3 seconds
            if time.monotonic() - last_update > 3:
                line_index = (line_index + 1) % len(opening_lines)
                last_update = time.monotonic()

            self.display.show_text(opening_lines[line_index], centered=True)

            # Check for encoder press
            self.inputs.update()
            if self.inputs.encoder_button_pressed():
                return

            time.sleep(0.05)

    def select_difficulty(self):
        """Let player select difficulty

        Returns:
            Difficulty string: "easy", "medium", or "hard"
        """
        choices = ["Easy", "Medium", "Hard"]

        # No timeout for difficulty selection
        selected_index = 0
        last_encoder_pos = self.inputs.get_encoder_position()
        self.display.show_text(f"Choose difficulty\n{choices[0]}", centered=True)

        while True:
            self.inputs.update()

            # Check for rotary encoder rotation
            current_encoder_pos = self.inputs.get_encoder_position()
            if current_encoder_pos != last_encoder_pos:
                print(f"Encoder position changed: {last_encoder_pos} -> {current_encoder_pos}")
                if current_encoder_pos > last_encoder_pos:
                    # Clockwise rotation
                    selected_index = (selected_index + 1) % len(choices)
                    print(f"Rotated clockwise, selected: {choices[selected_index]}")
                else:
                    # Counter-clockwise rotation
                    selected_index = (selected_index - 1) % len(choices)
                    print(f"Rotated counter-clockwise, selected: {choices[selected_index]}")
                self.display.show_text(f"Choose difficulty\n{choices[selected_index]}", centered=True)
                last_encoder_pos = current_encoder_pos

            # Also keep left/right button support
            if self.inputs.left_button_pressed():
                selected_index = (selected_index - 1) % len(choices)
                self.display.show_text(f"Choose difficulty\n{choices[selected_index]}", centered=True)

            if self.inputs.right_button_pressed():
                selected_index = (selected_index + 1) % len(choices)
                self.display.show_text(f"Choose difficulty\n{choices[selected_index]}", centered=True)

            if self.inputs.encoder_button_pressed():
                print(f"Encoder button pressed, selected difficulty: {choices[selected_index].lower()}")
                return choices[selected_index].lower()

            time.sleep(0.01)

    def run_chapter(self, chapter_name):
        """Run a specific chapter

        Args:
            chapter_name: Name of chapter to run (e.g., "chapter_01")

        Returns:
            Next chapter name or None if game complete
        """
        if chapter_name not in self.chapters:
            print(f"Error: Chapter {chapter_name} not found!")
            return None

        # AGGRESSIVE garbage collection before loading new chapter
        # Call 3 times to ensure all circular references are cleaned
        gc.collect()
        gc.collect()
        gc.collect()

        # Lazy import - only load the chapter we need
        module_path = self.chapters[chapter_name]
        module_name, class_name = module_path.rsplit(".", 1)

        # Import the module
        module = __import__(module_name, None, None, [class_name])
        chapter_class = getattr(module, class_name)

        # Instantiate and run chapter
        chapter = chapter_class(self)
        result = chapter.run()

        # Clean up after chapter - be very aggressive
        del chapter
        del chapter_class

        # Remove module from sys.modules to fully unload it
        import sys
        if module_name in sys.modules:
            del sys.modules[module_name]

        del module

        # AGGRESSIVE garbage collection after chapter cleanup
        # Call 3 times to ensure all circular references are cleaned
        gc.collect()
        gc.collect()
        gc.collect()

        return result

    def handle_game_completion(self, completion_time):
        """Handle game completion - check high score and display results

        Args:
            completion_time: Time in seconds to complete the game
        """
        # Show completion message
        time_str = self.highscore_manager.format_time(completion_time)
        self.display.show_text(f"Game Complete!\nTime: {time_str}", centered=True)
        time.sleep(2)

        # Check if high score
        if self.highscore_manager.is_high_score(completion_time):
            rank = self.highscore_manager.get_rank(completion_time)

            # Show high score achievement
            self.display.show_text(f"NEW HIGH SCORE!\nRank #{rank}", centered=True)
            time.sleep(2)

            # Enter initials
            initials = self.enter_initials()

            # Save high score
            self.highscore_manager.add_score(initials, completion_time)
            print(f"High score saved: {initials} - {completion_time}s")

        # Display high score board
        self.show_high_scores()

        gc.collect()  # Cleanup after high score handling

    def enter_initials(self):
        """Let player enter 3 initials using rotary encoder and push buttons

        Controls:
        - Rotary encoder: Change letter at current position
        - Left/Right buttons: Switch between initial positions
        - Encoder button: Confirm and finish

        Returns:
            3-character string of initials
        """
        initials = ["A", "A", "A"]  # Default initials
        current_position = 0  # Which letter we're editing (0, 1, or 2)
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        last_encoder_pos = self.inputs.get_encoder_position()
        needs_update = True  # Flag to control when to update display

        while True:
            # Only update display when there's a change
            if needs_update:
                # Display current initials with cursor
                display_str = "Enter Initials:\n"
                for i, letter in enumerate(initials):
                    if i == current_position:
                        display_str += f"[{letter}]"  # Show cursor
                    else:
                        display_str += f" {letter} "

                self.display.show_text(display_str, centered=True)
                needs_update = False

            self.inputs.update()

            # Rotary encoder changes letter at current position
            current_encoder_pos = self.inputs.get_encoder_position()
            if current_encoder_pos != last_encoder_pos:
                if current_encoder_pos > last_encoder_pos:
                    # Clockwise - next letter
                    current_index = letters.index(initials[current_position])
                    initials[current_position] = letters[(current_index + 1) % len(letters)]
                else:
                    # Counter-clockwise - previous letter
                    current_index = letters.index(initials[current_position])
                    initials[current_position] = letters[(current_index - 1) % len(letters)]
                last_encoder_pos = current_encoder_pos
                needs_update = True

            # Left button: Move to previous position
            if self.inputs.left_button_pressed():
                current_position = (current_position - 1) % 3
                needs_update = True
                time.sleep(0.15)  # Debounce

            # Right button: Move to next position
            if self.inputs.right_button_pressed():
                current_position = (current_position + 1) % 3
                needs_update = True
                time.sleep(0.15)  # Debounce

            # Encoder button confirms final initials
            if self.inputs.encoder_button_pressed():
                # Confirm and exit
                break

            time.sleep(0.01)

        result = "".join(initials)
        print(f"Initials entered: {result}")
        gc.collect()
        return result

    def show_high_scores(self):
        """Display high score board"""
        scores = self.highscore_manager.get_scores()

        if not scores:
            # No high scores yet
            self.display.show_text("HIGH SCORES\n\nNo scores yet!", centered=True)
            self.inputs.wait_for_encoder_press()
            return

        # Display each score
        for i, (initials, time_seconds) in enumerate(scores):
            time_str = self.highscore_manager.format_time(time_seconds)
            rank = i + 1

            display_text = f"HIGH SCORES\n\n#{rank} {initials}\n{time_str}"
            self.display.show_text(display_text, centered=True)

            # Show for 3 seconds or until button press
            start = time.monotonic()
            while time.monotonic() - start < 3:
                self.inputs.update()
                if self.inputs.encoder_button_pressed():
                    break
                time.sleep(0.01)

        gc.collect()

    def prompt_restart(self):
        """Prompt player to restart game

        Returns:
            True to restart, False to quit
        """
        choices = ["Yes", "No"]
        selected_index = 0

        self.display.show_text(f"Do you want\nto restart\n{choices[0]}", centered=True)

        while True:
            self.inputs.update()

            if self.inputs.left_button_pressed():
                selected_index = (selected_index - 1) % len(choices)
                self.display.show_text(f"Do you want\nto restart\n{choices[selected_index]}", centered=True)

            if self.inputs.right_button_pressed():
                selected_index = (selected_index + 1) % len(choices)
                self.display.show_text(f"Do you want\nto restart\n{choices[selected_index]}", centered=True)

            if self.inputs.encoder_button_pressed():
                return selected_index == 0  # True if "Yes"

            time.sleep(0.01)