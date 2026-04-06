from src.main import (
    load_faq,
    build_tfidf_index,
    detect_intents,
    select_top_intents,
    generate_response,
)
from src.sentiment import detect_sentiment

import json
import subprocess


TEST_CASES = [
    {"input": "I forgot my password", "expected": ["password_reset"]},
    {"input": "reset my password", "expected": ["password_reset"]},
    {"input": "cant remember password", "expected": ["password_reset"]},

    {"input": "I can't log in", "expected": ["login_issue"]},
    {"input": "login not working", "expected": ["login_issue"]},
    {"input": "sign in problem", "expected": ["login_issue"]},

    {"input": "my account is locked", "expected": ["account_locked"]},
    {"input": "account blocked", "expected": ["account_locked"]},
    {"input": "access denied", "expected": ["account_locked"]},

    {"input": "my payment failed", "expected": ["payment_failed"]},
    {"input": "payment not working", "expected": ["payment_failed"]},
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
    {"input": "billing help", "expected": ["billing_question"]},
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

    # regression tests for ambiguity handling
    {"input": "it's not working", "expected": ["general_help"]},
    {"input": "I need billing help", "expected": ["billing_question"]},
    {"input": "I want a refund", "expected": ["refund_request"]},
]


SENTIMENT_TEST_CASES = [
    {"input": "where is my order", "expected": "neutral"},
    {"input": "this is not working", "expected": "frustrated"},
    {"input": "this is terrible!", "expected": "angry"},
    {"input": "I need help ASAP", "expected": "urgent"},
]


def save_test_logs(logs, file_path="chat_log.jsonl"):
    with open(file_path, "w", encoding="utf-8") as f:
        for entry in logs:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


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

        ranked = detect_intents(user_text, faq_data, vectorizer, matrix, mapping)
        selected = select_top_intents(ranked, user_text)
        predicted = sorted([intent["topic"] for intent in selected])
        response = generate_response(selected)
        sentiment = detect_sentiment(user_text)

        success = predicted == expected

        if success:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"

        print(f"{idx:02d}. {status}")
        print(f"Input:     {user_text}")
        print(f"Expected:  {expected}")
        print(f"Predicted: {predicted}")
        print(f"Sentiment: {sentiment['label']}")
        print(f"Response:  {response}\n")

        logs.append({
            "user_message": user_text,
            "intents": selected,
            "response": response,
            "primary_intent": selected[0]["topic"] if selected else None,
            "sentiment": sentiment,
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


def run_tests():
    intent_ok = run_intent_tests()
    sentiment_ok = run_sentiment_tests()

    print("\nRunning analyze_logs.py...\n")
    subprocess.run(["python", "analyze_logs.py"])

    if intent_ok and sentiment_ok:
        print("\nAll tests passed.")
    else:
        print("\nSome tests failed. Review the failed cases above.")


if __name__ == "__main__":
    run_tests()