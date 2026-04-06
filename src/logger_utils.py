import json
from datetime import datetime
from src.config import LOG_FILE


def log_interaction(user_message, intents, response, sentiment=None, primary_intent=None):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_message": user_message,
        "intents": intents,
        "response": response,
    }

    if sentiment is not None:
        log_entry["sentiment"] = sentiment

    if primary_intent is not None:
        log_entry["primary_intent"] = primary_intent

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")