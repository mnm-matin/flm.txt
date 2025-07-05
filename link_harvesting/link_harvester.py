"""
Forward-Link Harvester  –  single-file MVP 

Usage:
    python link_harvester.py <seed_url> <brand_name>
Example:
    python link_harvester.py https://www.bmw.com bmw
"""

import os, re, sys, time, json, hashlib, sqlite3, signal, requests, openai
from urllib.parse import urljoin, urldefrag, urlparse
from bs4 import BeautifulSoup
import pathlib

# ──────────────────────── 0. load .env manually ──────────────────────
from dotenv import load_dotenv
load_dotenv()

# ─────────────────────────── 1. config ───────────────────────────────
openai.api_key = os.getenv("OPENAI_API_KEY") or "MISSING_KEY"

UA            = "ForwardLinkBot/0.1 (+https://your-project)"
HEADERS       = {"User-Agent": UA}
CACHE_DIR     = ".cache_html"; os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_HOURS   = 24
DB_PATH       = "link_harvesting/links.db"
interrupted   = False          # set by Ctrl-C

GPT_SEARCH    = "gpt-4o-search-preview"   # web-search model
GPT_VERIFY    = "gpt-4o-mini"             # relevance checker
GPT_SUM       = "gpt-3.5-turbo"           # 30-token summary

# ─────────────────── 2. domain helpers ───────────────────────────────
def norm_domain(d: str) -> str:
    if not d:
        return d
    d = d.split(":")[0]           # strip port
    return d.lstrip("www.").lower()

def base_domain(url: str) -> str:
    try:
        return norm_domain(urlparse(url).netloc)
    except Exception:
        return "unknown"

def same_domain(u1: str, u2: str) -> bool:
    d1, d2 = base_domain(u1), base_domain(u2)
    return d1 == d2 or d1.endswith("." + d2) or d2.endswith("." + d1)

# ─────────────────── 3. fetch with disk cache ────────────────────────
def cache_path(url: str) -> str:
    h = hashlib.md5(url.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{h}.html")

def fetch(url: str, timeout=20) -> str:
    p = cache_path(url)
    if os.path.exists(p) and time.time() - os.path.getmtime(p) < CACHE_HOURS * 3600:
        return open(p, encoding="utf-8").read()
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        if r.ok and r.headers.get("content-type", "").startswith("text"):
            open(p, "w", encoding="utf-8").write(r.text)
            return r.text
    except requests.RequestException:
        pass
    return ""

# ───────────────────── 4. plain-Soup text extractor ──────────────────
def extract_text(html: str) -> str:
    """Return crude plain-text version of HTML (max 3 000 chars)."""
    if not html:
        return ""
    try:
        soup = BeautifulSoup(html, "lxml")
        txt  = soup.get_text(" ", strip=True)
        return txt[:3000]
    except Exception:
        return ""

# ─────────────────── 5. SQLite mini-ORM ─────────────────────────────
conn = sqlite3.connect(DB_PATH)
conn.execute(
    """CREATE TABLE IF NOT EXISTS links(
         id INTEGER PRIMARY KEY,
         brand TEXT, url TEXT, summary TEXT,
         provenance TEXT, added TEXT DEFAULT CURRENT_TIMESTAMP)"""
)

def store(brand, url, summary, prov):
    conn.execute(
        "INSERT INTO links (brand, url, summary, provenance) VALUES (?,?,?,?)",
        (brand, url, summary, prov),
    )
    conn.commit()

# ─────────────────── 6. OpenAI helper calls ─────────────────────────
def seed_urls_via_openai(brand: str, limit=40) -> list[str]:
    sys_prompt = (
        "Do a web search and return ONLY a JSON object "
        '{"urls": ["https://example.com/..."]} listing external pages that '
        f"meaningfully discuss {brand}. No markdown, no commentary."
    )
    rsp = openai.chat.completions.create(
        model=GPT_SEARCH,
        messages=[{"role": "system", "content": sys_prompt},
                  {"role": "user",   "content": ""}],
        web_search_options={"search_context_size": "low"},
    )
    try:
        data = json.loads(rsp.choices[0].message.content)
        return data.get("urls", [])[:limit]
    except json.JSONDecodeError:
        print("⚠️  OpenAI search did not return valid JSON.")
        return []

def verify(text: str, brand: str) -> bool:
    sys_prompt = (
        "Return JSON {\"relevant\": bool} — true only if the passage meaningfully "
        f"discusses the company {brand}."
    )
    rsp = openai.chat.completions.create(
        model=GPT_VERIFY,
        messages=[{"role": "system", "content": sys_prompt},
                  {"role": "user",   "content": text[:1500]}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(rsp.choices[0].message.content)["relevant"]

def summarise(text: str, brand: str) -> str:
    rsp = openai.chat.completions.create(
        model=GPT_SUM,
        messages=[{"role": "system",
                   "content": f"Summarise in <=30 tokens what this passage says about {brand}."},
                  {"role": "user", "content": text[:2000]}],
        temperature=0.3,
        max_tokens=60,
    )
    return rsp.choices[0].message.content.strip()

# ───────────────────────── 7. FLM fetch ─────────────────────────────
def fetch_flm(domain: str):
    for path in ("/flm.txt", "/.well-known/flm.txt", "/robots.txt"):
        url = f"https://{domain}{path}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=8)
            if r.ok:
                for m in re.finditer(r"(?i)^forward:\s*(\S+)", r.text, re.M):
                    yield m.group(1).strip()
        except requests.RequestException:
            continue

# ─────────────────── 8. simple outward crawler ──────────────────────
def crawl_outward(seed: str, limit=200, delay=1.0):
    queue, seen, results = [seed.rstrip("/")], set(), set()
    while queue and len(seen) < limit and not interrupted:
        url = queue.pop(0); seen.add(url)
        html = fetch(url); time.sleep(delay)
        for href in re.findall(r'href=["\'](.*?)["\']', html):
            link = urldefrag(urljoin(url, href))[0]
            if link.startswith(("mailto:", "javascript")):
                continue
            if same_domain(seed, link):
                if link not in seen:
                    queue.append(link)
            else:
                results.add(link)
    return results

# ─────────────────────── 9. main orchestrator ───────────────────────
def main(seed_url: str, brand: str):
    domain = base_domain(seed_url)

    # 1. owner-declared FLM links
    for fwd in fetch_flm(domain):
        store(brand, fwd, "(from FLM)", "flm")
        print("✓ FLM", fwd)

    # 2. external pages via OpenAI search
    for ext in seed_urls_via_openai(brand):
        html = fetch(ext)
        txt  = extract_text(html)
        if txt and verify(txt, brand):
            store(brand, ext, summarise(txt, brand), "openai-search")
            print("✓ ext", ext)

    # 3. outward links from the seed domain
    # for ext in crawl_outward(seed_url):
    #     html = fetch(ext)
    #     txt  = extract_text(html)
    #     if txt and verify(txt, brand):
    #         store(brand, ext, summarise(txt, brand), "forward-link")
    #         print("✓ out", ext)

    print("\nRun complete. Rows in DB:",
          conn.execute("SELECT COUNT(*) FROM links").fetchone()[0])

# ─────────────── Ctrl-C graceful handler ────────────────
def _sig_handler(sig, frame):
    global interrupted
    interrupted = True
    print("\nCTRL-C detected — finishing current task then exiting…")
signal.signal(signal.SIGINT, _sig_handler)

# ─────────────────────────  entry  ───────────────────────
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python link_harvesting/link_harvester.py <seed_url> <brand_name>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
