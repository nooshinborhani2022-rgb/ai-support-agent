import string

CONTRACTIONS = {
    "can't": "cannot",
    "won't": "will not",
    "n't": " not",
    "i'm": "i am",
    "it's": "it is",
    "he's": "he is",
    "she's": "she is",
    "that's": "that is",
    "what's": "what is",
    "there's": "there is",
    "i've": "i have",
    "we've": "we have",
    "they've": "they have",
    "i'll": "i will",
    "you'll": "you will",
    "they'll": "they will",
    "isn't": "is not",
    "aren't": "are not",
    "wasn't": "was not",
    "weren't": "were not",
    "don't": "do not",
    "doesn't": "does not",
    "didn't": "did not",
}


STOPWORDS = {
    "i", "me", "my", "you", "your", "the", "a", "an", "is", "are", "am",
    "to", "for", "of", "and", "or", "in", "on", "at", "it", "this", "that",
    "be", "can", "cannot", "do", "did", "was", "were", "with",
    "working"
}


def expand_contractions(text):
    text = text.lower()

    for contraction, expanded in CONTRACTIONS.items():
        text = text.replace(contraction, expanded)

    return text


def preprocess_text(text):
    text = expand_contractions(text)

    text = text.translate(str.maketrans("", "", string.punctuation))

    words = text.split()

    words = [w for w in words if w not in STOPWORDS]

    return " ".join(words)