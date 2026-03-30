import json

with open("faq.json", "r") as file:
    faq_data = json.load(file)

def find_answer(user_input, faq_data):
    user_input = user_input.lower()

    for item in faq_data:
        for question in item["questions"]:
            if user_input in question.lower():
                return item["answer"]

    return None

print("AI Support Agent Started")

while True:
    user_message = input("You: ")

    if user_message.lower() == "bye":
        print("Bot: Goodbye!")
        break

    answer = find_answer(user_message, faq_data)

    if answer:
        print("Bot:", answer)
    else:
        print("Bot: Sorry, I do not understand your request yet.")