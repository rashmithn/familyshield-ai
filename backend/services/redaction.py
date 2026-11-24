"""Secret redaction for anything that is stored or displayed.

We NEVER persist raw OTPs, card numbers, phone numbers, email addresses or UPI
handles. Detection runs on the original in-memory text; only redacted versions
reach the database and API responses.
"""

from __future__ import annotations

import re

# Order matters: more specific patterns run first.
UPI_HANDLE_RE = re.compile(
    r"(?i)\b[a-z0-9._-]{2,}@(?:upi|paytm|phonepe|paypal|ybl|oksbi|okhdfcbank|okicici|"
    r"apl|sbi|hdfc|icici|axl|kotak|pnb|iob|canara|bob)\b"
)
EMAIL_RE = re.compile(r"(?i)\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b")
SECRET_CODE_RE = re.compile(
    r"(?i)\b(otp|one[\s-]?time\s+(?:password|code)|pin|passcode|cvv|code)\b"
    r"\s*(?:is|are|:|=|-)?\s*(\d{4,8})\b"
)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?91[\s-]?)?[6-9]\d{9}(?!\d)")
CARD_RE = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")
LONG_DIGITS_RE = re.compile(r"(?<!\d)(?:\d[\s-]?){6,}(?!\d)")


def redact_text(text: str | None) -> str:
    """Replace secrets with labelled placeholders."""
    if not text:
        return ""
    redacted = UPI_HANDLE_RE.sub("[UPI ID REDACTED]", text)
    redacted = EMAIL_RE.sub("[EMAIL REDACTED]", redacted)
    redacted = SECRET_CODE_RE.sub(r"\1 [REDACTED]", redacted)
    redacted = PHONE_RE.sub("[PHONE REDACTED]", redacted)
    redacted = CARD_RE.sub("[CARD REDACTED]", redacted)
    redacted = LONG_DIGITS_RE.sub("[NUMBER REDACTED]", redacted)
    return redacted


def redact_phrase(phrase: str | None, max_len: int = 140) -> str:
    """Redact and shorten an indicator phrase for safe display."""
    value = redact_text(phrase)
    value = " ".join(value.split())
    if len(value) > max_len:
        value = value[: max_len - 3].rstrip() + "..."
    return value


def content_excerpt(text: str | None, max_len: int = 320) -> str:
    """Redacted, whitespace-normalised excerpt for storage/display."""
    value = redact_text(text)
    value = " ".join(value.split())
    if len(value) > max_len:
        value = value[: max_len - 3].rstrip() + "..."
    return value
