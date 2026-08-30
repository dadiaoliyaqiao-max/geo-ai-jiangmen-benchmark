#!/usr/bin/env python3
"""Summarize normalized GEO visibility records without reparsing raw answers."""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def get(record, generic, compatibility):
    return record[generic] if generic in record else record.get(compatibility)


def valid(record):
    status = str(record.get("status", "")).strip().lower()
    return status == "success" or status.startswith("success_") or status.startswith("成功")


def metrics(rows):
    rows = [r for r in rows if valid(r)]
    mentions = sum(bool(get(r, "target_mentioned", "kinwai_mentioned")) for r in rows)
    recommendations = sum(bool(get(r, "target_recommended", "kinwai_recommended")) for r in rows)
    top3 = sum(bool(r.get("top3")) for r in rows)
    top1 = sum(bool(r.get("top1")) for r in rows)
    strong = sum(int(r.get("strength", 0) or 0) == 3 for r in rows)
    cases = sum(bool(r.get("property_case")) for r in rows)
    ranks = [float(get(r, "target_rank", "kinwai_rank")) for r in rows if bool(get(r, "target_recommended", "kinwai_recommended")) and get(r, "target_rank", "kinwai_rank") not in (None, "")]
    n = len(rows)
    rate = lambda x: x / n if n else 0
    return {
        "valid": n, "mentioned": mentions, "recommended": recommendations, "top3": top3, "top1": top1,
        "strong": strong, "property_case": cases, "mention_rate": rate(mentions), "recommendation_rate": rate(recommendations),
        "top3_rate": rate(top3), "top1_rate": rate(top1), "strong_rate": rate(strong),
        "average_rank": round(sum(ranks) / len(ranks), 2) if ranks else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--target-name", required=True)
    args = parser.parse_args()
    rows = json.loads(args.records.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        parser.error("--records must contain a JSON array")

    platforms = list(dict.fromkeys(str(r.get("platform", "")) for r in rows))
    themes = list(dict.fromkeys(str(r.get("theme", "")) for r in rows))
    brand_counts = Counter()
    brand_ranks = defaultdict(list)
    brand_platforms = defaultdict(set)
    domains = Counter()
    target_key = args.target_name.casefold()
    for r in rows:
        seen = set()
        for index, brand in enumerate(r.get("all_recommended_brands", []) or [], 1):
            if not brand or brand in seen:
                continue
            seen.add(brand)
            if str(brand).casefold() == target_key:
                continue
            brand_counts[brand] += 1
            brand_ranks[brand].append(index)
            brand_platforms[brand].add(r.get("platform", ""))
        for domain in set(r.get("domains", []) or []):
            if domain:
                domains[domain] += 1

    competitors = [{
        "brand": brand, "recommendations": count,
        "average_rank": round(sum(brand_ranks[brand]) / len(brand_ranks[brand]), 2),
        "platform_coverage": len(brand_platforms[brand]), "platforms": sorted(brand_platforms[brand]),
    } for brand, count in brand_counts.most_common()]
    result = {
        "target": args.target_name,
        "records": len(rows),
        "overall": metrics(rows),
        "by_platform": {p: metrics([r for r in rows if r.get("platform") == p]) for p in platforms},
        "by_theme": {t: metrics([r for r in rows if r.get("theme") == t]) for t in themes},
        "competitors": competitors,
        "top_domains": domains.most_common(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "records": len(rows), "platforms": len(platforms), "themes": len(themes)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
