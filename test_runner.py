import json
import subprocess
import sys
from pathlib import Path

from main import load_faq, detect_intents, select_top_intents, generate_response


LOG_FILE = "chat_log.jsonl"


TEST_CASES = [
    # password_reset
    {"input": "I forgot my password", "expected": ["password_reset"]},
    {"input": "reset my password", "expected": ["password_reset"]},
    {"input": "cant remember password", "expected": ["password_reset"]},

    # login_issue
    {"input": "I can't log in", "expected": ["login_issue"]},
    {"input": "login not working", "expected": ["login_issue"]},
    {"input": "sign in problem", "expected": ["login_issue"]},

    # account_locked
    {"input": "my account is locked", "expected": ["account_locked"]},
    {"input": "account blocked", "expected": ["account_locked"]},
    {"input": "access denied", "expected": ["account_locked"]},

    # payment_failed
    {"input": "my payment failed", "expected": ["payment_failed"]},
    {"input": "payment not working", "expected": ["payment_failed"]},
    {"input": "card declined", "expected": ["payment_failed"]},

    # charge_explanation
    {"input": "why did you charge me", "expected": ["charge_explanation"]},
    {"input": "I don't understand this charge", "expected": ["charge_explanation"]},
    {"input": "what is this charge", "expected": ["charge_explanation"]},

    # double_charge
    {"input": "I was charged twice", "expected": ["double_charge"]},
    {"input": "double charged", "expected": ["double_charge"]},
    {"input": "duplicate charge on my card", "expected": ["double_charge"]},

    # refund_request
    {"input": "I want a refund", "expected": ["refund_request"]},
    {"input": "refund pls", "expected": ["refund_request"]},
    {"input": "give me my money back", "expected": ["refund_request"]},

    # billing_question
    {"input": "I have a billing question", "expected": ["billing_question"]},
    {"input": "billing help", "expected": ["billing_question"]},
    {"input": "I don't understand this invoice", "expected": ["billing_question"]},

    # subscription_cancel
    {"input": "cancel my subscription", "expected": ["subscription_cancel"]},
    {"input": "unsubscribe", "expected": ["subscription_cancel"]},

    # fraud_report
    {"input": "someone used my card", "expected": ["fraud_report"]},
    {"input": "this is fraud", "expected": ["fraud_report"]},

    # order_status
    {"input": "where is my order", "expected": ["order_status"]},
    {"input": "order?", "expected": ["order_status"]},
    {"input": "track my package", "expected": ["order_status"]},

    # delivery_issue
    {"input": "my delivery is late", "expected": ["delivery_issue"]},
    {"input": "package not arrived", "expected": ["delivery_issue"]},

    # general_help
    {"input": "I need help", "expected": ["general_help"]},
    {"input": "help me", "expected": ["general_help"]},
    {"input": "I have a problem", "expected": ["general_help"]},

    # multi-intent
    {"input": "my payment failed and I can't log in", "expected": ["payment_failed", "login_issue"]},
    {"input": "I was charged twice and I want a refund", "expected": ["double_charge", "refund_request"]},
    {"input": "access denied and I can't log in", "expected": ["account_locked", "login_issue"]},
    {"input": "my delivery is late and where is my order", "expected": ["order_status", "delivery_issue"]},
]


def clear_log(file_path=LOG_FILE):
    Path(file_path).write_text("", encoding="utf-8")


def append_log(user_message, selected_intents, response, file_path=LOG_FILE):
    log_entry = {
        "user_message": user_message,
        "intents": [
            {
                "topic": intent["topic"],
                "score": intent["score"],
                "action": intent["action"]
            }
            for intent in selected_intents
        ],
        "primary_intent": selected_intents[0]["topic"] if selected_intents else None,
        "response": response
    }

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


def normalize_expected(expected):
    return sorted(expected)


def normalize_predicted(selected):
    return sorted([intent["topic"] for intent in selected])


def run_tests():
    faq_data = load_faq()
    clear_log()

    passed = 0
    failed = 0

    print("\nRunning full validation suite...\n")

    for i, case in enumerate(TEST_CASES, start=1):
        user_text = case["input"]
        expected = normalize_expected(case["expected"])

        ranked = detect_intents(user_text, faq_data)
        selected = select_top_intents(ranked, user_text)
        response = generate_response(selected)

        predicted = normalize_predicted(selected)
        ok = predicted == expected

        append_log(user_text, selected, response)

        status = "PASS" if ok else "FAIL"
        print(f"{i:02d}. {status}")
        print(f"Input:     {user_text}")
        print(f"Expected:  {expected}")
        print(f"Predicted: {predicted}")
        print(f"Response:  {response}\n")

        if ok:
            passed += 1
        else:
            failed += 1

    total = passed + failed
    accuracy = (passed / total) * 100 if total else 0

    print("=" * 60)
    print(f"Passed:   {passed}")
    print(f"Failed:   {failed}")
    print(f"Accuracy: {accuracy:.2f}%")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_tests()

    print("\nSaved test interactions to chat_log.jsonl")

    print("\nRunning analyze_logs.py...\n")
    try:
        subprocess.run([sys.executable, "analyze_logs.py"], check=False)
    except Exception as e:
        print(f"Could not run analyze_logs.py: {e}")

    if success:
        print("\nAll tests passed.")
    else:
        print("\nSome tests failed. Review the failed cases above.")