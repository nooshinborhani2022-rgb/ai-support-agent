import json

with open("faq.json", "r") as file:
    faq_data = json.load(file)


def find_best_answer(user_input, faq_data):
    user_words = set(user_input.lower().split())

    best_score = 0
    best_answer = None
    best_topic = None

    for item in faq_data:
        for question in item["questions"]:
            question_words = set(question.lower().split())

            common_words = user_words & question_words
            score = len(common_words)

            if score > best_score:
                best_score = score
                best_answer = item["answer"]
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

        elif topic == "refund":
            print("Bot:", answer)
            print("Bot: If you need more help, contact support@example.com")
            log_chat(user_message, topic, score, "answered")

        elif topic == "payment_issue":
            print("Bot: This seems like a payment issue.")
            print("Bot: I will escalate this to a human agent.")
            log_chat(user_message, topic, score, "escalated")

        else:
            print("Bot:", answer)
            log_chat(user_message, topic, score, "answered")

    else:
        print("Bot: Sorry, I am not confident about your request.")
        log_chat(user_message, "unknown", score, "not_confident")