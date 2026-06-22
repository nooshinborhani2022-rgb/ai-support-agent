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


NEGATION_WORDS = ["not", "no", "never", "didn't", "don't", "wasn't", "isn't", "haven't", "can't", "cannot"]

def contains_negation(text):
    """
    Detects if a negation word appears before a key term.
    Example: 'I was NOT charged twice' → True
    """
    text_lower = text.lower()
    words = text_lower.split()
    
    for i, word in enumerate(words):
        clean_word = word.strip(".,!?")
        if clean_word in NEGATION_WORDS:
            return True
    return False


def remove_negated_terms(text, terms):
    """
    Removes terms from a list if they appear after a negation in the text.
    Example: text='I was not charged twice', terms=['double_charge'] → []
    """
    if not contains_negation(text):
        return terms
    
    text_lower = text.lower()
    
    NEGATION_MAP = {
        "double_charge": ["charged twice", "double charge", "duplicate charge"],
        "fraud_report": ["not fraud", "not a scam", "not stolen"],
        "login_issue": ["can login", "i can log in", "not locked"],
        "payment_failed": ["payment worked", "payment went through"],
    }
    
    filtered = []
    for term in terms:
        negated = False
        if term in NEGATION_MAP:
            for phrase in NEGATION_MAP[term]:
                if phrase in text_lower:
                    negated = True
                    break
        if not negated:
            filtered.append(term)
    
    return filtered