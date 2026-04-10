from src.preprocessing import preprocess_text, expand_contractions
from src.logger_utils import log_interaction
from src.sentiment import detect_sentiment
from src.confidence_utils import get_confidence, extract_confidence_details

import json
import random
import string

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


ACTION_PRIORITY = {
    "escalate": 0,
    "answer": 1,
    "clarify": 2
}


LOW_CONFIDENCE_THRESHOLD = 0.4


DEFAULT_GENERAL_HELP_INTENT = {
    "topic": "general_help",
    "score": 1.0,
    "action": "clarify",
    "responses": [
        "I can help. Is your issue about login, billing, payment, or an order?",
        "Please share a bit more detail so I can guide you to the right support.",
        "What kind of issue are you facing?"
    ]
}


SUCCESS_RESPONSES = [
    "Glad to hear everything is working now! Let me know if you need anything else.",
    "That's great to hear. If anything comes up, I'm here to help.",
    "Awesome, happy it's resolved! Just let me know if you need help again.",
    "Good to hear! Feel free to reach out anytime if you run into issues.",
]


NO_ISSUE_RESPONSES = [
    "Got it. Let me know if you need help with anything.",
    "Thanks for confirming. If anything comes up, I’m here to help.",
    "Sounds good. Let me know if you run into any issues."
]


URGENT_PRIORITY_TOPICS = {
    "account_locked",
    "login_issue",
    "payment_failed",
    "fraud_report",
}


ANSWER_STYLE_RESPONSES = {
    "general_help": "Please tell me whether this is about login, payment, billing, or an order, and I’ll help you from there.",
    "login_issue": "Please try resetting your password first, and if that does not work, let me know whether you see an error message or a lockout notice.",
    "billing_question": "Please tell me whether this is about an invoice, a plan charge, or a subscription fee.",
    "order_status": "Please share your order details or tracking information if you have them, and I’ll help you check the status.",
}


