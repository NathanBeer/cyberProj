"""
Feature extraction from parsed HTTP requests for the ML classifier.
"""
import re
import urllib.parse
import numpy as np


SQL_KEYWORDS = re.compile(
    r"\b(select|union|insert|update|delete|drop|create|alter|exec|execute|"
    r"xp_|sp_|cast|convert|char|nchar|varchar|waitfor|sleep|benchmark|"
    r"information_schema|sys\.tables|load_file|outfile|dumpfile)\b",
    re.IGNORECASE,
)
SQL_OPERATORS = re.compile(r"(--|;|/\*|\*/|@@|0x[0-9a-f]+)", re.IGNORECASE)
XSS_PATTERNS = re.compile(
    r"(<script|javascript:|on\w+=|<iframe|<img[^>]+src|alert\s*\(|"
    r"document\.cookie|document\.write|eval\s*\(|fromcharcode)",
    re.IGNORECASE,
)
CMD_INJECTION = re.compile(
    r"(;|\||&&|\$\(|`|\bcat\b|\bls\b|\bwget\b|\bcurl\b|\bchmod\b|\becho\b"
    r"|\bping\b|\bnmap\b|\bnetstat\b|\bpasswd\b|\bshadow\b|\betc/)",
    re.IGNORECASE,
)
PATH_TRAVERSAL = re.compile(r"(\.\./|\.\.\\|%2e%2e|%252e)", re.IGNORECASE)
LDAP_PATTERNS = re.compile(r"(\)\s*\(|\|\s*\(|&\s*\(|!\s*\(|\*\s*\))", re.IGNORECASE)
ENCODING_ANOMALY = re.compile(r"(%[0-9a-f]{2}){3,}", re.IGNORECASE)


def _count_special_chars(text: str) -> int:
    return sum(1 for c in text if c in "';\"<>(){}[]|&$`\\")


def _decode_url(text: str) -> str:
    try:
        return urllib.parse.unquote(text)
    except Exception:
        return text


def extract_features(request: dict) -> dict:
    """
    Extract a flat dict of numerical/boolean features from a parsed request dict.
    Works on both training data and live requests.
    """
    url = _decode_url(request.get("url", ""))
    body = _decode_url(request.get("body", ""))
    method = request.get("method", "").upper()
    headers = request.get("headers", {})
    combined = url + " " + body

    user_agent = headers.get("user-agent", "")
    content_type = headers.get("content-type", "")

    return {
        # Length features
        "url_length": len(url),
        "body_length": len(body),
        "num_params": len(re.findall(r"[?&]", url)),
        # Special character counts
        "url_special_chars": _count_special_chars(url),
        "body_special_chars": _count_special_chars(body),
        # Attack pattern flags
        "has_sql_keyword": int(bool(SQL_KEYWORDS.search(combined))),
        "has_sql_operator": int(bool(SQL_OPERATORS.search(combined))),
        "has_xss": int(bool(XSS_PATTERNS.search(combined))),
        "has_cmd_injection": int(bool(CMD_INJECTION.search(combined))),
        "has_path_traversal": int(bool(PATH_TRAVERSAL.search(combined))),
        "has_ldap_pattern": int(bool(LDAP_PATTERNS.search(combined))),
        "has_encoding_anomaly": int(bool(ENCODING_ANOMALY.search(combined))),
        # HTTP method
        "is_post": int(method == "POST"),
        "is_get": int(method == "GET"),
        # Header anomalies
        "short_user_agent": int(len(user_agent) < 20),
        "empty_user_agent": int(user_agent == ""),
        "has_multipart": int("multipart" in content_type.lower()),
        # SQL count
        "sql_keyword_count": len(SQL_KEYWORDS.findall(combined)),
        "encoded_chars_count": len(re.findall(r"%[0-9a-fA-F]{2}", combined)),
    }


def requests_to_feature_matrix(requests: list[dict]) -> np.ndarray:
    """Convert a list of request dicts to a numpy feature matrix."""
    rows = [list(extract_features(r).values()) for r in requests]
    return np.array(rows, dtype=float)


FEATURE_NAMES = list(extract_features({}).keys())
