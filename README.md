# 🤖 AI Support Agent

A hybrid AI-powered customer support agent that combines rule-based logic with statistical NLP to deliver accurate, explainable, and production-ready support responses.

---

## 🚀 Features

### 🧠 NLP & Intent Detection

* Hybrid intent detection (TF-IDF + keyword matching)
* Strong multi-intent detection
* Conflict resolution between overlapping intents
* Vague query handling

---

### 💬 Sentiment Awareness

* Sentiment detection:

  * neutral
  * frustrated
  * angry
  * urgent
* Sentiment-aware routing (affects final action)

---

### 🎯 Decision Engine

* Confidence scoring using score gap:

  * `confidence = top1_score - top2_score`
* Confidence-aware routing
* Action types:

  * answer
  * clarify
  * escalate

---

### 🧠 Advanced Decision Behavior (NEW)

#### ✔ Smart Low-Confidence Handling

* Detects when multiple intents exist but confidence is low
* Instead of generic fallback, generates **context-aware clarification**

Example:

```
"It looks like this may involve both your payment and refund request..."
```

#### ✔ Multi-Intent Conservative Routing

* Detects multiple intents aggressively
* Commits only when confidence is sufficient
* Avoids incorrect answers by falling back intelligently

---

### 🔍 Explainability (XAI)

* Routing reasons:

  * normal_routing
  * low_confidence_fallback
  * sentiment_override_angry
  * sentiment_override_frustrated

* Confidence breakdown:

  * top1_score
  * top2_score
  * score_gap
  * **pre_rule_confidence (NEW)**

---

### 📊 Confidence Transparency (NEW)

The system now distinguishes between:

* **Pre-rule confidence** → real model uncertainty
* **Final confidence** → after routing decisions

Example:

```
Confidence: 1.0 (pre_rule=0.131, top1=1.0, top2=0.0, gap=1.0)
```

---

### 🎭 Dynamic Response Tone (NEW)

#### ✔ Empathy-aware

* Adjusts tone based on user sentiment

#### ✔ Action-aware

* Escalate → reassurance
* Clarify → guided response

#### ✔ Confidence-aware

* Low confidence → cautious tone:

```
"I’m not fully sure I understood correctly..."
```

---

### 📊 Logging & Analysis

* Structured logs (`chat_log.jsonl`)
* Log analysis includes:

  * intent distribution
  * action distribution
  * sentiment distribution
  * routing reason distribution
  * confidence metrics
  * **multi-intent behavior (raw vs final vs reduced) (NEW)**

---

### 🧪 Testing

* Intent tests
* Sentiment tests
* Routing tests
* Regression tests:

  * multi-intent behavior
  * success / no_issue handling

---

## 🧠 System Architecture

```
User Input
   ↓
Preprocessing
   ↓
Intent Detection (TF-IDF + Keywords)
   ↓
Multi-Intent Selection + Conflict Resolution
   ↓
Sentiment Detection
   ↓
Confidence Calculation (score gap)
   ↓
Routing Logic (confidence + sentiment)
   ↓
Response Generation (dynamic tone)
   ↓
Logging & Explainability
```

---

## 🔍 Explainability

The system provides transparency into its decision-making:

* Detected sentiment
* Predicted topics (before rules) ✅
* Final topics (after rules) ✅
* Final action (answer / clarify / escalate)
* Confidence score (with pre-rule insight)
* Routing reason:

  * normal_routing
  * low_confidence_fallback
  * sentiment overrides

### Example Output

```
Detected sentiment: frustrated
Predicted topics before rules: ['payment_failed', 'refund_request']
Final topics after rules: ['general_help']
Final action: clarify (reason=low_confidence_fallback)
Confidence: 1.0 (pre_rule=0.131, top1=1.0, top2=0.0, gap=1.0)
```

---

## 📊 Log Analysis

Run:

```bash
python analyze_logs.py
```

This provides:

* Total messages
* Intent distribution
* Final action distribution
* Sentiment distribution
* Routing reason distribution
* Average confidence
* Score gap statistics

### 🧠 Multi-Intent Analysis (NEW)

* Raw multi-intent queries (before rules)
* Final multi-intent queries (after rules)
* Reduced multi-intent cases (fallback)

---

## ▶️ How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the chatbot

```bash
python -m src.main
```

---

## 🧪 Run Tests

```bash
python test_runner.py
```

Includes:

* Intent validation
* Sentiment validation
* Routing validation
* Regression tests

---

## 📁 Project Structure

```
src/
 ├── main.py
 ├── preprocessing.py
 ├── sentiment.py
 ├── logger_utils.py
 ├── confidence_utils.py

analyze_logs.py
test_runner.py
faq.json
chat_log.jsonl
README.md
```

---

## 🧩 Key Capabilities

* Hybrid AI (rules + statistical NLP)
* Multi-intent understanding
* Sentiment-aware decision making
* Confidence-based routing
* Explainable AI (XAI)
* Logging and analytics
* Regression-safe testing
* **Confidence-aware behavior (NEW)**
* **Dynamic response tone (NEW)**

---

## 🚀 Future Roadmap

* Embeddings-based semantic search
* ML intent classifier (LogReg / Transformer)
* Context-aware multi-turn conversations
* Advanced explainability (feature-level reasoning)
* Benchmarking (BANKING77, CLINC150)
* API deployment (FastAPI)
* UI dashboard

---

## 📌 Summary

This project is not a simple chatbot.
It is a **hybrid AI support system** designed with:

* Explainability
* Reliability
* Observability
* Production-readiness

---

## 👤 Author

Developed by Nooshin Borhani Rayeni
