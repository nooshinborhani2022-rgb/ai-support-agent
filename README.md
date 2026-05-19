# 🤖 NEXA — Explainable AI Support Agent

### Production-Style AI Decision Engine for Customer Support

NEXA is an intelligent, explainable customer support assistant designed to simulate how modern AI support systems operate in real-world products.

Unlike basic intent-classification chatbots, NEXA combines:

- multi-intent reasoning
- sentiment-aware routing
- confidence-based decision making
- conversation memory
- risk-aware escalation
- domain-aware local RAG retrieval
- explainable AI reasoning
- structured robustness and failure-mode evaluation
- real-time interactive Streamlit UI

to create a more reliable, transparent, and research-oriented AI support experience.

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
- 🔎 Retrieved support context from local knowledge base
- 📘 Source-aware RAG evidence display
- 🔄 Smooth auto-scroll chat experience
- 🧪 Robustness and failure-mode evaluation suite

Run locally:

```bash
streamlit run app.py
```

---

# 🧠 Why This Project Is Different

Most chatbot projects follow a simple pattern:

```text
intent → response
```

NEXA behaves more like an explainable AI decision engine:

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
Domain-Aware Retrieval
    ↓
Explainable Reasoning
    ↓
Response + Debug Evidence
```

The system actively decides:

- whether it understands the user
- whether clarification is needed
- whether escalation is safer
- what support domain is active
- what retrieved knowledge is relevant
- how tone should change based on sentiment
- what reasoning evidence should be exposed in the debug panel

---

# 🎯 Core AI Capabilities

## 🔹 Multi-Intent Understanding

NEXA can detect multiple simultaneous intents in a single message.

Example:

```text
"I can't login and I was charged twice"
```

Detected intents:

- login_issue
- double_charge

Uses:

- TF-IDF similarity
- keyword matching
- conflict-aware intent selection
- confidence gap analysis

---

## 🔹 Confidence-Aware Decision Engine

Instead of blindly responding, the system evaluates certainty:

```python
confidence = top1_score - top2_score
```

Routing behavior:

- High confidence → answer
- Ambiguous confidence → clarify
- High-risk issue → escalate
- Multi-intent uncertainty → structured multi-topic response or clarification

---

## 🔹 Sentiment-Aware Routing

Detects emotional state:

- neutral
- frustrated
- angry
- urgent

Behavior adapts dynamically:

- angry → faster escalation
- frustrated → more empathetic support tone
- urgent → priority-aware response
- neutral → standard support flow

---

## 🔹 Explainable AI Reasoning

NEXA exposes its internal reasoning process through a dedicated debug dashboard.

Visible reasoning includes:

- detected intents
- sentiment
- final action
- confidence score
- routing reason
- top intent scores
- score gap
- predicted topics before rules
- final topics after rules
- memory state
- active domain
- risk level
- retrieved support context
- retrieved source file

This makes the system transparent, inspectable, and easier to debug or evaluate.

---

## 🔹 Multi-Turn Conversation Memory

The system tracks:

- active domain
- active intents
- conversation turns
- escalation state
- issue summary
- risk level
- previous user message
- follow-up context

This enables:

- context-aware replies
- smarter follow-ups
- better clarification handling
- safer escalation behavior

---

## 🔹 Smart Clarification System

Instead of generic fallback responses:

```text
Can you clarify?
```

NEXA generates targeted follow-up questions:

```text
Just to clarify, is this about a failed payment, a declined card, or a refund request?
```

Clarification is domain-aware and based on detected ambiguity.

---

## 🔹 Risk-Aware Escalation

High-risk support cases are automatically escalated.

Example:

```text
Someone used my card
```

Triggers:

- fraud/security intent detection
- security escalation workflow
- urgent and safety-oriented response
- retrieved fraud-related support context
- high-risk memory state

---

# 📘 Local RAG System

NEXA now includes a lightweight local Retrieval-Augmented Generation foundation.

The RAG layer uses:

- local support documents
- sentence-transformer embeddings
- ChromaDB vector retrieval
- domain-aware retrieval routing
- source-aware explainability

The knowledge base is stored locally in:

```text
knowledge_base/
 ├── login.txt
 ├── billing.txt
 ├── refund.txt
 ├── fraud.txt
 └── orders.txt
