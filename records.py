"""Load and save the local Asteroids high-score list."""

import json
import os


RECORD_FILE = os.path.join(os.path.dirname(__file__), "records.json")
MAX_RECORDS = 5


def load_scores():
    """Return saved scores, or an empty list when no records exist."""
    try:
        with open(RECORD_FILE, encoding="utf-8") as record_file:
            scores = json.load(record_file)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []

    if not isinstance(scores, list):
        return []

    valid_scores = []
    for score in scores:
        if isinstance(score, int) and score >= 0:
            valid_scores.append(score)

    valid_scores.sort(reverse=True)
    return valid_scores[:MAX_RECORDS]


def save_score(new_score):
    """Add one score and return the updated top-five list."""
    scores = load_scores()

    if isinstance(new_score, int) and new_score >= 0:
        scores.append(new_score)
        scores.sort(reverse=True)
        scores = scores[:MAX_RECORDS]

        try:
            with open(RECORD_FILE, "w", encoding="utf-8") as record_file:
                json.dump(scores, record_file, indent=2)
        except OSError:
            # The game can continue even if local records cannot be saved.
            pass

    return scores
