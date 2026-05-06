import streamlit as st
from src.engine import SupportEngine
import time
import streamlit.components.v1 as components
import base64
import html

st.set_page_config(page_title="AI Support Agent", layout="wide")

st.markdown("""
<style>
.quick-container {
    display: flex;
    gap: 12px;
    justify-content: flex-start;
    margin-top: 10px;
}

.quick-btn {
    padding: 14px 20px;
    border-radius: 16px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    color: white;
    font-size: 15px;
    cursor: pointer;
    white-space: nowrap;
    text-align: center;
    text-decoration: none !important;
    display: block;
    flex: 1;
    min-width: 0;

}
            
[data-testid="stChatInput"] {
    margin-top: -20px;
}
            
</style>
""", unsafe_allow_html=True)

quick_buttons = [
    ("🔐", "Login Issue", "I can't login to my account"),
    ("💳", "Payment Problem", "My payment failed"),
    ("🚨", "Fraud Report", "Someone used my card"),
    ("📦", "Order Status", "Where is my order?"),
]

FAQ_CATEGORIES = {
    "🔐 Account": [
        "I can't login to my account",
        "I forgot my password",
        "My account is locked",
    ],
    "💳 Billing & Payments": [
        "I have a billing issue",
        "Why was I charged?",
        "I was charged twice",
        "My payment failed",
        "I want a refund",
    ],
    "📦 Orders": [
        "Where is my order?",
        "My delivery is late",
        "Track my package",
    ],
    "🚨 Security": [
        "Someone used my card",
        "This charge is not mine",
        "This looks like fraud",
    ],
}

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

.quick-card {
    padding: 16px;
    border-radius: 16px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 10px;
    min-height: 110px;
    transition: all 0.25s ease;
}

.quick-card:hover {
    transform: translateY(-4px);
    border: 1px solid rgba(147,197,253,0.45);
    box-shadow: 0 10px 24px rgba(14,165,233,0.18);
    background: rgba(255,255,255,0.06);
}            

div.stButton > button {
    width: 100%;
    border-radius: 12px !important;
}

div.stButton > button {
    width: 100% !important;
    min-width: 0 !important;
    max-width: none !important;
    white-space: nowrap !important;
    min-height: 64px !important;
    border-radius: 16px !important;
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #f8fafc !important;
    text-align: center !important;
    white-space: nowrap !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    line-height: 1.5 !important;
    padding: 10px 12px !important;
    transition: all 0.25s ease !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    div.stButton {
    margin: 0 6px !important;
    }
    }

div.stButton > button:hover {
    transform: translateY(-4px);
    border: 1px solid rgba(147,197,253,0.45) !important;
    box-shadow: 0 10px 24px rgba(14,165,233,0.18);
    background: rgba(255,255,255,0.06) !important;
}      
            
[data-baseweb="popover"] {
    background: #0f172a !important;
}

[data-baseweb="menu"] {
    background: #0f172a !important;
    color: #f8fafc !important;
}

[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.06) !important;
    color: #f8fafc !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
}

[data-baseweb="select"] span {
    color: #f8fafc !important;
}

[data-baseweb="select"] input {
    color: #f8fafc !important;
}

div[role="listbox"] {
    background: #0f172a !important;
    color: #f8fafc !important;
}

div[role="option"] {
    background: #0f172a !important;
    color: #f8fafc !important;
}

div[role="option"]:hover {
    background: #1e293b !important;
    color: #ffffff !important;
}

/* Compact quick action buttons */
.compact-quick-actions-label {
    color: #93c5fd !important;
    font-weight: 700;
    margin-top: 0.5rem;
    margin-bottom: 0.75rem;
    font-size: 1rem;
}

div.stButton > button[kind="secondary"] {
    min-height: auto !important;
}

.compact-quick-row {
    margin-bottom: 0.35rem;
}
            
/* FIX: FAQ expander stays dark when open */
[data-testid="stExpander"] {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    overflow: hidden !important;
}

[data-testid="stExpander"] details {
    background: transparent !important;
}

[data-testid="stExpander"] summary {
    background: rgba(255,255,255,0.02) !important;
    color: #f8fafc !important;
    border-radius: 14px !important;
}

