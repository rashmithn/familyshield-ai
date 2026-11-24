"""Safe, static URL analysis.

Rules only inspect the URL string. Optional external checks are limited to:
  * a TLS certificate handshake (no HTTP request, no page content, no scripts)
  * Google Safe Browsing's threat-match API (if a key is configured)
Network probes are opt-in via SAFE_URL_PROBE (default false). No browser is
ever opened and no fetched content is executed.
"""

from __future__ import annotations

import ipaddress
import logging
import re
import socket
import ssl
from difflib import SequenceMatcher
from urllib.parse import urlsplit

import httpx

from backend.config import settings
from backend.services.message_analysis import (
    AnalysisResult,
    CATEGORY_LABELS,
    Indicator,
    OFFICIAL_DOMAINS,
)
from backend.services.redaction import redact_phrase

logger = logging.getLogger(__name__)

BRANDS = (
    "bank", "upi", "paytm", "phonepe", "google", "microsoft", "amazon", "sbi",
    "hdfc", "icici", "axis", "paypal", "flipkart", "whatsapp", "netflix",
)
SUSPICIOUS_TLDS = {
    "tk", "ml", "ga", "cf", "gq", "xyz", "top", "cc", "su", "pw", "zip",
    "mov", "click", "country", "stream", "download", "info", "biz",
}
SENSITIVE_PATH_RE = re.compile(
    r"(?:login|signin|verify|otp|password|bank|update|kyc|secure|account|confirm|reset)",
    re.I,
)
SENSITIVE_QUERY_RE = re.compile(r"[?&](?:otp|pin|password|passcode|card|cvv|token|secret)=", re.I)
CONFUSABLES = str.maketrans({
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x", "і": "i",
    "А": "A", "Е": "E", "О": "O", "Р": "P", "С": "C", "У": "Y", "Х": "X", "І": "I",
})


def _make_result(
    indicators: list[Indicator], ml_probability: float | None, extra_details: dict[str, object]
) -> AnalysisResult:
    rule_score = min(100, sum(item.weight for item in indicators))
    if ml_probability is None:
        risk_score = rule_score
    else:
        risk_score = max(0, min(100, round(0.65 * rule_score + 0.35 * float(ml_probability) * 100)))
    risk_level = "high_risk" if risk_score >= 60 else "suspicious" if risk_score >= 25 else "safe"

    category_weights: dict[str, int] = {}
    for item in indicators:
        category_weights[item.category] = category_weights.get(item.category, 0) + item.weight
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
        summary = f"This URL has several traits of {category.lower()}."
    elif risk_level == "suspicious":
        summary = f"This URL contains a few warning signs of {category.lower()}."
    else:
        summary = "No obvious suspicious URL indicators were detected."

    details: dict[str, object] = {
        "rule_score": rule_score,
        "rules_triggered": [item.code for item in indicators],
        "ml_used": ml_probability is not None,
        "ml_probability": round(ml_probability, 4) if ml_probability is not None else None,
        "ml_note": (
            "ML classifier trained on synthetic examples only; it is a weak signal, not proof."
            if ml_probability is not None
            else "ML artifact not loaded; result is based on rules only."
        ),
    }
    details.update(extra_details)
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


def _add(
    items: list[Indicator], code: str, label: str, severity: str, weight: int,
    category: str, description: str, phrase: str,
) -> None:
    items.append(
        Indicator(
            code=code,
            label=label,
            severity=severity,
            phrase=redact_phrase(phrase, max_len=200),
            description=description,
            category=category,
            weight=weight,
        )
    )


def _is_private_host(host: str) -> bool:
    try:
        return ipaddress.ip_address(host).is_private
    except ValueError:
        return host in {"localhost"} or host.endswith(".local") or host.endswith(".localhost")


def _tls_probe(host: str, port: int) -> str | None:
    """Return None when the TLS certificate is valid, else a short error label."""
    context = ssl.create_default_context()
    context.check_hostname = True
    try:
        with socket.create_connection((host, port), timeout=settings.TLS_PROBE_TIMEOUT_SECONDS) as raw:
            with context.wrap_socket(raw, server_hostname=host) as tls:
                tls.getpeercert()
        return None
    except ssl.SSLCertVerificationError:
        return "certificate verification failed"
    except (socket.timeout, TimeoutError):
        return "connection timed out"
    except OSError:
        return "connection failed"
    except Exception:  # pragma: no cover - defensive
        return "probe failed"