def load_faq(file_path="faq.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def tokenize(text):
    return preprocess_text(text).split()


def normalize_phrase_text(text):
    text = expand_contractions(text.lower())
    text = text.translate(str.maketrans("", "", string.punctuation))
    return " ".join(text.split())


def has_any_normalized_phrase(user_text, phrases):
    normalized = normalize_phrase_text(user_text)
    return any(normalize_phrase_text(p) in normalized for p in phrases)


def has_any_phrase(user_text, phrases, blocked_phrases=None):
    if blocked_phrases and has_any_normalized_phrase(user_text, blocked_phrases):
        return False

    normalized = normalize_phrase_text(user_text)
    return any(normalize_phrase_text(p) in normalized for p in phrases)


def has_success_signal(user_text):
    return has_any_normalized_phrase(user_text, [
        "i can login",
        "i can log in",
        "i can sign in",
        "i was able to login",
        "i was able to log in",
        "i was able to sign in",
        "it worked",
        "it worked for me",
        "it is working now",
        "its working now",
        "it works now",
        "fixed it",
        "problem solved",
        "issue resolved",
        "now it works",
        "everything works",
        "payment worked",
        "payment went through"
    ])


def has_no_issue_signal(user_text):
    return has_any_normalized_phrase(user_text, [
        "i am not locked out",
        "im not locked out",
        "i'm not locked out",
        "my account is not locked",
        "account is not locked",
        "i was not charged twice",
        "i wasnt charged twice",
        "i wasn't charged twice",
        "i was not billed twice",
        "i wasnt billed twice",
        "i wasn't billed twice",
        "i was not double charged",
        "i am not being charged twice",
        "i am not blocked",
        "my account is not blocked"
    ])


def get_topic_blocked_phrases(topic):
    topic_blockers = {
        "login_issue": [
            "can login",
            "can log in",
            "can sign in",
            "able to login",
            "able to log in",
            "able to sign in",
            "successfully login",
            "successfully log in",
            "successfully sign in"
        ],
        "account_locked": [
            "not locked out",
            "am not locked out",
            "im not locked out",
            "i am not locked out",
            "i'm not locked out",
            "account not locked",
            "account is not locked",
            "my account is not locked",
            "not account locked",
            "not blocked",
            "account not blocked",
            "account is not blocked",
            "my account is not blocked"
        ],
        "payment_failed": [
            "payment worked",
            "payment went through",
            "payment succeeded",
            "payment did not fail",
            "payment was not declined",
            "card was not declined"
        ],
        "double_charge": [
            "not charged twice",
            "was not charged twice",
            "wasnt charged twice",
            "wasn't charged twice",
            "not billed twice",
            "was not billed twice",
            "not double charged",
            "not a double charge",
            "no duplicate payment"
        ],
        "charge_explanation": [
            "was not charged",
            "wasnt charged",
            "wasn't charged",
            "not charged",
            "did not charge me",
            "didnt charge me",
            "didn't charge me"
        ],
        "refund_request": [
            "do not refund",
            "dont refund",
            "don't refund",
            "not asking for a refund",
            "no refund"
        ],
        "fraud_report": [
            "not fraud",
            "no fraud",
            "not a scam",
            "no scam"
        ],
        "delivery_issue": [
            "not late",
            "not delayed",
            "package arrived",
            "delivery arrived",
            "shipping was fine"
        ],
    }

    return topic_blockers.get(topic, [])


def is_blocked_topic(user_text, topic):
    blocked_phrases = get_topic_blocked_phrases(topic)
    if not blocked_phrases:
        return False
    return has_any_normalized_phrase(user_text, blocked_phrases)


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


def apply_sentiment_score_boost(results, sentiment_label):
    if sentiment_label != "urgent":
        return results

    boosted_results = []

    for item in results:
        updated_item = item.copy()

        if updated_item["topic"] in URGENT_PRIORITY_TOPICS:
            updated_item["score"] = round(updated_item["score"] + 0.3, 3)

        boosted_results.append(updated_item)

    boosted_results.sort(key=lambda x: x["score"], reverse=True)
    return boosted_results


def detect_intents(user_text, faq_data, vectorizer, matrix, mapping, sentiment_label=None):
    results = []

    tfidf_scores = compute_tfidf_score(user_text, vectorizer, matrix, mapping, faq_data)

    for item in faq_data:
        topic = item["topic"]
        action = item["action"]

        if is_blocked_topic(user_text, topic):
            continue

        tfidf_score = tfidf_scores.get(topic, 0)
        keyword_score = compute_keyword_score(user_text, item.get("keywords", []))

        total_score = (tfidf_score * 2.0) + (keyword_score * 0.5)

        if keyword_score >= 2:
            total_score += 0.2

        if total_score > 0:
            results.append({
                "topic": topic,
                "score": round(total_score, 3),
                "action": action,
                "responses": item.get("responses", [])
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return apply_sentiment_score_boost(results, sentiment_label)


def has_account_locked_cue(user_text):
    return has_any_phrase(
        user_text,
        [
            "account locked",
            "locked out",
            "account blocked",
            "access denied"
        ],
        blocked_phrases=get_topic_blocked_phrases("account_locked")
    )


def has_login_cue(user_text):
    return has_any_phrase(
        user_text,
        [
            "login",
            "log in",
            "sign in",
            "cant login",
            "cannot login",
            "cannot log in",
            "cant log in"
        ],
        blocked_phrases=get_topic_blocked_phrases("login_issue")
    )


def has_password_reset_cue(user_text):
    return has_any_phrase(user_text, [
        "forgot password",
        "reset password",
        "change password",
        "new password",
        "lost password",
        "cant remember password"
    ])


def has_payment_cue(user_text):
    return has_any_phrase(
        user_text,
        [
            "payment",
            "card declined",
            "checkout failed",
            "transaction failed",
            "payment failed"
        ],
        blocked_phrases=get_topic_blocked_phrases("payment_failed")
    )


def has_double_charge_cue(user_text):
    return has_any_phrase(
        user_text,
        [
            "charged twice",
            "double charge",
            "duplicate payment",
            "billed twice",
            "double charged",
            "charged two times",
            "billed two times"
        ],
        blocked_phrases=get_topic_blocked_phrases("double_charge")
    )


def has_billing_cue(user_text):
    return has_any_phrase(user_text, [
        "billing",
        "bill",
        "invoice",
        "subscription fee",
        "plan cost",
        "bill question"
    ])


def has_charge_explanation_cue(user_text):
    return has_any_phrase(
        user_text,
        [
            "explain charge",
            "what is this charge",
            "why was i charged",
            "why did you charge me",
            "dont understand this charge",
            "do not understand this charge",
            "what am i being charged for",
            "you charged me"
        ],
        blocked_phrases=get_topic_blocked_phrases("charge_explanation")
    )


def has_refund_cue(user_text):
    return has_any_phrase(
        user_text,
        [
            "refund",
            "money back",
            "return my money",
            "get my money back"
        ],
        blocked_phrases=get_topic_blocked_phrases("refund_request")
    )


def has_subscription_cancel_cue(user_text):
    return has_any_phrase(user_text, [
        "cancel subscription",
        "unsubscribe",
        "stop plan",
        "cancel plan",
        "end subscription"
    ])


def has_fraud_cue(user_text):
    return has_any_phrase(
        user_text,
        [
            "fraud",
            "scam",
            "unauthorized charge",
            "stolen card",
            "suspicious charge",
            "someone used my card",
            "used without permission"
        ],
        blocked_phrases=get_topic_blocked_phrases("fraud_report")
    )


def has_delivery_cue(user_text):
    return has_any_phrase(
        user_text,
        [
            "delivery",
            "late",
            "shipping",
            "package",
            "delayed"
        ],
        blocked_phrases=get_topic_blocked_phrases("delivery_issue")
    )


def has_order_cue(user_text):
    return has_any_phrase(user_text, [
        "order",
        "track order",
        "where is my order"
    ])


TOPIC_CUE_FUNCTIONS = {
    "password_reset": has_password_reset_cue,
    "login_issue": has_login_cue,
    "account_locked": has_account_locked_cue,
    "payment_failed": has_payment_cue,
    "double_charge": has_double_charge_cue,
    "charge_explanation": has_charge_explanation_cue,
    "refund_request": has_refund_cue,
    "billing_question": has_billing_cue,
    "subscription_cancel": has_subscription_cancel_cue,
    "fraud_report": has_fraud_cue,
    "order_status": has_order_cue,
    "delivery_issue": has_delivery_cue,
}


def get_strong_cue_topics(user_text):
    strong_topics = set()

    for topic, cue_fn in TOPIC_CUE_FUNCTIONS.items():
        if cue_fn(user_text):
            strong_topics.add(topic)

    return strong_topics


def has_strong_domain_cue(user_text):
    return any([
        has_login_cue(user_text),
        has_payment_cue(user_text),
        has_billing_cue(user_text),
        has_refund_cue(user_text),
        has_delivery_cue(user_text),
        has_order_cue(user_text),
        has_account_locked_cue(user_text),
        has_password_reset_cue(user_text),
        has_double_charge_cue(user_text),
        has_charge_explanation_cue(user_text),
        has_subscription_cancel_cue(user_text),
        has_fraud_cue(user_text),
    ])


def is_vague_query(user_text):
    original = user_text.lower().strip()
    normalized = preprocess_text(user_text)
    tokens = normalized.split()

    vague_exact_inputs = {
        "help",
        "help me",
        "i need help",
        "problem",
        "i have a problem",
        "issue",
        "i have an issue",
        "i have issue",
        "something is wrong",
        "something wrong",
        "it's not working",
        "its not working",
        "not working",
    }

    vague_phrases = [
        "need help",
        "have a problem",
        "have an issue",
        "something is wrong",
        "something wrong",
        "not working",
    ]

    if has_strong_domain_cue(user_text):
        return False

    if original in vague_exact_inputs:
        return True

    if any(phrase in original for phrase in vague_phrases):
        return True

    weak_words = {"help", "problem", "issue", "wrong"}

    if len(tokens) <= 4 and any(word in tokens for word in weak_words):
        return True

    return False


def select_top_intents(ranked_intents, user_text, min_score=0.2, max_intents=2):
    if is_vague_query(user_text):
        return [DEFAULT_GENERAL_HELP_INTENT]

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

    strong_cue_topics = get_strong_cue_topics(user_text)

    if len(strong_cue_topics) >= 2 and len(candidates) < max_intents:
        for intent in ranked_intents:
            if intent["topic"] == "general_help":
                continue

            if intent["score"] < min_score:
                continue

            if intent["topic"] not in strong_cue_topics:
                continue

            if not any(c["topic"] == intent["topic"] for c in candidates):
                candidates.append(intent)

            if len(candidates) >= max_intents:
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
            topics.discard("charge_explanation")

        if t == "billing_question" and "refund_request" in topics:
            if not has_billing_cue(user_text):
                continue

        if t == "refund_request" and "billing_question" in topics:
            if not has_refund_cue(user_text):
                continue

        if t == "billing_question" and "charge_explanation" in topics:
            if not has_billing_cue(user_text):
                continue
            if has_charge_explanation_cue(user_text):
                continue

        if t == "charge_explanation" and "billing_question" in topics:
            if has_charge_explanation_cue(user_text):
                selected = [x for x in selected if x["topic"] != "billing_question"]
                topics.discard("billing_question")

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


def get_urgent_general_help_response():
    return "Please tell me if this is about login, payment, billing, or an order so I can help right away."


def get_frustrated_general_help_response():
    return "Please tell me whether this is a login, payment, billing, or order issue, and I’ll guide you step by step."


def get_action_consistent_response(intent, sentiment_label=None):
    topic = intent["topic"]
    action = intent["action"]

    if sentiment_label == "urgent" and topic == "general_help":
        return get_urgent_general_help_response()

    if sentiment_label == "frustrated" and topic == "general_help":
        return get_frustrated_general_help_response()

    if action == "answer" and topic in ANSWER_STYLE_RESPONSES:
        return ANSWER_STYLE_RESPONSES[topic]

    return get_single_response(intent)


def merge_responses(r1, r2, t1, t2):
    return (
        f"I can help with both your {t1} and {t2}.\n\n"
        f"For your {t1}, {r1}\n\n"
        f"For your {t2}, {r2}"
    )


def sort_intents_by_priority(intents):
    return sorted(
        intents,
        key=lambda x: (ACTION_PRIORITY.get(x["action"], 99), -x["score"])
    )


def apply_sentiment_routing(selected_intents, sentiment_label):
    updated_intents = []

    for intent in selected_intents:
        updated_intent = intent.copy()

        if sentiment_label == "urgent" and updated_intent["action"] == "clarify":
            updated_intent["action"] = "answer"

        if sentiment_label == "angry" and updated_intent["action"] == "answer":
            updated_intent["action"] = "escalate"

        if sentiment_label == "frustrated" and updated_intent["action"] == "clarify":
            updated_intent["action"] = "answer"

        updated_intents.append(updated_intent)

    return updated_intents


def get_final_action(selected_intents):
    if not selected_intents:
        return None

    ordered = sort_intents_by_priority(selected_intents)
    return ordered[0]["action"]


def apply_confidence_sentiment_rules(selected_intents, confidence, sentiment_label):
    if confidence < LOW_CONFIDENCE_THRESHOLD:
        return [DEFAULT_GENERAL_HELP_INTENT], "low_confidence_fallback"

    updated_intents = []
    routing_reason = "normal_routing"

    for intent in selected_intents:
        updated_intent = intent.copy()

        if sentiment_label == "angry" and confidence < 0.7:
            updated_intent["action"] = "escalate"
            routing_reason = "sentiment_override_angry"

        elif sentiment_label == "frustrated" and confidence < 0.6:
            updated_intent["action"] = "clarify"
            routing_reason = "sentiment_override_frustrated"

        updated_intents.append(updated_intent)

    return updated_intents, routing_reason


def generate_response(selected_intents, sentiment_label=None):
    if not selected_intents:
        return "I'm sorry, I didn’t understand. Could you rephrase?"

    ordered = sort_intents_by_priority(selected_intents)

    if len(ordered) == 1:
        return get_action_consistent_response(ordered[0], sentiment_label)

    t1 = topic_label(ordered[0]["topic"])
    t2 = topic_label(ordered[1]["topic"])

    r1 = get_action_consistent_response(ordered[0], sentiment_label)
    r2 = get_action_consistent_response(ordered[1], sentiment_label)

    return merge_responses(r1, r2, t1, t2)


def add_empathy_and_politeness(response, sentiment_label, topics):
    if topics and topics[0] in {"success", "no_issue"}:
        return response

    empathy_map = {
        "angry": "I'm really sorry you're dealing with this. I understand how frustrating this must be, and I'll do my best to help.",
        "frustrated": "I understand how frustrating this must be, and I'll do my best to help.",
        "urgent": "I understand this is urgent, and I'll help you as quickly as possible.",
        "neutral": "Thank you for reaching out. I'll be happy to help you with this."
    }

    empathy = empathy_map.get(sentiment_label, "")
    return f"{empathy} {response}".strip()


def main():
    faq_data = load_faq()
    vectorizer, matrix, mapping = build_tfidf_index(faq_data)

    print("AI Support Agent is running. Type 'exit' to quit.\n")

    while True:
        user = input("You: ").strip()

        if user.lower() in ["exit", "bye", "quit"]:
            print("Bot: Goodbye!")
            break

        sentiment = detect_sentiment(user)
        sentiment_label = sentiment["label"]

        if has_success_signal(user):
            selected = [{
                "topic": "success",
                "score": 1.0,
                "action": "answer",
                "responses": SUCCESS_RESPONSES
            }]
        elif has_no_issue_signal(user):
            selected = [{
                "topic": "no_issue",
                "score": 1.0,
                "action": "answer",
                "responses": NO_ISSUE_RESPONSES
            }]
        elif is_vague_query(user):
            selected = [DEFAULT_GENERAL_HELP_INTENT]
            selected = apply_sentiment_routing(selected, sentiment_label)
        else:
            ranked = detect_intents(
                user,
                faq_data,
                vectorizer,
                matrix,
                mapping,
                sentiment_label=sentiment_label
            )

            if not ranked:
                selected = [{
                    "topic": "no_issue",
                    "score": 1.0,
                    "action": "answer",
                    "responses": NO_ISSUE_RESPONSES
                }]
            else:
                selected = select_top_intents(ranked, user)
                selected = apply_sentiment_routing(selected, sentiment_label)

        predicted_topics_before_rules = [intent["topic"] for intent in selected]

        pre_rule_confidence = get_confidence(selected)

        selected, routing_reason = apply_confidence_sentiment_rules(
            selected,
            pre_rule_confidence,
            sentiment_label
        )

        final_topics_after_rules = [intent["topic"] for intent in selected]

        confidence = get_confidence(selected)
        top1_score, top2_score, score_gap = extract_confidence_details(selected)

        response = generate_response(selected, sentiment_label=sentiment_label)
        final_response = add_empathy_and_politeness(
            response,
            sentiment_label,
            final_topics_after_rules
        )

        primary_intent = selected[0]["topic"] if selected else None
        final_action = get_final_action(selected)

        print(f"Detected sentiment: {sentiment_label}")
        print(f"Predicted topics before rules: {predicted_topics_before_rules}")
        print(f"Final topics after rules: {final_topics_after_rules}")
        print(f"Final action: {final_action} (reason={routing_reason})")
        print(f"Confidence: {confidence} (top1={top1_score}, top2={top2_score}, gap={score_gap})")
        print("Bot:", final_response)

        log_interaction(
            user,
            selected,
            final_response,
            sentiment,
            primary_intent,
            final_action,
            confidence,
            top1_score,
            top2_score,
            score_gap,
            routing_reason,
            predicted_topics_before_rules=predicted_topics_before_rules,
            final_topics_after_rules=final_topics_after_rules
        )


if __name__ == "__main__":
    main()