[data-testid="stExpander"] details[open] > summary {
    background: rgba(255,255,255,0.04) !important;
    color: #f8fafc !important;
}

[data-testid="stExpander"] summary:hover {
    background: rgba(255,255,255,0.06) !important;
}

[data-testid="stExpander"] .streamlit-expanderContent {
    background: transparent !important;
    color: #f8fafc !important;
}


  /* Right panel metric cards */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 14px 16px;
}

[data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
}

[data-testid="stMetricValue"] {
    color: #f8fafc !important;
    font-weight: 700 !important;
}



div[data-testid="stColumn"]:first-of-type div.stButton > button:hover {
    background: rgba(59,130,246,0.14);
    border: 1px solid rgba(59,130,246,0.25);
    color: #bfdbfe;
}          

/* Sidebar buttons: left aligned */
div[data-testid="stColumn"]:first-of-type div.stButton > button {
    justify-content: flex-start !important;
    text-align: left !important;
    padding-left: 16px !important;
}

div[data-testid="stColumn"]:first-of-type div.stButton > button p {
    text-align: left !important;
    width: 100% !important;
}

 /* remove left padding from sidebar column */
div[data-testid="stColumn"]:first-of-type {
    padding-left: 0 !important;
}

/* push content fully to the left */
div[data-testid="stColumn"]:first-of-type > div {
    margin-left: -12px;
}           

    section.main > div {
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

.block-container {
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 100% !important;
}   

/* ==== SIDEBAR FIX ==== */
div[data-testid="stColumn"]:first-of-type div.stButton > button {
    display: flex !important;
    justify-content: flex-start !important;
    align-items: center !important;
    text-align: left !important;

    padding: 8px 12px !important;
    border-radius: 12px !important;
    height: 42px !important;
}

div[data-testid="stColumn"]:first-of-type div.stButton > button span {
    width: 100% !important;
    text-align: left !important;
}

/* Quick Actions button alignment fallback */
button[key^="quick_"] {
    margin-left: -8px !important;
}          

[data-testid="column"] {
    padding-left: 6px !important;
    padding-right: 6px !important;
}
            
/* Sidebar buttons fixed width */
div[data-testid="stColumn"]:first-of-type div.stButton > button {
    width: 170px !important;
    min-width: 170px !important;
    max-width: 170px !important;
    height: 52px !important;
    justify-content: center !important;
}

.main-content {
    max-width: 980px;
    margin-left: auto;
    margin-right: auto;
}
.quick-actions-wrapper {
    transform: translateX(-24px);
}

.quick-form-area [data-testid="stForm"] {
    border: 0 !important;
    padding: 0 !important;
    background: transparent !important;
}

.quick-form-area div.stButton > button {
    width: 100% !important;
    min-height: 64px !important;
    border-radius: 16px !important;
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #f8fafc !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    white-space: nowrap !important;
    text-align: center !important;
}

</style>
""", unsafe_allow_html=True)

if "engine" not in st.session_state:
    st.session_state.engine = SupportEngine()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

if "scroll_to_bottom" not in st.session_state:
    st.session_state.scroll_to_bottom = False
    
if "stats" not in st.session_state:
    st.session_state.stats = {
        "total_messages": 0,
        "escalations": 0,
        "clarifications": 0,
        "last_action": "-"
    }


if "active_page" not in st.session_state:
    st.session_state.active_page = "chat"

if "show_ticket" not in st.session_state:
    st.session_state.show_ticket = False

if "show_debug" not in st.session_state:
    st.session_state.show_debug = False



def load_image_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

avatar_base64 = load_image_base64("assets/nexa_avatar.png")


sidebar_col, left_col, right_col = st.columns([0.75, 2.35, 1])

with sidebar_col:
    st.markdown("""
    <div style="margin-top:24px; margin-bottom:22px; margin-left:10px;">
    <div style="font-size:26px; font-weight:900; color:#38bdf8; letter-spacing:4px;">NEXA</div>
    <div style="font-size:12px; color:#94a3b8; letter-spacing:2px; margin-top:4px;">
        AI SUPPORT AGENT
    </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("💬 Chat", key="nav_chat"):
       st.session_state.active_page = "chat"

    if st.button("❓ FAQ", key="nav_faq"):
       st.session_state.active_page = "faq"

    if st.button("🎫 Open Ticket", key="nav_ticket"):
       st.session_state.active_page = "ticket"
       st.session_state.show_ticket = True
    
    if st.button("🗑 Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_result = None
        st.session_state.stats = {
        "total_messages": 0,
        "escalations": 0,
        "clarifications": 0,
        "last_action": "-"
        }
        st.rerun()

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

def get_thinking_steps():
    return [
        "🔍 Analyzing intent...",
        "🙂 Detecting sentiment...",
        "🧭 Applying routing rules...",
        "✨ Generating response...",
    ]

def process_user_prompt(prompt: str):
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    thinking_placeholder = st.empty()

    for step in get_thinking_steps():
        thinking_placeholder.markdown(
            f"""
            <div style="
                display:flex;
                align-items:center;
                gap:10px;
                background:rgba(255,255,255,0.06);
                border:1px solid rgba(255,255,255,0.08);
                border-radius:16px;
                padding:14px 16px;
                color:#cbd5e1;
                margin:12px 0;
            ">
                <span>🤖</span>
                <span>{step}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        time.sleep(0.65)

        result = st.session_state.engine.handle_message(prompt)

        thinking_placeholder.markdown(
        """
        <div style="
            display:flex;
            align-items:center;
            gap:10px;
            background:rgba(59,130,246,0.12);
            border:1px solid rgba(59,130,246,0.22);
            border-radius:16px;
            padding:14px 16px;
            color:#bfdbfe;
            margin:12px 0;
        ">
            <span>✍️</span>
            <span>NEXA is typing...</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    time.sleep(0.9)
    thinking_placeholder.empty()

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
    st.session_state.scroll_to_bottom = True
    st.rerun()

quick_action_prompts = {
    "login": "I can't login to my account",
    "payment": "My payment failed",
    "fraud": "Someone used my card",
    "order": "Where is my order?",
}

quick_action_key = st.query_params.get("quick_action")

if quick_action_key in quick_action_prompts:
    st.query_params.clear()
    process_user_prompt(quick_action_prompts[quick_action_key])

quick_actions = [
    {"icon": "🔐", "title": "Account Login", "prompt": "I can't login to my account"},
    {"icon": "💳", "title": "Payment Problem", "prompt": "My payment failed"},
    {"icon": "🚨", "title": "Fraud Report", "prompt": "Someone used my card"},
    {"icon": "📦", "title": "Order Status", "prompt": "Where is my order?"},
]

def stream_text(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.03)

        
with left_col:

    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    st.markdown(
        f"""<div style="display:flex; align-items:center; gap:18px; margin-top:28px; margin-bottom:16px;">
<img src="data:image/png;base64,{avatar_base64}" width="82" style="border-radius:50%; box-shadow:0 0 18px rgba(59,130,246,0.25);">
<div>
<div style="font-size:30px; font-weight:700; line-height:1.2;">
Welcome to <span style="color:#3b82f6;">NEXA</span>
</div>
<div style="color:#94a3b8; margin-top:6px; font-size:15px;">
Your AI support assistant for explainable customer support
</div>
</div>
</div>

<hr style="border:1px solid rgba(255,255,255,0.08); margin-top:14px; margin-bottom:24px;">""",
        unsafe_allow_html=True
    )
    st.markdown("""
    <div style="
    color:#cbd5e1;
    font-size:16px;
    margin-bottom:12px;
    line-height:1.8;
    ">
    <strong style="color:#e2e8f0;">This demo showcases:</strong><br>
    • Multi-intent understanding<br>
    • Sentiment-aware routing<br>
    • Confidence-based decisions<br>
    • Explainable AI reasoning
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.active_page == "ticket":
        st.markdown("### 🎫 Open Support Ticket")

        with st.expander("📨 Submit a Support Ticket", expanded=True):
            name = st.text_input("Your Name", key="ticket_name")
            email = st.text_input("Email", key="ticket_email")
            issue = st.text_input("Issue Summary", key="ticket_issue")
            message = st.text_area("Describe your issue", key="ticket_message")

            ticket_submit_col, ticket_cancel_col = st.columns([1, 1])

            with ticket_submit_col:
                if st.button("Submit Ticket", key="ticket_submit", use_container_width=True):
                    import random

                    ticket_id = f"TICKET-{random.randint(1000,9999)}"

                    st.success(f"✅ Ticket submitted! ID: {ticket_id}")
                    st.info("Our support team will get back to you shortly.")

                    st.session_state.show_ticket = False
                    st.session_state.active_page = "chat"

            with ticket_cancel_col:
                if st.button("Cancel", key="ticket_cancel", use_container_width=True):
                    st.session_state.show_ticket = False
                    st.session_state.active_page = "chat"
                    st.rerun()

    if st.session_state.active_page == "faq":
        st.markdown("### 📚 FAQ & Common Questions")

        with st.expander("Browse common support topics", expanded=True):
            for category, questions in FAQ_CATEGORIES.items():
                with st.expander(category, expanded=False):
                    for q_idx, question in enumerate(questions):
                        if st.button(
                            question,
                            key=f"faq_top_{category}_{q_idx}",
                            use_container_width=True
                        ):
                            st.session_state.active_page = "chat"
                            process_user_prompt(question)

            if st.button("Close FAQ", key="faq_close", use_container_width=True):
                st.session_state.active_page = "chat"
                st.rerun()

    st.markdown('<div class="quick-actions-wrapper">', unsafe_allow_html=True)
    quick_area, quick_empty = st.columns([6, 1], gap="small")

with quick_area:
    st.markdown("### ⚡ Quick Actions")
    st.markdown("""
<div class="quick-container">
    <a class="quick-btn" href="?quick_action=login" target="_self">🔐 Account Login</a>
    <a class="quick-btn" href="?quick_action=payment" target="_self">💳 Payment Problem</a>
    <a class="quick-btn" href="?quick_action=fraud" target="_self">🚨 Fraud Report</a>
    <a class="quick-btn" href="?quick_action=order" target="_self">📦 Order Status</a>
</div>
""", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    input_col = st.container()

    st.markdown("<div style='margin-top:-28px;'></div>", unsafe_allow_html=True)


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
    

    for message in st.session_state.messages:
        content = message.get("content", "")

        if message["role"] == "assistant":
            
            safe_content = html.escape(format_assistant_response(content)).replace("\n", "<br>")
            explanation = message.get("explanation")

            if explanation:
                explanation_html = (
            "<div style='margin-top:10px; color:#94a3b8; font-size:13px; line-height:1.5;'>"
            f"🧠 {html.escape(explanation)}"
            "</div>"
            )
            else:
                explanation_html = ""

            st.markdown(
                f"""
                <div style="display:flex; align-items:flex-start; gap:12px; margin:18px 0;">
                <img src="data:image/png;base64,{avatar_base64}"
                     style="width:42px; height:42px; border-radius:50%; object-fit:cover;">
                <div style="
                    max-width:72%;
                    background:rgba(255,255,255,0.06);
                    border:1px solid rgba(255,255,255,0.08);
                    border-radius:18px;
                    padding:16px 18px;
                    color:#f8fafc;
                    line-height:1.7;
                ">
                    <div style="font-weight:800; color:#38bdf8; margin-bottom:6px;">NEXA</div>
                    <div>{safe_content}</div>
                    {explanation_html}
                </div>
            </div>
            """,
                unsafe_allow_html=True
            )

        else:
            safe_content = html.escape(content).replace("\n", "<br>")

            st.markdown(
                f"""
                <div style="display:flex; justify-content:flex-end; align-items:flex-start; gap:12px; margin:18px 0;">
                <div style="
                    max-width:62%;
                    background:rgba(37,99,235,0.18);
                    border:1px solid rgba(59,130,246,0.35);
                    border-radius:18px;
                    padding:16px 18px;
                    color:#f8fafc;
                    line-height:1.7;
                ">
                    {safe_content}
                </div>
                <div style="
                    width:42px;
                    height:42px;
                    border-radius:50%;
                    background:#2563eb;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:22px;
                ">
                    👤
                </div>
            </div>
            """,
            unsafe_allow_html=True
            )

message_count = len(st.session_state.messages)
anchor_id = f"chat-bottom-anchor-{message_count}"

st.markdown(f'<div id="{anchor_id}"></div>', unsafe_allow_html=True)

if st.session_state.get("scroll_to_bottom", False):
    components.html(
        f"""
        <script>
            const scrollToChat = () => {{
                const anchor = window.parent.document.getElementById("{anchor_id}");
                if (anchor) {{
                    anchor.scrollIntoView({{
                        behavior: "smooth",
                        block: "center"
                    }});
                }}
            }};

            setTimeout(scrollToChat, 100);
            setTimeout(scrollToChat, 350);
            setTimeout(scrollToChat, 700);
        </script>
        """,
        height=0,
    )
    st.session_state.scroll_to_bottom = False
            
with input_col:
        user_input = st.chat_input("Type your message...")
if user_input and str(user_input).strip():
    process_user_prompt(str(user_input).strip())

    

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
 
st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
    st.markdown("""
<div style="margin-top:12px; margin-bottom:14px;">
    <div style="font-size:18px; font-weight:700; color:#f8fafc;">📊 Mini Analytics</div>
    <div style="font-size:18px; color:#94a3b8; margin-top:4px;">
        Live conversation summary
    </div>
</div>
""", unsafe_allow_html=True)

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

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # Debug toggle button
    if st.session_state.show_debug:
        if st.button("🛠 Hide Debug Panel", use_container_width=True):
            st.session_state.show_debug = False
            st.rerun()
    else:
        if st.button("🛠 Show Debug Panel", use_container_width=True):
            st.session_state.show_debug = True
            st.rerun()

    if st.session_state.show_debug:
        st.markdown("### 🛠 Debug Panel")
        st.markdown("Inspect routing and reasoning details")

        if "last_result" in st.session_state and st.session_state.last_result is not None:
            result = st.session_state.last_result

            st.markdown('<div class="metric-label">Sentiment</div>', unsafe_allow_html=True)
            st.markdown(sentiment_badge(result.get("sentiment", "neutral")), unsafe_allow_html=True)

            st.markdown('<div class="metric-label">Intents</div>', unsafe_allow_html=True)
            if result.get("intents"):
                st.markdown(intent_badges(result.get("intents", [])), unsafe_allow_html=True)
            else:
                st.markdown('<div class="metric-value">None</div>', unsafe_allow_html=True)

            st.markdown('<div class="metric-label">Action</div>', unsafe_allow_html=True)
            st.markdown(action_badge(result.get("action", "-")), unsafe_allow_html=True)
            st.markdown(f"**Confidence:** {float(result.get('confidence', 0.0)):.3f}")
            st.markdown(f"**Routing:** {result.get('routing_reason', '-')}")

            memory = result.get("memory", {})
            st.markdown("#### 🧠 Memory")
            if memory:
                st.markdown(f"**Domain:** {memory.get('active_domain', '-')}")
                st.markdown(f"**Memory Intents:** {', '.join(memory.get('active_intents', [])) if memory.get('active_intents') else '-'}")
                st.markdown(f"**Risk:** {memory.get('risk_level', '-')}")
                st.markdown(f"**Escalation:** {memory.get('needs_escalation', '-')}")
                st.markdown(f"**Turns:** {memory.get('turn_count', '-')}")
                if memory.get("active_issue_summary"):
                    st.markdown(f"**Summary:** {memory.get('active_issue_summary')}")
                else:
                    st.markdown("No memory data yet.")

                st.markdown("#### 📈 Scores")
                st.markdown(f"**Top1 Score:** {result.get('top1_score', '-')}")
                st.markdown(f"**Top2 Score:** {result.get('top2_score', '-')}")
                st.markdown(f"**Score Gap:** {result.get('score_gap', '-')}")

                st.markdown("#### 🔎 Topics Before Rules")
                st.code(
                    "\n".join(result.get("predicted_topics_before_rules", []))
                    if result.get("predicted_topics_before_rules")
                    else "None",
                    language=None
                )

                st.markdown("#### ✅ Topics After Rules")
                st.code(
                    "\n".join(result.get("final_topics_after_rules", []))
                    if result.get("final_topics_after_rules")
                    else "None",
                    language=None
                )


            else:
                st.info("Send a message to see reasoning details here.")
    