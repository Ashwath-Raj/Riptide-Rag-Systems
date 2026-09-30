# 01 — PRODUCT REQUIREMENTS DOCUMENT

## Product

Riptide is a voice-controlled zero-trust retrieval-augmented generation assistant for searching a large email archive.

## Problem

A conventional RAG assistant creates three dangerous assumptions:

1. the user query is benign,
2. retrieved content is trustworthy,
3. generated output is safe to expose.

The challenge explicitly introduces hostile instructions inside spoken queries and documents, while the archive contains personal information.

## Target user

An analyst/user who needs fast answers from a large email archive and wants visible guarantees that malicious instructions and personal data are not blindly propagated.

## Primary user journey

```text
User speaks
   ↓
Speech-to-text
   ↓
Query risk analysis
   ↓
Retrieve evidence
   ↓
Score every retrieved chunk
   ↓
Quarantine unsafe evidence
   ↓
Generate from safe evidence
   ↓
Validate + redact
   ↓
Answer + sources
```

## Functional requirements

### FR-01 — Speech input
The application SHALL support microphone-driven speech-to-text using an allowed sprint mechanism.

### FR-02 — Typed fallback
The application SHALL allow typed input without changing the downstream security pipeline.

### FR-03 — Corpus size
The application SHALL index at least 10,000 Enron emails.

### FR-04 — Dynamic chunking
The application SHALL use content-aware chunk boundaries.

### FR-05 — Query security
Every transcript SHALL receive an ML-based injection score before retrieval/generation.

### FR-06 — Retrieval security
Every retrieved chunk SHALL receive an ML-based injection score before context admission.

### FR-07 — Context isolation
Retrieved content SHALL be treated as evidence/data, not as instructions.

### FR-08 — Output privacy
Generated output SHALL be scanned and sanitized for supported PII classes before release.

### FR-09 — Evidence
Answers SHOULD expose source email/chunk provenance.

### FR-10 — Refusal
The system SHOULD refuse unsupported requests rather than fabricate evidence.

## Non-functional requirements

### Reliability
The core demo cannot depend on a fragile chain of external systems.

### Explainability
A judge should understand the major trust boundaries from the UI.

### Determinism
Data preprocessing and index generation should be reproducible.

### Fail-closed security
Security dependency failures must not silently become allow decisions.

## Acceptance table

| Requirement | Acceptance |
|---|---|
| Voice | spoken query becomes visible transcript |
| 10k corpus | health/status reports >= 10,000 source emails |
| Dynamic chunks | chunk metadata shows boundary reason |
| Query guard | visible model risk + decision |
| Chunk guard | every returned chunk has score + decision |
| Isolation | retrieved instruction cannot override system policy |
| PII guard | raw email/phone identifiers absent from released answer |
| Grounding | answer references evidence |
| Refusal | unsupported/high-risk request can be blocked |

## Scope priority

**Never cut:** query guard, chunk guard, dynamic chunking, privacy gate.

**Cut first:** animation, secondary screens, advanced analytics, stretch features.
