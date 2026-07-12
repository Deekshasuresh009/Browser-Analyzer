# analyzer.py
import json
import re
from pathlib import Path
from urllib.parse import urlparse
import idna  # make sure installed


# Permission risk weights
PERMISSION_WEIGHTS = {
    "cookies": 35,
    "history": 35,
    "webRequest": 45,
    "webRequestBlocking": 60,
    "tabs": 20,
    "activeTab": 5,
    "downloads": 30,
    "bookmarks": 10,
    "storage": 10,
    "management": 20,
}

TRACKER_KEYWORDS = ["track", "tracker", "analytics", "google-analytics", "mixpanel", "segment", "amplitude", "gtag"]
SUSPICIOUS_TLDS = [".ru", ".tk", ".ml", ".ga", ".cf", ".xyz"]

def read_manifest(root_dir: str):
    root = Path(root_dir)
    for m in root.rglob("manifest.json"):
        try:
            return json.loads(m.read_text(encoding="utf-8")), str(m)
        except Exception:
            continue
    return None, None

def permission_analysis(manifest: dict):
    perms = manifest.get("permissions", []) + manifest.get("optional_permissions", [])
    details = []
    total = 0
    for p in perms:
        if isinstance(p, str) and (p.startswith("http") or "*" in p or p.startswith(".")):
            details.append({"type":"host_pattern","value":p,"weight":8})
            total += 8
            continue
        w = PERMISSION_WEIGHTS.get(p, 5)
        details.append({"type":"permission","value":p,"weight":w})
        total += w
    return total, details

def _extract_hosts_from_string(s: str):
    hosts = set()
    for m in re.finditer(r"https?://([A-Za-z0-9\.\-]+)(?:[:/]|$)", s):
        hosts.add(m.group(1))
    return hosts

def _extract_urls_from_string(s: str):
    urls = set()
    for m in re.finditer(r"https?://[^\s'\"<>]+", s):
        urls.add(m.group(0).rstrip('.,;'))
    return urls

def find_hosts_in_js(root_dir: str):
    hosts = set()
    root = Path(root_dir)
    for js in root.rglob("*.js"):
        try:
            txt = js.read_text(errors="ignore")
            hosts.update(_extract_hosts_from_string(txt))
            try:
                parsed = esprima.parseScript(txt, tolerant=True)
                # walk AST and collect literal strings
                stack = [parsed]
                while stack:
                    node = stack.pop()
                    if isinstance(node, dict):
                        if node.get("type") == "Literal":
                            val = node.get("value")
                            if isinstance(val, str):
                                hosts.update(_extract_hosts_from_string(val))
                        for v in node.values():
                            if isinstance(v, (dict, list)):
                                stack.append(v)
                    elif isinstance(node, list):
                        for item in node:
                            if isinstance(item, (dict, list)):
                                stack.append(item)
            except Exception:
                pass
        except Exception:
            continue
    return list(hosts)

def find_links_in_files(root_dir: str):
    urls = set()
    root = Path(root_dir)
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".js", ".json", ".html", ".htm", ".css"}:
            try:
                txt = p.read_text(errors="ignore")
                urls.update(_extract_urls_from_string(txt))
            except Exception:
                continue
    return sorted(urls)

def detect_sensitive_apis(root_dir: str):
    findings = []
    patterns = [
        (r"\bchrome\.cookies\b", "chrome.cookies"),
        (r"\bchrome\.history\b", "chrome.history"),
        (r"\bchrome\.tabs\b", "chrome.tabs"),
        (r"\bchrome\.webRequest\b", "chrome.webRequest"),
        (r"\bchrome\.webRequestBlocking\b", "chrome.webRequestBlocking"),
        (r"\bchrome\.storage\b", "chrome.storage"),
        (r"\bchrome\.downloads\b", "chrome.downloads"),
        (r"\beval\s*\(", "eval"),
        (r"\bnew\s+Function\s*\(", "dynamic Function"),
        (r"\bdocument\.cookie\b", "document.cookie"),
        (r"\bsetRequestHeader\s*\(", "setRequestHeader"),
        (r"\bXMLHttpRequest\b", "XMLHttpRequest"),
        (r"\bfetch\s*\(", "fetch"),
    ]
    root = Path(root_dir)
    for p in root.rglob("*.js"):
        try:
            txt = p.read_text(errors="ignore")
            for patt, desc in patterns:
                if re.search(patt, txt):
                    findings.append({"file": str(p), "pattern": desc})
        except Exception:
            continue
    return findings

def punycode_check(domain: str):
    try:
        puny = idna.encode(domain).decode()
        is_puny = puny.startswith("xn--")
        unicode_back = None
        try:
            unicode_back = idna.decode(puny)
        except Exception:
            unicode_back = domain
        return {"original": domain, "punycode": puny, "is_homograph": is_puny, "unicode": unicode_back}
    except Exception:
        return {"original": domain, "punycode": domain, "is_homograph": False, "unicode": domain}

def classify_host(host: str):
    score = 0
    reasons = []
    host_l = host.lower()
    if any(k in host_l for k in TRACKER_KEYWORDS):
        score += 30; reasons.append("tracker-keyword")
    if any(host_l.endswith(tld) for tld in SUSPICIOUS_TLDS):
        score += 15; reasons.append("suspicious-tld")
    if re.match(r"^\d+\.\d+\.\d+\.\d+$", host_l):
        score += 25; reasons.append("ip-address")
    if re.search(r"[0-9a-f]{8,}", host_l):
        score += 10; reasons.append("random-substring")
    return {"host": host, "score": score, "reasons": reasons}

def normalize_score(perm_score, host_score, api_findings_count):
    total = perm_score + host_score + api_findings_count * 20
    normalized = max(0, min(100, int(total)))
    return normalized

