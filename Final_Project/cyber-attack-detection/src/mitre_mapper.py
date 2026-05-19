"""
MITRE ATT&CK technique database for web application attacks.
Maps detected attack patterns to ATT&CK techniques.
"""
import re

# ─── ATT&CK technique definitions ────────────────────────────────────────────

MITRE_TECHNIQUES = {
    "sql_injection": {
        "id": "T1190",
        "name": "Exploit Public-Facing Application",
        "tactic": "Initial Access",
        "tactic_id": "TA0001",
        "subtechnique": None,
        "description": (
            "Adversaries exploit SQL injection vulnerabilities to manipulate backend "
            "database queries, potentially exfiltrating data, bypassing authentication, "
            "or executing commands on the database server."
        ),
        "mitigations": ["M1048 - Application Isolation", "M1051 - Update Software", "M1030 - Network Segmentation"],
        "detection": "Monitor for unusual database queries, error messages revealing schema, or excessive query times.",
        "references": ["https://attack.mitre.org/techniques/T1190/"],
    },
    "xss": {
        "id": "T1059.007",
        "name": "Command and Scripting Interpreter: JavaScript",
        "tactic": "Execution",
        "tactic_id": "TA0002",
        "subtechnique": "T1059",
        "description": (
            "Cross-Site Scripting (XSS) injects malicious JavaScript into web pages "
            "viewed by other users, enabling session hijacking, credential theft, or "
            "malware distribution via the browser."
        ),
        "mitigations": ["M1021 - Restrict Web-Based Content", "M1017 - User Training"],
        "detection": "Monitor HTTP responses for script tag injection; deploy Content Security Policy headers.",
        "references": ["https://attack.mitre.org/techniques/T1059/007/"],
    },
    "command_injection": {
        "id": "T1059",
        "name": "Command and Scripting Interpreter",
        "tactic": "Execution",
        "tactic_id": "TA0002",
        "subtechnique": None,
        "description": (
            "Command injection exploits improper input sanitization to execute arbitrary "
            "OS commands on the server, potentially leading to full system compromise."
        ),
        "mitigations": ["M1026 - Privileged Account Management", "M1038 - Execution Prevention"],
        "detection": "Monitor for unusual process spawning from web server processes.",
        "references": ["https://attack.mitre.org/techniques/T1059/"],
    },
    "path_traversal": {
        "id": "T1083",
        "name": "File and Directory Discovery",
        "tactic": "Discovery",
        "tactic_id": "TA0007",
        "subtechnique": None,
        "description": (
            "Path traversal attacks use ../ sequences or encoded equivalents to access "
            "files and directories outside the intended web root, potentially exposing "
            "sensitive configuration files or credentials."
        ),
        "mitigations": ["M1022 - Restrict File and Directory Permissions"],
        "detection": "Monitor for requests containing ../ sequences or encoded path traversal strings.",
        "references": ["https://attack.mitre.org/techniques/T1083/"],
    },
    "buffer_overflow": {
        "id": "T1203",
        "name": "Exploitation for Client Execution",
        "tactic": "Execution",
        "tactic_id": "TA0002",
        "subtechnique": None,
        "description": (
            "Buffer overflow attacks send oversized input to overflow memory buffers, "
            "potentially overwriting control data and redirecting execution to attacker-controlled code."
        ),
        "mitigations": ["M1050 - Exploit Protection", "M1051 - Update Software"],
        "detection": "Monitor for abnormally long request fields that exceed typical application limits.",
        "references": ["https://attack.mitre.org/techniques/T1203/"],
    },
    "ldap_injection": {
        "id": "T1190",
        "name": "Exploit Public-Facing Application",
        "tactic": "Initial Access",
        "tactic_id": "TA0001",
        "subtechnique": None,
        "description": (
            "LDAP injection manipulates LDAP queries to bypass authentication or "
            "enumerate directory service entries, often used to gain unauthorized access."
        ),
        "mitigations": ["M1048 - Application Isolation", "M1051 - Update Software"],
        "detection": "Monitor authentication logs for unexpected LDAP query patterns.",
        "references": ["https://attack.mitre.org/techniques/T1190/"],
    },
    "csrf": {
        "id": "T1185",
        "name": "Browser Session Hijacking",
        "tactic": "Collection",
        "tactic_id": "TA0009",
        "subtechnique": None,
        "description": (
            "Cross-Site Request Forgery (CSRF) tricks authenticated users into submitting "
            "unintended requests, exploiting the trust a web application has in the user's browser."
        ),
        "mitigations": ["M1017 - User Training", "M1054 - Software Configuration"],
        "detection": "Monitor for missing CSRF tokens in state-changing requests; validate Referer headers.",
        "references": ["https://attack.mitre.org/techniques/T1185/"],
    },
    "parameter_tampering": {
        "id": "T1565.001",
        "name": "Stored Data Manipulation",
        "tactic": "Impact",
        "tactic_id": "TA0040",
        "subtechnique": "T1565",
        "description": (
            "Parameter tampering modifies HTTP parameters (hidden fields, cookies, query strings) "
            "to manipulate application logic, escalate privileges, or alter stored data."
        ),
        "mitigations": ["M1047 - Audit", "M1054 - Software Configuration"],
        "detection": "Monitor for parameter values outside expected ranges or formats.",
        "references": ["https://attack.mitre.org/techniques/T1565/001/"],
    },
}

