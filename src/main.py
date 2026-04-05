from src.preprocessing import preprocess_text
from src.config import SIMILARITY_THRESHOLD, TOP_K_INTENTS
from src.logger_utils import log_interaction
import json
import random

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


ACTION_PRIORITY = {
    "escalate": 0,
    "answer": 1,
    "clarify": 2
}


def load_faq(file_path="faq.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def tokenize(text):
    return preprocess_text(text).split()


def build_tfidf_index(faq_data):
    corpus = []
    mapping = []

    for idx, item in enumerate(faq_data):
        for example in item.get("examples", []):
            processed = preprocess_text(example)
            if processed:
                corpus.append(processed)
                mapping.append(idx)

    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(corpus)

    return vectorizer, matrix, mapping


def compute_tfidf_score(user_text, vectorizer, matrix, mapping, faq_data):
    processed = preprocess_text(user_text)
    if not processed:
        return {}

    query_vec = vectorizer.transform([processed])
    similarities = cosine_similarity(query_vec, matrix)[0]

    scores = {}

    for sim, idx in zip(similarities, mapping):
        topic = faq_data[idx]["topic"]
        scores[topic] = max(scores.get(topic, 0), sim)

    return scores


def compute_keyword_score(user_text, keywords):
    user_tokens = set(tokenize(user_text))
    score = 0

    for keyword in keywords:
        keyword_tokens = set(tokenize(keyword))
        if keyword_tokens and keyword_tokens.issubset(user_tokens):
            score += 1

    return score


def detect_intents(user_text, faq_data, vectorizer, matrix, mapping):
    results = []

    tfidf_scores = compute_tfidf_score(user_text, vectorizer, matrix, mapping, faq_data)

    for item in faq_data:
        topic = item["topic"]
        action = item["action"]

        tfidf_score = tfidf_scores.get(topic, 0)
        keyword_score = compute_keyword_score(user_text, item.get("keywords", []))

        total_score = (tfidf_score * 2) + (keyword_score * 0.5)

        if total_score > 0:
            results.append({
                "topic": topic,
                "score": round(total_score, 3),
                "action": action,
                "responses": item.get("responses", [])
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def has_any_phrase(user_text, phrases):
    normalized = preprocess_text(user_text)
    return any(preprocess_text(p) in normalized for p in phrases)


def has_account_locked_cue(user_text):
    return has_any_phrase(user_text, [
        "account locked", "locked out", "account blocked", "access denied"
    ])


def has_login_cue(user_text):
    return has_any_phrase(user_text, [
        "login", "log in", "sign in", "cant login", "cannot login"
    ])


def has_payment_cue(user_text):
    return has_any_phrase(user_text, [
        "payment", "card declined", "checkout failed", "transaction failed"
    ])


def has_billing_cue(user_text):
    return has_any_phrase(user_text, [
        "billing", "bill", "charged", "charge", "payment", "invoice"
    ])


def has_delivery_cue(user_text):
    return has_any_phrase(user_text, [
        "delivery", "late", "shipping", "package", "delayed"
    ])


def has_order_cue(user_text):
    return has_any_phrase(user_text, [
        "order", "track order", "where is my order"
    ])


def select_top_intents(ranked_intents, user_text, min_score=0.2, max_intents=2):
    if not ranked_intents:
        return []

    top_score = ranked_intents[0]["score"]

    candidates = [
        i for i in ranked_intents
        if i["score"] >= top_score * 0.75
    ]

    if any(i["topic"] != "general_help" for i in candidates):
        candidates = [i for i in candidates if i["topic"] != "general_help"]

    if has_account_locked_cue(user_text):
        if not any(i["topic"] == "account_locked" for i in candidates):
            for intent in ranked_intents:
                if intent["topic"] == "account_locked":
                    candidates.append(intent)
                    break

    selected = []
    topics = set()

    for intent in candidates:
        t = intent["topic"]

        if t in topics:
            continue

        if t == "charge_explanation" and "double_charge" in topics:
            continue

        if t == "double_charge" and "charge_explanation" in topics:
            selected = [x for x in selected if x["topic"] != "charge_explanation"]

        if t == "login_issue" and "payment_failed" in topics:
            if not has_login_cue(user_text):
                continue

        if t == "payment_failed" and "login_issue" in topics:
            if not has_payment_cue(user_text):
                continue

        if t == "delivery_issue" and "order_status" in topics:
            if not has_delivery_cue(user_text):
                continue

        if t == "order_status" and "delivery_issue" in topics:
            if not has_order_cue(user_text):
                continue

        selected.append(intent)
        topics.add(t)

        if len(selected) >= max_intents:
            break

    return selected


def topic_label(topic):
    return topic.replace("_", " ")


def get_single_response(intent):
    if intent.get("responses"):
        return random.choice(intent["responses"])

    return "I can help with that."


def sort_intents_by_priority(intents):
    return sorted(
        intents,
        key=lambda x: (ACTION_PRIORITY.get(x["action"], 99), -x["score"])
    )


def generate_response(selected_intents):
    if not selected_intents:
        return "I'm sorry, I didn’t understand. Could you rephrase?"

    ordered = sort_intents_by_priority(selected_intents)

    if len(ordered) == 1:
        return get_single_response(ordered[0])

    t1 = topic_label(ordered[0]["topic"])
    t2 = topic_label(ordered[1]["topic"])

    r1 = get_single_response(ordered[0])
    r2 = get_single_response(ordered[1])

    return f"I can help with both your {t1} and {t2}.\n\nFirst, {r1}\n\nAlso, {r2}"


def main():
    faq_data = load_faq()

    vectorizer, matrix, mapping = build_tfidf_index(faq_data)

    print("AI Support Agent is running. Type 'exit' to quit.\n")

    while True:
        user = input("You: ").strip()

        if user.lower() in ["exit", "bye", "quit"]:
            print("Bot: Goodbye!")
            break

        ranked = detect_intents(user, faq_data, vectorizer, matrix, mapping)
        selected = select_top_intents(ranked, user)
        response = generate_response(selected)

        print("Bot:", response)
        log_interaction(user, selected, response)


if __name__ == "__main__":
    main()