import streamlit as st
from src.engine import SupportEngine
import time

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
            
/* FIX: scenario buttons */
button[kind="secondary"] {
    background-color: #1e293b !important;
    color: #f8fafc !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    padding: 10px !important;
}

button[kind="secondary"]:hover {
    background-color: #334155 !important;
    color: white !important;
}

/* spacing improvements */
[data-testid="stChatMessage"] {
    margin-bottom: 12px !important;
}

/* chat container padding */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}

/* nicer input spacing */
[data-testid="stChatInput"] {
    margin-top: 15px !important;
}

/* smoother look for debug panel */
.debug-box {
    backdrop-filter: blur(6px);
}
                       
</style>
""", unsafe_allow_html=True)

if "engine" not in st.session_state:
    st.session_state.engine = SupportEngine()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

if "stats" not in st.session_state:
    st.session_state.stats = {
        "total_messages": 0,
        "escalations": 0,
        "clarifications": 0,
        "last_action": "-"
    }

st.markdown("""
<h1 style="margin-bottom: 0;">
🤖 AI Support Agent
</h1>

<p style="color:#94a3b8; margin-top:5px;">
Explainable AI for customer support • Multi-intent • Sentiment-aware • Confidence-driven
</p>

<hr style="border:1px solid rgba(255,255,255,0.08); margin-top:15px; margin-bottom:25px;">
""", unsafe_allow_html=True)

def stream_text(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.03)

def get_thinking_steps():
    return [
        "Analyzing intent...",
        "Detecting sentiment...",
        "Applying routing rules...",
        "Generating response...",
    ]

def format_assistant_response(text):
    formatted = text

    formatted = formatted.replace("For your login issue:", "\n\n**🔐 Login issue**\n")
    formatted = formatted.replace("For your payment failed:", "\n\n**💳 Payment issue**\n")
    formatted = formatted.replace("For your refund request:", "\n\n**💸 Refund request**\n")
    formatted = formatted.replace("For your account access part,", "\n\n**🔒 Account access**\n")
    formatted = formatted.replace("For your billing part,", "\n\n**🧾 Billing**\n")
    formatted = formatted.replace("For your order part,", "\n\n**📦 Order**\n")
    formatted = formatted.replace("For your security part,", "\n\n**🚨 Security**\n")

    return formatted.strip()

left_col, right_col = st.columns([2, 1])

demo_scenarios = [
    "I was charged twice and this is ridiculous!!!",
    "I can't login and my payment failed",
    "Someone used my card. This charge is not mine.",
    "I want a refund for a charge from yesterday",
]

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

def build_explanation_text(result):
    intents = result.get("intents", [])
    action = result.get("action", "-")
    confidence = float(result.get("confidence", 0.0))
    sentiment = result.get("sentiment", "neutral")

    intent_text = ", ".join(intents) if intents else "unknown"

    return (
        f"Detected intents: {intent_text} • "
        f"Sentiment: {sentiment} • "
        f"Action: {action} • "
        f"Confidence: {confidence:.3f}"
    )

with left_col:
    st.subheader("Chat")

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        st.session_state.last_result = None
        st.session_state.stats = {
            "total_messages": 0,
            "escalations": 0,
            "clarifications": 0,
            "last_action": "-"
        }
        st.rerun()

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown("""
        <div style="
            padding: 28px;
            border-radius: 20px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 20px;
        ">
            <h3 style="margin-top: 0; color: #f8fafc;">👋 Welcome to AI Support Agent</h3>
            <p style="color: #cbd5e1; margin-bottom: 10px;">
                This demo showcases an explainable customer support AI with:
            </p>
            <ul style="color: #cbd5e1; line-height: 1.9;">
                <li>Multi-intent understanding</li>
                <li>Sentiment-aware routing</li>
                <li>Confidence-based decisions</li>
                <li>Step-by-step AI reasoning</li>
            </ul>
            <p style="color: #93c5fd; margin-top: 14px;">
                Try one of the quick actions below or type your own message.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### ⚡ Quick Actions")

    quick_actions = [
        {
            "title": "🔐 Login Issue",
            "desc": "Password reset, sign-in failure, locked account",
            "prompt": "I can't login to my account",
        },
        {
            "title": "💳 Payment Problem",
            "desc": "Failed payment, card declined, billing issue",
            "prompt": "My payment failed and I was charged",
        },
        {
            "title": "🚨 Fraud Report",
            "desc": "Unauthorized charge or suspicious transaction",
            "prompt": "Someone used my card. This charge is not mine.",
        },
        {
            "title": "📦 Order Status",
            "desc": "Tracking, delays, package status",
            "prompt": "Where is my order?",
        },
    ]

    cols = st.columns(2)

    for i, item in enumerate(quick_actions):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="
                padding:16px;
                border-radius:16px;
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                margin-bottom:10px;
                min-height:110px;
            ">
                <div style="font-size:18px; font-weight:700; color:#f8fafc; margin-bottom:6px;">
                    {item["title"]}
                </div>
                <div style="font-size:14px; color:#cbd5e1; line-height:1.5;">
                    {item["desc"]}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Use {item['title']}", key=f"quick_{i}"):
                prompt = item["prompt"]

                st.session_state.messages.append({
                    "role": "user",
                    "content": prompt
                })

                result = st.session_state.engine.handle_message(prompt)

                st.session_state.stats["total_messages"] += 1
                st.session_state.stats["last_action"] = result["action"]

                if result["action"] == "escalate":
                    st.session_state.stats["escalations"] += 1

                if result["action"] == "clarify":
                    st.session_state.stats["clarifications"] += 1

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["response"],
                    "explanation": build_explanation_text(result)
                    })

                st.session_state.last_result = result
                st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                st.markdown(format_assistant_response(message["content"]))

            if "explanation" in message:
                st.caption("🧠 " + message["explanation"])
            else:
                st.markdown(message["content"])

    user_input = st.chat_input("Type your message...", key="main_chat_input")