NORMAL = {
    "id": None,
    "name": "No attack detected",
    "tactic": "N/A",
    "tactic_id": "N/A",
    "description": "This request matches normal traffic patterns.",
    "mitigations": [],
    "detection": "",
    "references": [],
}

# ─── Attack type detection rules (applied to raw request text) ───────────────

_RULES = [
    ("sql_injection", re.compile(
        r"(?:union\s+select|select\s+.+from|insert\s+into|drop\s+table|"
        r"exec\s*\(|xp_\w+|--\s*$|/\*.*\*/|0x[0-9a-f]+|waitfor\s+delay|"
        r"sleep\s*\(|benchmark\s*\(|information_schema)",
        re.IGNORECASE,
    )),
    ("xss", re.compile(
        r"(?:<script|javascript:|on\w+\s*=|<iframe|alert\s*\(|"
        r"document\.cookie|document\.write|eval\s*\(|fromcharcode|<img[^>]+onerror)",
        re.IGNORECASE,
    )),
    ("command_injection", re.compile(
        r"(?:;\s*(?:ls|cat|whoami|id|wget|curl|chmod|bash|sh|nc|ncat|python|perl|ruby)"
        r"|\|\s*(?:ls|cat|whoami|wget|curl|bash)"
        r"|\$\([^)]+\)|`[^`]+`"
        r"|/etc/passwd|/etc/shadow|/bin/bash|/bin/sh)",
        re.IGNORECASE,
    )),
    ("path_traversal", re.compile(
        r"(?:\.\./|\.\.\\|%2e%2e(?:/|%2f)|%252e%252e)",
        re.IGNORECASE,
    )),
    ("buffer_overflow", re.compile(
        r"(?:[A-Za-z0-9+/]{200,}|[AAAA]{50,}|%u\w{4}(?:%u\w{4}){20,})",
    )),
    ("ldap_injection", re.compile(
        r"(?:\)\s*\(|\|\s*\(|&\s*\(|!\s*\(|\*\)\s*\(|\(\||\(&)",
        re.IGNORECASE,
    )),
    ("xss", re.compile(r"<\s*script", re.IGNORECASE)),
]


def detect_attack_type(request: dict) -> str:
    """
    Rule-based detection of specific attack type from a parsed request.
    Returns the attack type key or 'unknown_attack' if anomalous but unclassified.
    """
    combined = (
        request.get("url", "")
        + " "
        + request.get("body", "")
        + " "
        + " ".join(request.get("headers", {}).values())
    )

    for attack_type, pattern in _RULES:
        if pattern.search(combined):
            return attack_type

    # Heuristic: abnormally long fields -> possible buffer overflow
    if len(request.get("url", "")) > 500 or len(request.get("body", "")) > 2000:
        return "buffer_overflow"

    return "parameter_tampering"


def get_mitre_info(attack_type: str) -> dict:
    """Return MITRE ATT&CK details for a given attack type key."""
    return MITRE_TECHNIQUES.get(attack_type, MITRE_TECHNIQUES["parameter_tampering"])
