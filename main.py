import json
from datetime import datetime


def load_faq(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def log_chat(user_message, topic, score, action_result):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_message": user_message,
        "topic": topic,
        "score": score,
        "action": action_result
    }

    with open("chat_log.jsonl", "a") as log_file:
        log_file.write(json.dumps(log_entry) + "\n")


def find_best_answer(user_input, faq_data):
    user_words = set(user_input.lower().split())

    best_score = 0
    best_answer = None
    best_topic = None
    best_action = None

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
            best_action = item["action"]

    return best_answer, best_score, best_topic, best_action


faq_data = load_faq("faq.json")

print("Chatbot is ready! Type 'bye' to exit.")

while True:
    user_message = input("You: ")

    if user_message.lower() == "bye":
        print("Bot: Goodbye!")
        break

    answer, score, topic, action = find_best_answer(user_message, faq_data)

    if score >= 2:
        if action == "answer":
            print("Bot:", answer)
            log_chat(user_message, topic, score, "answered")

        elif action == "escalate":
            print("Bot: This issue needs human support.")
            print("Bot: I will escalate this to a human agent.")
            log_chat(user_message, topic, score, "escalated")

        else:
            print("Bot:", answer)
            log_chat(user_message, topic, score, "answered")

    else:
        print("Bot: Sorry, I am not confident about your request.")
        log_chat(user_message, "unknown", score, "not_confident")