"""Scan orchestration: analyse, redact, persist, alert."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.deps import require_family_member
from backend.models import FamilyAlert, FamilyMember, Notification, Scan, ScamIndicator, User
from backend.services.explanation import build_explanation
from backend.services.message_analysis import AnalysisResult, analyze_message
from backend.services.ml_classifier import scam_probability
from backend.services.redaction import content_excerpt
from backend.services.url_analysis import analyze_url


def _persist_scan(
    db: Session,
    user: User,
    family_id: str | None,
    scan_type: str,
    analysis: AnalysisResult,
    excerpt: str,
) -> Scan:
    explanation = build_explanation(analysis)
    engine = "rules" if analysis.ml_probability is None else "rules+ml"
    if explanation.groq_used:
        engine += "+groq"

    details = dict(analysis.details)
    if explanation.groq_error:
        details["groq_error"] = explanation.groq_error
    details["explanation_engine"] = "groq" if explanation.groq_used else "deterministic fallback"
    details["disclaimer"] = "Analysis is indicative only and never a guarantee of safety."

    scan = Scan(
        user_id=user.id,
        family_id=family_id,
        scan_type=scan_type,
        risk_score=analysis.risk_score,
        risk_level=analysis.risk_level,
        category=analysis.category,
        confidence_score=analysis.confidence,
        summary=explanation.summary,
        explanation=explanation.explanation,
        recommended_actions=explanation.recommended_actions,
        details=details,
        engine=engine,
        content_excerpt=excerpt,
    )
    scan.indicators = [
        ScamIndicator(
            code=item.code,
            label=item.label,
            severity=item.severity,
            phrase=item.phrase,
            description=item.description,
        )
        for item in analysis.indicators
    ]
    db.add(scan)
    db.flush()
    return scan


def create_family_alert(db: Session, scan: Scan, family_id: str) -> FamilyAlert:
    """Create (or reuse) a family alert and notify every family member."""
    existing = db.scalar(
        select(FamilyAlert).where(FamilyAlert.family_id == family_id, FamilyAlert.scan_id == scan.id)
    )
    if existing:
        return existing

    severity = "high" if scan.risk_level == "high_risk" else "medium" if scan.risk_level == "suspicious" else "low"
    alert = FamilyAlert(
        family_id=family_id,
        scan_id=scan.id,
        title=f"{severity.capitalize()}-risk {scan.scan_type} detected",
        severity=severity,
        risk_level=scan.risk_level,
        summary=scan.summary,
        status="unread",
    )
    db.add(alert)
    db.flush()

    members = db.scalars(select(FamilyMember).where(FamilyMember.family_id == family_id)).all()
    for member in members:
        db.add(
            Notification(
                user_id=member.user_id,
                alert_id=alert.id,
                title=alert.title,
                body=f"A family member shared a {scan.risk_level.replace('_', ' ')} scan. {alert.summary}",
            )
        )
    db.flush()
    return alert


def run_message_scan(db: Session, user: User, text: str, family_id: str | None) -> Scan:
    if family_id:
        require_family_member(db, family_id, user.id)
    analysis = analyze_message(text, scam_probability(text))
    scan = _persist_scan(db, user, family_id, "message", analysis, content_excerpt(text))
    if family_id and scan.risk_level in ("suspicious", "high_risk"):
        create_family_alert(db, scan, family_id)
    db.commit()
    db.refresh(scan)
    return scan


def run_url_scan(db: Session, user: User, url: str, family_id: str | None) -> Scan:
    if family_id:
        require_family_member(db, family_id, user.id)
    analysis = analyze_url(url, scam_probability(url))
    scan = _persist_scan(db, user, family_id, "url", analysis, content_excerpt(url))
    if family_id and scan.risk_level in ("suspicious", "high_risk"):
        create_family_alert(db, scan, family_id)
    db.commit()
    db.refresh(scan)
    return scan
