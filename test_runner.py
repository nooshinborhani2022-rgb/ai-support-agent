from src.main import (
    load_faq,
    build_tfidf_index,
    detect_intents,
    select_top_intents,
    generate_response,
    apply_sentiment_routing,
    get_final_action,
    get_confidence,
    apply_confidence_sentiment_rules,
    has_success_signal,
    has_no_issue_signal,
    SUCCESS_RESPONSES,
    NO_ISSUE_RESPONSES,
    create_conversation_state,
    should_treat_as_clarification_followup,
    merge_with_clarification_context,
    get_clarification_refined_response,
    is_vague_query,
    detect_clarification_domain,
    generate_domain_clarification,
    DEFAULT_GENERAL_HELP_INTENT,
)
from src.sentiment import detect_sentiment

import json
import subprocess
import sys


TEST_CASES = [
    {"input": "I forgot my password", "expected": ["password_reset"]},
    {"input": "reset my password", "expected": ["password_reset"]},
    {"input": "cant remember password", "expected": ["password_reset"]},

    {"input": "I can't log in", "expected": ["login_issue"]},
    {"input": "login not working", "expected": ["account_clarification"]},
    {"input": "sign in problem", "expected": ["account_clarification"]},

    {"input": "my account is locked", "expected": ["account_locked"]},
    {"input": "account blocked", "expected": ["account_locked"]},
    {"input": "access denied", "expected": ["account_locked"]},

    {"input": "my payment failed", "expected": ["payment_failed"]},
    {"input": "payment not working", "expected": ["payment_clarification"]},
    {"input": "card declined", "expected": ["payment_failed"]},

    {"input": "why did you charge me", "expected": ["charge_explanation"]},
    {"input": "I don't understand this charge", "expected": ["charge_explanation"]},
    {"input": "what is this charge", "expected": ["charge_explanation"]},

    {"input": "I was charged twice", "expected": ["double_charge"]},
    {"input": "double charged", "expected": ["double_charge"]},
    {"input": "duplicate charge on my card", "expected": ["double_charge"]},

    {"input": "I want a refund", "expected": ["refund_request"]},
    {"input": "refund pls", "expected": ["refund_request"]},
    {"input": "give me my money back", "expected": ["refund_request"]},

    {"input": "I have a billing question", "expected": ["billing_question"]},
    {"input": "billing help", "expected": ["billing_clarification"]},
    {"input": "I don't understand this invoice", "expected": ["billing_question"]},

    {"input": "cancel my subscription", "expected": ["subscription_cancel"]},
    {"input": "unsubscribe", "expected": ["subscription_cancel"]},

    {"input": "someone used my card", "expected": ["fraud_report"]},
    {"input": "this is fraud", "expected": ["fraud_report"]},

    {"input": "where is my order", "expected": ["order_status"]},
    {"input": "order?", "expected": ["order_status"]},
    {"input": "track my package", "expected": ["order_status"]},

    {"input": "my delivery is late", "expected": ["delivery_issue"]},
    {"input": "package not arrived", "expected": ["delivery_issue"]},

    {"input": "I need help", "expected": ["general_help"]},
    {"input": "help me", "expected": ["general_help"]},
    {"input": "I have a problem", "expected": ["general_help"]},

    {"input": "my payment failed and I can't log in", "expected": ["login_issue", "payment_failed"]},
    {"input": "I was charged twice and I want a refund", "expected": ["double_charge", "refund_request"]},
    {"input": "access denied and I can't log in", "expected": ["account_locked", "login_issue"]},
    {"input": "my delivery is late and where is my order", "expected": ["delivery_issue", "order_status"]},

    {"input": "I can't log in", "expected": ["login_issue"]},
    {"input": "I'm being charged twice", "expected": ["double_charge"]},
    {"input": "I need general help", "expected": ["general_help"]},

    {"input": "it's not working", "expected": ["general_help"]},
    {"input": "I need billing help", "expected": ["billing_clarification"]},
    {"input": "I want a refund", "expected": ["refund_request"]},

    {"input": "I cant login and I was charged twice", "expected": ["login_issue", "double_charge"]},
    {"input": "my payment failed and I want a refund", "expected": ["payment_failed", "refund_request"]},
    {"input": "access denied and I can't log in", "expected": ["account_locked", "login_issue"]},
    {"input": "I was charged twice and I want a refund ASAP", "expected": ["double_charge", "refund_request"]},

    {"input": "I need help ASAP, I can't log in and my payment failed", "expected": ["account_clarification"]},

    {"input": "I can login", "expected": ["success"]},
    {"input": "It works now", "expected": ["success"]},
    {"input": "I was not charged twice", "expected": ["no_issue"]},
    {"input": "I am not locked out", "expected": ["no_issue"]},

    {"input": "I was charged and need help", "expected": ["charge_clarification"]},
    {"input": "I have an issue with my account", "expected": ["account_clarification"]},
    {"input": "I have a payment problem", "expected": ["payment_clarification"]},
    {"input": "There is a problem with my order", "expected": ["order_clarification"]},
]


