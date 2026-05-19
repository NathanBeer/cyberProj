"""
Detection agent — fully offline, no external API required.
Runs the trained ML classifier + rule engine + MITRE mapper,
then generates a structured analysis report from the findings.
"""
from __future__ import annotations

from .classifier import AttackClassifier
from .features import extract_features
from .mitre_mapper import detect_attack_type, get_mitre_info
from .preprocessor import parse_http_request

_CLASSIFIER: AttackClassifier | None = None


def _get_classifier() -> AttackClassifier:
    global _CLASSIFIER
    if _CLASSIFIER is None:
        _CLASSIFIER = AttackClassifier.load()
    return _CLASSIFIER


def _build_analysis(raw_request: str, is_attack: bool, attack_type: str | None,
                    mitre_info: dict | None, features: dict, confidence: float) -> str:
    pct = round(confidence * 100)

    if not is_attack:
        return (
            f"No attack patterns were detected in this request (confidence: {pct}%). "
            "The HTTP method, URL, headers, and body all fall within normal traffic parameters "
            "as observed in the CSIC 2010 training dataset. No MITRE ATT&CK techniques apply."
        )

    label = (attack_type or "unknown").replace("_", " ").title()
    mitre_id = mitre_info["id"] if mitre_info else "N/A"
    mitre_name = mitre_info["name"] if mitre_info else "Unknown"
    mitre_tactic = mitre_info["tactic"] if mitre_info else "N/A"
    mitre_desc = mitre_info.get("description", "")
    detection_hint = mitre_info.get("detection", "")

    # Summarise which feature flags fired
    fired = [
        k.replace("has_", "").replace("_", " ")
        for k, v in features.items()
        if k.startswith("has_") and v
    ]
    indicators = ", ".join(fired) if fired else "statistical anomalies"

    lines = [
        f"ATTACK DETECTED — {label} (classifier confidence: {pct}%).",
        f"The request contains indicators of: {indicators}.",
        f"MITRE ATT&CK mapping: {mitre_id} · {mitre_name} | Tactic: {mitre_tactic}.",
        mitre_desc,
    ]
    if detection_hint:
        lines.append(f"Detection guidance: {detection_hint}")

    return " ".join(line for line in lines if line)


def analyze(raw_request: str) -> dict:
    """
    Run the full detection pipeline on a raw HTTP request.
    Returns a structured result dict.
    """
    request_parsed = parse_http_request(raw_request)
    ml_result = _get_classifier().predict(request_parsed)
    is_attack = ml_result["label"] == "anomalous"
    attack_type = detect_attack_type(request_parsed) if is_attack else None
    mitre_info = get_mitre_info(attack_type) if attack_type else None
    features = extract_features(request_parsed)

    analysis = _build_analysis(
        raw_request, is_attack, attack_type, mitre_info, features, ml_result["confidence"]
    )

    return {
        "is_attack": is_attack,
        "label": ml_result["label"],
        "confidence": ml_result["confidence"],
        "attack_type": attack_type,
        "mitre": mitre_info,
        "analysis": analysis,
        "features": features,
    }