```

---

## 🔹 Domain-Aware Retrieval

Retrieval is not purely semantic.

NEXA combines intent routing with retrieval.

Example:

```text
Someone used my card
```

Flow:

```text
fraud_report intent
    ↓
security domain
    ↓
fraud.txt retrieval
    ↓
retrieved context shown in Debug Panel
```

This prevents unsafe retrieval mismatches where a fraud issue might otherwise retrieve a generic billing document.

---

## 🔹 Retrieved Context in Debug Panel

Retrieved knowledge is shown separately from the chat response to keep the user-facing conversation clean.

Debug panel displays:

```text
Retrieved Source: fraud.txt
Retrieved Context: Fraud and security issues may include unauthorized charges...
```

This makes the RAG layer explainable and auditable.

---

# 🖥️ Streamlit UI Features

## 💬 Conversational Chat Experience

- Custom left/right message bubbles
- AI avatar
- User avatar
- Floating chat input
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
- risk level
- score comparisons
- topics before and after rules
- retrieved RAG context
- retrieved source document

Designed for explainability, debugging, and evaluation.

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
- clarification frequency
- confidence patterns
- sentiment trends
- multi-intent behavior
- fallback behavior
- score gap patterns

---

# 🧪 Testing & Evaluation

Run test suite:

```bash
python test_runner.py
```

Covers:

- intent detection
- sentiment detection
- routing logic
- multi-turn clarification behavior
- regression testing
- robustness scenarios
- failure-mode evaluation

---

## 🔹 Robustness & Failure-Mode Testing

NEXA includes structured evaluation scenarios for:

- ambiguous inputs
- multi-intent queries
- out-of-scope requests
- emotionally intense messages
- high-risk fraud/security cases
- boundary-condition prompts
- low-confidence routing behavior

Examples:

```text
???
help
Tell me a joke
Write me a Python game
I can't login and my payment failed
Someone used my card and this charge is not mine
```

The goal is not to claim the system is perfect, but to systematically probe where it succeeds, where it fails, and how routing decisions can be improved.

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
Conversation Memory
   ↓
Domain-Aware Retrieval
   ↓
Response Generation
   ↓
Explainability Layer
   ↓
UI + Logging + Evaluation
```

---

# 📁 Project Structure

```text
assets/
 └── nexa_avatar.png

knowledge_base/
 ├── login.txt
 ├── billing.txt
 ├── refund.txt
 ├── fraud.txt
 └── orders.txt

src/
 ├── engine.py
 ├── main.py
 ├── retrieval.py
 ├── preprocessing.py
 ├── sentiment.py
 ├── confidence_utils.py
 ├── logger_utils.py
 └── config.py

app.py
analyze_logs.py
test_runner.py
faq.json
requirements.txt
README.md
```

---

# 🧩 Design Principles

- Hybrid AI: rule-based logic + lightweight NLP + local retrieval
- Explainable routing instead of black-box responses
- Confidence-driven decisions
- Domain-aware RAG retrieval
- Risk-aware escalation
- Memory-aware interaction design
- Human-centered support UX
- Structured robustness testing
- Research-oriented failure analysis

---

# 🛠️ Tech Stack

- Python
- Streamlit
- scikit-learn
- TF-IDF similarity
- sentence-transformers
- ChromaDB
- lightweight NLP
- local knowledge base retrieval
- custom HTML/CSS UI components

---

# 🚀 Future Improvements

Planned improvements include:

- multi-document retrieval
- chunk-level retrieval
- retrieval similarity scores
- source metadata and citation-style evidence
- stronger hallucination guards
- prompt-injection and jailbreak evaluation
- larger adversarial testing suite
- FastAPI backend
- persistent database
- analytics dashboard
- production deployment
- optional LLM-based response generation

---

# 💡 Why This Project Matters

Modern customer support systems require more than simple intent classification.

Real-world AI assistants must handle:

- uncertainty
- ambiguity
- escalation risk
- emotional context
- multi-step interactions
- explainability
- retrieved evidence
- failure analysis

NEXA demonstrates how such systems can be designed using hybrid AI techniques without relying entirely on black-box models.

It is built as a research-oriented conversational AI prototype focused on:

- reliability
- transparency
- robust decision behavior
- explainable support automation
- safe escalation workflows

---

# 👤 Author

Developed by Nooshin Borhani Rayeni