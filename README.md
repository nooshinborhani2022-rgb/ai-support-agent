# 🤖 AI Support Agent

### Explainable AI Decision Engine for Customer Support

A **production-style AI support system** that goes beyond simple intent detection and makes **explainable, confidence-aware decisions** in real-time customer interactions.

Unlike typical chatbots, this system can:

* Understand **multiple intents simultaneously**
* Detect **user sentiment**
* Decide whether to **answer, clarify, or escalate**
* Maintain **conversation context across turns**
* Provide **transparent reasoning behind every decision**

---

## 🚀 Live Demo (Streamlit UI)

Interactive chat interface with:

* Real-time responses
* Step-by-step AI reasoning
* Confidence visualization
* Debug panel (intents, routing, memory)

```bash
streamlit run app.py
```

---

## 🧠 What Makes This Different?

Most chatbot projects:

* classify intent → return response ❌

This system:

* detects multiple possible intents
* measures uncertainty (confidence gap)
* applies decision rules
* adapts behavior based on sentiment
* explains *why* it made that decision

👉 This is closer to a **decision engine** than a chatbot.

---

## 🎯 Core Capabilities

### 🔹 Multi-Intent Understanding

* Hybrid detection (TF-IDF + keyword matching)
* Detects overlapping intents in a single query
* Resolves conflicts intelligently

Example:
“I can't login and my payment failed”

---

### 🔹 Confidence-Aware Decision Making

Instead of blindly answering:

```
confidence = top1_score - top2_score
```

The system:

* answers when confident
* clarifies when uncertain
* escalates high-risk cases

---

### 🔹 Sentiment-Aware Routing

Detects:

* neutral
* frustrated
* angry
* urgent

And adjusts behavior:

* angry → escalate
* frustrated → avoid over-clarifying
* urgent → respond faster

---

### 🔹 Explainable AI (XAI)

Every response includes reasoning:

* Detected intents
* Confidence score
* Routing decision
* Routing reason

Example:

```
Detected intents: payment_failed, refund_request
Sentiment: frustrated
Action: clarify
Confidence: 0.13
Reason: low_confidence_multi_intent
```

---

### 🔹 Multi-Turn Conversation Memory

The system tracks:

* Active domain (billing, account, etc.)
* Active intents
* Risk level
* Conversation summary

This enables:

* smarter follow-ups
* context-aware responses
* better clarification handling

---

### 🔹 Smart Clarification System

Instead of generic fallback:

❌ Can you clarify?
✅ Is this about a subscription fee, invoice, or billing issue?

Even follow-ups are handled intelligently:
“I have a billing issue” → “subscription fee”

---

### 🔹 Risk-Aware Escalation

High-risk cases (e.g. fraud):

```
Someone used my card
```

→ Automatically escalated with proper tone and guidance.

---

## 🧱 System Architecture

```
User Input
   ↓
Preprocessing
   ↓
Intent Detection (TF-IDF + Keywords)
   ↓
Multi-Intent Selection
   ↓
Sentiment Detection
   ↓
Confidence Calculation
   ↓
Decision Engine (Answer / Clarify / Escalate)
   ↓
Response Generation (Tone-aware)
   ↓
Explainability + Logging
```

---

## 🖥️ UI Features (Streamlit)

* Chat interface
* Quick demo scenarios
* AI thinking visualization
* Confidence bar
* Intent / sentiment badges
* Debug panel with full reasoning
* Conversation memory display

---

## 📊 Logging & Analytics

All interactions are logged:

```
chat_log.jsonl
```

Analyze with:

```bash
python analyze_logs.py
```

Includes:

* intent distribution
* action distribution
* sentiment trends
* routing reasons
* confidence metrics
* multi-intent behavior

---

## 🧪 Testing

Run full test suite:

```bash
python test_runner.py
```

Covers:

* intent detection
* sentiment classification
* routing logic
* multi-turn behavior
* regression scenarios

---

## 📁 Project Structure

```
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

## 🧩 Key Design Ideas

* Hybrid AI (rules + statistical NLP)
* Confidence-driven decisions
* Explainable routing logic
* Multi-intent reasoning
* Conversation memory
* Risk-aware escalation

---

## 🚀 Future Work

* RAG (Retrieval-Augmented Generation) over real support knowledge
* ML-based intent classifier
* Benchmarking (BANKING77, CLINC150)
* API deployment (FastAPI)
* Production-ready multi-tenant system

---

## 💡 Why This Project Matters

Customer support AI systems in real-world products need:

* reliability under uncertainty
* explainable decisions
* safe escalation handling

This project demonstrates how to design such a system
without relying purely on black-box models.

---
update

## 👤 Author

Developed by Nooshin Borhani Rayeni
