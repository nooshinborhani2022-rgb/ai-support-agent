# src/sentiment.py

from src.preprocessing import expand_contractions


SENTIMENT_KEYWORDS = {
    "angry": [
        "angry",
        "mad",
        "furious",
        "ridiculous",
        "terrible",
        "awful",
        "horrible",
        "unacceptable",
        "stupid",
        "useless",
        "scam",
        "hate",
    ],
    "frustrated": [
        "not working",
        "problem",
        "issue",
        "broken",
        "error",
        "failed",
        "still not working",
        "does not work",
        "cannot",
        "cannot login",
        "cannot log in",
        "can't log in",
        "cant log in",
        "can't login",
        "cant login",
        "annoying",
        "frustrating",
        "confusing",
        "stuck",
    ],
    "urgent": [
        "urgent",
        "asap",
        "immediately",
        "right now",
        "as soon as possible",
        "emergency",
        "now",
    ],
}


def normalize_for_sentiment(text):
    text = expand_contractions(text.lower())
    return " ".join(text.split())


def detect_sentiment(user_text):
    normalized = normalize_for_sentiment(user_text)

    scores = {
        "angry": 0,
        "frustrated": 0,
        "urgent": 0,
    }

    matched_keywords = {
        "angry": [],
        "frustrated": [],
        "urgent": [],
    }

    for label, keywords in SENTIMENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in normalized:
                scores[label] += 1
                matched_keywords[label].append(keyword)

    if "!" in user_text:
        scores["angry"] += 1

    if scores["urgent"] > 0:
        sentiment = "urgent"
    elif scores["angry"] > 0:
        sentiment = "angry"
    elif scores["frustrated"] > 0:
        sentiment = "frustrated"
    else:
        sentiment = "neutral"

    return {
        "label": sentiment,
        "scores": scores,
        "matched_keywords": matched_keywords,
    }


# NEW: helper function
def get_sentiment_label(user_text):
    """
    Returns only the sentiment label (simple interface).
    """
    return detect_sentiment(user_text)["label"]


def get_sentiment_prefix(sentiment_label):
    prefixes = {
        "neutral": "",
        "frustrated": "I understand how frustrating this must be. ",
        "angry": "I'm sorry you're dealing with this experience. ",
        "urgent": "I understand this is urgent, and I'll help as quickly as possible. ",
    }

    return prefixes.get(sentiment_label, "")