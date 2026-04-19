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
    "clarify": 2,
}


LOW_CONFIDENCE_THRESHOLD = 0.4

INITIAL_CONVERSATION_STATE = {
    "awaiting_clarification": False,
    "followup_context_active": False,
    "last_user_message": None,
    "last_topics": [],
    "last_action": None,
    "last_routing_reason": None,
}


DEFAULT_GENERAL_HELP_INTENT = {
    "topic": "general_help",
    "score": 1.0,
    "action": "clarify",
    "responses": [
        "I can help. Is your issue about login, billing, payment, or an order?",
        "Please share a bit more detail so I can guide you to the right support.",
        "What kind of issue are you facing?",
    ],
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
    "Sounds good. Let me know if you run into any issues.",
]


URGENT_PRIORITY_TOPICS = {
    "account_locked",
    "login_issue",
    "payment_failed",
    "fraud_report",
}


ANSWER_STYLE_RESPONSES = {
    "general_help": "Please tell me whether this is about login, payment, billing, or an order, and I’ll help you from there.",
    "login_issue": "Try resetting your password first. If that doesn’t work, let me know if you see an error message or a lockout notice.",
    "billing_question": "Please tell me whether this is about an invoice, a plan charge, or a subscription fee.",
    "order_status": "Share your order details or tracking info, and I’ll help you check the status.",
}

CLARIFICATION_OPTIONS = {
    "account": [
        "a login issue",
        "an account lockout",
        "a password reset",
    ],
    "charge": [
        "a charge you don’t recognize",
        "a duplicate charge",
        "a refund request",
    ],
    "billing": [
        "an invoice question",
        "a subscription fee question",
        "a general billing issue",
    ],
    "payment": [
        "a failed payment",
        "a declined card or checkout problem",
        "a refund request",
    ],
    "subscription": [
        "canceling your subscription",
        "a subscription fee question",
        "another billing issue",
    ],
    "security": [
        "a suspicious or unauthorized charge",
        "a duplicate charge",
        "a charge you don’t recognize",
    ],
    "order": [
        "an order status update",
        "a delayed delivery",
        "a missing package",
    ],
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
    return has_any_normalized_phrase(
        user_text,
        [
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
            "payment went through",
        ],
    )


def has_no_issue_signal(user_text):
    return has_any_normalized_phrase(
        user_text,
        [
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
            "my account is not blocked",
        ],
    )


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
            "successfully sign in",
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
            "my account is not blocked",
        ],
        "payment_failed": [
            "payment worked",
            "payment went through",
            "payment succeeded",
            "payment did not fail",
            "payment was not declined",
            "card was not declined",
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
            "no duplicate payment",
        ],
        "charge_explanation": [
            "was not charged",
            "wasnt charged",
            "wasn't charged",
            "not charged",
            "did not charge me",
            "didnt charge me",
            "didn't charge me",
        ],
        "refund_request": [
            "do not refund",
            "dont refund",
            "don't refund",
            "not asking for a refund",
            "no refund",
        ],
        "fraud_report": [
            "not fraud",
            "no fraud",
            "not a scam",
            "no scam",
        ],
        "delivery_issue": [
            "not late",
            "not delayed",
            "package arrived",
            "delivery arrived",
            "shipping was fine",
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
            results.append(
                {
                    "topic": topic,
                    "score": round(total_score, 3),
                    "action": action,
                    "responses": item.get("responses", []),
                }
            )

    results.sort(key=lambda x: x["score"], reverse=True)
    return apply_sentiment_score_boost(results, sentiment_label)


def has_account_locked_cue(user_text):
    return has_any_phrase(
        user_text,
        [
            "account locked",
            "locked out",
            "account blocked",
            "access denied",
        ],
        blocked_phrases=get_topic_blocked_phrases("account_locked"),
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
            "cant log in",
        ],
        blocked_phrases=get_topic_blocked_phrases("login_issue"),
    )


def has_password_reset_cue(user_text):
    return has_any_phrase(
        user_text,
        [
            "forgot password",
            "reset password",
            "change password",
            "new password",
            "lost password",
            "cant remember password",
        ],
    )


