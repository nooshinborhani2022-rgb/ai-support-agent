# src/context_detector.py

TEMPORAL_SIGNALS = [
    "since yesterday", "since last week", "since this morning",
    "for two days", "for a week", "started yesterday",
    "from yesterday", "since monday", "since today"
]

SEVERITY_SIGNALS = [
    "getting worse", "more painful", "still not working",
    "still happening", "keeps happening", "not resolved",
    "same problem", "again", "still"
]

CONFIRMATION_SIGNALS = [
    "yes", "yeah", "correct", "exactly", "that's right",
    "right", "yep", "confirmed", "that is correct"
]

DENIAL_SIGNALS = [
    "no", "nope", "that's wrong", "not exactly",
    "not quite", "incorrect", "not right"
]


def detect_context_signals(user_text):
    """
    Detects contextual signals in user message:
    - temporal: time references like 'since yesterday'
    - severity: escalation signals like 'getting worse'
    - confirmation: user confirming system understanding
    - denial: user denying system understanding
    """
    text_lower = user_text.lower()

    signals = {
        "temporal": False,
        "severity": False,
        "confirmation": False,
        "denial": False,
        "detected_phrases": []
    }

    for phrase in TEMPORAL_SIGNALS:
        if phrase in text_lower:
            signals["temporal"] = True
            signals["detected_phrases"].append(phrase)

    for phrase in SEVERITY_SIGNALS:
        if phrase in text_lower:
            signals["severity"] = True
            signals["detected_phrases"].append(phrase)

    for phrase in CONFIRMATION_SIGNALS:
        if phrase in text_lower.split():
            signals["confirmation"] = True
            signals["detected_phrases"].append(phrase)

    for phrase in DENIAL_SIGNALS:
        if phrase in text_lower.split():
            signals["denial"] = True
            signals["detected_phrases"].append(phrase)

    return signals


def enrich_with_context(user_text, conversation_state):
    """
    Enriches user message with context from conversation history.
    If message is short and ambiguous, adds context from last topic.
    """
    signals = detect_context_signals(user_text)
    last_topics = conversation_state.get("last_topics", [])
    last_message = conversation_state.get("last_user_message", "")

    enriched = {
        "original_text": user_text,
        "enriched_text": user_text,
        "context_signals": signals,
        "context_applied": False
    }

   
    if len(user_text.split()) <= 4 and last_topics:
        enriched["enriched_text"] = f"{last_message} {user_text}"
        enriched["context_applied"] = True

    
    if signals["severity"] and last_topics:
        enriched["severity_escalation"] = True

    return enriched