"""
Parse CSIC 2010 HTTP request data.

Supports the Kaggle CSV format (csic_database.csv) which has one request per row
with columns: Method, URL, content, classification, and individual header fields.
"""
import re
import pandas as pd
from pathlib import Path


def parse_http_request(raw_text: str) -> dict:
    """Parse a single raw HTTP request string into a structured dict."""
    lines = raw_text.strip().splitlines()
    if not lines:
        return {}

    request = {"method": "", "url": "", "protocol": "", "headers": {}, "body": ""}

    first_line = lines[0].strip()
    parts = first_line.split(" ")
    if len(parts) >= 2:
        request["method"] = parts[0]
        request["url"] = parts[1]
        request["protocol"] = parts[2] if len(parts) > 2 else "HTTP/1.1"

    body_start = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "":
            body_start = i + 1
            break
        if ": " in line:
            key, _, value = line.partition(": ")
            request["headers"][key.lower()] = value.strip()

    if body_start and body_start < len(lines):
        request["body"] = "\n".join(lines[body_start:]).strip()

    return request


def _extract_path(url_field: str) -> str:
    """
    The CSV URL column contains the full URL + HTTP version, e.g.:
      http://localhost:8080/tienda1/index.jsp HTTP/1.1
    Extract just the path+query portion, stripping UI submit-button params
    (B1=Añadir / B1=Comprar) that are CSIC-specific and would let the model
    cheat by learning button text rather than attack features.
    """
    if not isinstance(url_field, str):
        return ""
    # Strip trailing HTTP version
    url_field = re.sub(r"\s+HTTP/\S+$", "", url_field.strip())
    # Strip scheme + host
    url_field = re.sub(r"^https?://[^/]+", "", url_field)
    # Strip B1 submit-button parameter (CSIC artefact, not a real attack signal)
    url_field = re.sub(r"[&?]B1=[^&]*", "", url_field)
    return url_field or "/"


def _row_to_request(row: pd.Series) -> dict:
    """Convert a CSV row to the standard request dict used by features.py."""
    headers = {}
    for col in ("User-Agent", "Pragma", "Cache-Control", "Accept",
                "Accept-encoding", "Accept-charset", "language",
                "host", "cookie", "content-type", "connection"):
        val = row.get(col, "")
        if pd.notna(val) and str(val).strip():
            headers[col.lower()] = str(val).strip()

    return {
        "method": str(row.get("Method", "")).strip().upper(),
        "url": _extract_path(row.get("URL", "")),
        "protocol": "HTTP/1.1",
        "headers": headers,
        "body": str(row.get("content", "")) if pd.notna(row.get("content")) else "",
    }


def load_dataset(data_dir: str) -> pd.DataFrame:
    """
    Load the CSIC 2010 dataset from data_dir.
    Expects csic_database.csv (the Kaggle format).
    """
    data_path = Path(data_dir)

    # Search recursively for the CSV
    candidates = list(data_path.rglob("csic_database.csv"))
    if not candidates:
        raise FileNotFoundError(
            f"csic_database.csv not found under {data_dir}. "
            "Download the dataset from Kaggle and place csic_database.csv in the data/ folder."
        )

    csv_path = candidates[0]
    print(f"  Loading {csv_path} ...")
    raw = pd.read_csv(csv_path, low_memory=False)

    records = []
    for _, row in raw.iterrows():
        req = _row_to_request(row)
        req["label"] = "normal" if int(row.get("classification", 0)) == 0 else "anomalous"
        records.append(req)

    df = pd.DataFrame(records)
    df["url"] = df["url"].fillna("")
    df["body"] = df["body"].fillna("")
    df["method"] = df["method"].fillna("")

    normal = (df["label"] == "normal").sum()
    anomalous = (df["label"] == "anomalous").sum()
    print(f"  Loaded {len(df)} requests — {normal} normal, {anomalous} anomalous")
    return df