def has_payment_cue(user_text):
    return has_any_phrase(
        user_text,
        [
            "payment",
            "card declined",
            "checkout failed",
            "transaction failed",
            "payment failed",
        ],
        blocked_phrases=get_topic_blocked_phrases("payment_failed"),
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
            "billed two times",
        ],
        blocked_phrases=get_topic_blocked_phrases("double_charge"),
    )


def has_billing_cue(user_text):
    return has_any_phrase(
        user_text,
        [
            "billing",
            "bill",
            "invoice",
            "subscription fee",
            "plan cost",
            "bill question",
        ],
    )


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
            "you charged me",
        ],
        blocked_phrases=get_topic_blocked_phrases("charge_explanation"),
    )


def has_refund_cue(user_text):
    return has_any_phrase(
        user_text,
        [
            "refund",
            "money back",
            "return my money",
            "get my money back",
        ],
        blocked_phrases=get_topic_blocked_phrases("refund_request"),
    )


def has_subscription_cancel_cue(user_text):
    return has_any_phrase(
        user_text,
        [
            "cancel subscription",
            "unsubscribe",
            "stop plan",
            "cancel plan",
            "end subscription",
        ],
    )


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
            "used without permission",
        ],
        blocked_phrases=get_topic_blocked_phrases("fraud_report"),
    )


def has_delivery_cue(user_text):
    return has_any_phrase(
        user_text,
        [
            "delivery",
            "late",
            "shipping",
            "package",
            "delayed",
        ],
        blocked_phrases=get_topic_blocked_phrases("delivery_issue"),
    )


def has_order_cue(user_text):
    return has_any_phrase(
        user_text,
        [
            "order",
            "track order",
            "where is my order",
        ],
    )


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
    return any(
        [
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
        ]
    )


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

    weak_words = {"help", "problem", "issue", "wrong"}
    domain = detect_clarification_domain(user_text)

    # 1) کاملاً مبهم
    if original in vague_exact_inputs:
        return True

    if any(phrase in original for phrase in vague_phrases):
        return True


    if domain is not None and any(word in original for word in weak_words):
        return True

    if has_strong_domain_cue(user_text):
        return False

    if len(tokens) <= 6 and any(word in tokens for word in weak_words):
        return True

    return False


def select_top_intents(ranked_intents, user_text, min_score=0.2, max_intents=2):
    if is_vague_query(user_text):
        return [DEFAULT_GENERAL_HELP_INTENT]

    if not ranked_intents:
        return []

    top_score = ranked_intents[0]["score"]

    candidates = [i for i in ranked_intents if i["score"] >= top_score * 0.75]

    if any(i["topic"] != "general_help" for i in candidates):
        candidates = [i for i in candidates if i["topic"] != "general_help"]

    if has_account_locked_cue(user_text):
        if not any(i["topic"] == "account_locked" for i in candidates):
            for intent in ranked_intents:
                if intent["topic"] == "account_locked":
                    candidates.append(intent)
                    break

    strong_cue_topics = get_strong_cue_topics(user_text)

    normalized = normalize_phrase_text(user_text)

    if (
        "charge explanation" in normalized
        or "explanation for a charge" in normalized
        or "what is this charge" in normalized
        or "explain this charge" in normalized
        or "unfamiliar payment" in normalized
        or "unknown charge" in normalized
    ):
        ranked_intents = [
            intent for intent in ranked_intents
            if intent["topic"] not in {"payment_failed", "fraud_report"}
        ]
        candidates = [
            intent for intent in candidates
            if intent["topic"] not in {"payment_failed", "fraud_report"}
        ]
        ranked_intents = [intent for intent in ranked_intents if intent["topic"] != "payment_failed"]
        candidates = [intent for intent in candidates if intent["topic"] != "payment_failed"]

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


