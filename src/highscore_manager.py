# highscore_manager.py - High score tracking and persistence

import gc


class HighScoreManager:
    """Manages high scores with persistent storage to flash memory"""

    def __init__(self, filename="highscores.txt"):
        """Initialize high score manager

        Args:
            filename: Name of file to store high scores
        """
        self.filename = filename
        self.scores = []  # List of (initials, time_seconds) tuples
        self.load_scores()

    def load_scores(self):
        """Load high scores from file

        File format: Each line is "INITIALS,TIME_SECONDS"
        Example: AAA,120
        """
        try:
            with open(self.filename, "r") as f:
                self.scores = []
                for line in f:
                    line = line.strip()
                    if line:  # Skip empty lines
                        try:
                            initials, time_str = line.split(",")
                            self.scores.append((initials, int(time_str)))
                        except:
                            continue  # Skip malformed lines
            print(f"Loaded {len(self.scores)} high scores")
        except OSError:
            # File doesn't exist yet - start fresh
            self.scores = []
            print("No high scores file found - starting fresh")
        except Exception as e:
            print(f"Error loading high scores: {e}")
            self.scores = []

        gc.collect()  # Cleanup after file I/O

    def save_scores(self):
        """Save high scores to file

        Writes all scores to file, one per line
        """
        try:
            with open(self.filename, "w") as f:
                for initials, time_seconds in self.scores:
                    f.write(f"{initials},{time_seconds}\n")
            print(f"Saved {len(self.scores)} high scores")
        except Exception as e:
            print(f"Error saving high scores: {e}")

        gc.collect()  # Cleanup after file I/O

    def is_high_score(self, time_seconds):
        """Check if time qualifies as a high score

        Args:
            time_seconds: Completion time in seconds

        Returns:
            True if time is in top 3, False otherwise
        """
        # If we have fewer than 3 scores, it's automatically a high score
        if len(self.scores) < 3:
            return True

        # Check if time beats the slowest high score
        return time_seconds < self.scores[-1][1]

    def add_score(self, initials, time_seconds):
        """Add new score and keep top 3

        Args:
            initials: 3-character player initials
            time_seconds: Completion time in seconds
        """
        # Add new score
        self.scores.append((initials, time_seconds))

        # Sort by time (fastest first)
        self.scores.sort(key=lambda x: x[1])

        # Keep only top 3
        self.scores = self.scores[:3]

        # Save to file
        self.save_scores()

        gc.collect()  # Cleanup after modifications

    def get_scores(self):
        """Get list of high scores

        Returns:
            List of (initials, time_seconds) tuples, sorted fastest first
        """
        return self.scores.copy()

    def format_time(self, seconds):
        """Format time in seconds to MM:SS format

        Args:
            seconds: Time in seconds

        Returns:
            Formatted string like "12:34"
        """
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def get_rank(self, time_seconds):
        """Get what rank a time would achieve

        Args:
            time_seconds: Completion time in seconds

        Returns:
            Rank (1-3) or None if not a high score
        """
        if not self.is_high_score(time_seconds):
            return None

        # Count how many scores are faster
        rank = 1
        for _, score_time in self.scores:
            if score_time < time_seconds:
                rank += 1

        return rank