def build_report(root_dir: str, job_id: str):
    manifest, manifest_path = read_manifest(root_dir)
    if manifest is None:
        return {"job_id": job_id, "error": "manifest not found", "overall_score": 0}

    perm_score, perm_details = permission_analysis(manifest)

    hosts = set()
    for h in manifest.get("host_permissions", []) if isinstance(manifest.get("host_permissions", []), list) else []:
        hosts.add(h)
    for cs in manifest.get("content_scripts", []):
        for m in cs.get("matches", []):
            hosts.add(m)
    js_hosts = find_hosts_in_js(root_dir)
    hosts.update(js_hosts)

    urls = find_links_in_files(root_dir)
    manifest_text = json.dumps(manifest)
    urls.update(_extract_urls_from_string(manifest_text))

    url_items = []
    url_hosts = set()
    for url in sorted(urls):
        parsed = urlparse(url)
        host = parsed.hostname or url
        if host:
            url_hosts.add(host)
        classification = classify_host(host)
        url_items.append({
            "url": url,
            "host": host,
            "score": classification["score"],
            "reasons": classification["reasons"],
        })

    hosts.update(url_hosts)

    host_classified = []
    host_total_score = 0
    homograph_warnings = []
    for h in hosts:
        bare = h
        if "://" in bare:
            bare = bare.split("://",1)[1].split("/",1)[0]
        bare = bare.replace("*.", "")
        puny = punycode_check(bare)
        if puny["is_homograph"]:
            homograph_warnings.append(puny)
        classification = classify_host(bare)
        host_total_score += classification["score"]
        classification["punycode"] = puny["punycode"]
        host_classified.append(classification)

    api_findings = detect_sensitive_apis(root_dir)
    overall_score = normalize_score(perm_score, host_total_score, len(api_findings))

    report = {
        "job_id": job_id,
        "name": manifest.get("name"),
        "version": manifest.get("version"),
        "manifest_version": manifest.get("manifest_version"),
        "manifest_path": manifest_path,
        "permissions_score": perm_score,
        "permissions": perm_details,
        "hosts": host_classified,
        "links": url_items,
        "homograph_warnings": homograph_warnings,
        "api_findings": api_findings,
        "overall_score": overall_score,
        "recommendation": "High risk" if overall_score > 50 else ("Moderate" if overall_score > 25 else "Low"),
    }
    return report
# --- URL ANALYZER ------------------------------------------------------
from urllib.parse import urlparse
import re
import idna

SUSPICIOUS_KEYWORDS = [
    "login", "verify", "update", "secure", "account", "bank",
    "wallet", "free", "gift", "bonus", "prize", "offer",
    "discount", "limited", "claim", "promo", "promo code",
    "bitcoin", "crypto", "password", "signin", "confirm",
    "credentials", "urgent", "click", "reward", "cash"
]

def _to_punycode(host: str) -> str:
    try:
        return idna.encode(host).decode("ascii")
    except Exception:
        return host

def _looks_like_ip(host: str) -> bool:
    # crude IPv4 / IPv6 check
    return bool(re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host)) or ":" in host

def _has_suspicious_keyword(path_or_query: str) -> list[str]:
    text = path_or_query.lower()
    return [kw for kw in SUSPICIOUS_KEYWORDS if kw in text]

def _looks_like_homograph(host: str) -> bool:
    """
    Very simple heuristic:
    - if the host contains non-ASCII chars BUT punycode is different,
      mark as suspicious.
    """
    if host.isascii():
        return False
    puny = _to_punycode(host)
    return puny != host

def analyze_url(url: str) -> dict:
    """
    Analyze a URL string and return a simple privacy / phishing risk report.
    This does NOT crawl the page, only inspects the URL itself.
    """
    original = url.strip()
    if not original:
        raise ValueError("Empty URL")

    if not re.match(r"^https?://", original):
        # assume https if scheme missing
        original = "https://" + original

    parsed = urlparse(original)

    scheme = parsed.scheme
    host = parsed.hostname or ""
    path = parsed.path or "/"
    query = parsed.query or ""

    is_https = scheme.lower() == "https"
    is_ip = _looks_like_ip(host)
    punycode_host = _to_punycode(host)
    homograph_suspicious = _looks_like_homograph(host)
    path_len = len(path)
    query_len = len(query)
    keywords = _has_suspicious_keyword(host + path + "?" + query)

    score = 0
    reasons = []

    # Basic scoring heuristic (0–100; higher = more risky)
    if not is_https:
        score += 25
        reasons.append("Uses HTTP instead of HTTPS")

    if is_ip:
        score += 20
        reasons.append("Uses raw IP address instead of domain name")

    if homograph_suspicious:
        score += 20
        reasons.append("Domain uses non-ASCII characters (possible IDN homograph)")

    if path_len > 40 or query_len > 80:
        score += 15
        reasons.append("Very long path or query string")

    if keywords:
        score += 20
        reasons.append(f"Contains suspicious words: {', '.join(keywords)}")

    # clamp score
    score = max(0, min(100, score))

    if score >= 70:
        recommendation = "High risk – do NOT trust this URL without extra verification."
        risk_level = "high"
    elif score >= 40:
        recommendation = "Medium risk – proceed with caution."
        risk_level = "medium"
    else:
        recommendation = "Low risk – looks okay, but always stay alert."
        risk_level = "low"

    return {
        "url": original,
        "scheme": scheme,
        "host": host,
        "punycode_host": punycode_host,
        "path": path,
        "query": query,
        "is_https": is_https,
        "is_ip_address": is_ip,
        "homograph_suspicious": homograph_suspicious,
        "suspicious_keywords": keywords,
        "overall_score": score,
        "risk_level": risk_level,
        "reasons": reasons,
        "recommendation": recommendation,
    }
