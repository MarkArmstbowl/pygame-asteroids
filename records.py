"""Read and save the five highest scores in records.json."""

import json
import os


RECORD_FILE = os.path.join(os.path.dirname(__file__), "records.json")
MAX_RECORDS = 5


def load_scores():
    """Read saved scores, or start with an empty list."""
    try:
        with open(RECORD_FILE, encoding="utf-8") as record_file:
            scores = json.load(record_file)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        # Start with no scores if the file is missing or cannot be read.
        return []

    if not isinstance(scores, list):
        return []

    # Keep only whole numbers that are zero or higher.
    valid_scores = []
    for score in scores:
        if isinstance(score, int) and score >= 0:
            valid_scores.append(score)

    # Put the highest scores first and keep only five.
    valid_scores.sort(reverse=True)
    return valid_scores[:MAX_RECORDS]


def save_score(new_score):
    """Add a score, save the best five, and return the list."""
    scores = load_scores()

    if isinstance(new_score, int) and new_score >= 0:
        scores.append(new_score)
        scores.sort(reverse=True)
        scores = scores[:MAX_RECORDS]

        try:
            # Writing creates records.json the first time a score is saved.
            with open(RECORD_FILE, "w", encoding="utf-8") as record_file:
                json.dump(scores, record_file, indent=2)
        except OSError:
            # Keep playing if the folder does not allow saving the file.
            pass

    return scores
