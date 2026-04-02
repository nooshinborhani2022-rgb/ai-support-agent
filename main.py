import json
import random
import string
from datetime import datetime, timezone


STOPWORDS = {
    "i", "me", "my", "you", "your", "the", "a", "an", "is", "are", "am",
    "to", "for", "of", "and", "or", "in", "on", "at", "it", "this", "that",
    "be", "can", "cant", "cannot", "do", "did", "was", "were", "with",
    "working"
}


ACTION_PRIORITY = {
    "escalate": 0,
    "answer": 1,
    "clarify": 2
}


def load_faq(file_path="faq.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def preprocess_text(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    words = text.split()
    words = [w for w in words if w not in STOPWORDS]
    return " ".join(words)


def tokenize(text):
    return preprocess_text(text).split()


def compute_keyword_score(user_text, keywords):
    user_tokens = set(tokenize(user_text))
    score = 0

    for keyword in keywords:
        keyword_tokens = set(tokenize(keyword))
        if keyword_tokens and keyword_tokens.issubset(user_tokens):
            score += 1

    return score


def compute_example_score(user_text, examples):
    user_tokens = set(tokenize(user_text))
    best_score = 0

    for example in examples:
        example_tokens = set(tokenize(example))
        if not example_tokens:
            continue

        common = user_tokens.intersection(example_tokens)
        score = len(common) / len(example_tokens)

        if score > best_score:
            best_score = score

    return best_score


def detect_intents(user_text, faq_data):
    results = []

    for item in faq_data:
        topic = item["topic"]
        action = item["action"]

        example_score = compute_example_score(user_text, item.get("examples", []))
        keyword_score = compute_keyword_score(user_text, item.get("keywords", []))
        total_score = (example_score * 2) + keyword_score

        if total_score > 0:
            results.append({
                "topic": topic,
                "score": round(total_score, 2),
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
        "account locked",
        "locked out",
        "account blocked",
        "access denied",
        "blocked account"
    ])


def has_login_cue(user_text):
    return has_any_phrase(user_text, [
        "login",
        "log in",
        "sign in",
        "cant login",
        "cannot login",
        "cant log in",
        "cannot log in",
        "access account"
    ])


def has_payment_cue(user_text):
    return has_any_phrase(user_text, [
        "payment",
        "card declined",
        "checkout failed",
        "transaction failed",
        "payment failed"
    ])


def has_delivery_cue(user_text):
    return has_any_phrase(user_text, [
        "delivery",
        "late",
        "shipping",
        "package",
        "delayed"
    ])


def has_order_cue(user_text):
    return has_any_phrase(user_text, [
        "order",
        "track order",
        "where is my order",
        "order status",
        "track package"
    ])


def select_top_intents(ranked_intents, user_text, min_score=1.0, max_intents=2):
    candidates = [i for i in ranked_intents if i["score"] >= min_score]

    if not candidates:
        return []

    top_score = candidates[0]["score"]

    candidates = [
        i for i in candidates
        if i["score"] >= top_score * 0.75
    ]

    if any(i["topic"] != "general_help" for i in candidates):
        candidates = [i for i in candidates if i["topic"] != "general_help"]

    # 🔥 FIX اصلی همینجاست
    # اگر access denied یا lock دیده شد → account_locked را force اضافه کن
    if has_account_locked_cue(user_text):
        if not any(i["topic"] == "account_locked" for i in candidates):
            for intent in ranked_intents:
                if intent["topic"] == "account_locked":
                    candidates.append(intent)
                    break

    selected = []
    selected_topics = set()

    for intent in candidates:
        topic = intent["topic"]

        if topic in selected_topics:
            continue

        if topic == "charge_explanation" and "double_charge" in selected_topics:
            continue

        if topic == "double_charge" and "charge_explanation" in selected_topics:
            selected = [x for x in selected if x["topic"] != "charge_explanation"]
            selected_topics.discard("charge_explanation")

        if topic == "login_issue" and "payment_failed" in selected_topics:
            if not has_login_cue(user_text):
                continue

        if topic == "payment_failed" and "login_issue" in selected_topics:
            if not has_payment_cue(user_text):
                continue

        if topic == "delivery_issue" and "order_status" in selected_topics:
            if not has_delivery_cue(user_text):
                continue

        if topic == "order_status" and "delivery_issue" in selected_topics:
            if not has_order_cue(user_text):
                continue

        selected.append(intent)
        selected_topics.add(topic)

        if len(selected) >= max_intents:
            break

    return selected


def topic_label(topic):
    labels = {
        "password_reset": "password reset",
        "login_issue": "login issue",
        "account_locked": "locked account",
        "payment_failed": "payment failure",
        "double_charge": "double charge",
        "charge_explanation": "charge explanation",
        "refund_request": "refund request",
        "billing_question": "billing question",
        "subscription_cancel": "subscription cancellation",
        "fraud_report": "fraud report",
        "order_status": "order status",
        "delivery_issue": "delivery issue",
        "general_help": "general support"
    }
    return labels.get(topic, topic.replace("_", " "))


def get_single_response(intent):
    if intent.get("responses"):
        return random.choice(intent["responses"])

    if intent["action"] == "escalate":
        return "This issue requires a human support agent. I'm escalating it now."

    if intent["action"] == "clarify":
        return "Could you share a bit more detail so I can help you better?"

    return "I found your issue, but I don’t have a response ready."


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


def log_interaction(user_message, intents, response, file_path="chat_log.jsonl"):
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_message": user_message,
        "intents": intents,
        "response": response
    }

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


def main():
    faq_data = load_faq()

    print("AI Support Agent is running. Type 'exit', 'bye', or 'quit' to quit.\n")

    while True:
        user = input("You: ").strip()

        if user.lower() in ["exit", "bye", "quit"]:
            print("Bot: Goodbye!")
            break

        ranked = detect_intents(user, faq_data)
        selected = select_top_intents(ranked, user)
        response = generate_response(selected)

        print("Bot:", response)
        log_interaction(user, selected, response)


if __name__ == "__main__":
    main()