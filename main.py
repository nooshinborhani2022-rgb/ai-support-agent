import random
import json
from datetime import datetime

STOPWORDS = {
    "i", "a", "the", "is", "to", "my", "you", "me",
    "and", "of", "in", "on", "for", "it", "this"
}


def load_faq(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def log_chat(user_message, topic, score, action_result):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_message": user_message,
        "topic": topic,
        "score": score,
        "action": action_result
    }

    with open("chat_log.jsonl", "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(log_entry) + "\n")


def normalize_text(text):
    text = text.lower()

    for ch in [".", ",", "!", "?", ":", ";", "'", '"']:
        text = text.replace(ch, "")

    words = text.split()
    filtered_words = [word for word in words if word not in STOPWORDS]

    return filtered_words


def find_best_answer(user_input, faq_data):
    user_words = set(normalize_text(user_input))

    best_score = 0
    best_answer = None
    best_topic = None
    best_action = None

    for item in faq_data:
        example_score = 0
        keyword_score = 0

        for example in item["examples"]:
            example_words = set(normalize_text(example))
            common_words = user_words & example_words
            score = len(common_words)

            if score > example_score:
                example_score = score

        for keyword in item["keywords"]:
            keyword_words = set(normalize_text(keyword))
            common_words = user_words & keyword_words
            keyword_score += len(common_words)

        total_score = (example_score * 2) + keyword_score

        if total_score > best_score:
            best_score = total_score
            best_answer = random.choice(item["responses"])
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

        elif action == "clarify":
            print("Bot:", answer)
            log_chat(user_message, topic, score, "clarify")

        elif action == "escalate":
            print("Bot:", answer)
            log_chat(user_message, topic, score, "escalated")

        else:
            print("Bot:", answer)
            log_chat(user_message, topic, score, "answered")

    else:
        print("Bot: Can you please clarify your request?")
        log_chat(user_message, "unknown", score, "clarify")