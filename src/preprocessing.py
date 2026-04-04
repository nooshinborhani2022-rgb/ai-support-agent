import re


CONTRACTIONS = {
    "can't": "cannot",
    "won't": "will not",
    "don't": "do not",
    "doesn't": "does not",
    "didn't": "did not",
    "i'm": "i am",
    "it's": "it is",
    "you're": "you are",
    "i've": "i have",
    "we're": "we are",
    "they're": "they are",
}


STOPWORDS = {
    "i", "me", "my", "you", "your", "the", "a", "an", "is", "are", "am",
    "to", "for", "of", "and", "or", "in", "on", "at", "it", "this", "that",
    "be", "can", "cant", "cannot", "do", "did", "was", "were", "with",
    "working"
}


def expand_contractions(text):
    text = text.lower()

    for contraction, expanded in CONTRACTIONS.items():
        text = text.replace(contraction, expanded)

    return text


def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    words = text.split()
    words = [w for w in words if w not in STOPWORDS]
    return " ".join(words)