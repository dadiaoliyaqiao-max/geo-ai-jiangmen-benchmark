import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

from build_dataset import clean_text, source_type

ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / "work" / "analysis"

LOCAL_BRANDS = {
    "健威家居", "盛世周木匠", "峰尚汇装饰", "森之原装饰", "木晟美家装饰",
    "斯米帝", "杰普家居", "图斯家居", "森润整木", "美域高定", "领尚木作",
    "中域设计装饰", "墅境全屋设计", "优豪斯空间设计", "叁明堂设计",
    "建鸿古典家具", "卡芬达家居", "鲁班匠心", "壹品装饰", "壹家装饰",
    "点石设计", "点睛设计", "简艺空间设计", "艾特空间设计", "博睿装饰",
    "九浔装饰", "九艺装饰", "上乘装饰", "尚筑品家装饰", "伯爵家居",
    "麦格门窗", "恒锐石材", "强立", "建雅摩托", "腾辉机械", "美景皮革",
}

NATIONAL_BRANDS = {
    "华浔品味装饰", "星艺装饰", "名匠装饰", "劳卡", "索菲亚", "欧派",
    "名雕装饰", "尚品宅配", "华美乐装饰", "居众装饰", "尚层装饰",
    "博洛尼", "威法", "轩怡装饰", "木里木外", "科凡高定", "维意定制",
    "华宁装饰", "图森", "蜗窝家", "佰怡家", "顾家家居", "我乐家居",
    "金牌家居", "诗尼曼", "梦居装饰", "好莱客", "摩力克", "米兰软装",
    "百得胜", "欧铂丽", "三星装饰", "简一全屋定制", "金螳螂·家",
    "红星美凯龙", "生活家装饰", "东易日盛", "联邦高登", "如鱼得水",
    "铂尼思", "顶固", "柏厨家居", "欧铂尼", "法曼威", "未来家",
    "大自然地板", "绿城M·确幸家", "珠江装饰", "卡芬达家居",
}

TRACKS = [
    "江门全屋定制",
    "江门装修",
    "江门高端定制品牌",
    "江门高端装修",
    "江门全屋设计",
    "楼盘场景",
]


def readable_title(title):
    if not title or "�" in title:
        return False
    chinese = len(re.findall(r"[\u4e00-\u9fff]", title))
    return chinese >= 2 or (chinese == 0 and title.isascii())


def support_from_validation(row, validation):
    url = row.get("citation_url", "")
    if not url:
        return "未核验（AI未提供链接）"
    item = validation.get(url)
    if not item:
        return "未核验（引用与品牌未建立对应）"
    if not item.get("opened"):
        return "未核验（页面无法访问）"
    if row["brand"] not in item.get("brand_hits", []):
        return "否（页面未检出对应品牌）"
    if item.get("jiangmen_hit") and item.get("topic_hit"):
        return "是（品牌、江门与业务均可核验）"
    if item.get("topic_hit"):
        return "部分支持（品牌与业务可核验）"
    if item.get("jiangmen_hit"):
        return "部分支持（品牌与江门可核验）"
    return "部分支持（仅品牌可核验）"


def brand_scope(brand):
    if brand in LOCAL_BRANDS:
        return "江门本地品牌"
    if brand in NATIONAL_BRANDS:
        return "全国/跨区域品牌"
    return "其他/未判定"


def domain_of(url):
    return urlparse(url).netloc.lower().removeprefix("www.").removeprefix("m.")


