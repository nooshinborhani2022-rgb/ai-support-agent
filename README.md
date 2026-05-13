# 🤖 NEXA — Explainable AI Support Agent

### Production-Style AI Decision Engine for Customer Support

NEXA is an intelligent customer support assistant designed to simulate how modern AI support systems operate in real-world products.

Unlike basic intent-classification chatbots, NEXA combines:

- multi-intent reasoning
- sentiment-aware routing
- confidence-based decision making
- conversation memory
- explainable AI reasoning
- real-time interactive UI

to create a more reliable and transparent support experience.

---

# 🚀 Demo Features

Interactive Streamlit interface with:

- 💬 Real-time conversational chat UI
- 🧠 AI thinking & typing indicators
- ⚡ Quick support actions
- 📚 FAQ workflow
- 🎫 Ticket submission flow
- 📊 Explainable debug dashboard
- 🧭 Confidence-aware routing
- 🧠 Conversation memory tracking
- 🔄 Smooth auto-scroll chat experience

Run locally:

```bash
streamlit run app.py
```

---

# 🧠 Why This Project Is Different

Most chatbot projects:

```text
intent → response
```

NEXA behaves more like a decision engine:

```text
User Message
    ↓
Intent Detection
    ↓
Sentiment Analysis
    ↓
Confidence Evaluation
    ↓
Decision Routing
    ↓
Answer / Clarify / Escalate
    ↓
Explainable Reasoning
```

The system actively decides:

- whether it understands the user
- whether clarification is needed
- whether escalation is safer
- how tone should change based on sentiment

---

# 🎯 Core AI Capabilities

## 🔹 Multi-Intent Understanding

NEXA can detect multiple simultaneous intents in a single message.

Example:

```text
"I can't login and my payment failed"
```

Detected intents:

- login_issue
- payment_failed

Uses:

- TF-IDF similarity
- keyword matching
- conflict-aware intent selection

---

## 🔹 Confidence-Aware Decision Engine

Instead of blindly responding, the system evaluates certainty:

```python
confidence = top1_score - top2_score
```

Routing behavior:

- High confidence → answer
- Medium confidence → clarify
- High-risk uncertainty → escalate

---

## 🔹 Sentiment-Aware Routing

Detects emotional state:

- neutral
- frustrated
- angry
- urgent

Behavior adapts dynamically:

- angry → faster escalation
- frustrated → reduced clarification loops
- urgent → high-priority tone

---

## 🔹 Explainable AI (XAI)

NEXA exposes its reasoning process through a dedicated debug dashboard.

Visible reasoning includes:

- detected intents
- confidence score
- routing action
- routing reason
- topic transitions
- memory state
- risk assessment

This makes the system transparent and easier to debug or evaluate.

---

## 🔹 Multi-Turn Conversation Memory

The system tracks:

- active domain
- active intents
- conversation turns
- escalation state
- issue summary
- risk level

This enables:

- context-aware replies
- smarter follow-ups
- better clarification handling

---

## 🔹 Smart Clarification System

Instead of generic fallback responses:

❌ “Can you clarify?”

NEXA generates targeted follow-up questions:

✅ “Is this about a subscription fee, invoice, or billing issue?”

---

## 🔹 Risk-Aware Escalation

High-risk support cases are automatically escalated.

Example:

```text
"Someone used my card"
```

Triggers:

- escalation workflow
- urgency-aware tone
- safety-oriented guidance

---

# 🖥️ Streamlit UI Features

## 💬 Conversational Chat Experience

- Left/right message bubbles
- AI avatar
- Smooth scrolling behavior
- Thinking simulation
- Typing indicator
- Real-time updates

---

## ⚡ Quick Actions

Prebuilt demo scenarios:

- Account Login
- Payment Problem
- Fraud Report
- Order Status

Useful for showcasing system behavior quickly.

---

## 📚 FAQ Workflow

Interactive FAQ exploration with:

- categorized support topics
- one-click question injection
- contextual chat continuation

---

## 🎫 Ticket Submission Flow

Mock support ticket system with:

- name/email form
- issue summary
- generated ticket IDs
- UI-based support escalation demo

---

## 📊 Debug Dashboard

Dedicated reasoning panel showing:

- sentiment
- intents
- routing decisions
- confidence metrics
- memory state
- retrieved topics
- score comparisons

Designed for explainability and debugging.

---

# 📊 Logging & Analytics

All interactions are logged:

```text
chat_log.jsonl
```

Analyze logs with:

```bash
python analyze_logs.py
```

Tracks:

- intent distribution
- routing decisions
- escalation frequency
- confidence patterns
- sentiment trends
- multi-intent behavior

---

# 🧪 Testing

Run test suite:

```bash
python test_runner.py
```

Covers:

- intent detection
- routing logic
- sentiment analysis
- multi-turn conversations
- regression testing

---

# 🧱 Project Architecture

```text
User Input
   ↓
Preprocessing
   ↓
Intent Detection
(TF-IDF + Keywords)
   ↓
Multi-Intent Selection
   ↓
Sentiment Analysis
   ↓
Confidence Scoring
   ↓
Decision Engine
(answer / clarify / escalate)
   ↓
Response Generation
   ↓
Conversation Memory
   ↓
Explainability Layer
   ↓
UI + Logging
```

---

# 📁 Project Structure

```text
src/
 ├── engine.py
 ├── main.py
 ├── preprocessing.py
 ├── sentiment.py
 ├── confidence_utils.py
 ├── logger_utils.py

app.py
analyze_logs.py
test_runner.py
faq.json
```

---

# 🧩 Design Principles

- Hybrid AI (rules + statistical NLP)
- Confidence-driven decisions
- Explainable routing logic
- Risk-aware escalation
- Memory-aware interactions
- Human-centered support UX

---

# 🚀 Future Improvements

- Retrieval-Augmented Generation (RAG)
- Vector search over support documents
- LLM-based response generation
- FastAPI deployment
- Benchmark evaluation
- Production observability
- Multi-tenant architecture

---

# 💡 Why This Project Matters

Modern customer support systems require more than intent classification.

Real-world AI assistants must handle:

- uncertainty
- escalation risk
- emotional context
- explainability
- multi-step interactions

NEXA demonstrates how such systems can be designed using hybrid AI techniques without relying entirely on black-box models.

---

# 👤 Author

Developed by Nooshin Borhani Rayeni