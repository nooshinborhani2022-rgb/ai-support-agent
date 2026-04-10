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
    routing_reasons = Counter()

    fallback_count = 0
    fallback_queries = []

    final_multi_intent_queries = []
    raw_multi_intent_queries = []
    reduced_multi_intent_queries = []

    confidence_values = []
    score_gaps = []

    for log in logs:
        primary_intent = log.get("primary_intent")
        response = log.get("response", "")
        intents = log.get("intents", [])
        user_message = log.get("user_message", "")
        sentiment = log.get("sentiment", {})
        final_action = log.get("final_action")
        routing_reason = log.get("routing_reason")
        confidence = log.get("confidence")
        score_gap = log.get("score_gap")

        predicted_topics_before_rules = log.get("predicted_topics_before_rules", [])
        final_topics_after_rules = log.get("final_topics_after_rules", [])

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

        if routing_reason:
            routing_reasons[routing_reason] += 1

        if confidence is not None:
            confidence_values.append(confidence)

        if score_gap is not None:
            score_gaps.append(score_gap)

        if "I didn’t understand" in response or "Could you rephrase" in response:
            fallback_count += 1
            fallback_queries.append(user_message)

        if len(predicted_topics_before_rules) > 1:
            raw_multi_intent_queries.append(user_message)

        if len(final_topics_after_rules) > 1:
            final_multi_intent_queries.append(user_message)

        if len(predicted_topics_before_rules) > 1 and len(final_topics_after_rules) <= 1:
            reduced_multi_intent_queries.append(user_message)

    avg_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0.0
    avg_score_gap = sum(score_gaps) / len(score_gaps) if score_gaps else 0.0

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

    print("\nRouting reason distribution:")
    for reason, count in routing_reasons.most_common():
        print(f"- {reason}: {count}")

    print(f"\nAverage confidence: {avg_confidence:.3f}")
    print(f"Average score gap: {avg_score_gap:.3f}")

    print("\nExplainability summary:")
    print(f"- low_confidence_fallback: {routing_reasons.get('low_confidence_fallback', 0)}")
    print(f"- sentiment_override_angry: {routing_reasons.get('sentiment_override_angry', 0)}")
    print(f"- sentiment_override_frustrated: {routing_reasons.get('sentiment_override_frustrated', 0)}")

    print(f"\nRaw multi-intent query count (before rules): {len(raw_multi_intent_queries)}")
    print(f"Final multi-intent query count (after rules): {len(final_multi_intent_queries)}")
    print(f"Reduced multi-intent query count: {len(reduced_multi_intent_queries)}")

    print("\nFallback queries:")
    for q in fallback_queries[:10]:
        print(f"- {q}")

    print("\nRaw multi-intent queries (before rules):")
    for q in raw_multi_intent_queries[:10]:
        print(f"- {q}")

    print("\nFinal multi-intent queries (after rules):")
    for q in final_multi_intent_queries[:10]:
        print(f"- {q}")

    print("\nReduced multi-intent queries:")
    for q in reduced_multi_intent_queries[:10]:
        print(f"- {q}")


def main():
    logs = load_logs()
    analyze_logs(logs)


if __name__ == "__main__":
    main()