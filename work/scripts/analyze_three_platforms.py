import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / "work" / "analysis"
TARGETS = ["豆包", "DeepSeek", "腾讯元宝"]

rows = json.loads((ANALYSIS / "recommendations_enriched.json").read_text(encoding="utf-8"))
rows = [row for row in rows if row["platform"] in TARGETS]


def summarize(items):
    grouped = defaultdict(list)
    for row in items:
        grouped[row["brand"]].append(row)
    result = []
    for brand, values in grouped.items():
        result.append({
            "brand": brand,
            "count": len(values),
            "average_rank": round(sum(x["rank"] for x in values) / len(values), 2),
            "platforms": sorted({x["platform"] for x in values}),
            "platform_count": len({x["platform"] for x in values}),
            "tracks": Counter(x["track"] for x in values).most_common(3),
            "scope": values[0]["brand_scope"],
        })
    result.sort(key=lambda x: (-x["count"], x["average_rank"], x["brand"]))
    return result


platform_stats = {}
for platform in TARGETS:
    items = [row for row in rows if row["platform"] == platform]
    platform_stats[platform] = {
        "recommendation_rows": len(items),
        "unique_brands": len({x["brand"] for x in items}),
        "average_rank": round(sum(x["rank"] for x in items) / len(items), 2),
        "linked_rows": sum(bool(x["citation_url"]) for x in items),
        "effective": sum(x["support"].startswith("是（") for x in items),
        "partial": sum(x["support"].startswith("部分支持") for x in items),
        "unsupported": sum(x["support"].startswith("否（") for x in items),
        "unverified": sum(x["support"].startswith("未核验") for x in items),
        "top15": summarize(items)[:15],
        "source_types": Counter(x["source_type"] for x in items),
        "local_rows": sum(x["brand_scope"] == "江门本地品牌" for x in items),
        "national_rows": sum(x["brand_scope"] == "全国/跨区域品牌" for x in items),
    }

track_stats = {}
for track in sorted({x["track"] for x in rows}):
    track_stats[track] = summarize([x for x in rows if x["track"] == track])[:10]

overall = summarize(rows)
cross_platform = [x for x in overall if x["platform_count"] == 3]

question_overlap = []
for qn in range(1, 37):
    brands = {
        platform: {
            x["brand"]
            for x in rows
            if x["platform"] == platform and x["question_number"] == qn
        }
        for platform in TARGETS
    }
    intersection = set.intersection(*(brands[p] for p in TARGETS))
    union = set.union(*(brands[p] for p in TARGETS))
    question_overlap.append({
        "question_number": qn,
        "common_brands": sorted(intersection),
        "common_count": len(intersection),
        "union_count": len(union),
    })

output = {
    "sample_count": 108,
    "recommendation_rows": len(rows),
    "unique_brands": len({x["brand"] for x in rows}),
    "overall_top20": overall[:20],
    "brands_on_all_three_platforms": cross_platform,
    "platform_stats": platform_stats,
    "track_top10": track_stats,
    "question_overlap": question_overlap,
    "questions_with_common_brand": sum(x["common_count"] > 0 for x in question_overlap),
    "average_common_brands_per_question": round(
        sum(x["common_count"] for x in question_overlap) / 36, 2
    ),
}

(ANALYSIS / "three_platform_summary.json").write_text(
    json.dumps(output, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print(json.dumps(output, ensure_ascii=False, indent=2))
