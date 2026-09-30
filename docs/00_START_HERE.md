# 00 — START HERE

## Mission

Build a voice-controlled zero-trust RAG assistant over the provided Enron email archive in a 60-minute sprint.

The system must assume that:
- the spoken/transcribed query is untrusted,
- retrieved email content is untrusted,
- model output is untrusted.

The challenge explicitly requires voice input, RAG over at least 10,000 emails, dynamic chunking, ML injection scoring on the query and every retrieved chunk, and PII protection before output.

## Product thesis

> Retrieval provides evidence. Retrieval never provides authority.

The product should make the following pipeline visible:

```text
VOICE
  ↓
TRANSCRIPT
  ↓
QUERY SECURITY
  ↓
RETRIEVAL
  ↓
CHUNK SECURITY
  ↓
SAFE EVIDENCE
  ↓
LLM
  ↓
OUTPUT VALIDATION
  ↓
SANITIZED ANSWER
```

## Hard gates

### 1. Voice
Use browser Web Speech API, Sarvam AI, or Whisper/faster-whisper.
Typed fallback is allowed when microphone capture fails.

### 2. Corpus
Use at least 10,000 Enron emails.

### 3. Dynamic chunking
Do not use fixed-size-only splitting.
Use structure-aware, semantic, sentence-window, parent-child, or adaptive methods.

### 4. Injection scoring
Every spoken query gets a model score before it reaches the LLM.
Every retrieved chunk gets a model score before it reaches the LLM.

Retrieved text is data, never instructions.

### 5. Personal-data guard
Detect and redact email addresses, phone numbers, and other available personal identifiers before release.

## P0

- voice input
- typed fallback
- 10k+ email ingestion
- dynamic chunking
- embeddings + retrieval
- query injection score
- per-chunk injection score
- LLM generation
- output PII guard
- citations/evidence
- attack-testable UI

## P1 stretch

- chunk inspector
- step-up verification
- live session trust score
- cite-or-refuse

## Explicitly avoid

- auth systems
- multi-tenant architecture
- Kubernetes
- elaborate analytics
- event-bus infrastructure
- agent orchestration for its own sake
- huge settings surfaces

Those consume sprint time without satisfying a qualification gate.

## Definition of done

- app boots
- >=10,000 source emails are indexed
- dynamic chunker is active
- query security runs before generation
- every retrieved chunk is scored
- unsafe chunks are quarantined
- untrusted context cannot redefine policy
- output is PII-scanned before release
- unsupported questions can refuse
- happy-path demo runs in <=90 seconds