SENTIMENT_TEST_CASES = [
    {"input": "where is my order", "expected": "neutral"},
    {"input": "this is not working", "expected": "frustrated"},
    {"input": "this is terrible!", "expected": "angry"},
    {"input": "I am very angry!!!", "expected": "angry"},
    {"input": "I need help ASAP", "expected": "urgent"},
]


ROUTING_TEST_CASES = [
    {
        "input": "I need help ASAP",
        "expected_sentiment": "urgent",
        "expected_final_action": "answer",
    },
    {
        "input": "this is terrible, my payment failed",
        "expected_sentiment": "angry",
        "expected_final_action": "escalate",
    },
    {
        "input": "it's not working",
        "expected_sentiment": "frustrated",
        "expected_final_action": "answer",
    },
    {
        "input": "I can login",
        "expected_sentiment": "neutral",
        "expected_final_action": "answer",
    },
    {
        "input": "I was not charged twice",
        "expected_sentiment": "neutral",
        "expected_final_action": "answer",
    },
    {
        "input": "I was charged and need help",
        "expected_sentiment": "neutral",
        "expected_final_action": "clarify",
    },
    {
        "input": "I have an issue with my account",
        "expected_sentiment": "frustrated",
        "expected_final_action": "clarify",
    },
    {
        "input": "I have a payment problem",
        "expected_sentiment": "frustrated",
        "expected_final_action": "clarify",
    },
    {
        "input": "There is a problem with my order",
        "expected_sentiment": "frustrated",
        "expected_final_action": "clarify",
    },
]


MULTITURN_TEST_CASES = [
    {
        "name": "payment clarification follow-up",
        "initial_user": "I have a payment problem",
        "followup_user": "my card was declined",
        "expected_merged": "I have a payment problem my card was declined",
        "selected_intents": [
            {"topic": "payment_clarification", "score": 1.0, "action": "clarify", "responses": []},
        ],
        "expected_keywords": [],
    },
    {
        "name": "account clarification follow-up",
        "initial_user": "I have an issue with my account",
        "followup_user": "I already tried reset",
        "expected_merged": "I have an issue with my account I already tried reset",
        "selected_intents": [
            {"topic": "account_clarification", "score": 1.0, "action": "clarify", "responses": []},
        ],
        "expected_keywords": [],
    },
]


def save_test_logs(logs, file_path="chat_log.jsonl"):
    with open(file_path, "w", encoding="utf-8") as f:
        for entry in logs:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def build_special_case_selection(user_text):
    if has_success_signal(user_text):
        return [{
            "topic": "success",
            "score": 1.0,
            "action": "answer",
            "responses": SUCCESS_RESPONSES
        }]

    if has_no_issue_signal(user_text):
        return [{
            "topic": "no_issue",
            "score": 1.0,
            "action": "answer",
            "responses": NO_ISSUE_RESPONSES
        }]

    return None


def build_selection_like_main(user_text, faq_data, vectorizer, matrix, mapping, sentiment_label):
    selected = build_special_case_selection(user_text)

    if selected is not None:
        return selected

    if is_vague_query(user_text):
        domain = detect_clarification_domain(user_text)

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
        return selected

    ranked = detect_intents(
        user_text,
        faq_data,
        vectorizer,
        matrix,
        mapping,
        sentiment_label=sentiment_label
    )

    if not ranked:
        return [{
            "topic": "no_issue",
            "score": 1.0,
            "action": "answer",
            "responses": NO_ISSUE_RESPONSES
        }]

    selected = select_top_intents(ranked, user_text)
    selected = apply_sentiment_routing(selected, sentiment_label)
    return selected