def main():
    rows = json.loads((ANALYSIS / "recommendations.json").read_text(encoding="utf-8"))
    validation_rows = json.loads((ANALYSIS / "link_validation.json").read_text(encoding="utf-8"))
    validation = {item["url"]: item for item in validation_rows}

    enriched = []
    for row in rows:
        item = validation.get(row.get("citation_url", ""))
        new = dict(row)
        if item:
            actual_title = item.get("page_title", "")
            if readable_title(actual_title):
                new["citation_title"] = actual_title
            if item.get("publication_date") and item["publication_date"] != "未核验":
                new["publication_date"] = item["publication_date"]
            new["final_url"] = item.get("final_url", "")
            new["http_status"] = item.get("status")
            new["page_opened"] = bool(item.get("opened"))
            new["page_has_brand"] = row["brand"] in item.get("brand_hits", [])
            new["page_has_jiangmen"] = bool(item.get("jiangmen_hit"))
            new["page_has_topic"] = bool(item.get("topic_hit"))
            new["validation_error"] = item.get("error", "")
        else:
            new.update({
                "final_url": "",
                "http_status": None,
                "page_opened": False,
                "page_has_brand": False,
                "page_has_jiangmen": False,
                "page_has_topic": False,
                "validation_error": "",
            })
        new["source_type"] = source_type(new.get("citation_url", ""), new.get("citation_title", ""))
        new["support"] = support_from_validation(row, validation)
        new["site"] = domain_of(new.get("citation_url", ""))
        new["brand_scope"] = brand_scope(new["brand"])
        enriched.append(new)

    (ANALYSIS / "recommendations_enriched.json").write_text(
        json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    brand_rows = defaultdict(list)
    track_rows = defaultdict(list)
    platform_rows = defaultdict(list)
    for row in enriched:
        brand_rows[row["brand"]].append(row)
        track_rows[row["track"]].append(row)
        platform_rows[row["platform"]].append(row)

    overall = []
    for brand, items in brand_rows.items():
        track_counts = Counter(x["track"] for x in items)
        site_counts = Counter(x["site"] for x in items if x["site"])
        page_counts = Counter(
            (x["citation_title"], x["citation_url"]) for x in items if x["citation_url"]
        )
        linked = [x for x in items if x["citation_url"]]
        official = sum(x["source_type"] == "品牌官网" for x in linked)
        third_party = len(linked) - official
        valid = sum(x["support"].startswith("是（") for x in items)
        partial = sum(x["support"].startswith("部分支持") for x in items)
        unsupported = sum(x["support"].startswith("否（") for x in items)
        unverified = len(items) - valid - partial - unsupported
        overall.append({
            "brand": brand,
            "count": len(items),
            "average_rank": round(sum(x["rank"] for x in items) / len(items), 2),
            "brand_scope": brand_scope(brand),
            "main_tracks": [
                {"track": track, "count": count}
                for track, count in track_counts.most_common(3)
            ],
            "most_cited_sites": [
                {"site": site, "count": count}
                for site, count in site_counts.most_common(3)
            ],
            "most_cited_pages": [
                {"title": title, "url": url, "count": count}
                for (title, url), count in page_counts.most_common(3)
            ],
            "linked_count": len(linked),
            "official_count": official,
            "third_party_count": third_party,
            "official_share": round(official / len(linked), 3) if linked else None,
            "valid_count": valid,
            "partial_count": partial,
            "unsupported_count": unsupported,
            "unverified_count": unverified,
        })
    overall.sort(key=lambda x: (-x["count"], x["average_rank"], x["brand"]))

    track_top10 = {}
    for track in TRACKS:
        counter = defaultdict(list)
        for row in track_rows[track]:
            counter[row["brand"]].append(row["rank"])
        table = [
            {
                "brand": brand,
                "count": len(ranks),
                "average_rank": round(sum(ranks) / len(ranks), 2),
                "brand_scope": brand_scope(brand),
            }
            for brand, ranks in counter.items()
        ]
        table.sort(key=lambda x: (-x["count"], x["average_rank"], x["brand"]))
        track_top10[track] = table[:10]

    source_types = []
    for kind, items in sorted(
        defaultdict(list, {
            kind: [x for x in enriched if x["source_type"] == kind]
            for kind in {x["source_type"] for x in enriched}
        }).items(),
        key=lambda kv: -len(kv[1]),
    ):
        source_types.append({
            "source_type": kind,
            "recommendation_rows": len(items),
            "unique_urls": len({x["citation_url"] for x in items if x["citation_url"]}),
            "valid": sum(x["support"].startswith("是（") for x in items),
            "partial": sum(x["support"].startswith("部分支持") for x in items),
            "unsupported": sum(x["support"].startswith("否（") for x in items),
            "unverified": sum(x["support"].startswith("未核验") for x in items),
        })

    scope_stats = []
    for scope in ("江门本地品牌", "全国/跨区域品牌", "其他/未判定"):
        items = [x for x in enriched if x["brand_scope"] == scope]
        scope_stats.append({
            "scope": scope,
            "recommendation_rows": len(items),
            "unique_brands": len({x["brand"] for x in items}),
            "average_rank": round(sum(x["rank"] for x in items) / len(items), 2) if items else None,
            "unique_questions": len({(x["platform"], x["question_number"]) for x in items}),
            "linked_rows": sum(bool(x["citation_url"]) for x in items),
            "valid_or_partial": sum(
                x["support"].startswith("是（") or x["support"].startswith("部分支持")
                for x in items
            ),
        })

    platform_stats = []
    for platform, items in sorted(platform_rows.items()):
        platform_stats.append({
            "platform": platform,
            "sample_count": 36,
            "samples_with_recommendations": len({x["question_number"] for x in items}),
            "zero_recommendation_samples": 36 - len({x["question_number"] for x in items}),
            "recommendation_rows": len(items),
            "unique_brands": len({x["brand"] for x in items}),
            "linked_rows": sum(bool(x["citation_url"]) for x in items),
            "valid": sum(x["support"].startswith("是（") for x in items),
            "partial": sum(x["support"].startswith("部分支持") for x in items),
            "unsupported": sum(x["support"].startswith("否（") for x in items),
            "unverified": sum(x["support"].startswith("未核验") for x in items),
        })

    title_groups = defaultdict(set)
    title_urls = defaultdict(set)
    for row in enriched:
        title = re.sub(r"\s+", "", clean_text(row.get("citation_title", "")).lower())
        title = re.sub(r"^\d+[.、]?", "", title)
        if len(title) >= 12 and row.get("citation_url"):
            title_groups[title].add(row["site"])
            title_urls[title].add(row["citation_url"])
    repeated_titles = [
        {
            "title": next(
                x["citation_title"] for x in enriched
                if re.sub(r"\s+", "", clean_text(x.get("citation_title", "")).lower()).lstrip("0123456789.、") == title
            ),
            "sites": sorted(title_groups[title]),
            "urls": sorted(title_urls[title]),
        }
        for title in title_groups
        if len(title_groups[title]) > 1
    ]

    link_summary = []
    for item in validation_rows:
        link_summary.append({
            **item,
            "site": domain_of(item["url"]),
            "source_type": source_type(item["url"], item.get("page_title", "")),
        })

    summary = {
        "search_period": "2026-07-25—2026-07-29",
        "sample_count": 180,
        "recommendation_row_count": len(enriched),
        "unique_brand_count": len(brand_rows),
        "unique_citation_count": len({x["citation_url"] for x in enriched if x["citation_url"]}),
        "opened_candidate_pages": sum(bool(x.get("opened")) for x in validation_rows),
        "candidate_pages": len(validation_rows),
        "overall": overall,
        "track_top10": track_top10,
        "source_type_stats": source_types,
        "scope_stats": scope_stats,
        "platform_stats": platform_stats,
        "repeated_titles_across_sites": repeated_titles,
        "link_validation": link_summary,
    }
    (ANALYSIS / "final_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({
        "rows": len(enriched),
        "brands": len(brand_rows),
        "candidate_pages": len(validation_rows),
        "opened": summary["opened_candidate_pages"],
        "support": Counter(x["support"].split("（")[0] for x in enriched),
        "source_types": Counter(x["source_type"] for x in enriched),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
