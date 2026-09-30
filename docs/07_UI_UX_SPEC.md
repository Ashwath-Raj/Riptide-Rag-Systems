# 07 — UI/UX SPECIFICATION

## Product character

The interface should look like a serious enterprise security product, not a consumer AI chatbot.

### Desired impression

- precise
- calm
- authoritative
- information-dense
- operational
- trustworthy
- modern without being fashionable for its own sake

### Explicitly avoid

- purple/blue AI gradients
- neon effects
- giant rounded cards everywhere
- glassmorphism as the primary language
- cartoon robot illustrations
- floating chatbot bubbles
- decorative “AI sparkle” icons
- excessive shadows
- oversized hero typography

## Visual direction

### Theme

White-first enterprise workspace.

Use:
- warm paper white for the page background
- pure white for surfaces
- near-black ink for headings and primary controls
- graphite for secondary surfaces
- warm neutral gray for borders
- restrained safety colors only for status semantics

### Suggested palette

```text
Paper        #F7F7F4
Surface      #FFFFFF
Ink          #111111
Graphite     #2A2A2A
Border       #D9D9D4
Muted        #73736D
Soft        #EEEDE8

Safe         #2D6A4F
Caution      #A16207
Danger       #A12A2A
```

Do not introduce purple or blue as brand colors.

## Layout philosophy

Use a **security operations console** layout rather than a chat layout.

```text
┌─────────────────────────────────────────────────────────────────┐
│ RIPTIDE                                     ZERO-TRUST / READY  │
├───────────────┬─────────────────────────────────────────────────┤
│ WORKSPACE     │ COMMAND HEADER                                 │
│               │                                                 │
│ Search        │ ASK THE ARCHIVE                                 │
│ Evidence      │                                                 │
│ Security      │ [ waveform / transcript / mic ]                 │
│ Inspect       │                                                 │
│               │                                                 │
│               │ TRUST PIPELINE                                  │
│               │ ┌────┬──────┬──────┬──────┬──────┐            │
│               │ │STT │QUERY │RETR. │CHUNK │OUTPUT│            │
│               │ └────┴──────┴──────┴──────┴──────┘            │
│               │                                                 │
│               │ ANSWER                                         │
│               │ ┌───────────────────────────────────────────┐ │
│               │ │ Evidence-backed answer...                 │ │
│               │ └───────────────────────────────────────────┘ │
│               │                                                 │
│               │ EVIDENCE                                       │
│               │ ┌───────────────────────────────────────────┐ │
│               │ │ email-19382 · SAFE · 0.02                │ │
│               │ │ email-44210 · QUARANTINED · 0.94         │ │
│               │ └───────────────────────────────────────────┘ │
└───────────────┴─────────────────────────────────────────────────┘
```

## Navigation

Use a compact left rail:

- **Search**
- **Evidence**
- **Security**
- **Inspect**

Do not build separate pages unless needed; panel swapping is enough for the sprint.

## Primary interaction

### Voice control

The microphone should be a strong rectangular or squared control rather than a giant floating circle.

States:

**Idle**
`Speak`

**Listening**
`Listening · 00:03`

**Transcribing**
`Transcribing`

**Blocked**
`Query blocked`

The typed fallback should remain visibly available beneath the voice control.

## Security pipeline

This is the visual differentiator.

Five stages:

1. STT
2. Query Guard
3. Retrieval
4. Chunk Guard
5. Output Gate

Each stage has:
- status
- latency
- score/decision when relevant

Example:

```text
STT             COMPLETE       320ms
QUERY GUARD     SAFE           0.03
RETRIEVAL       5 CANDIDATES   118ms
CHUNK GUARD     4 SAFE / 1     92ms
OUTPUT GATE     2 PII REDACT   18ms
```

This is more enterprise-grade than a generic “thinking…” spinner.

## Answer surface

Use a clean document-like answer panel.

Header:
`ANSWER`

Metadata:
`Grounded · 4 sources · PII filtered`

Body:
- concise answer
- inline evidence markers `[1] [2]`
- no giant chat bubble

Footer:
`Privacy gate passed`

## Evidence surface

Each evidence row contains:

```text
EMAIL 19382
Contract discussion
SAFE · 0.02
[Inspect]
```

For quarantined content:

```text
EMAIL 44210
Potential instruction injection
QUARANTINED · 0.94
[Inspect]
```

Avoid showing raw PII in list previews.

## Chunk inspector

Open as a right-side sheet rather than a new route.

Layout:

```text
CHUNK INSPECTOR

Email ID       19382
Chunk ID       body-02
Section        body
Size           1,432 chars
Boundary       paragraph + semantic
Risk           0.02
Decision       SAFE

SOURCE PREVIEW
────────────────────
...
```

## Security incident state

When a query is blocked, change the content area into an incident-style state.

```text
QUERY BLOCKED

Injection risk detected.

Risk score       0.94
Policy           BLOCK
LLM call         NOT EXECUTED

[View detection details]
```

Do not use a huge red screen. Enterprise security products use restraint.

## Typography

### Heading
A clean grotesk or neo-grotesk.

Preferred feel:
- Inter
- Geist
- IBM Plex Sans
- Helvetica/Arial fallback

### Data / diagnostics
Use a mono font for:
- IDs
- scores
- latency
- request traces

### Scale

```text
Page title     28–32px
Section title  16–18px
Body           14–15px
Metadata       12–13px
```

No 64px SaaS hero typography inside the product.

## Spacing

Use a disciplined 4/8px rhythm.

Primary spacing:
- 8
- 12
- 16
- 24
- 32
- 48

## Component shape

Use modest radii:
- controls: 6px
- cards: 8px
- panels: 10px

Avoid every object becoming a pill.

## Borders and shadows

Prefer borders over shadows.

Default:
`1px solid #D9D9D4`

Use shadows only for:
- right-side inspector
- transient dialog
- command surface

## Motion

Motion should communicate system state.

Use:
- 120–180ms transitions
- subtle status pulse while listening
- stage progression in the trust pipeline

Avoid:
- floating particles
- gradient animations
- infinite shimmer everywhere

## Responsive behavior

Desktop-first for judging.

Minimum supported:
- 1280px desktop

Tablet:
- collapse side rail

Mobile:
- stacked security pipeline
- full-width voice control

## Accessibility

- keyboard operation
- visible focus
- transcript always visible
- color is never the only status indicator
- status has text labels
- sufficient contrast
- reduced-motion support

## UI content rules

Prefer:
- “SAFE”
- “BLOCKED”
- “QUARANTINED”
- “REDACTED”
- “4 SOURCES”

Avoid:
- “Magic”
- “AI brain”
- “Super smart”
- “Trust me”
- “Thinking…”

The product should sound like infrastructure, not marketing.
