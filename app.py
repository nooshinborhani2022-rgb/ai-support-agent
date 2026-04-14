import streamlit as st
from src.engine import SupportEngine

st.set_page_config(page_title="AI Support Agent", layout="wide")

if "engine" not in st.session_state:
    st.session_state.engine = SupportEngine()

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("AI Support Agent Demo")

left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("Chat")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Type your message...")

    if user_input:
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )

        result = st.session_state.engine.handle_message(user_input)

        st.session_state.messages.append(
            {"role": "assistant", "content": result["response"]}
        )

        st.session_state.last_result = result
        st.rerun()

with right_col:
    st.subheader("Debug Panel")

    if "last_result" in st.session_state:
        result = st.session_state.last_result

        st.write("**Sentiment:**", result["sentiment"])
        st.write("**Intents:**", result["intents"])
        st.write("**Confidence:**", result["confidence"])
        st.write("**Action:**", result["action"])
        st.write("**Routing Reason:**", result["routing_reason"])
        st.write("**Top1 Score:**", result["top1_score"])
        st.write("**Top2 Score:**", result["top2_score"])
        st.write("**Score Gap:**", result["score_gap"])
        st.write("**Predicted Topics Before Rules:**", result["predicted_topics_before_rules"])
        st.write("**Final Topics After Rules:**", result["final_topics_after_rules"])
    else:
        st.info("Send a message to see reasoning details here.")