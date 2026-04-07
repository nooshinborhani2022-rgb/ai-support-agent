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
    final_actions = Counter()
    sentiment_counts = Counter()
    fallback_count = 0

    fallback_queries = []
    multi_intent_queries = []

    for log in logs:
        primary_intent = log.get("primary_intent")
        response = log.get("response", "")
        intents = log.get("intents", [])
        user_message = log.get("user_message", "")
        sentiment = log.get("sentiment", {})
        final_action = log.get("final_action")

        if primary_intent:
            primary_intents[primary_intent] += 1

        for intent in intents:
            action = intent.get("action")
            if action:
                actions[action] += 1

        if final_action:
            final_actions[final_action] += 1

        sentiment_label = sentiment.get("label")
        if sentiment_label:
            sentiment_counts[sentiment_label] += 1

        if "I didn’t understand" in response or "Could you rephrase" in response:
            fallback_count += 1
            fallback_queries.append(user_message)

        if len(intents) > 1:
            multi_intent_queries.append(user_message)

    print("\n=== Log Analysis Report ===")
    print(f"Total messages: {total_messages}")
    print(f"Fallback responses: {fallback_count}")

    print("\nTop primary intents:")
    for intent, count in primary_intents.most_common():
        print(f"- {intent}: {count}")

    print("\nAction counts (per intent):")
    for action, count in actions.most_common():
        print(f"- {action}: {count}")

    print("\nFinal action distribution:")
    for action, count in final_actions.most_common():
        print(f"- {action}: {count}")

    print("\nSentiment distribution:")
    for label, count in sentiment_counts.most_common():
        print(f"- {label}: {count}")

    print("\nFallback queries:")
    for q in fallback_queries[:10]:
        print(f"- {q}")

    print("\nMulti-intent queries:")
    for q in multi_intent_queries[:10]:
        print(f"- {q}")


def main():
    logs = load_logs()
    analyze_logs(logs)


if __name__ == "__main__":
    main()