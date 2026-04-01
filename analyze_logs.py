import json
from collections import Counter


def load_logs(file_path="chat_log.jsonl"):
    logs = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            logs.append(json.loads(line))

    return logs


def analyze_logs(logs):
    total_messages = len(logs)
    primary_intents = Counter()
    actions = Counter()
    fallback_count = 0

    for log in logs:
        primary_intent = log.get("primary_intent")
        response = log.get("response", "")
        intents = log.get("intents", [])

        if primary_intent:
            primary_intents[primary_intent] += 1

        for intent in intents:
            action = intent.get("action")
            if action:
                actions[action] += 1

        if "I didn’t understand" in response or "Could you rephrase" in response:
            fallback_count += 1

    print("\n=== Log Analysis Report ===")
    print(f"Total messages: {total_messages}")
    print(f"Fallback responses: {fallback_count}")

    print("\nTop primary intents:")
    for intent, count in primary_intents.most_common():
        print(f"- {intent}: {count}")

    print("\nAction counts:")
    for action, count in actions.most_common():
        print(f"- {action}: {count}")


def main():
    logs = load_logs()
    analyze_logs(logs)


if __name__ == "__main__":
    main()