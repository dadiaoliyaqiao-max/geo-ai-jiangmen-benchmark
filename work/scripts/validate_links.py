import concurrent.futures
import html
import json
import re
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from charset_normalizer import from_bytes

from build_dataset import BRANDS, clean_text, infer_date

ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / "work" / "analysis"
MAX_BYTES = 2_000_000
TIMEOUT = 15


def strip_html(raw):
    raw = re.sub(r"(?is)<(?:script|style|noscript|svg)[^>]*>.*?</(?:script|style|noscript|svg)>", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(raw)).strip()


def html_title(raw):
    match = re.search(r"(?is)<title[^>]*>(.*?)</title>", raw)
    return strip_html(match.group(1))[:300] if match else ""


def publication_date(raw, title, url):
    patterns = [
        r'(?i)(?:article:published_time|pubdate|publishdate|datepublished)["\']?\s*(?:content=|[:=])\s*["\']([^"\']+)',
        r'(?i)<time[^>]+datetime=["\']([^"\']+)',
        r'(?i)"datePublished"\s*:\s*"([^"]+)"',
        r'(?i)"publishTime"\s*:\s*"([^"]+)"',
    ]
    for pattern in patterns:
        match = re.search(pattern, raw)
        if match:
            value = match.group(1)
            date_match = re.search(r"(20\d{2})[-/](\d{1,2})[-/](\d{1,2})", value)
            if date_match:
                return f"{int(date_match.group(1)):04d}-{int(date_match.group(2)):02d}-{int(date_match.group(3)):02d}"
    return infer_date(title, url)


def decode_page(raw_bytes, content_type):
    charset_match = re.search(r"charset=([\w-]+)", content_type, re.I)
    candidates = [charset_match.group(1)] if charset_match else []
    head = raw_bytes[:10000].decode("ascii", errors="ignore")
    meta_match = re.search(r"(?i)charset\s*=\s*[\"']?\s*([\w-]+)", head)
    if meta_match:
        candidates.append(meta_match.group(1))
    for charset in candidates:
        try:
            return raw_bytes.decode(charset)
        except (LookupError, UnicodeDecodeError):
            continue
    detected = from_bytes(raw_bytes).best()
    if detected is not None:
        return str(detected)
    return raw_bytes.decode("utf-8", errors="replace")


def fetch_one(url, brands):
    result = {
        "url": url,
        "requested_brands": sorted(brands),
        "status": None,
        "final_url": "",
        "page_title": "",
        "publication_date": "未核验",
        "text_length": 0,
        "brand_hits": [],
        "jiangmen_hit": False,
        "topic_hit": False,
        "opened": False,
        "error": "",
    }
    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/136 Safari/537.36",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.7",
            },
        )
        context = ssl.create_default_context()
        with urllib.request.urlopen(request, timeout=TIMEOUT, context=context) as response:
            raw_bytes = response.read(MAX_BYTES)
            content_type = response.headers.get("Content-Type", "")
            raw = decode_page(raw_bytes, content_type)
            text = clean_text(strip_html(raw))
            page_title = clean_text(html_title(raw))
            result.update({
                "status": getattr(response, "status", 200),
                "final_url": response.geturl(),
                "page_title": page_title,
                "publication_date": publication_date(raw, page_title, url),
                "text_length": len(text),
                "jiangmen_hit": "江门" in text or "江门" in page_title,
                "topic_hit": any(token in text for token in ("全屋定制", "装修", "整装", "全案设计", "软装", "家居", "家具")),
                "opened": True,
            })
            hay = f"{page_title} {text[:250000]}".lower()
            for brand in brands:
                if any(alias.lower() in hay for alias in BRANDS.get(brand, [brand])):
                    result["brand_hits"].append(brand)
    except urllib.error.HTTPError as exc:
        result.update({"status": exc.code, "final_url": getattr(exc, "url", ""), "error": f"HTTP {exc.code}"})
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {str(exc)[:180]}"
    return result


def main():
    rows = json.loads((ANALYSIS / "recommendations.json").read_text(encoding="utf-8"))
    targets = {}
    for row in rows:
        if not str(row.get("support", "")).startswith("待打开"):
            continue
        url = row.get("citation_url", "")
        if url:
            targets.setdefault(url, set()).add(row["brand"])
    started = time.time()
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        future_map = {pool.submit(fetch_one, url, brands): url for url, brands in targets.items()}
        for index, future in enumerate(concurrent.futures.as_completed(future_map), 1):
            url = future_map[future]
            try:
                results.append(future.result())
            except Exception as exc:
                results.append({"url": url, "opened": False, "error": str(exc)})
            if index % 20 == 0:
                print(f"validated {index}/{len(targets)}")
    results.sort(key=lambda item: item["url"])
    (ANALYSIS / "link_validation.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    opened = sum(bool(item.get("opened")) for item in results)
    with_brand = sum(bool(item.get("brand_hits")) for item in results)
    print(json.dumps({
        "targets": len(targets),
        "opened": opened,
        "with_brand_hit": with_brand,
        "elapsed_seconds": round(time.time() - started, 1),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