def get_partial_answer_for_topic(topic):
    partial_answers = {
        "login_issue": "For the login part, please try resetting your password first and let me know if you see an error message or a lockout notice.",
        "account_locked": "For the account access part, please check whether you see a lockout or access denied message.",
        "payment_failed": "For the payment part, please try the payment again and check whether your card was declined or the checkout failed.",
        "double_charge": "For the billing part, I can help review whether this looks like a duplicate charge.",
        "refund_request": "For the refund part, I can help with the request once I understand what happened with the payment or charge.",
        "billing_question": "For the billing part, I can help explain whether this is related to an invoice, subscription fee, or plan charge.",
        "order_status": "For the order part, I can help check the current order status if you share the order details.",
        "delivery_issue": "For the delivery part, I can help look into whether the package is delayed or still in transit.",
        "charge_explanation": "For the charge part, I can help explain what the charge may be related to.",
        "subscription_cancel": "For the subscription part, I can help with cancellation steps.",
        "fraud_report": "For the security part, this may need urgent review if the charge looks unauthorized.",
        "password_reset": "For the password part, I can help you with reset steps.",
    }

    return partial_answers.get(topic, "I can help with part of this issue.")


def merge_responses(r1, r2, t1, t2):
    return (
        f"I can help with both your {t1} and {t2}.\n\n"
        f"For your {t1}:\n{r1}\n\n"
        f"For your {t2}:\n{r2}"
    )


