"""Human-friendly explanations.

Groq is used only when GROQ_API_KEY is configured. Otherwise a deterministic,
well-written fallback is used. Both always include an explicit no-guarantee
caveat. No user text or API key is logged.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass

import httpx

from backend.config import settings
from backend.services.message_analysis import AnalysisResult

logger = logging.getLogger(__name__)

CAVEAT = (
    "This assessment is not a guarantee of safety: scammers can imitate legitimate "
    "messages and links, so always verify independently with the organisation using "
    "contact details you already trust."
)

_GENERAL_ACTIONS = [
    "Do not click links or share information until you have verified the message independently.",
    "Call the organisation using the number on their official website or the back of your card.",
    "Report suspicious messages to your bank and to the national cybercrime helpline (1930 in India).",
]

_ACTIONS_BY_CATEGORY: dict[str, list[str]] = {
    "otp_request": ["Never share your OTP, PIN or password with anyone, including someone claiming to be bank staff."],
    "fake_bank": ["Contact your bank directly on its official helpline before taking any action."],
    "upi_payment_scam": ["Do not approve any UPI collect request you were not expecting; open your payment app yourself to check."],
    "lottery": ["Do not pay any fee or tax to claim a prize you never entered."],
    "fake_job_offer": ["Do not pay registration or training fees for a job offered only over chat."],
    "investment_scam": ["Verify any adviser's registration with the regulator before investing money."],
    "delivery_scam": ["Track the parcel using the courier's official website instead of the message link."],
    "digital_arrest": ["Digital arrest does not exist; disconnect the call and contact your local police station directly."],
    "fake_customer_care": ["Find support numbers only on the company's official website, not from search ads or messages."],
    "impersonation": ["Do not act on claims of authority from an unknown caller; verify through an official channel."],
    "urgent_payment_request": ["Pause before paying: urgency is a common pressure tactic."],
    "phishing": ["Type the website address yourself rather than opening the link in the message."],
}


@dataclass
class ExplanationResult:
    summary: str
    explanation: str
    recommended_actions: list[str]
    groq_used: bool
    groq_error: str | None = None


def _actions(analysis: AnalysisResult) -> list[str]:
    actions: list[str] = []
    for indicator in analysis.indicators:
        for action in _ACTIONS_BY_CATEGORY.get(indicator.category, []):
            if action not in actions:
                actions.append(action)
    for action in _GENERAL_ACTIONS:
        if action not in actions:
            actions.append(action)
        if len(actions) >= 5:
            break
    if analysis.risk_level == "safe":
        return [
            "Stay cautious: no obvious scam indicators were found, but this is not a guarantee.",
            "Verify unexpected requests through an official phone number or app.",
        ]
    return actions[:5]


def _fallback(analysis: AnalysisResult) -> ExplanationResult:
    if analysis.risk_level == "safe":
        explanation = (
            "No obvious scam indicators were detected in this text. Nothing in the content "
            "matched our known warning patterns, but new scams appear every day. " + CAVEAT
        )
    else:
        names = ", ".join(indicator.label.lower() for indicator in analysis.indicators[:3]) or "suspicious wording"
        explanation = (
            f"We noticed {names}. Signals like these are commonly used to rush people into "
            "sharing information or money. The score combines transparent rule evidence with "
            + (
                "a classifier trained only on synthetic examples. "
                if analysis.ml_probability is not None
                else "rule evidence only (no ML model loaded). "
            )
            + CAVEAT
        )
    return ExplanationResult(
        summary=analysis.summary,
        explanation=explanation,
        recommended_actions=_actions(analysis),
        groq_used=False,
    )


def build_explanation(analysis: AnalysisResult) -> ExplanationResult:
    """Return explanation + actions, using Groq only when configured."""
    fallback = _fallback(analysis)
    if not settings.GROQ_API_KEY:
        return fallback

    system_prompt = (
        "You are a fraud-awareness assistant for families. Explain risks in plain, calm language "
        "for a non-technical person. Never claim certainty. Always include the exact caveat: "
        + CAVEAT
        + " Return ONLY JSON with keys: summary (string), explanation (string), "
        "recommended_actions (array of short concrete strings). Do not invent facts."
    )
    user_prompt = (
        f"Risk level: {analysis.risk_level}\nCategory: {analysis.category}\n"
        f"Indicators: {[indicator.label for indicator in analysis.indicators]}\n"
        f"Score: {analysis.risk_score}/100\n"
        "Write a short summary, a 2-3 sentence explanation and up to 5 concrete actions."
    )
    try:
        response = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.2,
                "max_tokens": 500,
                "response_format": {"type": "json_object"},
            },
            timeout=8.0,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        data = json.loads(content)
        summary = str(data.get("summary") or analysis.summary).strip()
        explanation = str(data.get("explanation") or "").strip()
        actions = [str(item).strip() for item in data.get("recommended_actions", []) if str(item).strip()]
        if not explanation or not actions:
            raise ValueError("incomplete Groq response")
        if CAVEAT not in explanation:
            explanation = explanation.rstrip() + " " + CAVEAT
        return ExplanationResult(
            summary=summary[:300],
            explanation=explanation[:4000],
            recommended_actions=actions[:5],
            groq_used=True,
        )
    except Exception as exc:
        # Log only the exception type: responses can contain user-submitted text.
        logger.warning("Groq explanation unavailable (%s); using deterministic fallback.", type(exc).__name__)
        fallback.groq_error = type(exc).__name__
        return fallback