if user_input is not None and str(user_input).strip():
    user_input = str(user_input).strip()

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    result = st.session_state.engine.handle_message(user_input)

    st.session_state.stats["total_messages"] += 1
    st.session_state.stats["last_action"] = result["action"]

    if result["action"] == "escalate":
        st.session_state.stats["escalations"] += 1

    if result["action"] == "clarify":
        st.session_state.stats["clarifications"] += 1

    with st.chat_message("assistant"):
        thinking_placeholder = st.empty()
        visible_steps = []

        for step in get_thinking_steps():
            visible_steps.append(step)
            thinking_placeholder.markdown(
                "```text\n" + "\n".join(visible_steps) + "\n```"
            )
            time.sleep(0.55)

        time.sleep(0.4)
        thinking_placeholder.empty()

        typing_placeholder = st.empty()
        typing_placeholder.markdown("**AI is responding...**")
        time.sleep(0.6)
        typing_placeholder.empty()

        streamed_response = st.write_stream(stream_text(result["response"]))

    st.session_state.messages.append({
        "role": "assistant",
        "content": streamed_response,
        "explanation": build_explanation_text(result)
    })

    st.session_state.last_result = result
    st.rerun()

with right_col:
    st.subheader("Mini Analytics")

    a1, a2 = st.columns(2)
    a3, a4 = st.columns(2)

    with a1:
        st.metric("Total Messages", st.session_state.stats["total_messages"])

    with a2:
        st.metric("Escalations", st.session_state.stats["escalations"])

    with a3:
        st.metric("Clarifications", st.session_state.stats["clarifications"])

    with a4:
        st.metric("Last Action", st.session_state.stats["last_action"])

    st.markdown("---")
    st.subheader("Debug Panel")

    if "last_result" in st.session_state and st.session_state.last_result is not None:
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