def sort_intents_by_priority(intents):
    return sorted(
        intents,
        key=lambda x: (ACTION_PRIORITY.get(x["action"], 99), -x["score"]),
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


def should_escalate_to_human(selected_intents, sentiment_label, confidence):
    if not selected_intents:
        return False

    topics = [intent["topic"] for intent in selected_intents]

    high_risk_topics = {
        "fraud_report",
    }

    if any(t in high_risk_topics for t in topics):
        return True

    if "account_locked" in topics and "fraud_report" in topics:
        return True

    if sentiment_label == "angry" and confidence < 0.5:
        if any(t in {"payment_failed", "double_charge", "charge_explanation"} for t in topics):
            return True

    return False


def apply_confidence_sentiment_rules(selected_intents, confidence, sentiment_label):
    if confidence < LOW_CONFIDENCE_THRESHOLD:
        if should_escalate_to_human(selected_intents, sentiment_label, confidence):
            updated = []
            for intent in selected_intents:
                new_intent = intent.copy()
                new_intent["action"] = "escalate"
                updated.append(new_intent)
            return updated, "human_escalation"

        if len(selected_intents) > 1:
            return selected_intents, "low_confidence_multi_intent"

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


def add_empathy_and_politeness(response, sentiment_label, topics, confidence=None):
    if topics and topics[0] in {"success", "no_issue"}:
        return response

    if response.startswith("Thanks, that helps."):
        return response

    if confidence is not None and confidence < 0.6:
        return response

    empathy_map = {
        "angry": "I'm really sorry you're dealing with this. I understand how frustrating this must be, and I'll do my best to help.",
        "frustrated": "I understand how frustrating this must be, and I'll do my best to help.",
        "urgent": "I understand this is urgent, and I'll help you as quickly as possible.",
        "neutral": "Thank you for reaching out. I'll be happy to help you with this.",
    }

    empathy = empathy_map.get(sentiment_label, "")
    return f"{empathy} {response}".strip()


def apply_confidence_tone(response, confidence):
    if confidence < 0.3:
        return f"I’m not fully sure I understood correctly, but {response}"

    if confidence < 0.6:
        return f"Based on what I understand, {response}"

    return response

def apply_action_tone(response, action, skip_clarify_tail=False):
    if action == "clarify" and not skip_clarify_tail:
        return response
    if action == "escalate":
        return response + " A support specialist will handle this for you."
    return response


def get_low_confidence_multi_intent_response(predicted_topics):
    if not predicted_topics:
        return DEFAULT_GENERAL_HELP_INTENT["responses"][0]

    topic_labels = [topic.replace("_", " ") for topic in predicted_topics[:2]]

    if len(predicted_topics) < 2:
        return DEFAULT_GENERAL_HELP_INTENT["responses"][0]

    first_topic = predicted_topics[0]
    partial_answer = get_partial_answer_for_topic(first_topic)

    clarification_question = generate_clarification_question(predicted_topics)

    if clarification_question:
        return (
        f"It looks like this may involve both your {topic_labels[0]} and {topic_labels[1]}.\n\n"
        f"{partial_answer}\n\n"
        f"{clarification_question}"
    )
    return (
    f"It looks like this may involve both your {topic_labels[0]} and {topic_labels[1]}.\n\n"
    f"{partial_answer}\n\n"
    f"Could you clarify which part you want help with first?"
    )

def create_conversation_state():
    return {
        "awaiting_clarification": False,
        "followup_context_active": False,
        "last_user_message": None,
        "last_topics": [],
        "last_action": None,
        "last_routing_reason": None,
    }

def should_keep_followup_context(final_topics, final_action):
    if final_action == "clarify":
        return True

    followup_topics = {
        "billing_question",
        "billing_clarification",
        "charge_explanation",
        "charge_clarification",
        "refund_request",
        "account_clarification",
        "security_clarification",
        "fraud_report",
    }

    return any(topic in followup_topics for topic in final_topics)

def should_treat_as_clarification_followup(user_text, conversation_state):
    if not conversation_state.get("awaiting_clarification") and not conversation_state.get("followup_context_active"):
        return False

    last_topics = conversation_state.get("last_topics", [])
    if not last_topics:
        return False

    last_topic = last_topics[0]

    domain_map = {
        "billing_clarification": "billing",
        "billing_question": "billing",
        "account_clarification": "account",
        "login_issue": "account",
        "account_locked": "account",
        "password_reset": "account",
        "payment_clarification": "payment",
        "payment_failed": "payment",
        "order_clarification": "order",
        "order_status": "order",
        "delivery_issue": "order",
        "charge_clarification": "charge",
        "double_charge": "charge",
        "refund_request": "charge",
        "charge_explanation": "charge",
        "security_clarification": "security",
        "fraud_report": "security",
    }

    domain = domain_map.get(last_topic)
    if not domain:
        return False

    normalized = normalize_phrase_text(user_text)
    token_count = len(normalized.split())

    if token_count <= 12:
        return True

    new_domain = detect_clarification_domain(user_text)
    if new_domain == domain:
        return True

    domain_keywords = {
        "billing": [
            "invoice",
            "subscription",
            "subscription fee",
            "plan cost",
            "billing",
            "bill",
            "renewal",
            "plan",
            "price",
            "cost",
        ],
        "account": [
            "password",
            "reset",
            "login",
            "log in",
            "sign in",
            "locked",
            "lockout",
            "access denied",
            "verification",
            "error",
        ],
        "payment": [
            "declined",
            "card",
            "checkout",
            "payment",
            "transaction",
            "failed",
            "did not go through",
        ],
        "order": [
            "delivery",
            "missing",
            "late",
            "tracking",
            "track",
            "order",
            "package",
            "shipment",
            "delayed",
        ],
        "charge": [
            "refund",
            "charged",
            "charge",
            "charged twice",
            "duplicate",
            "double charge",
            "unknown charge",
            "billing history",
            "yesterday",
            "today",
            "recent",
            "completed charge",
            "money back",
        ],
        "security": [
            "fraud",
            "unauthorized",
            "suspicious",
            "not mine",
            "used my card",
            "stolen card",
            "without permission",
            "security",
        ],
    }

    if domain in domain_keywords and any(keyword in normalized for keyword in domain_keywords[domain]):
        return True

    return False


def merge_with_clarification_context(user_text, conversation_state):
    previous_message = conversation_state.get("last_user_message") or ""
    return f"{previous_message} {user_text}".strip()


def get_clarification_refined_response(user_text, selected_intents):
    topics = [intent["topic"] for intent in selected_intents]
    normalized = normalize_phrase_text(user_text)

    billing_topics = {"billing_question", "billing_clarification"}
    charge_topics = {"charge_explanation", "charge_clarification", "refund_request", "double_charge"}
    account_topics = {"login_issue", "account_clarification", "account_locked", "password_reset"}
    security_topics = {"security_clarification", "fraud_report"}

    # --------------------
    # Billing follow-ups
    # --------------------
    if any(topic in billing_topics for topic in topics) and "subscription fee" in normalized:
        return (
            "Thanks, that helps. If your question is about a subscription fee, "
            "please check the billing or plan section in your account where your active plan, "
            "renewal date, and recurring charge details are listed. "
            "If the amount looks different from what you expected, I can help you review that next."
        )

    if any(topic in billing_topics for topic in topics) and "subscription" in normalized:
        return (
            "Thanks, that helps. It sounds like this is about your subscription fee. "
            "Please open the billing or subscription section in your account to review your current plan cost "
            "and renewal details. If the charge looks different from what you expected, I can help you check that next."
        )

    if any(topic in billing_topics for topic in topics) and "invoice" in normalized:
        return (
            "Thanks, that helps. If this is about an invoice, "
            "please open the billing section of your account and review the latest invoice details there. "
            "If something on the invoice looks unclear, tell me which part and I’ll help you narrow it down."
        )

    if any(topic in billing_topics for topic in topics) and "plan cost" in normalized:
        return (
            "Thanks, that helps. If you're asking about plan cost, "
            "please check your account's billing or subscription page where the current plan and price are shown. "
            "If the price changed unexpectedly, I can help you investigate that."
        )

    if any(topic in billing_topics for topic in topics) and (
        "renewal" in normalized or "price" in normalized or "cost" in normalized
    ):
        return (
            "Thanks, that helps. Please check the billing or subscription section of your account "
            "to review your current plan, renewal timing, and the price being charged. "
            "If one of those details looks wrong, tell me which one and I’ll help you narrow it down."
        )

    # --------------------
    # Charge / explanation (MOST SPECIFIC FIRST)
    # --------------------
    if "charge_explanation" in topics and (
        "explanation for a charge" in normalized
        or "what is this charge" in normalized
        or "unknown charge" in normalized
        or "explain this charge" in normalized
        or "why was i charged" in normalized
    ):
        return (
            "Thanks, that helps. If you're looking for an explanation for a charge, "
            "please review the date, amount, and any recent subscription, order, or account activity in your account first. "
            "If it still does not look familiar, tell me what seems unclear and I’ll help narrow it down."
        )

    if "charge_explanation" in topics and (
        "unfamiliar payment" in normalized or "unfamiliar" in normalized
    ):
        return (
            "Thanks, that helps. If the payment looks unfamiliar, "
            "please review the date, amount, and any recent subscription, order, or account activity first. "
            "If it still does not look recognizable, it may need to be treated as an unauthorized or suspicious charge."
        )
    if "refund_request" in topics and (
        "charge" in normalized or "charged" in normalized
    ) and (
        "yesterday" in normalized or "today" in normalized or "recent" in normalized
    ):
        return (
            "Thanks, that helps. It sounds like you want a refund for a recent charge. "
            "Please open the relevant charge in your billing or order history and start the refund request there. "
            "If you're unsure which charge it is, tell me what looks unusual and I’ll help narrow it down."
        )

    if any(topic in charge_topics for topic in topics) and (
        "yesterday" in normalized or "today" in normalized or "recent" in normalized
    ):
        return (
            "Thanks, that helps. Since this was a recent charge, "
            "please check the charge details in your account and review whether it matches a recent purchase, "
            "subscription renewal, or refund-related request. If it still looks wrong, I can help you narrow it down."
        )

    # --------------------
    # Refund / charge handling
    # --------------------
    if "refund_request" in topics and "completed charge" in normalized:
        return (
            "Thanks, that helps. It sounds like you're asking for a refund for a completed charge. "
            "Please go to your account dashboard and open the order or charge details to start the refund request. "
            "If the charge looks incorrect or unexpected, I can help you review that too."
        )

    if "refund_request" in topics and ("refund" in normalized or "money back" in normalized):
        return (
            "Thanks, that helps. If you're asking for a refund, "
            "please open your account's billing or order history section and start the refund request from the relevant charge. "
            "If you want, I can also help you figure out which charge this should apply to."
        )

    if "refund_request" in topics and ("charge" in normalized or "charged" in normalized):
        return (
            "Thanks, that helps. It sounds like you want a refund for a specific charge. "
            "Please open the relevant charge in your billing or order history and start the refund request there. "
            "If you're unsure which charge it is, tell me what looks unusual and I’ll help narrow it down."
        )

    if "double_charge" in topics and (
        "charged twice" in normalized or "duplicate" in normalized or "double charge" in normalized
    ):
        return (
            "Thanks, that helps. This sounds like a possible duplicate charge. "
            "Please review the charge dates and amounts in your billing history first. "
            "If the same payment appears more than once, this should be investigated further."
        )

    # --------------------
    # Security / fraud
    # --------------------
    if any(topic in security_topics for topic in topics) and (
        "not mine" in normalized
        or "unauthorized" in normalized
        or "used my card" in normalized
        or "without permission" in normalized
        or "fraud" in normalized
        or "suspicious" in normalized
    ):
        return (
            "Thanks, that helps. This looks like a potentially unauthorized charge. "
            "Please secure the account or card first if you have not already done so, "
            "then review the charge details and report it for investigation as soon as possible."
        )

    if "fraud_report" in topics and "charge" in normalized:
        return (
            "Thanks, that helps. Since this appears to be a suspicious charge, "
            "it should be treated as a security issue and reviewed quickly. "
            "Please report the charge through the appropriate support or security channel and secure the affected payment method if needed."
        )

    # --------------------
    # Account follow-ups
    # --------------------
    if any(topic in account_topics for topic in topics) and "reset" in normalized:
        return (
            "Thanks, that helps. Since this is still an account access issue after trying reset-related steps, "
            "please tell me whether you're seeing a password error, a lockout message, or a verification problem."
        )

    if any(topic in account_topics for topic in topics) and "password" in normalized:
        return (
            "Thanks, that helps. If this is about your password, "
            "please try the password reset flow from the login page and then check whether you can sign in again. "
            "If that still fails, tell me what message you see."
        )

    if any(topic in account_topics for topic in topics) and (
        "locked" in normalized or "lockout" in normalized or "access denied" in normalized
    ):
        return (
            "Thanks, that helps. If your account appears locked, "
            "please check whether you received a warning, verification request, or security message during sign-in. "
            "Tell me what message you see and I’ll help narrow it down."
        )

    if any(topic in account_topics for topic in topics) and "verification" in normalized:
        return (
            "Thanks, that helps. If the problem is related to verification, "
            "please tell me whether you're not receiving a code, the code is failing, or the verification step is not loading properly."
        )

    return None

def detect_clarification_domain(user_text):
    normalized = normalize_phrase_text(user_text)

    security_phrases = [
        "fraud",
        "scam",
        "unauthorized charge",
        "suspicious charge",
        "stolen card",
        "used my card",
        "without permission",
        "not mine",
        "suspicious",
    ]

    account_phrases = [
        "account",
        "login",
        "log in",
        "sign in",
        "password",
        "locked",
        "lockout",
        "access denied",
        "blocked",
    ]

    order_phrases = [
        "order",
        "delivery",
        "package",
        "shipping",
        "track",
        "late",
        "delayed",
        "shipment",
    ]

    payment_phrases = [
        "payment",
        "card",
        "checkout",
        "transaction",
        "declined",
        "payment failed",
        "payment problem",
        "card problem",
        "checkout problem",
    ]

    billing_phrases = [
        "billing",
        "invoice",
        "bill",
        "subscription fee",
        "plan cost",
    ]

    subscription_phrases = [
        "subscription",
        "unsubscribe",
        "cancel plan",
        "cancel subscription",
        "stop plan",
        "end subscription",
    ]

    charge_phrases = [
        "charge",
        "charged",
        "charged twice",
        "double charge",
        "billed twice",
        "duplicate payment",
        "refund",
        "money back",
    ]

    if any(phrase in normalized for phrase in security_phrases):
        return "security"

    if any(phrase in normalized for phrase in account_phrases):
        return "account"

    if any(phrase in normalized for phrase in order_phrases):
        return "order"

    if any(phrase in normalized for phrase in payment_phrases):
        return "payment"

    if any(phrase in normalized for phrase in billing_phrases):
        return "billing"

    if any(phrase in normalized for phrase in subscription_phrases):
        return "subscription"

    if any(phrase in normalized for phrase in charge_phrases):
        return "charge"

    return None

def generate_domain_clarification(domain):
    options = CLARIFICATION_OPTIONS.get(domain)

    if not options or len(options) < 2:
        return None

    if len(options) == 2:
        return f"Just to clarify, is this about {options[0]} or {options[1]}?"

    if len(options) == 3:
        return (
            f"Just to clarify, is this about {options[0]}, "
            f"{options[1]}, or {options[2]}?"
        )

    leading = ", ".join(options[:-1])
    trailing = options[-1]
    return f"Just to clarify, is this about {leading}, or {trailing}?"

def generate_clarification_question(predicted_topics):
    if not predicted_topics or len(predicted_topics) < 2:
        return None

    t1, t2 = predicted_topics[:2]

    topic_map = {
        "payment_failed": "did the payment fail",
        "refund_request": "are you asking for a refund",
        "login_issue": "are you having trouble logging in",
        "account_locked": "is your account locked",
        "double_charge": "were you charged twice",
        "charge_explanation": "do you want an explanation for a charge",
        "order_status": "are you checking your order status",
        "delivery_issue": "is your delivery late or delayed",
        "fraud_report": "are you reporting a suspicious or unauthorized charge",
    }

    q1 = topic_map.get(t1)
    q2 = topic_map.get(t2)

    if q1 and q2:
        return f"Just to clarify, {q1}, or {q2}?"

    return None

def should_skip_clarification_for_strong_multi_intent(user_text, predicted_topics):
    if not predicted_topics or len(predicted_topics) < 2:
        return False

    normalized = normalize_phrase_text(user_text)

    strong_topic_phrases = {
        "payment_failed": ["payment failed", "card declined", "checkout failed"],
        "refund_request": ["refund", "money back", "return my money"],
        "login_issue": ["cant login", "cannot login", "log in", "sign in"],
        "account_locked": ["account locked", "locked out", "access denied"],
        "double_charge": ["charged twice", "double charge", "billed twice"],
        "order_status": ["where is my order", "track order", "order status"],
        "delivery_issue": ["delivery is late", "late delivery", "package delayed"],
    }

    matches = 0

    for topic in predicted_topics[:2]:
        phrases = strong_topic_phrases.get(topic, [])
        if any(normalize_phrase_text(phrase) in normalized for phrase in phrases):
            matches += 1

    return matches >= 2


def main():
    faq_data = load_faq()
    vectorizer, matrix, mapping = build_tfidf_index(faq_data)
    conversation_state = create_conversation_state()

    print("AI Support Agent is running. Type 'exit' to quit.\n")

    while True:
        user = input("You: ").strip()

        if user.lower() in ["exit", "bye", "quit"]:
            print("Bot: Goodbye!")
            break

        effective_user = user
        skip_clarify_tail = False
        is_followup_clarification = should_treat_as_clarification_followup(user, conversation_state)

        if is_followup_clarification:
            effective_user = merge_with_clarification_context(user, conversation_state)
            print(f"[follow-up merged] {effective_user}")

        sentiment = detect_sentiment(effective_user)
        sentiment_label = sentiment["label"]

        if has_success_signal(effective_user):
            selected = [
                {
                    "topic": "success",
                    "score": 1.0,
                    "action": "answer",
                    "responses": SUCCESS_RESPONSES,
                }
            ]
        if has_success_signal(effective_user):
            selected = [{
                "topic": "success",
                "score": 1.0,
                "action": "answer",
                "responses": SUCCESS_RESPONSES
            }]
        elif has_no_issue_signal(effective_user):
            selected = [{
                "topic": "no_issue",
                "score": 1.0,
                "action": "answer",
                "responses": NO_ISSUE_RESPONSES
            }]
        elif is_vague_query(effective_user):
            domain = detect_clarification_domain(effective_user)

            if domain:
                clarification = generate_domain_clarification(domain)

                if clarification:
                    selected = [{
                        "topic": f"{domain}_clarification",
                        "score": 1.0,
                        "action": "clarify",
                        "responses": [clarification],
                    }]
                else:
                    selected = [DEFAULT_GENERAL_HELP_INTENT]
            else:
                selected = [DEFAULT_GENERAL_HELP_INTENT]

            selected = apply_sentiment_routing(selected, sentiment_label)
        else:
            ranked = detect_intents(
                effective_user,
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
                selected = select_top_intents(ranked, effective_user)
                selected = apply_sentiment_routing(selected, sentiment_label)

        predicted_topics_before_rules = [intent["topic"] for intent in selected]
        pre_rule_confidence = get_confidence(selected)

        selected, routing_reason = apply_confidence_sentiment_rules(
            selected,
            pre_rule_confidence,
            sentiment_label,
    )
        # ensure clarification topics always stay clarify
        for intent in selected:
          if intent["topic"].endswith("_clarification"):
              intent["action"] = "clarify"
        if (
    routing_reason == "low_confidence_multi_intent"
    and should_skip_clarification_for_strong_multi_intent(
        effective_user,
        predicted_topics_before_rules
        )
    ):
            updated = []
            for intent in selected:
                new_intent = intent.copy()
                new_intent["action"] = "answer"
                updated.append(new_intent)
                selected = updated
                routing_reason = "strong_multi_intent_answer"

        if routing_reason == "low_confidence_multi_intent":
            updated = []
            for intent in selected:
                new_intent = intent.copy()
                new_intent["action"] = "clarify"
                updated.append(new_intent)
                selected = updated
        elif routing_reason == "strong_multi_intent_answer":
            updated = []
            for intent in selected:
                new_intent = intent.copy()
                new_intent["action"] = "answer"
                updated.append(new_intent)
            selected = updated

        final_topics_after_rules = [intent["topic"] for intent in selected]

        confidence = get_confidence(selected)
        top1_score, top2_score, score_gap = extract_confidence_details(selected)

        if is_followup_clarification:
            refined_response = get_clarification_refined_response(effective_user, selected)
            if refined_response is not None:
                response = refined_response
                skip_clarify_tail = True

                updated = []
                for intent in selected:
                    new_intent = intent.copy()
                    new_intent["action"] = "answer"
                    updated.append(new_intent)
                selected = updated
            elif routing_reason in {"low_confidence_fallback", "low_confidence_multi_intent"} and len(predicted_topics_before_rules) > 1:
                response = get_low_confidence_multi_intent_response(predicted_topics_before_rules)
            else:
                response = generate_response(selected, sentiment_label=sentiment_label)
        else:
            if routing_reason in {"low_confidence_fallback", "low_confidence_multi_intent"} and len(predicted_topics_before_rules) > 1:
                response = get_low_confidence_multi_intent_response(predicted_topics_before_rules)
            else:
                response = generate_response(selected, sentiment_label=sentiment_label)

        final_topics_after_rules = [intent["topic"] for intent in selected]

        confidence = get_confidence(selected)
        top1_score, top2_score, score_gap = extract_confidence_details(selected)

        primary_intent = selected[0]["topic"] if selected else None
        final_action = get_final_action(selected)

        final_response = add_empathy_and_politeness(
            response,
            sentiment_label,
            final_topics_after_rules,
            pre_rule_confidence,
        )

        final_response = apply_action_tone(
            final_response,
            final_action,
            skip_clarify_tail=skip_clarify_tail
        )
        final_response = apply_confidence_tone(final_response, pre_rule_confidence)

        print(f"Detected sentiment: {sentiment_label}")
        print(f"Predicted topics before rules: {predicted_topics_before_rules}")
        print(f"Final topics after rules: {final_topics_after_rules}")
        print(f"Final action: {final_action} (reason={routing_reason})")
        print(
            f"Confidence: {confidence} "
            f"(pre_rule={pre_rule_confidence}, top1={top1_score}, top2={top2_score}, gap={score_gap})"
        )
        print("Bot:", final_response)

        log_interaction(
            user_message=user,
            intents=selected,
            response=final_response,
            sentiment=sentiment,
            primary_intent=primary_intent,
            final_action=final_action,
            confidence=confidence,
            top1_score=top1_score,
            top2_score=top2_score,
            score_gap=score_gap,
            routing_reason=routing_reason,
            predicted_topics_before_rules=predicted_topics_before_rules,
            final_topics_after_rules=final_topics_after_rules,
        )

        conversation_state["awaiting_clarification"] = final_action == "clarify"
        conversation_state["followup_context_active"] = should_keep_followup_context(
            final_topics_after_rules,
            final_action
        )
        conversation_state["last_user_message"] = user
        conversation_state["last_topics"] = final_topics_after_rules
        conversation_state["last_action"] = final_action
        conversation_state["last_routing_reason"] = routing_reason

        print(f"State: {conversation_state}")


if __name__ == "__main__":
    main()