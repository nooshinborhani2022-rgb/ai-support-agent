# src/logger_utils.py

import json
from datetime import datetime
from src.config import LOG_FILE


def log_interaction(user_message, intents, response, sentiment=None):
    """
    Logs each interaction to a JSONL file.

    Added:
    - sentiment field (optional)
    """

    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_message": user_message,
        "intents": intents,
        "response": response,
    }

    # NEW: add sentiment if available
    if sentiment is not None:
        log_entry["sentiment"] = sentiment

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")