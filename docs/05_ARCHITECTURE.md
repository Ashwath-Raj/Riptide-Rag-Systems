# 05 — ARCHITECTURE

## Design goal

Use the smallest architecture that clearly demonstrates the required trust boundaries.

## Reference stack

### Frontend
- React
- Vite
- Tailwind CSS

### Voice
- Browser Web Speech API
- Whisper/faster-whisper or Sarvam if already configured

### Backend
- FastAPI

### Retrieval
- sentence-transformers
- FAISS or another local vector index

### Injection detection
- pretrained ML prompt-injection classifier

### LLM
- already-configured API model

### Privacy
- regex + PII/NER detector

## Logical architecture

```text
                    ┌────────────────────────┐
                    │      React Client      │
                    │ Voice / Text / Evidence│
                    └───────────┬────────────┘
                                ↓
                    ┌────────────────────────┐
                    │        FastAPI          │
                    └───────────┬────────────┘
                                ↓
                     ┌──────────┴──────────┐
                     │    Query Security   │
                     └──────────┬──────────┘
                                ↓
                     ┌─────────────────────┐
                     │      Retriever      │
                     └──────────┬──────────┘
                                ↓
                     ┌─────────────────────┐
                     │  Chunk Security     │
                     └──────────┬──────────┘
                                ↓
                     ┌─────────────────────┐
                     │  Safe Evidence      │
                     └──────────┬──────────┘
                                ↓
                           ┌─────────┐
                           │   LLM   │
                           └────┬────┘
                                ↓
                     ┌─────────────────────┐
                     │ Privacy / Evidence  │
                     │      Gate           │
                     └──────────┬──────────┘
                                ↓
                             ANSWER
```

## Suggested tree

```text
/
├── frontend/
├── backend/
│   └── app/
│       ├── main.py
│       ├── api/
│       ├── services/
│       │   ├── ingestion.py
│       │   ├── chunking.py
│       │   ├── retrieval.py
│       │   ├── injection_guard.py
│       │   ├── generation.py
│       │   └── privacy_guard.py
│       ├── schemas/
│       └── config.py
├── scripts/
├── data/
│   ├── raw/
│   ├── processed/
│   └── index/
├── tests/
├── docs/
└── README.md
```

## Request trace

```json
{
  "request_id": "req-001",
  "source": "voice",
  "query_risk": 0.03,
  "candidate_count": 5,
  "quarantined_count": 1,
  "safe_count": 4,
  "pii_redacted": true,
  "citations": ["email-19382-body-02"]
}
```

This trace drives the UI and makes the security path debuggable.

## Resilience

- microphone fail → typed fallback
- classifier fail → fail closed
- privacy scanner fail → fail closed
- index fail → explicit failure
- LLM fail → explicit failure / labeled safe fallback

Avoid microservices and orchestration complexity in the sprint.
