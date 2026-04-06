# AI Customer Support Agent

A hybrid AI-powered customer support chatbot designed to handle real-world support queries using a combination of rule-based logic, TF-IDF retrieval, multi-intent detection, and basic sentiment awareness.

## Features
- Intent detection (single + multi-intent)
- Action-based routing:
  - Answer
  - Clarify
  - Escalate
- TF-IDF + keyword hybrid matching
- Vague query handling (e.g. "it's not working")
- Conflict resolution between intents
- Basic sentiment detection:
  - neutral
  - frustrated
  - angry
  - urgent
- Sentiment-aware response tone
- Sentiment-aware urgent intent boosting
- Logging system (`chat_log.jsonl`)
- Log analysis
- Full validation test suite (100% accuracy)

## How It Works

### 1. Preprocessing
- Lowercasing
- Contraction expansion (e.g. "can't" → "cannot")
- Stopword removal

### 2. Intent Detection
- TF-IDF similarity
- Keyword matching
- Hybrid scoring

### 3. Multi-Intent Handling
- Select top intents
- Apply conflict resolution rules
- Prevent false multi-intent predictions

### 4. Sentiment Detection
- Rule-based sentiment detection
- Keyword-based matching
- Contraction-aware normalization
- Priority-based sentiment label selection

### 5. Response Generation
- Single intent → direct response
- Multi-intent → combined response
- Sentiment-aware tone prefix
- Routing:
  - Answer
  - Clarify
  - Escalate

## Recent Improvements

### Vague Query Handling
Handles ambiguous inputs like:
- "it's not working"
- "I have a problem"
- "help me"

These are safely routed to `general_help` instead of incorrect intents.

### Contraction Normalization
Expands contractions:
- "I'm" → "I am"
- "can't" → "cannot"
- "it's" → "it is"

Improves matching quality for both TF-IDF and keywords.

### Intent Disambiguation
Reduced confusion between:
- `billing_question`
- `refund_request`

Using domain-specific cues.

### Hybrid Scoring Improvements
- TF-IDF + keyword scoring combined
- Stable weighting to avoid breaking multi-intent detection

### Sentiment Analysis (Phase E - Step 1)
Added a simple rule-based sentiment layer with support for:
- `neutral`
- `frustrated`
- `angry`
- `urgent`

Current sentiment usage:
- adds empathetic response prefixes
- stores sentiment results in logs
- supports sentiment distribution analysis
- gives a small boost to urgent high-priority intents

### Regression Testing
Added tests for:
- Vague queries
- Billing vs refund edge cases
- Urgent multi-intent queries
- Angry sentiment detection

Ensures future changes don’t break existing behavior.

## Testing

Run full validation:

```bash
python test_runner.py
```

## Logging & Analysis

Logs are saved in:

```bash
chat_log.jsonl
```

Analyze logs:

```bash
python analyze_logs.py
```

## Current Capabilities
- Multi-intent detection
- Hybrid intent scoring
- Clarify / Answer / Escalate routing
- Vague query detection
- Basic sentiment detection
- Sentiment-aware tone handling
- Sentiment-aware urgent boosting
- Logging + analytics
- 100% test accuracy

## Tech Stack
- Python
- scikit-learn (TF-IDF, cosine similarity)
- Rule-based NLP
- JSON-based dataset

## Future Work
- Embedding-based retrieval
- ML-based intent classification
- Sentiment-aware routing
- Explainable AI (XAI)
- Benchmarking (BANKING77, CLINC150, etc.)
- FastAPI + UI deployment

## Project Status
Active development — improving NLP, ML, and product capabilities step by step.