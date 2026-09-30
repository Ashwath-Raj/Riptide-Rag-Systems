from __future__ import annotations

import re
from dataclasses import dataclass

HEADER_LINE = re.compile(
    r"^(from|to|cc|bcc|date|sent|subject|received):\s+.+$",
    re.IGNORECASE,
)
REPLY_BOUNDARY = re.compile(
    r"^(-{2,}\s*original message\s*-{2,}|on .+ wrote:|from:\s.+\n?sent:)",
    re.IGNORECASE,
)
FORWARD_BOUNDARY = re.compile(
    r"^(-{2,}.*forwarded message.*-{2,}|begin forwarded message)",
    re.IGNORECASE,
)
SIGNATURE_BOUNDARY = re.compile(
    r"^(--\s*$|thanks[,!]?\s*$|best regards[,.]?\s*$|sent from my|confidentiality notice)",
    re.IGNORECASE,
)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'])")

@dataclass
class Chunk:
    chunk_id: str
    email_id: str
    parent_id: str
    section: str
    text: str
    boundary_reason: str
    char_count: int
    token_estimate: int


def estimate_tokens(text: str) -> int:
    return max(1, round(len(text) / 4))


class DynamicEmailChunker:
    """Structure-aware email chunker using meaningful document boundaries."""

    def chunk_email(self, email_id: str, text: str) -> list[Chunk]:
        sections = self._structural_segments(text)
        chunks: list[Chunk] = []
        counters: dict[str, int] = {}
        for section, body, reason in sections:
            units = self._paragraph_units(body, reason)
            merged = self._adaptive_merge(units)
            for unit_text, boundary in merged:
                counters[section] = counters.get(section, 0) + 1
                index = counters[section]
                chunk_id = f"{email_id}-{section}-{index:02d}"
                cleaned = unit_text.strip()
                if not cleaned:
                    continue
                chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        email_id=email_id,
                        parent_id=email_id,
                        section=section,
                        text=cleaned,
                        boundary_reason=boundary,
                        char_count=len(cleaned),
                        token_estimate=estimate_tokens(cleaned),
                    )
                )
        if not chunks and text.strip():
            cleaned = text.strip()
            chunks.append(
                Chunk(
                    chunk_id=f"{email_id}-body-01",
                    email_id=email_id,
                    parent_id=email_id,
                    section="body",
                    text=cleaned,
                    boundary_reason="paragraph_boundary",
                    char_count=len(cleaned),
                    token_estimate=estimate_tokens(cleaned),
                )
            )
        return chunks

    def _structural_segments(self, text: str) -> list[tuple[str, str, str]]:
        lines = text.replace("\r\n", "\n").split("\n")
        header_lines: list[str] = []
        idx = 0
        while idx < len(lines) and (HEADER_LINE.match(lines[idx].strip()) or (header_lines and not lines[idx].strip())):
            if lines[idx].strip():
                header_lines.append(lines[idx])
            idx += 1
        rest = lines[idx:]
        segments: list[tuple[str, list[str], str]] = []
        current_section = "body"
        current_reason = "paragraph_boundary"
        buffer: list[str] = []

        def flush() -> None:
            nonlocal buffer
            if buffer:
                segments.append((current_section, buffer, current_reason))
                buffer = []

        for line in rest:
            stripped = line.strip()
            if FORWARD_BOUNDARY.match(stripped):
                flush()
                current_section = "forward"
                current_reason = "forward_boundary"
                buffer = [line]
                continue
            if REPLY_BOUNDARY.match(stripped) or stripped.startswith(">"):
                if current_section != "reply":
                    flush()
                    current_section = "reply"
                    current_reason = "reply_boundary"
                buffer.append(line)
                continue
            if SIGNATURE_BOUNDARY.match(stripped) and current_section in {"body", "reply", "forward"}:
                flush()
                current_section = "signature"
                current_reason = "signature_boundary"
                buffer = [line]
                continue
            buffer.append(line)
        flush()
        out: list[tuple[str, str, str]] = []
        if header_lines:
            out.append(("header", "\n".join(header_lines).strip(), "header_boundary"))
        for section, buf, reason in segments:
            joined = "\n".join(buf).strip()
            if joined:
                out.append((section, joined, reason))
        return out or [("body", text.strip(), "paragraph_boundary")]

    def _paragraph_units(self, text: str, inherited_reason: str) -> list[tuple[str, str]]:
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
        units: list[tuple[str, str]] = []
        for para in paragraphs:
            reason = inherited_reason if inherited_reason != "paragraph_boundary" else "paragraph_boundary"
            sentences = self._split_sentences(para)
            if len(sentences) > 1:
                units.extend((sentence, "sentence_boundary") for sentence in sentences)
            else:
                units.append((para, reason))
        return units

    def _split_sentences(self, text: str) -> list[str]:
        parts = SENTENCE_SPLIT.split(text.strip())
        return [part.strip() for part in parts if part.strip()] or [text.strip()]

    def _adaptive_merge(self, units: list[tuple[str, str]]) -> list[tuple[str, str]]:
        return units
