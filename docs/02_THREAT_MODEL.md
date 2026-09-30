# 02 — THREAT MODEL

## Objective

The security model is based on explicit trust boundaries and fail-closed behavior.

## Assets

- source emails
- email metadata
- personal identifiers
- transcript
- retrieved chunks
- vector index
- model prompt
- model output
- citations
- session trust state

## Trust zones

### Zone A — External input
Voice transcript and typed query.

**Trust:** untrusted.

### Zone B — Retrieved data
Email bodies, headers, replies, forwards, signatures, metadata.

**Trust:** untrusted.

### Zone C — Guarded evidence
Chunks that passed the injection policy.

**Trust:** usable only as data/evidence.

### Zone D — Generated output
LLM response.

**Trust:** untrusted.

### Zone E — Released answer
Output after privacy/evidence validation.

**Trust:** displayable.

## Threats

### T1 — Direct prompt injection
User attempts to override system behavior.

**Defense**
- ML query classifier
- policy threshold
- early block

### T2 — Indirect prompt injection
A retrieved email contains instructions aimed at the model.

**Defense**
- per-chunk classifier
- quarantine
- strict role/data separation

### T3 — Forwarded or quoted injection
Attack text is buried in a mail thread.

**Defense**
- structure-aware chunking
- provenance
- per-chunk scoring

### T4 — PII leakage
Model repeats email addresses, phone numbers, signatures, names, or other identifiers.

**Defense**
- output PII scanner
- redaction before display/audio

### T5 — Unsupported answer
LLM invents a conclusion.

**Defense**
- evidence/citation requirement
- cite-or-refuse behavior

### T6 — Retrieval poisoning
A malicious chunk ranks highly because of semantic similarity.

**Defense**
- score all retrieved chunks before generation

### T7 — Output injection
The LLM emits content that bypasses intended UI policy.

**Defense**
- final release gate

### T8 — Speech failure
Recognition fails or transcribes incorrectly.

**Defense**
- visible transcript
- typed fallback
- transcript remains untrusted

## Initial risk policy

Suggested configurable bands:

| Score | State | Default action |
|---:|---|---|
| 0.00–0.30 | Safe | allow |
| 0.30–0.70 | Review | tighter policy / inspect |
| 0.70–1.00 | High risk | block or quarantine |

These numbers are application parameters and must be validated against the selected classifier.

## Fail-closed behavior

If an injection model, privacy scanner, or evidence validator cannot make a decision:
- do not bypass it
- mark the request degraded
- refuse or use an explicit safe fallback

## Security principle

> Retrieval increases knowledge, not authority.
