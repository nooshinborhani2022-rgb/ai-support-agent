# 🤖 AI Support Agent

A hybrid AI-powered customer support agent that combines rule-based logic with statistical NLP to deliver accurate, explainable, and production-ready support responses.

---

## 🚀 Features

### 🧠 NLP & Intent Detection

* Hybrid intent detection (TF-IDF + keyword matching)
* Strong multi-intent detection
* Conflict resolution between overlapping intents
* Vague query handling

### 💬 Sentiment Awareness

* Sentiment detection:

  * neutral
  * frustrated
  * angry
  * urgent
* Sentiment-aware routing (affects final action)

### 🎯 Decision Engine

* Confidence scoring using score gap:

  * `confidence = top1_score - top2_score`
* Confidence-aware routing
* Action types:

  * answer
  * clarify
  * escalate

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

### 📊 Logging & Analysis

* Structured logs (`chat_log.jsonl`)
* Log analysis includes:

  * intent distribution
  * action distribution
  * sentiment distribution
  * routing reason distribution
  * confidence metrics

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
Response Generation
   ↓
Logging & Explainability
```

---

## 🔍 Explainability

The system provides transparency into its decision-making:

* Detected sentiment
* Selected intents (topics)
* Final action (answer / clarify / escalate)
* Confidence score (based on score gap)
* Routing reason:

  * normal_routing
  * low_confidence_fallback
  * sentiment overrides

### Example Output

```
Detected sentiment: frustrated
Selected topics: ['login_issue', 'double_charge']
Final action: escalate (reason=normal_routing)
Confidence: 1.279 (top1=3.153, top2=1.874, gap=1.279)
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
* Multi-intent queries

---

## ▶️ How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the chatbot

```bash
python src/main.py
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
 ├── config.py

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
