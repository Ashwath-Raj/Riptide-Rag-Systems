# 12 — DESIGN SYSTEM

## Brand direction

Riptide should look like an **enterprise security intelligence console**.

Not a consumer chatbot.
Not a purple AI dashboard.
Not a neon cyberpunk UI.

The identity comes from:
- paper-white surfaces
- black typography
- strong grid
- data density
- restrained safety colors
- documentary/evidence presentation
- visible system state

## Color tokens

```css
--paper: #F7F7F4;
--surface: #FFFFFF;
--ink: #111111;
--graphite: #2A2A2A;
--muted: #73736D;
--border: #D9D9D4;
--soft: #EEEDE8;

--safe: #2D6A4F;
--caution: #A16207;
--danger: #A12A2A;
```

No purple.
No blue brand accent.
No neon gradients.

## Surfaces

### Page
Warm white background.

### Primary surface
Pure white with a 1px neutral border.

### Secondary surface
Soft warm gray.

### Dark action
Near-black with white text.

Use dark surfaces intentionally for:
- security incident panels
- primary action
- command controls
- dense diagnostic blocks

## Buttons

### Primary
Black background, white text.

### Secondary
White background, black text, 1px border.

### Danger
White background, red border/text.

Do not use pill-shaped buttons everywhere.

## Cards

Cards are functional containers, not decoration.

Recommended:
- 8px radius
- 1px border
- 20–24px padding
- minimal shadow

## Status treatment

Status must use:
- text
- icon
- semantic color

Example:

`● SAFE`
`● REVIEW`
`● QUARANTINED`
`● BLOCKED`

Never communicate status by color alone.

## Data density

The interface should favor compact metadata lines:

```text
SAFE     0.02     142 ms     4 sources
```

This gives the product an operational feel.

## Typography

Use a modern neutral sans:
- Inter
- Geist
- IBM Plex Sans
- system sans fallback

For identifiers:
- JetBrains Mono
- SF Mono
- system monospace fallback

## Type hierarchy

```text
H1             30–32px / 700
H2             20–22px / 650
Section        14–16px / 650
Body           14–15px / 400
Metadata       12–13px / 500
Diagnostic     12–13px mono
```

## Icons

Use simple outline icons:
- microphone
- shield
- search
- file
- chevron
- alert triangle
- lock

Avoid playful sticker-style iconography.

## Grid

Use a 12-column desktop grid.

Recommended shell:
- left rail: 220–240px
- content max: 1440px
- gutters: 24–32px

## Enterprise patterns

Use:
- sticky command header
- persistent trust status
- compact tables
- right-side inspectors
- status bars
- evidence rows
- explicit audit trail

Avoid:
- feed-like social layouts
- chat bubble UIs
- oversized cards
- excessive whitespace that hides operational information

## Microcopy

Good:
- “QUERY BLOCKED”
- “4 SAFE / 1 QUARANTINED”
- “LLM CALL NOT EXECUTED”
- “PII REMOVED”
- “EVIDENCE INSUFFICIENT”

Bad:
- “Oops!”
- “Magic happened”
- “AI is thinking”
- “Looks good!”
- “Trust me”

## Motion

120–180ms transitions.
Use motion to show system progression only.

Examples:
- status ring during listening
- pipeline stage completion
- inspector slide-in

No perpetual shimmer.

## Final visual test

At 100% browser zoom, ask:

> Does this look more like a security operations console than an AI chatbot?

The answer should be yes.
