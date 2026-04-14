import streamlit as st
from src.engine import SupportEngine

st.set_page_config(page_title="AI Support Agent", layout="wide")

if "engine" not in st.session_state:
    st.session_state.engine = SupportEngine()

st.title("AI Support Agent")

user_input = st.text_input("Type your message:")

if st.button("Send") and user_input.strip():
    result = st.session_state.engine.handle_message(user_input)

    st.subheader("Bot Response")
    st.write(result["response"])

    st.subheader("Debug Info")
    st.write("Sentiment:", result["sentiment"])
    st.write("Intents:", result["intents"])
    st.write("Confidence:", result["confidence"])
    st.write("Action:", result["action"])
    st.write("Routing Reason:", result["routing_reason"])
    st.write("Top1 Score:", result["top1_score"])
    st.write("Top2 Score:", result["top2_score"])
    st.write("Score Gap:", result["score_gap"])
    st.write("Predicted Topics Before Rules:", result["predicted_topics_before_rules"])
    st.write("Final Topics After Rules:", result["final_topics_after_rules"])