def apply_post_rule_action_alignment(final_selected, routing_reason):
    if routing_reason == "low_confidence_multi_intent":
        updated = []
        for intent in final_selected:
            new_intent = intent.copy()
            new_intent["action"] = "clarify"
            updated.append(new_intent)
        return updated

    if routing_reason == "strong_multi_intent_answer":
        updated = []
        for intent in final_selected:
            new_intent = intent.copy()
            new_intent["action"] = "answer"
            updated.append(new_intent)
        return updated

    updated = []
    for intent in final_selected:
        new_intent = intent.copy()
        if new_intent["topic"].endswith("_clarification"):
            new_intent["action"] = "clarify"
        updated.append(new_intent)

    return updated


def run_intent_tests():
    faq_data = load_faq()
    vectorizer, matrix, mapping = build_tfidf_index(faq_data)

    passed = 0
    failed = 0
    logs = []

    print("\nRunning intent validation suite...\n")

    for idx, test in enumerate(TEST_CASES, start=1):
        user_text = test["input"]
        expected = sorted(test["expected"])

        sentiment = detect_sentiment(user_text)
        sentiment_label = sentiment["label"]

        selected = build_selection_like_main(
            user_text,
            faq_data,
            vectorizer,
            matrix,
            mapping,
            sentiment_label,
        )

        predicted = sorted([intent["topic"] for intent in selected])
        predicted_topics_before_rules = [intent["topic"] for intent in selected]

        pre_rule_confidence = get_confidence(selected)

        final_selected, routing_reason = apply_confidence_sentiment_rules(
            selected,
            pre_rule_confidence,
            sentiment_label
        )

        final_selected = apply_post_rule_action_alignment(final_selected, routing_reason)

        final_topics_after_rules = [intent["topic"] for intent in final_selected]

        confidence = get_confidence(final_selected)
        top1_score = final_selected[0]["score"] if final_selected else 0.0
        top2_score = final_selected[1]["score"] if len(final_selected) > 1 else 0.0
        score_gap = round(top1_score - top2_score, 3)

        response = generate_response(final_selected, sentiment_label=sentiment_label)
        final_action = get_final_action(final_selected)

        success = predicted == expected

        if success:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"

        print(f"{idx:02d}. {status}")
        print(f"Input:          {user_text}")
        print(f"Expected:       {expected}")
        print(f"Predicted:      {predicted}")
        print(f"Sentiment:      {sentiment_label}")
        print(f"Final action:   {final_action}")
        print(f"Routing reason: {routing_reason}")
        print(f"Confidence:     {confidence:.3f} (top1={top1_score}, top2={top2_score}, gap={score_gap})")
        print(f"Response:       {response}\n")

        logs.append({
            "user_message": user_text,
            "intents": final_selected,
            "response": response,
            "primary_intent": final_selected[0]["topic"] if final_selected else None,
            "sentiment": sentiment,
            "final_action": final_action,
            "confidence": round(confidence, 3),
            "top1_score": top1_score,
            "top2_score": top2_score,
            "score_gap": score_gap,
            "routing_reason": routing_reason,
            "predicted_topics_before_rules": predicted_topics_before_rules,
            "final_topics_after_rules": final_topics_after_rules,
        })

    total = passed + failed
    accuracy = (passed / total) * 100 if total > 0 else 0

    print("=" * 60)
    print(f"Intent Tests Passed:   {passed}")
    print(f"Intent Tests Failed:   {failed}")
    print(f"Intent Accuracy:       {accuracy:.2f}%")
    print("=" * 60)

    save_test_logs(logs)
    print("\nSaved test interactions to chat_log.jsonl\n")

    return failed == 0


def run_sentiment_tests():
    passed = 0
    failed = 0

    print("\nRunning sentiment validation suite...\n")

    for idx, test in enumerate(SENTIMENT_TEST_CASES, start=1):
        user_text = test["input"]
        expected = test["expected"]

        result = detect_sentiment(user_text)
        predicted = result["label"]

        success = predicted == expected

        if success:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"

        print(f"S{idx:02d}. {status}")
        print(f"Input:     {user_text}")
        print(f"Expected:  {expected}")
        print(f"Predicted: {predicted}")
        print(f"Details:   {result}\n")

    total = passed + failed
    accuracy = (passed / total) * 100 if total > 0 else 0

    print("=" * 60)
    print(f"Sentiment Tests Passed:   {passed}")
    print(f"Sentiment Tests Failed:   {failed}")
    print(f"Sentiment Accuracy:       {accuracy:.2f}%")
    print("=" * 60)

    return failed == 0


