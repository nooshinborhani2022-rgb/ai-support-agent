# src/logger_utils.py

import json
from datetime import datetime, timezone


def log_interaction(user_message, intents, response, file_path="chat_log.jsonl"):
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_message": user_message,
        "intents": intents,
        "response": response
    }

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")