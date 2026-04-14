import streamlit as st

def handle_message(user_input):
    
    return {
        "response": f"You said: {user_input}",
        "sentiment": "neutral",
        "intents": ["test_intent"],
        "confidence": 0.9,
        "action": "answer"
    }

st.set_page_config(page_title="AI Support Agent", layout="wide")

st.title("AI Support Agent")

user_input = st.text_input("Type your message:")

if st.button("Send"):
    result = handle_message(user_input)

    st.subheader("Bot Response")
    st.write(result["response"])

    st.subheader("Debug Info")
    st.write("Sentiment:", result["sentiment"])
    st.write("Intents:", result["intents"])
    st.write("Confidence:", result["confidence"])
    st.write("Action:", result["action"])