import json
import random
import string
from datetime import datetime, timezone


STOPWORDS = {
    "i", "me", "my", "you", "your", "the", "a", "an", "is", "are", "am",
    "to", "for", "of", "and", "or", "in", "on", "at", "it", "this", "that",
    "be", "can", "cant", "cannot", "do", "did", "was", "were", "with"
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


def select_top_intents(ranked_intents, min_score=1.0, max_intents=2):
    selected = []

    for intent in ranked_intents:
        if intent["score"] >= min_score:
            selected.append(intent)

    return selected[:max_intents]


def topic_label(topic):
    labels = {
        "password_reset": "password reset",
        "login_issue": "login issue",
        "account_locked": "locked account",
        "payment_failed": "payment failure",
        "double_charge": "double charge",
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
    topic = intent["topic"]
    action = intent["action"]
    responses = intent.get("responses", [])

    if action == "escalate":
        if responses:
            return random.choice(responses)
        return "This issue requires a human support agent. I'm escalating it now."

    if action == "clarify":
        clarify_questions = {
            "login_issue": "Are you having a password problem, seeing an error message, or is your account locked?",
            "account_locked": "Did you receive any error message or security alert when trying to sign in?",
            "billing_question": "Is your question about an invoice, a subscription fee, or an unexpected charge?",
            "delivery_issue": "Is your package delayed, missing, or marked as delivered but not received?",
            "general_help": "Is your issue about login, billing, payment, or an order?"
        }
        return clarify_questions.get(
            topic,
            "Could you give me a bit more detail so I can help you better?"
        )

    if responses:
        return random.choice(responses)

    return "I found your issue, but I don’t have a response ready."


def sort_intents_by_priority(intents):
    return sorted(
        intents,
        key=lambda x: (ACTION_PRIORITY.get(x["action"], 99), -x["score"])
    )


def generate_response(selected_intents):
    if not selected_intents:
        return "I'm sorry, I didn’t understand. Could you rephrase?"

    ordered_intents = sort_intents_by_priority(selected_intents)

    if len(ordered_intents) == 1:
        return get_single_response(ordered_intents[0])

    first_intent = ordered_intents[0]
    second_intent = ordered_intents[1]

    t1 = topic_label(first_intent["topic"])
    t2 = topic_label(second_intent["topic"])

    response1 = get_single_response(first_intent)
    response2 = get_single_response(second_intent)

    intro = f"I can help with both your {t1} and {t2}."
    part1 = f"First, {response1}"
    part2 = f"Also, {response2}"

    return f"{intro}\n\n{part1}\n\n{part2}"


def log_interaction(user_message, intents, response, file_path="chat_log.jsonl"):
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_message": user_message,
        "intents": [
            {
                "topic": intent["topic"],
                "score": intent["score"],
                "action": intent["action"]
            }
            for intent in intents
        ],
        "primary_intent": intents[0]["topic"] if intents else None,
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
        selected = select_top_intents(ranked)
        response = generate_response(selected)

        print("Bot:", response)
        log_interaction(user, selected, response)


if __name__ == "__main__":
    main()