def _safe_browsing_lookup(url: str) -> tuple[str, bool]:
    """Return (status_label, flagged). Never logs the API key or URL content."""
    api_key = settings.GOOGLE_SAFE_BROWSING_API_KEY
    if not api_key:
        return "disabled", False
    payload = {
        "client": {"clientId": "familyshield-ai", "clientVersion": "1.0.0"},
        "threatInfo": {
            "threatTypes": [
                "MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION",
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        },
    }
    try:
        response = httpx.post(
            "https://safebrowsing.googleapis.com/v4/threatMatches:find",
            params={"key": api_key},
            json=payload,
            timeout=3.0,
        )
        if response.status_code == 200:
            return "checked", bool(response.json().get("matches"))
        return "unavailable", False
    except Exception:
        return "unavailable", False


def analyze_url(url: str, ml_probability: float | None = None) -> AnalysisResult:
    """Analyse a URL string and return indicators, score, level and confidence."""
    indicators: list[Indicator] = []
    raw = url.strip()
    extra: dict[str, object] = {"host": None, "scheme": None, "tls_probe": "disabled", "safe_browsing": "disabled"}

    try:
        parts = urlsplit(raw)
        host = (parts.hostname or "").lower()
        scheme = parts.scheme.lower()
        path_query = f"{parts.path or ''}{('?' + parts.query) if parts.query else ''}"
    except ValueError:
        host, scheme, path_query = "", "", ""
        parts = None  # type: ignore[assignment]

    extra["host"] = host or None
    extra["scheme"] = scheme or None

    if not host:
        _add(
            indicators, "url_malformed", "Malformed URL", "high", 55, "phishing",
            "The URL could not be parsed; treat unparseable links as unsafe.", raw[:120],
        )
        return _make_result(indicators, ml_probability, extra)

    # --- host-based checks -------------------------------------------------
    ip_host = host.strip("[]")
    try:
        ipaddress.ip_address(ip_host)
        is_ip = True
    except ValueError:
        is_ip = False
    if is_ip:
        _add(
            indicators, "url_ip_host", "IP address instead of a domain", "high", 45, "phishing",
            "Legitimate services use named domains, not bare IP addresses.", host,
        )
    elif re.fullmatch(r"\d{7,10}", host.split(".")[0]):
        _add(
            indicators, "url_numeric_host", "Numeric host encoding", "high", 35, "phishing",
            "Numeric hostnames can hide the real destination of a link.", host,
        )

    labels = host.split(".")
    if any(label.startswith("xn--") for label in labels):
        _add(
            indicators, "url_punycode", "Punycode (internationalised) domain", "high", 42, "phishing",
            "Punycode domains can be made to look like a familiar brand name.", host,
        )
    if any(ord(char) > 127 for char in host) or host.translate(CONFUSABLES) != host:
        _add(
            indicators, "url_homoglyph", "Lookalike / homoglyph characters", "high", 45, "phishing",
            "The address uses characters that visually resemble ordinary letters.", host,
        )

    official_for_brand: dict[str, tuple[str, ...]] = OFFICIAL_DOMAINS
    for brand in BRANDS:
        official = official_for_brand.get(brand, ())
        if any(host == domain or host.endswith("." + domain) for domain in official):
            continue
        for label in labels:
            normalised = label.replace("-", "").lower()
            brand_key = brand.replace(" ", "")
            if len(normalised) < 4 or normalised == brand_key:
                continue
            similarity = SequenceMatcher(None, normalised, brand_key).ratio()
            looks_like_brand = (
                similarity >= (0.85 if len(brand_key) <= 4 else 0.8)
                or (normalised.startswith(brand_key) and len(normalised) > len(brand_key))
            )
            if looks_like_brand:
                _add(
                    indicators, "url_brand_misspelling", "Misspelled brand domain", "high", 38, "phishing",
                    f"This address resembles '{brand}' but is not its official domain.", host,
                )
                break
        if any(item.code == "url_brand_misspelling" for item in indicators):
            break

    subdomains = labels[:-2] if len(labels) > 2 else []
    if len(subdomains) >= 3 or len(labels) >= 5:
        _add(
            indicators, "url_excessive_subdomains", "Excessive subdomains", "medium", 14, "phishing",
            "Many subdomains can disguise the real owner of a web address.", host,
        )

    tld = labels[-1] if len(labels) > 1 else ""
    if tld in SUSPICIOUS_TLDS:
        _add(
            indicators, "url_suspicious_tld", "High-abuse top-level domain", "medium", 18, "phishing",
            "This domain ending is frequently used by scam sites.", "." + tld,
        )

    if "@" in (parts.netloc or ""):
        _add(
            indicators, "url_at_symbol", "@ trick in address", "high", 45, "phishing",
            "An @ sign can make the real destination appear to be something else.", (parts.netloc or "")[:120],
        )
    try:
        port = parts.port
    except ValueError:
        port = None
        _add(
            indicators, "url_invalid_port", "Invalid port", "medium", 15, "phishing",
            "The URL specifies a port that is not valid.", raw[:120],
        )
    if port is not None and port not in (80, 443):
        _add(
            indicators, "url_nonstandard_port", "Unusual port", "medium", 12, "phishing",
            "Legitimate websites normally use standard web ports.", f":{port}",
        )

    if len(raw) > 200:
        _add(
            indicators, "url_excessive_length", "Very long URL", "medium", 16, "phishing",
            "Unusually long addresses are often used to hide suspicious parts.", f"URL length: {len(raw)} characters",
        )
    elif len(raw) > 120:
        _add(
            indicators, "url_long", "Long URL", "low", 8, "phishing",
            "Long addresses deserve a closer look before you open them.", f"URL length: {len(raw)} characters",
        )

    if scheme == "http":
        _add(
            indicators, "url_http", "Unencrypted connection", "medium", 10, "phishing",
            "HTTP is not encrypted; prefer HTTPS and still verify the domain.", "http://",
        )
    elif scheme not in ("https",):
        _add(
            indicators, "url_unknown_scheme", "Unusual URL scheme", "high", 30, "phishing",
            "Only ordinary http:// and https:// links should be opened.", scheme or "(none)",
        )

    sensitive_path = SENSITIVE_PATH_RE.search(path_query)
    if sensitive_path:
        _add(
            indicators, "url_sensitive_path", "Sensitive-looking page path", "high", 24, "phishing",
            "Scam links often point to fake login or verification pages.", sensitive_path.group(0),
        )
    sensitive_query = SENSITIVE_QUERY_RE.search(("?" + parts.query) if parts.query else "")
    if sensitive_query:
        _add(
            indicators, "url_secret_in_query", "Secret-like value in URL", "high", 30, "phishing",
            "Legitimate services do not put OTPs or passwords in web addresses.", sensitive_query.group(0),
        )

    if "%00" in raw or "//" in (parts.path or "")[1:]:
        _add(
            indicators, "url_obfuscation", "Obfuscated address", "low", 8, "phishing",
            "Unusual characters in an address can hide its true destination.", raw[:120],
        )

    # --- opt-in external checks --------------------------------------------
    if settings.SAFE_URL_PROBE and not is_ip and not _is_private_host(host):
        result = _tls_probe(host, port or 443)
        extra["tls_probe"] = "valid" if result is None else result
        if result is not None:
            _add(
                indicators, "url_tls_invalid", "TLS certificate problem", "high", 25, "phishing",
                "An active TLS check could not validate this site's certificate.", result,
            )
    elif settings.SAFE_URL_PROBE:
        extra["tls_probe"] = "skipped-private-or-ip-host"

    if settings.GOOGLE_SAFE_BROWSING_API_KEY:
        status, flagged = _safe_browsing_lookup(raw)
        extra["safe_browsing"] = status
        if flagged:
            _add(
                indicators, "url_safe_browsing", "Flagged by Safe Browsing", "high", 50, "phishing",
                "Google Safe Browsing lists this address as a threat.", "reported threat",
            )

    return _make_result(indicators, ml_probability, extra)
