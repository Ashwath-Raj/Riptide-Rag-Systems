# 11 — JUDGE CHECKLIST

## Qualification

### Voice
- [ ] microphone works
- [ ] transcript visible
- [ ] typed fallback available

### RAG
- [ ] Enron source
- [ ] >=10,000 emails
- [ ] source provenance

### Dynamic chunking
- [ ] fixed-size-only splitting is not used
- [ ] structure/semantic boundaries
- [ ] reason stored for each chunk

### Injection protection
- [ ] query scored with ML
- [ ] every retrieved chunk scored
- [ ] decisions are policy-driven
- [ ] risky chunks can be quarantined

### Zero trust
- [ ] retrieved text is data, not authority
- [ ] model output is treated as untrusted
- [ ] safe context is isolated

### Privacy
- [ ] email addresses detected
- [ ] phone numbers detected
- [ ] output is redacted before release

### Grounding
- [ ] evidence visible
- [ ] unsupported requests can refuse

## Stretch

- [ ] chunk inspector
- [ ] step-up verification
- [ ] session trust score
- [ ] cite-or-refuse

## Questions to expect

### Why dynamic chunking?
Because email structure carries meaning. Replies, forwards, signatures, and paragraphs are natural semantic boundaries.

### Why score the user query?
Because the voice transcript is an attacker-controlled input surface.

### Why score every retrieved chunk?
Because indirect prompt injection can be embedded in relevant documents.

### Why inspect model output?
Because an LLM is not a trusted security boundary.

### What if the classifier fails?
Fail closed rather than admitting unscored content.

### What if speech recognition fails?
Typed fallback uses the same downstream pipeline.

### How do you prove 10k+?
Expose source-email count in health/status metadata.

## Final gate

```text
VOICE               PASS / FAIL
10K+ EMAILS         PASS / FAIL
DYNAMIC CHUNKING    PASS / FAIL
QUERY ML SCORING    PASS / FAIL
CHUNK ML SCORING    PASS / FAIL
PII REDACTION       PASS / FAIL
CONTEXT ISOLATION   PASS / FAIL
REFUSAL PATH        PASS / FAIL
DEMO <= 90s         PASS / FAIL
```

If any required gate is FAIL, stop polishing and fix the gate.
