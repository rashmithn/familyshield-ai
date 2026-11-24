"""Rule-based scam detection for message text.

This is a transparent, labelled rule engine. Every triggered rule yields an
indicator with a code, human label, severity, redacted phrase and explanation.
A separate optional ML probability is blended into the final risk score by the
scan service; this module only produces the rule-side evidence.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher

from backend.services.redaction import redact_phrase

CATEGORY_LABELS: dict[str, str] = {
    "fake_bank": "Fake bank / banking phishing",
    "upi_payment_scam": "UPI payment scam",
    "otp_request": "OTP / credential phishing",
    "lottery": "Lottery / prize scam",
    "fake_job_offer": "Fake job offer",
    "investment_scam": "Investment scam",
    "delivery_scam": "Delivery / parcel scam",
    "phishing": "Phishing / suspicious link",
    "impersonation": "Impersonation scam",
    "urgent_payment_request": "Urgent payment request",
    "digital_arrest": "Digital arrest scam",
    "fake_customer_care": "Fake customer care",
}


@dataclass
class Indicator:
    code: str
    label: str
    severity: str  # low | medium | high
    phrase: str
    description: str
    category: str
    weight: int


@dataclass(frozen=True)
class Rule:
    code: str
    label: str
    severity: str
    weight: int
    category: str
    description: str
    patterns: tuple[str, ...] = field(default_factory=tuple)

    def match(self, text: str) -> str | None:
        for pattern in self.patterns:
            found = re.search(pattern, text, flags=re.IGNORECASE)
            if found:
                return " ".join(found.group(0).split())
        return None


# Known official domains (used for in-text domain mismatch detection).
OFFICIAL_DOMAINS: dict[str, tuple[str, ...]] = {
    "sbi": ("sbi.co.in", "onlinesbi.sbi"),
    "hdfc": ("hdfcbank.com", "hdfc.com"),
    "icici": ("icicibank.com", "icici.com"),
    "axis": ("axisbank.com",),
    "pnb": ("pnbindia.in",),
    "kotak": ("kotak.com",),
    "bank of baroda": ("bankofbaroda.in",),
    "paytm": ("paytm.com",),
    "phonepe": ("phonepe.com",),
    "google pay": ("google.com", "gpay.com"),
    "gpay": ("google.com", "gpay.com"),
    "amazon": ("amazon.in", "amazon.com"),
    "microsoft": ("microsoft.com",),
    "flipkart": ("flipkart.com",),
}

DOMAIN_RE = re.compile(r"(?:(?:https?://)|(?:www\.))?\b([a-z0-9][a-z0-9-]*(?:\.[a-z0-9-]+)+)\b", re.I)


RULES: tuple[Rule, ...] = (
    Rule(
        code="otp_request",
        label="OTP request",
        severity="high",
        weight=38,
        category="otp_request",
        description="Banks and legitimate services never ask for your OTP.",
        patterns=(
            r"\b(?:share|send|provide|enter|tell|give|type|submit|reveal|confirm)\b.{0,45}"
            r"\b(?:otp|one[\s-]?time\s+(?:password|code)|passcode)\b",
            r"\b(?:otp|one[\s-]?time\s+(?:password|code)|passcode)\b.{0,45}"
            r"\b(?:share|send|provide|enter|tell|give|reveal|expire|submit)\b",
        ),
    ),
    Rule(
        code="credential_request",
        label="Credential / card detail request",
        severity="high",
        weight=32,
        category="otp_request",
        description="Asking for passwords, CVV or card details is a classic account-takeover tactic.",
        patterns=(
            r"\b(?:password|cvv|card\s*(?:number|details)|netbanking\s*(?:id|password|credentials)|"
            r"internet\s*banking\s*password|atm\s*pin)\b.{0,55}"
            r"\b(?:share|send|enter|provide|confirm|verify|type|submit)\b",
            r"\b(?:share|send|enter|provide|confirm|verify|type|submit)\b.{0,55}"
            r"\b(?:password|cvv|card\s*(?:number|details)|netbanking\s*(?:id|password|credentials))\b",
        ),
    ),
    Rule(
        code="fake_bank_alert",
        label="Fake bank alert",
        severity="high",
        weight=26,
        category="fake_bank",
        description="Banks rarely threaten immediate account closure in unsolicited messages.",
        patterns=(
            r"\b(?:sbi|hdfc|icici|axis|pnb|kotak|bank\s+of\s+baroda|state\s+bank)\b.{0,60}"
            r"\b(?:account|card|netbanking)\b.{0,80}"
            r"\b(?:block|blocked|suspend|suspended|deactivate|expire|verify|update|kyc)\b",
            r"\b(?:your|the)\s+bank\b.{0,50}\b(?:account|card)\b.{0,60}"
            r"\b(?:blocked|suspended|deactivated|expired|verify|update)\b",
        ),
    ),
    Rule(
        code="kyc_update",
        label="KYC update pressure",
        severity="medium",
        weight=20,
        category="fake_bank",
        description="Fraudsters often use the word KYC to push you into sharing personal data.",
        patterns=(r"\bkyc\b.{0,50}\b(?:update|verify|expired|pending|complete|suspend)\b",),
    ),
    Rule(
        code="upi_payment_scam",
        label="UPI payment request scam",
        severity="high",
        weight=24,
        category="upi_payment_scam",
        description="A collect request or payment request can drain your account if you approve it.",
        patterns=(
            r"\bupi\b.{0,60}\b(?:request|collect|payment|transfer|pay|verify|approve|receive)\b",
            r"\b(?:collect\s+request|payment\s+request|request\s+money)\b",
            r"\b(?:paytm|phonepe|google\s*pay|gpay)\b.{0,50}\b(?:request|verify|approve|send|collect)\b",
        ),
    ),
    Rule(
        code="payment_app_handle",
        label="Payment app handle",
        severity="low",
        weight=10,
        category="upi_payment_scam",
        description="Unknown payment handles are a common way to route fraudulent transfers.",
        patterns=(r"\b[a-z0-9._-]{2,}@(?:upi|paytm|phonepe|ybl|oksbi|okhdfcbank|okicici|apl)\b",),
    ),
    Rule(
        code="lottery_prize",
        label="Lottery / prize lure",
        severity="high",
        weight=30,
        category="lottery",
        description="Real prizes never require an advance fee, tax or bank details to be released.",
        patterns=(
            r"\b(?:lottery|lucky\s*draw|jackpot|cash\s*prize)\b.{0,80}"
            r"\b(?:claim|deposit|fee|tax|processing|pay|transfer|bank\s+details)\b",
            r"\byou\s+have\s+won\b|\bclaim\s+your\s+(?:prize|reward|lottery)\b",
        ),
    ),
    Rule(
        code="fake_job_offer",
        label="Fake job offer",
        severity="high",
        weight=24,
        category="fake_job_offer",
        description="Genuine employers do not ask for registration fees or bank details by chat.",
        patterns=(
            r"\b(?:job\s*offer|work\s+from\s+home|part[\s-]?time\s+job|remote\s+job|hiring|vacancy)\b"
            r".{0,90}\b(?:salary|stipend|registration\s*fee|training\s*fee|deposit|pay|bank\s+details|whatsapp)\b",
            r"\b(?:earn|salary|stipend)\b.{0,40}\b(?:per\s+day|per\s+week|₹\s?\d|rs\.?\s?\d)\b",
        ),
    ),
    Rule(
        code="investment_scam",
        label="Investment scam",
        severity="high",
        weight=28,
        category="investment_scam",
        description="Guaranteed or unusually high returns are a warning sign of investment fraud.",
        patterns=(
            r"\b(?:investment|invest|trading|crypto|bitcoin|mutual\s*fund|stock|forex)\b.{0,80}"
            r"\b(?:guaranteed|high\s+returns|profit|double|bonus|join\s+our\s+group|telegram)\b",
            r"\bguaranteed\s+returns?\b|\bdouble\s+your\s+money\b",
        ),
    ),
    Rule(
        code="delivery_scam",
        label="Delivery / parcel scam",
        severity="high",
        weight=24,
        category="delivery_scam",
        description="Delivery companies do not ask for unexpected customs or rescheduling fees by chat.",
        patterns=(
            r"\b(?:parcel|courier|delivery|package|shipment)\b.{0,80}"
            r"\b(?:customs|duty|fee|clearing|hold|reschedule|redeliver|pay|verify|confirm)\b",
            r"\b(?:delivery\s+failed|package\s+held|customs\s+duty)\b",
        ),
    ),
    Rule(
        code="phishing_link",
        label="Suspicious link request",
        severity="medium",
        weight=20,
        category="phishing",
        description="Links sent in unsolicited messages often lead to fake sign-in pages.",
        patterns=(
            r"\b(?:click|visit|open|tap)\b.{0,60}\b(?:link|here|below)\b",
            r"\b(?:verify\s+your\s+account|update\s+your\s+details|confirm\s+your\s+identity|login\s+here)\b",
        ),
    ),
    Rule(
        code="impersonation",
        label="Impersonation of authority",
        severity="medium",
        weight=22,
        category="impersonation",
        description="Scammers pose as officials or bank staff to pressure people into acting quickly.",
        patterns=(
            r"\b(?:i\s+am|this\s+is|from)\b.{0,40}"
            r"\b(?:manager|officer|director|executive|police|income\s+tax|rbi|cbi|bank)\b"
            r".{0,70}\b(?:call|message|contact|verify|urgent|notice)\b",
            r"\b(?:government|tax\s+department|rbi)\b.{0,60}\b(?:notice|action|verify|pay)\b",
        ),
    ),
    Rule(
        code="digital_arrest",
        label="Digital arrest threat",
        severity="high",
        weight=40,
        category="digital_arrest",
        description="Digital arrest is a scam; police never arrest people over a video call.",
        patterns=(
            r"\b(?:digital\s+arrest|online\s+arrest|you\s+are\s+under\s+arrest|arrest\s+warrant)\b",
            r"\b(?:do\s+not\s+disconnect|stay\s+on\s+the\s+video\s+call|under\s+investigation)\b",
        ),
    ),
    Rule(
        code="fake_customer_care",
        label="Fake customer care",
        severity="high",
        weight=22,
        category="fake_customer_care",
        description="Search-engine customer care numbers are often run by scammers.",
        patterns=(
            r"\b(?:customer\s+care|customer\s+service|helpline|support\s+team)\b.{0,80}"
            r"\b(?:call|contact|number|whatsapp|refund|verify|install|remote|connect)\b",
            r"\b(?:toll[\s-]?free)\b.{0,30}\d{3,4}[\s-]?\d{3,4}\b",
        ),
    ),
    Rule(
        code="urgency_pressure",
        label="Urgency / time pressure",
        severity="medium",
        weight=12,
        category="urgent_payment_request",
        description="Creating a false deadline is used to stop people from checking the facts.",
        patterns=(
            r"\b(?:urgent|immediately|right\s+now|asap|act\s+fast|last\s+chance|today\s+only)\b",
            r"\b(?:within\s+\d+\s*(?:minutes|hours)|expires?\s+(?:in|today|soon)|account\s+will\s+be)\b",
        ),
    ),
    Rule(
        code="reward_lure",
        label="Reward / lure language",
        severity="low",
        weight=10,
        category="lottery",
        description="Unusually generous rewards are often bait to collect personal information.",
        patterns=(
            r"\b(?:cashback|reward|bonus|gift|easy\s+money|lucrative)\b.{0,50}"
            r"\b(?:offer|earn|win|claim|get|free)\b",
            r"\b(?:limited\s+time|exclusive\s+offer|free\s+gift)\b",
        ),
    ),
    Rule(
        code="secrecy_pressure",
        label="Secrecy pressure",
        severity="high",
        weight=18,
        category="impersonation",
        description="Legitimate organisations do not ask you to hide a conversation from family.",
        patterns=(
            r"\b(?:do\s+not\s+tell|don'?t\s+tell|keep\s+this\s+(?:secret|confidential)|"
            r"do\s+not\s+share\s+this|don'?t\s+inform|hide\s+this)\b",
        ),
    ),
    Rule(
        code="threat_language",
        label="Threat / penalty language",
        severity="medium",
        weight=14,
        category="impersonation",
        description="Threats of legal action or fines are used to force quick payment.",
        patterns=(r"\b(?:legal\s+action|police\s+complaint|penalty|fine|jail|arrest|legal\s+notice)\b",),
    ),
    Rule(
        code="link_shortener",
        label="Obfuscated link",
        severity="low",
        weight=8,
        category="phishing",
        description="Shortened links hide the real destination and are common in scams.",
        patterns=(r"\b(?:bit\.ly|tinyurl\.com|t\.me|wa\.me)\b",),
    ),
)


def _domain_mismatch(text: str) -> str | None:
    """Flag a brand mentioned in text alongside a non-official lookalike domain."""
    domains = [match.group(1).lower().rstrip(".") for match in DOMAIN_RE.finditer(text)]
    if not domains:
        return None
    lowered = text.lower()
    for brand, official in OFFICIAL_DOMAINS.items():
        if not re.search(rf"\b{re.escape(brand)}\b", lowered):
            continue
        for domain in domains:
            if domain in official:
                continue
            label = domain.split(".")[0]
            close = SequenceMatcher(None, label.replace("-", ""), brand.replace(" ", "").replace("-", "")).ratio() >= 0.7
            contains = brand.replace(" ", "") in label.replace("-", "") or label.replace("-", "") in brand.replace(" ", "")
            if close or contains:
                return domain
    return None


@dataclass
class AnalysisResult:
    risk_score: int
    risk_level: str
    category: str
    confidence: float
    indicators: list[Indicator]
    rule_score: int
    ml_probability: float | None
    summary: str
    details: dict[str, object]


def analyze_message(text: str, ml_probability: float | None = None) -> AnalysisResult:
    """Run all rules, blend the optional ML score, and return a full analysis."""
    indicators: list[Indicator] = []
    for rule in RULES:
        phrase = rule.match(text)
        if phrase:
            indicators.append(
                Indicator(
                    code=rule.code,
                    label=rule.label,
                    severity=rule.severity,
                    phrase=redact_phrase(phrase),
                    description=rule.description,
                    category=rule.category,
                    weight=rule.weight,
                )
            )

    mismatch = _domain_mismatch(text)
    if mismatch:
        indicators.append(
            Indicator(
                code="domain_mismatch",
                label="Mismatched website domain",
                severity="high",
                phrase=redact_phrase(mismatch),
                description="The website address does not match the official domain of the organisation it claims to represent.",
                category="phishing",
                weight=30,
            )
        )

    rule_score = min(100, sum(indicator.weight for indicator in indicators))

    if ml_probability is None:
        risk_score = rule_score
    else:
        risk_score = round(0.65 * rule_score + 0.35 * (float(ml_probability) * 100))
        risk_score = max(0, min(100, risk_score))

    if risk_score >= 60:
        risk_level = "high_risk"
    elif risk_score >= 25:
        risk_level = "suspicious"
    else:
        risk_level = "safe"

    # Highest-weight category wins; first triggered rule breaks ties.
    category_weights: dict[str, int] = {}
    for indicator in indicators:
        category_weights[indicator.category] = category_weights.get(indicator.category, 0) + indicator.weight
    if category_weights:
        category_key = max(category_weights, key=lambda key: (category_weights[key], -list(category_weights).index(key)))
        category = CATEGORY_LABELS.get(category_key, category_key)
    elif ml_probability is not None and ml_probability >= 0.5:
        category = "Suspicious pattern"
    else:
        category = "No specific category detected"

    count = len(indicators)
    if ml_probability is not None:
        agreement = 1.0 - abs((rule_score / 100.0) - float(ml_probability))
        confidence = round(min(0.98, 0.5 + min(count, 5) * 0.06 + agreement * 0.16), 2)
    else:
        confidence = round(min(0.92, 0.52 + min(count, 5) * 0.08), 2)

    if risk_level == "high_risk":
        summary = f"This message has several traits of {category.lower()}."
    elif risk_level == "suspicious":
        summary = f"This message contains a few warning signs of {category.lower()}."
    else:
        summary = "No obvious scam indicators were detected in this message."

    details: dict[str, object] = {
        "rule_score": rule_score,
        "rules_triggered": [indicator.code for indicator in indicators],
        "ml_used": ml_probability is not None,
        "ml_probability": round(ml_probability, 4) if ml_probability is not None else None,
        "ml_note": (
            "ML classifier trained on synthetic examples only; it is a weak signal, not proof."
            if ml_probability is not None
            else "ML artifact not loaded; result is based on rules only."
        ),
    }
    return AnalysisResult(
        risk_score=risk_score,
        risk_level=risk_level,
        category=category,
        confidence=confidence,
        indicators=indicators,
        rule_score=rule_score,
        ml_probability=ml_probability,
        summary=summary,
        details=details,
    )
