import json

with open("faq.json", "r") as file:
    faq_data = json.load(file)


def find_best_answer(user_input, faq_data):
    user_words = set(user_input.lower().split())

    best_score = 0
    best_answer = None

    for item in faq_data:
        for question in item["questions"]:
            question_words = set(question.lower().split())

            common_words = user_words & question_words
            score = len(common_words)

            if score > best_score:
                best_score = score
                best_answer = item["answer"]

    return best_answer


print("AI Support Agent Started")

while True:
    user_message = input("You: ")

    if user_message.lower() == "bye":
        print("Bot: Goodbye!")
        break

    answer = find_best_answer(user_message, faq_data)

    if answer:
        print("Bot:", answer)
    else:
        print("Bot: Sorry, I do not understand your request yet.")