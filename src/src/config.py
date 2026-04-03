# src/config.py

# Thresholds for intent detection
SIMILARITY_THRESHOLD = 0.3

# Number of top intents to consider
TOP_K_INTENTS = 2

# Action priority
ACTION_PRIORITY = {
    "escalate": 3,
    "answer": 2,
    "clarify": 1,
}

# Multi-intent settings
ENABLE_MULTI_INTENT = True

# Logging settings
LOG_FILE = "chat_log.jsonl"