def run_routing_tests():
    faq_data = load_faq()
    vectorizer, matrix, mapping = build_tfidf_index(faq_data)

    passed = 0
    failed = 0

    print("\nRunning routing validation suite...\n")

    for idx, test in enumerate(ROUTING_TEST_CASES, start=1):
        user_text = test["input"]
        expected_sentiment = test["expected_sentiment"]
        expected_final_action = test["expected_final_action"]

        sentiment = detect_sentiment(user_text)
        sentiment_label = sentiment["label"]

        selected = build_selection_like_main(
            user_text,
            faq_data,
            vectorizer,
            matrix,
            mapping,
            sentiment_label,
        )

        confidence = get_confidence(selected)

        final_selected, routing_reason = apply_confidence_sentiment_rules(
            selected,
            confidence,
            sentiment_label
        )

        final_selected = apply_post_rule_action_alignment(final_selected, routing_reason)

        final_action = get_final_action(final_selected)

        success = (
            sentiment_label == expected_sentiment
            and final_action == expected_final_action
        )

        if success:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"

        print(f"R{idx:02d}. {status}")
        print(f"Input:                {user_text}")
        print(f"Expected sentiment:   {expected_sentiment}")
        print(f"Predicted sentiment:  {sentiment_label}")
        print(f"Expected action:      {expected_final_action}")
        print(f"Predicted action:     {final_action}")
        print(f"Routing reason:       {routing_reason}")
        print(f"Confidence:           {confidence:.3f}\n")

    total = passed + failed
    accuracy = (passed / total) * 100 if total > 0 else 0

    print("=" * 60)
    print(f"Routing Tests Passed:   {passed}")
    print(f"Routing Tests Failed:   {failed}")
    print(f"Routing Accuracy:       {accuracy:.2f}%")
    print("=" * 60)

    return failed == 0


def run_multiturn_tests():
    passed = 0
    failed = 0

    print("\nRunning multi-turn clarification suite...\n")

    for idx, test in enumerate(MULTITURN_TEST_CASES, start=1):
        state = create_conversation_state()
        state["awaiting_clarification"] = True
        state["last_user_message"] = test["initial_user"]
        state["last_topics"] = [intent["topic"] for intent in test["selected_intents"]]
        state["last_action"] = "clarify"
        state["last_routing_reason"] = "normal_routing"

        is_followup = should_treat_as_clarification_followup(test["followup_user"], state)
        merged = merge_with_clarification_context(test["followup_user"], state)
        refined = get_clarification_refined_response(merged, test["selected_intents"])

        checks = [
            is_followup is True,
            merged == test["expected_merged"],
        ]

        if test["expected_keywords"]:
            checks.append(refined is not None)
            if refined is not None:
                for keyword in test["expected_keywords"]:
                    checks.append(keyword.lower() in refined.lower())

        success = all(checks)

        if success:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"

        print(f"M{idx:02d}. {status}")
        print(f"Initial user:   {test['initial_user']}")
        print(f"Follow-up:      {test['followup_user']}")
        print(f"Is follow-up:   {is_followup}")
        print(f"Merged text:    {merged}")
        print(f"Refined:        {refined}\n")

    total = passed + failed
    accuracy = (passed / total) * 100 if total > 0 else 0

    print("=" * 60)
    print(f"Multi-turn Tests Passed:   {passed}")
    print(f"Multi-turn Tests Failed:   {failed}")
    print(f"Multi-turn Accuracy:       {accuracy:.2f}%")
    print("=" * 60)

    return failed == 0


def run_tests():
    intent_ok = run_intent_tests()
    sentiment_ok = run_sentiment_tests()
    routing_ok = run_routing_tests()
    multiturn_ok = run_multiturn_tests()

    print("\nRunning analyze_logs.py...\n")
    subprocess.run([sys.executable, "analyze_logs.py"])

    if intent_ok and sentiment_ok and routing_ok and multiturn_ok:
        print("\nAll tests passed.")
    else:
        print("\nSome tests failed. Review the failed cases above.")


if __name__ == "__main__":
    run_tests()