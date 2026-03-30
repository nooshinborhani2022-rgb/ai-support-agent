import json

with open("faq.json", "r") as file:
    faq_data = json.load(file)


def find_best_answer(user_input, faq_data):
    user_words = set(user_input.lower().split())

    best_score = 0
    best_answer = None
    best_topic = None

    for item in faq_data:
        example_score = 0
        keyword_score = 0

        for example in item["examples"]:
            example_words = set(example.lower().split())
            common_words = user_words & example_words
            score = len(common_words)

            if score > example_score:
                example_score = score

        for keyword in item["keywords"]:
            keyword_words = set(keyword.lower().split())
            common_words = user_words & keyword_words
            keyword_score += len(common_words)

        total_score = example_score + keyword_score

        if total_score > best_score:
            best_score = total_score
            best_answer = item["response"]
            best_topic = item["topic"]

    return best_answer, best_score, best_topic


def log_chat(user_message, topic, score, action):
    log_entry = {
        "user": user_message,
        "topic": topic,
        "score": score,
        "action": action
    }

    with open("chat_log.jsonl", "a") as log_file:
        log_file.write(json.dumps(log_entry) + "\n")


print("AI Support Agent Started")

while True:
    user_message = input("You: ")

    if user_message.lower() == "bye":
        print("Bot: Goodbye!")
        break

    answer, score, topic = find_best_answer(user_message, faq_data)

    if score >= 2:
        if topic == "password_reset":
            print("Bot:", answer)
            log_chat(user_message, topic, score, "answered")
        elif topic == "refund_request":
            print("Bot:", answer)
            print("Bot: If you need more help, contact support@example.com")
            log_chat(user_message, topic, score, "answered")
        elif topic == "payment_failed":
            print("Bot: This seems like a payment issue.")
            print("Bot: I will escalate this to a human agent.")
            log_chat(user_message, topic, score, "escalated")
        else:
            print("Bot:", answer)
            log_chat(user_message, topic, score, "answered")
    else:
        print("Bot: Sorry, I am not confident about your request.")
        log_chat(user_message, "unknown", score, "not_confident")