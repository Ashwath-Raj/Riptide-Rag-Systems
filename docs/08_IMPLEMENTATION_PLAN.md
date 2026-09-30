# 08 — 60-MINUTE IMPLEMENTATION PLAN

## 00:00–05:00 — Skeleton

- frontend/backend shell
- environment variables
- health endpoint
- route shell
- base design tokens
- boot verification

**Exit:** app runs.

## 05:00–12:00 — Corpus

- load >=10,000 Enron emails
- normalize
- persist processed corpus
- verify count

**Exit:** corpus count is visible.

## 12:00–22:00 — Chunking + retrieval

- structural parser
- dynamic chunks
- embeddings
- vector index
- provenance

**Exit:** retrieval returns source-aware chunks.

## 22:00–32:00 — Security

- query injection classifier
- per-chunk injection classifier
- thresholds
- quarantine
- security trace

**Exit:** direct injection blocks; indirect injection quarantines.

## 32:00–40:00 — Generation

- guarded system prompt
- safe evidence injection
- source IDs
- grounded answer

**Exit:** normal query produces useful answer.

## 40:00–48:00 — Privacy

- email detector
- phone detector
- additional PII if available
- redaction
- cite/refuse

**Exit:** release gate works.

## 48:00–54:00 — UI + voice

- Web Speech API
- typed fallback
- trust pipeline
- answer surface
- evidence cards
- inspector if stable

**Exit:** end-to-end voice demo.

## 54:00–60:00 — Attack hardening

Run:
1. normal voice question
2. direct injection
3. malicious retrieval
4. PII leakage
5. unsupported query
6. microphone failure fallback

Fix gates before polish.

## Agent split

### Data
ingestion, normalization, chunking, embeddings

### Security
classifier, policy, PII, tests

### UI
white enterprise design system, voice, evidence, inspector

### Integration
API, LLM, end-to-end

## Cut order

Cut:
1. animation
2. inspector polish
3. trust history
4. step-up polish

Never cut:
1. query scoring
2. chunk scoring
3. dynamic chunking
4. PII gate
5. evidence path
