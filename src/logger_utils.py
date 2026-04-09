import json
from datetime import datetime
from src.config import LOG_FILE


def log_interaction(
    user_message,
    intents,
    response,
    sentiment=None,
    primary_intent=None,
    final_action=None,
    confidence=None,
    top1_score=None,
    top2_score=None,
    score_gap=None,
    routing_reason=None
):
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

    if final_action is not None:
        log_entry["final_action"] = final_action

    if confidence is not None:
        log_entry["confidence"] = confidence

    if top1_score is not None:
        log_entry["top1_score"] = top1_score

    if top2_score is not None:
        log_entry["top2_score"] = top2_score

    if score_gap is not None:
        log_entry["score_gap"] = score_gap

    if routing_reason is not None:
        log_entry["routing_reason"] = routing_reason

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")