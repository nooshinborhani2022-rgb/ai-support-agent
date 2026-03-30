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


print("AI Support Agent Started")

while True:
    user_message = input("You: ")

    if user_message.lower() == "bye":
        print("Bot: Goodbye!")
        break

    answer, score, topic = find_best_answer(user_message, faq_data)

    if score >= 2:
        print("Topic:", topic)
        print("Bot:", answer)
    else:
        print("Bot: Sorry, I am not confident about your request.")