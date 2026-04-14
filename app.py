import streamlit as st
from src.engine import SupportEngine

st.set_page_config(page_title="AI Support Agent", layout="wide")

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a, #111827);
        color: white;
    }

    h1, h2, h3 {
        color: #f8fafc !important;
    }

    p, label, div, span {
        color: #e5e7eb !important;
    }

    [data-testid="stChatMessage"] {
        border-radius: 16px;
        padding: 0.8rem;
        margin-bottom: 0.6rem;
        border: 1px solid rgba(255,255,255,0.08);
        background: rgba(255,255,255,0.05);
    }

    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] div,
    [data-testid="stChatMessage"] span {
        color: #f8fafc !important;
    }

    .stChatInput input {
        border-radius: 12px !important;
        background: rgba(255,255,255,0.05) !important;
        color: white !important;
    }

    .debug-box {
        background: rgba(255,255,255,0.04);
        padding: 18px;
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.08);
    }

    .metric-label {
        color: #93c5fd !important;
        font-weight: 700;
        margin-top: 0.8rem;
        margin-bottom: 0.2rem;
    }

    .metric-value {
        color: #f8fafc !important;
        margin-bottom: 0.65rem;
        word-break: break-word;
    }

    /* FIX: dark code blocks in debug panel */
    pre, code {
        background: #0b1220 !important;
        color: #f8fafc !important;
    }

    .stCodeBlock {
        background: #0b1220 !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 12px !important;
    }

    .stCodeBlock pre {
        background: #0b1220 !important;
        color: #f8fafc !important;
    }

    [data-testid="stCodeBlock"] {
        background: #0b1220 !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 12px !important;
    }

    [data-testid="stCodeBlock"] pre {
        background: #0b1220 !important;
        color: #f8fafc !important;
    }

    [data-testid="stCode"] {
        background: #0b1220 !important;
        color: #f8fafc !important;
    }
</style>
""", unsafe_allow_html=True)

if "engine" not in st.session_state:
    st.session_state.engine = SupportEngine()

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🤖 AI Support Agent Demo")
st.caption("Explainable customer support AI with sentiment, routing, and confidence tracing")

left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("Chat")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Type your message...")

    if user_input:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        result = st.session_state.engine.handle_message(user_input)

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["response"]
        })

        st.session_state.last_result = result
        st.rerun()

def action_badge(action):
    colors = {
        "answer": "#16a34a",
        "clarify": "#f59e0b",
        "escalate": "#dc2626",
    }

    color = colors.get(action, "#475569")

    return f"""
    <div style="
        display:inline-block;
        padding:6px 12px;
        border-radius:999px;
        background:{color};
        color:white;
        font-weight:700;
        font-size:14px;
        margin-bottom:10px;
    ">
        {action.upper()}
    </div>
    """

def sentiment_badge(sentiment):
    colors = {
        "neutral": "#64748b",
        "frustrated": "#f97316",
        "angry": "#dc2626",
        "urgent": "#9333ea",
    }

    color = colors.get(sentiment, "#475569")

    return f"""
    <div style="
        display:inline-block;
        padding:6px 12px;
        border-radius:999px;
        background:{color};
        color:white;
        font-weight:700;
        font-size:14px;
        margin-bottom:10px;
    ">
        {sentiment.upper()}
    </div>
    """

def intent_badges(intents):
    colors = [
        "#0ea5e9",  
        "#22c55e",  
        "#a855f7",  
        "#f97316",  
    ]

    badges = ""
    for i, intent in enumerate(intents):
        color = colors[i % len(colors)]
        badges += f"""
        <span style="
            display:inline-block;
            padding:5px 10px;
            border-radius:999px;
            background:{color};
            color:white;
            font-size:13px;
            font-weight:600;
            margin-right:6px;
            margin-bottom:6px;
        ">
            {intent}
        </span>
        """

    return badges

with right_col:
    st.subheader("Debug Panel")

    if "last_result" in st.session_state:
        result = st.session_state.last_result

        st.markdown('<div class="debug-box">', unsafe_allow_html=True)

        st.markdown('<div class="metric-label">Sentiment</div>', unsafe_allow_html=True)
        st.markdown(sentiment_badge(result["sentiment"]), unsafe_allow_html=True)

        st.markdown('<div class="metric-label">Intents</div>', unsafe_allow_html=True)

        if result["intents"]:
            st.markdown(intent_badges(result["intents"]), unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-value">None</div>', unsafe_allow_html=True)

            st.markdown('<div class="metric-label">Confidence</div>', unsafe_allow_html=True)

        confidence_value = float(result["confidence"])
        confidence_percent = max(0, min(int(confidence_value * 100), 100))

        st.progress(confidence_percent)
        st.markdown(
        f'<div class="metric-value">{confidence_value:.3f} ({confidence_percent}%)</div>',
        unsafe_allow_html=True
        )

        st.markdown('<div class="metric-label">Action</div>', unsafe_allow_html=True)
        st.markdown(action_badge(result["action"]), unsafe_allow_html=True)

        st.markdown('<div class="metric-label">Routing Reason</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{result["routing_reason"]}</div>', unsafe_allow_html=True)

        st.markdown('<div class="metric-label">Top1 Score</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{result["top1_score"]}</div>', unsafe_allow_html=True)

        st.markdown('<div class="metric-label">Top2 Score</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{result["top2_score"]}</div>', unsafe_allow_html=True)

        st.markdown('<div class="metric-label">Score Gap</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{result["score_gap"]}</div>', unsafe_allow_html=True)

        st.markdown('<div class="metric-label">Predicted Topics Before Rules</div>', unsafe_allow_html=True)
        st.code(
            "\n".join(result["predicted_topics_before_rules"])
            if result["predicted_topics_before_rules"] else "None",
            language=None
        )

        st.markdown('<div class="metric-label">Final Topics After Rules</div>', unsafe_allow_html=True)
        st.code(
            "\n".join(result["final_topics_after_rules"])
            if result["final_topics_after_rules"] else "None",
            language=None
        )

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Send a message to see reasoning details here.")
    