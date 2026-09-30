# 03 — DATA AND DYNAMIC CHUNKING

## Corpus

The challenge specifies Enron email data and requires at least 10,000 emails.

Referenced sources:
- Hugging Face: `haritzpuerto/the_pile_00_Enron_Emails`
- Kaggle: `wcukierski/enron-email-dataset`

Optional injection classifier training data:
- Hugging Face: `geekyrakshit/prompt-injection-dataset`

## Ingestion contract

Normalize each source email while retaining provenance.

```json
{
  "email_id": "stable-id",
  "text": "...",
  "metadata": {
    "source": "enron",
    "from": "...",
    "to": "...",
    "cc": "...",
    "date": "...",
    "subject": "..."
  }
}
```

Do not discard source identity.

## Sprint strategy

Start with exactly 10,000+ emails to prove the entire pipeline.
Only scale further after retrieval and security gates are stable.

## Why fixed-size-only chunking fails here

Email has structure:

```text
EMAIL
├── metadata/header
├── current message
├── quoted reply
├── forwarded message
├── signature
└── separators
```

Arbitrary character/token windows can:
- split related evidence,
- merge unrelated conversations,
- split a malicious instruction from its provenance,
- hide PII inside apparently generic chunks.

## Recommended chunking algorithm

### Stage 1 — Structural segmentation

Detect:
- header region
- current body
- quoted reply sections
- forwarded message sections
- signature blocks

### Stage 2 — Semantic grouping

Within each structural region:
1. split at paragraph boundaries;
2. split oversized paragraphs at sentence boundaries;
3. merge very small adjacent units when semantically continuous;
4. use bounded overlap only when context continuity requires it.

Result: variable-size chunks whose boundaries are explainable.

## Chunk metadata

```json
{
  "chunk_id": "email-19382-body-02",
  "parent_id": "email-19382",
  "section": "body",
  "boundary_reason": "paragraph+semantic",
  "text": "...",
  "char_count": 1432,
  "token_estimate": 360
}
```

## Boundary reason taxonomy

- `header_boundary`
- `paragraph_boundary`
- `sentence_boundary`
- `reply_boundary`
- `forward_boundary`
- `signature_boundary`
- `semantic_topic_boundary`

## Retrieval metadata

Every vector result should preserve:
- email ID
- chunk ID
- parent ID
- source metadata
- chunk text
- boundary reason

## Chunk inspector

Stretch UI:

```text
EMAIL 19382
├── header      180 chars
├── body-01    1020 chars
├── body-02    1432 chars  ← paragraph + semantic
├── reply-01    880 chars  ← reply boundary
└── signature   210 chars
```

Display:
- boundary
- size
- reason
- injection score
- decision
- preview

## Privacy note

Chunking is not a privacy boundary. Headers and signatures can contain dense personal data, so output protection remains mandatory.
