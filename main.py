print("AI Support Agent Started")

while True:
    user_message = input("You: ")

    if user_message.lower() == "hello":
        print("Bot: Hi! How can I help you today?")
    elif user_message.lower() == "refund":
        print("Bot: I can help with refund requests.")
    elif user_message.lower() == "bye":
        print("Bot: Goodbye!")
        break
    else:
        print("Bot: Sorry, I do not understand your request yet.")