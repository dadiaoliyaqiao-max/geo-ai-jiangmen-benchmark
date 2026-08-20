import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "work" / "raw"
OUT = ROOT / "work" / "analysis"

BRANDS = {
    "健威家居": ["健威家居", "健威整装", "健威人性家具", "江门健威家具装饰有限公司", "健威家具"],
    "索菲亚": ["索菲亚全案定制", "索菲亚整家定制", "索菲亚衣柜全屋定制", "索菲亚全屋定制", "索菲亚家居", "索菲亚"],
    "欧派": ["欧派整装大家居", "欧派整家定制", "欧派全屋定制", "欧派家居", "欧派大家居", "欧派"],
    "劳卡": ["江门劳卡整装", "劳卡全屋整装", "劳卡整家定制", "劳卡全屋定制", "劳卡整装", "江门劳卡", "劳卡"],
    "盛世周木匠": ["盛世周木匠・细工坊", "盛世周木匠 / 细工坊", "盛世周木匠", "细工坊"],
    "杰普家居": ["杰普全屋定制", "杰普家具", "杰普家居", "JALPER"],
    "斯米帝": ["斯米帝・森尼帝高端整家定制", "斯米帝全屋定制", "斯米帝", "森尼帝"],
    "图斯家居": ["图斯家居"],
    "维意定制": ["维意定制江门店", "维意定制"],
    "尚品宅配": ["尚品宅配全屋定制", "尚品宅配"],
    "科凡高定": ["科凡高定", "科凡"],
    "佰怡家": ["佰怡家全屋家居", "佰怡家全屋定制", "佰怡家", "BEHOME"],
    "好莱客": ["好莱客"],
    "诗尼曼": ["诗尼曼全屋定制", "诗尼曼"],
    "联邦高登": ["联邦高登"],
    "森润整木": ["森润整木定制", "森润木业", "森润整木"],
    "梵享高定": ["梵享高端板木定制加工厂", "梵享高定", "梵享"],
    "DT高端定制": ["DT高端全屋家具定制", "DT高端定制"],
    "铂尼思": ["铂尼思 BAUNIS", "铂尼思", "BAUNIS"],
    "博洛尼": ["博洛尼全屋定制", "博洛尼 BOLONI", "博洛尼", "BOLONI"],
    "图森": ["图森 TUCSON", "图森", "TUCSON"],
    "威法": ["威法 VIFA", "威法", "VIFA"],
    "木里木外": ["木里木外 MULI", "木里木外", "MULI"],
    "顾家家居": ["顾家家居", "顾家"],
    "顶固": ["顶固全屋定制", "顶固"],
    "金牌家居": ["金牌家居", "金牌厨柜"],
    "我乐家居": ["我乐家居", "我乐"],
    "欧铂丽": ["欧铂丽"],
    "伯爵家居": ["伯爵家居"],
    "尚度全屋家居": ["新众拓工程有限公司（尚度全屋家居）", "尚度全屋家居", "新众拓工程有限公司"],
    "领尚木作": ["领尚木作"],
    "星艺装饰": ["广东星艺装饰集团江门分公司", "广东星艺装饰", "江门星艺装饰", "星艺装饰"],
    "华浔品味装饰": ["华浔品味装饰集团", "江门华浔品味装饰", "华浔品味装饰", "华浔装饰"],
    "名匠装饰": ["广东名匠装饰集团", "江门名匠装饰工程有限公司", "江门名匠装饰", "名匠装饰"],
    "名雕装饰": ["名雕装饰"],
    "峰尚汇装饰": ["江门峰尚汇装饰工程有限公司", "江门峰尚汇装饰", "峰尚汇装饰"],
    "森之原装饰": ["江门森之原装饰", "森之原装饰"],
    "尚层装饰": ["江门市尚层装饰设计工程有限公司", "尚层装饰"],
    "华美乐装饰": ["东莞市华美乐装饰工程有限公司江门分公司", "江门华美乐装饰", "华美乐装饰"],
    "居众装饰": ["江门居众装饰", "居众装饰"],
    "梦居装饰": ["江门梦居装饰", "梦居装饰"],
    "蜗窝家": ["江门蜗窝家整体家居有限公司", "江门蜗窝家整体家居", "蜗窝家"],
    "木晟美家装饰": ["江门市木晟美家装饰工程有限公司", "木晟美家装饰"],
    "九浔装饰": ["九浔装饰"],
    "中域设计装饰": ["广东中域设计装饰", "中域设计装饰"],
    "华宁装饰": ["华宁装饰"],
    "永庆装饰": ["永庆装饰"],
    "上乘装饰": ["上乘装饰"],
    "百安居装饰": ["江门百安居装饰", "百安居装饰", "百安居"],
    "鲁班匠心": ["鲁班匠心", "鲁班装饰"],
    "优豪斯空间设计": ["优豪斯空间设计", "UHOUSE"],
    "境垣空间设计": ["境垣空间设计"],
    "非意装饰": ["广东非意装饰设计工程有限公司", "非意装饰"],
    "恒庭私宅": ["江门恒庭私宅设计施工公司", "恒庭私宅"],
    "景筑别墅建造": ["江门景筑别墅建造中心", "景筑别墅建造"],
    "鼎饰空间": ["广东鼎饰空间", "鼎饰空间"],
    "建三设计": ["广州建三工程设计服务有限公司", "建三设计"],
    "墅境全屋设计": ["江门墅境全屋设计施工有限公司", "墅境全屋设计"],
    "梁志天设计集团": ["梁志天设计集团", "Steve Leung Design Group"],
    "鸿艺源设计": ["鸿艺源设计"],
    "道胜设计": ["广州道胜设计", "道胜设计"],
    "Rimadesio": ["Rimadesio"],
    "壹方精筑": ["深圳壹方精筑", "壹方精筑"],
    "艾特空间设计": ["江门市艾特空间设计有限公司", "艾特空间设计"],
    "博睿装饰": ["广州博睿装饰江门分公司", "博睿装饰"],
    "点石设计": ["江门市点石设计工作室", "点石设计工作室", "点石设计"],
    "点睛设计": ["江门市点睛设计工程有限公司", "点睛设计"],
    "金螳螂·家": ["金螳螂·家", "金螳螂家"],
    "壹品装饰": ["江门壹品装饰", "江门市壹品装饰设计工程有限公司", "壹品装饰"],
    "东易日盛": ["东易日盛"],
    "居研设计": ["居研设计"],
    "尚筑品家装饰": ["江门尚筑品家装饰", "尚筑品家装饰", "尙筑品家装饰"],
    "麦格门窗": ["江门市麦格门窗有限公司", "麦格门窗"],
    "建雅摩托": ["建雅摩托", "香帅重机"],
    "恒锐石材": ["江门恒锐石材装饰有限公司", "恒锐石材"],
    "强立": ["强立"],
    "轩怡装饰": ["轩怡家装", "轩怡装饰"],
    "红杉树装饰": ["红杉树装饰"],
    "九艺装饰": ["九艺装饰"],
    "腾辉机械": ["江门市新会区腾辉机械有限公司", "腾辉机械"],
    "美景皮革": ["江门美景皮革(新世界)直营店", "江门美景皮革", "美景皮革"],
    "嘉年华装饰": ["广州市嘉年华装饰设计工程有限公司", "嘉年华装饰"],
    "优家装饰": ["优家装饰"],
    "卡芬达家居": ["卡芬达家居", "卡芬达"],
    "法曼威": ["法曼威"],
    "未来式": ["未来式"],
    "大自然地板": ["大自然未央", "大自然地板", "大自然"],
    "绿城M·确幸家": ["绿城M·确幸家", "绿城M· 确幸家", "确幸家"],
    "珠江装饰": ["珠江装饰"],
    "简一全屋定制": ["简一全屋定制", "简一"],
    "叁明堂设计": ["广东叁明堂设计工程有限公司", "叁明堂设计", "SAMTOM"],
    "建鸿古典家具": ["建鸿古典家具", "建古红"],
    "美域高定": ["美域高定"],
    "百得胜": ["百得胜", "Paterson"],
    "三星装饰": ["三星装饰"],
    "M77": ["M77"],
    "简艺空间设计": ["简艺空间设计", "简艺空间"],
    "生活家装饰": ["生活家装饰"],
    "壹家装饰": ["江门市壹家装饰", "壹家装饰"],
    "红星美凯龙": ["红星美凯龙"],
    "米兰软装": ["米兰软装"],
    "宝岛家居": ["宝岛家居"],
    "固道": ["固道"],
    "维特丽全屋定制": ["维特丽全屋定制"],
    "如鱼得水": ["如鱼得水"],
    "摩力克": ["摩力克"],
    "奥莱娅家具": ["广州奥莱娅家具有限公司", "奥莱娅家具"],
}

OFFICIAL_DOMAINS = {
    "suofeiya.com", "oppein.com", "jmlaokazz.com", "sszmj.com",
    "simidi.com.cn", "senrun-wood.com", "homello.com", "kinwai.com.cn",
    "hxdec.com", "xydec.com.cn", "mjdec.com", "mjzs.cn", "mingdiao.com.cn",
    "ijuzhong.com", "boloni.com", "xingyizz.com", "morechange.cn",
}

CONTENT_DOMAINS = {
    "baijiahao.baidu.com", "mp.weixin.qq.com", "www.sohu.com", "news.sohu.com",
    "www.163.com", "m.163.com", "k.sina.com.cn", "cj.sina.com.cn",
    "www.toutiao.com", "m.toutiao.com", "www.iesdouyin.com",
    "www.cnblogs.com", "www.zhihu.com", "zhuanlan.zhihu.com",
    "www.bilibili.com", "mparticle.uc.cn",
}

MAP_REVIEW_DOMAINS = {
    "m.anjuke.com", "msale.58.com", "mfang.58.com", "jiangmen.city8.com",
    "m.city8.com", "www.dianhua.cn", "www.dianping.com", "map.baidu.com",
    "ditu.amap.com",
}

INDUSTRY_PLATFORMS = {
    "www.to8to.com", "m.to8to.com", "jiangmen.zx123.cn", "www.zx123.cn",
    "www.chinayigui.com", "jiangm.qizuang.com", "www.shejiben.com",
    "m.shejiben.com", "www.chinapp.com", "m.chinapp.com", "www.cnpp.cn",
    "jiangmen.to8to.com", "m.qizuang.com", "jiangm.qizuang.com",
    "m.jia400.com", "m.jc001.cn", "www.chinabm.cn", "m.maigoo.com",
    "m.pp918.com", "m.jia.com", "m.328f.cn", "www.328f.cn",
}

SOFT_SYNDICATION = {
    "www.chinabidding.com.cn", "www.cnpinpai.cn", "wap.hznet.tv",
    "www.zgswcn.com", "m.tech.china.com", "www.e-bidding.org",
    "jm.lieju.com", "m.liebiao.com", "www.liebiao.com",
    "www.cnblogs.com", "www.chinapp.net.cn", "m.chinapp.net.cn",
    "www.fjpce.com", "www.51sole.com", "tzb.jdzol.com", "m.ldqxn.com",
    "www.ldqxn.com", "www.shangyexinzhi.com", "www.echinagov.com",
    "m.cnpinpai.cn", "www.klzia.com", "m.lieju.com", "bk.taobao.com",
    "www.tz1288.com", "www.cndjj.com", "m.shzh.net", "www.chaojimendian.com.cn",
    "m.51xxsp.com",
}


def clean_text(text):
    text = unicodedata.normalize("NFKC", str(text or ""))
    text = re.sub(r"[\u200b\u200c\u200d\u2060\ufeff]", "", text)
    return text.replace("\r\n", "\n").replace("\r", "\n")


def track_for_question(qn):
    if 1 <= qn <= 6:
        return "江门全屋定制"
    if 7 <= qn <= 12:
        return "江门装修"
    if 13 <= qn <= 18:
        return "江门高端定制品牌"
    if 19 <= qn <= 24:
        return "江门高端装修"
    if 25 <= qn <= 30:
        return "江门全屋设计"
    return "楼盘场景"


def source_type(url, title=""):
    try:
        domain = urlparse(url).netloc.lower()
    except Exception:
        domain = ""
    bare = domain.removeprefix("www.").removeprefix("m.")
    title = clean_text(title)
    if not url:
        return "未提供链接"
    if domain.endswith(".gov.cn") or ".gov.cn" in domain:
        return "政府或官方机构"
    if domain.endswith(".org.cn") or "协会" in title:
        return "行业协会"
    if any(domain == d or domain.endswith("." + d) for d in OFFICIAL_DOMAINS):
        return "品牌官网"
    if domain in MAP_REVIEW_DOMAINS:
        return "地图、点评平台"
    if domain in CONTENT_DOMAINS:
        return "内容平台"
    if domain in INDUSTRY_PLATFORMS or any(domain.endswith("." + d) for d in INDUSTRY_PLATFORMS):
        return "行业平台"
    if domain in SOFT_SYNDICATION or any(domain.endswith("." + d) for d in SOFT_SYNDICATION) or "/shangxun/" in url:
        return "软文/转载平台"
    if any(x in domain for x in ("people.com.cn", "xinhuanet.com", "chinanews.com", "cnr.cn", "jiemian.com", "bjnews.com.cn")):
        return "权威媒体"
    if any(x in domain for x in ("pchouse.com.cn", "smzdm.com", "china.com", "sina.com.cn", "cet.com.cn")):
        return "媒体/行业媒体"
    if any(x in domain for x in ("baike.baidu.com", "aiqicha.baidu.com", "qcc.com", "tianyancha.com")):
        return "企业信息/百科"
    if any(x in domain for x in ("bbs", "forum", "tieba")):
        return "用户评价或论坛"
    if bare and any(token in bare for token in ("suofeiya", "oppein", "laoka", "kinwai", "sszmj", "simidi", "senrun", "homello")):
        return "品牌官网"
    return "其他网站"


def infer_date(title, url):
    text = f"{title} {url}"
    patterns = [
        r"(20\d{2})[-/年](\d{1,2})[-/月](\d{1,2})",
        r"/(20\d{2})/(\d{2})(\d{2})/",
        r"(20\d{2})年(\d{1,2})月",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            parts = match.groups()
            year = int(parts[0])
            month = int(parts[1]) if len(parts) > 1 else 1
            day = int(parts[2]) if len(parts) > 2 else 1
            if 1 <= month <= 12 and 1 <= day <= 31:
                return f"{year:04d}-{month:02d}-{day:02d}"
    year_match = re.search(r"\b(20\d{2})\b", text)
    return year_match.group(1) if year_match else "未核验"


def alias_pattern(alias):
    return re.escape(alias).replace(r"\ ", r"\s*")


def find_brand_occurrences(text):
    found = {}
    for brand, aliases in BRANDS.items():
        occurrences = []
        for alias in sorted(aliases, key=len, reverse=True):
            for match in re.finditer(alias_pattern(alias), text, re.I):
                occurrences.append((match.start(), match.end(), alias))
        if occurrences:
            found[brand] = sorted(occurrences)
    return found


def explicit_rank(text, brand):
    aliases = BRANDS[brand]
    candidates = []
    numeral_map = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5}
    for alias in aliases:
        ap = alias_pattern(alias)
        patterns = [
            rf"第\s*([1-5一二三四五])\s*(?:名|位|推荐)?\s*[：:\s-]*{ap}",
            rf"推荐(?:顺位|排序|优先级|顺序)?\s*[：:\s-]*第?\s*([1-5一二三四五])\s*(?:名|位)?[^。\n]{{0,50}}{ap}",
            rf"([1-5一二三四五])\s*[.、）):：]\s*{ap}",
            rf"(?<!\d)([1-5])\s*{ap}",
            rf"{ap}[^。\n]{{0,60}}推荐(?:顺位|排序|优先级)?\s*[：:\s-]*第?\s*([1-5一二三四五])",
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.I):
                raw = match.group(1)
                rank = int(raw) if raw.isdigit() else numeral_map.get(raw)
                if rank:
                    candidates.append((match.start(), rank))
    return min(candidates, default=(10**9, None))[1]


def line_is_recommendation(line):
    return bool(
        re.search(
            r"(?:第\s*[1-5一二三四五]\s*(?:名|位|推荐)|推荐(?:品牌|理由|顺位|排序|优先级)?|"
            r"首选|优选|备选|核心优势|适合人群|^\s*[1-5一二三四五]\s*[.、）):：]|"
            r"^\s*#{1,4}\s*[1-5一二三四五]?)",
            line,
            re.I,
        )
    )


def recommendation_candidates(text):
    occurrences = find_brand_occurrences(text)
    candidates = {}
    lines = text.splitlines()
    cursor = 0
    line_spans = []
    for line in lines:
        start = cursor
        end = cursor + len(line)
        line_spans.append((start, end, line))
        cursor = end + 1
    for brand, occs in occurrences.items():
        rank = explicit_rank(text, brand)
        heading_positions = []
        for start, end, line in line_spans:
            if any(re.search(alias_pattern(alias), line, re.I) for alias in BRANDS[brand]):
                if len(line.strip()) <= 180 and line_is_recommendation(line):
                    heading_positions.append(start)
        first_pos = occs[0][0]
        candidates[brand] = {
            "explicit_rank": rank,
            "heading_pos": min(heading_positions, default=None),
            "first_pos": first_pos,
        }
    ranked = sorted(
        [(brand, data) for brand, data in candidates.items() if data["explicit_rank"]],
        key=lambda item: (item[1]["explicit_rank"], item[1]["first_pos"]),
    )
    chosen = []
    used_ranks = set()
    for brand, data in ranked:
        if data["explicit_rank"] not in used_ranks and len(chosen) < 5:
            chosen.append((brand, data["explicit_rank"], data["first_pos"]))
            used_ranks.add(data["explicit_rank"])
    heading = sorted(
        [
            (brand, data["heading_pos"], data["first_pos"])
            for brand, data in candidates.items()
            if data["heading_pos"] is not None and brand not in {x[0] for x in chosen}
        ],
        key=lambda item: item[1],
    )
    next_rank = 1
    for brand, pos, first_pos in heading:
        while next_rank in used_ranks:
            next_rank += 1
        if next_rank > 5:
            break
        chosen.append((brand, next_rank, first_pos))
        used_ranks.add(next_rank)
        next_rank += 1
    if len(chosen) < 3:
        fallback = sorted(
            [
                (brand, data["first_pos"])
                for brand, data in candidates.items()
                if brand not in {x[0] for x in chosen}
            ],
            key=lambda item: item[1],
        )
        for brand, pos in fallback:
            while next_rank in used_ranks:
                next_rank += 1
            if next_rank > 5:
                break
            chosen.append((brand, next_rank, pos))
            used_ranks.add(next_rank)
            next_rank += 1
            if len(chosen) >= 5:
                break
    return sorted(chosen, key=lambda item: item[1])


def extract_reason(text, brand):
    occurrences = find_brand_occurrences(text).get(brand, [])
    if not occurrences:
        return ""
    start = occurrences[0][0]
    snippet = text[start:start + 500]
    snippet = re.sub(r"https?://\S+", "", snippet)
    snippet = re.sub(r"\s+", " ", snippet).strip()
    for other, aliases in BRANDS.items():
        if other == brand:
            continue
        cuts = [snippet.find(alias) for alias in aliases if snippet.find(alias) > 25]
        if cuts:
            snippet = snippet[:min(cuts)]
    snippet = re.sub(r"^[^:：]{0,60}[：:]\s*", "", snippet)
    return snippet[:220].rstrip(" ,，;；。") or "平台给出推荐，但未提供可独立提炼的理由"


def link_score(link, brand, question):
    title = clean_text(link.get("title", ""))
    site = clean_text(link.get("site", ""))
    url = str(link.get("url", "") or "")
    hay = f"{title} {site} {url}".lower()
    score = 0
    for alias in BRANDS[brand]:
        if alias.lower() in hay:
            score += 8 + min(len(alias), 8)
    if "江门" in title:
        score += 3
    if any(token in title for token in ("全屋", "装修", "设计", "定制", "整装", "家居")):
        score += 2
    stype = source_type(url, title)
    if stype == "品牌官网":
        score += 3
    elif stype in {"政府或官方机构", "行业协会", "权威媒体"}:
        score += 2
    elif stype == "软文/转载平台":
        score -= 2
    if not url:
        score -= 20
    return score


def pick_link(links, brand, question):
    if not links:
        return None
    scored = sorted(
        [(link_score(link, brand, question), idx, link) for idx, link in enumerate(links)],
        key=lambda item: (-item[0], item[1]),
    )
    score, _, link = scored[0]
    return dict(link, match_score=score)


def preliminary_support(link, brand):
    if not link or not link.get("url"):
        return "未核验"
    title = clean_text(link.get("title", ""))
    if any(alias.lower() in title.lower() for alias in BRANDS[brand]):
        if "江门" in title or any(token in title for token in ("全屋", "装修", "设计", "定制", "家居", "整装")):
            return "待打开核验（标题相关）"
        return "待打开核验（品牌相关）"
    return "未核验"


def load_samples():
    samples = []
    for path in sorted(RAW.glob("*/q*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        data["_path"] = str(path.relative_to(ROOT))
        data["answer"] = clean_text(data.get("messages", ["", ""])[1])
        data["question"] = clean_text(data.get("question", ""))
        data["question_number"] = int(data["question_number"])
        data["track"] = track_for_question(data["question_number"])
        samples.append(data)
    return samples


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    samples = load_samples()
    rows = []
    all_links = []
    anomalies = []
    for sample in samples:
        manual_recs = {
            ("DeepSeek", 2): ["索菲亚", "欧派", "美域高定", "尚品宅配"],
            ("DeepSeek", 5): ["威法", "博洛尼", "我乐家居", "欧派", "百得胜"],
            ("DeepSeek", 8): ["星艺装饰", "华宁装饰", "名雕装饰", "壹品装饰"],
            ("DeepSeek", 11): ["名匠装饰", "华浔品味装饰", "三星装饰", "星艺装饰"],
            ("DeepSeek", 15): ["木里木外", "威法", "图森", "博洛尼", "M77"],
            ("DeepSeek", 17): ["欧派", "索菲亚", "尚品宅配", "简一全屋定制"],
            ("DeepSeek", 18): ["盛世周木匠", "领尚木作", "科凡高定"],
            ("DeepSeek", 25): ["索菲亚", "尚品宅配", "简艺空间设计", "星艺装饰"],
            ("DeepSeek", 27): ["星艺装饰", "华浔品味装饰", "名匠装饰", "点睛设计", "金螳螂·家"],
            ("DeepSeek", 32): [("索菲亚", 1), ("如鱼得水", 1), ("欧派", 2), ("顾家家居", 3), ("尚品宅配", 4), ("红星美凯龙", 5)],
            ("DeepSeek", 34): ["华浔品味装饰", "索菲亚", "生活家装饰", "欧派", "壹家装饰"],
            ("腾讯元宝", 3): ["健威家居", "斯米帝", "盛世周木匠", "建鸿古典家具"],
            ("文心一言", 26): ["木晟美家装饰", "华美乐装饰", "蜗窝家", "尚层装饰"],
            ("千问", 29): [],
            ("千问", 30): ["华浔品味装饰", "叁明堂设计", "峰尚汇装饰", "森之原装饰"],
            ("千问", 31): [],
            ("千问", 24): ["优豪斯空间设计", "盛世周木匠", "峰尚汇装饰"],
        }
        manual = manual_recs.get((sample["platform"], sample["question_number"]))
        if manual is not None:
            recs = []
            for default_rank, item in enumerate(manual, 1):
                brand, rank = item if isinstance(item, tuple) else (item, default_rank)
                recs.append((brand, rank, find_brand_occurrences(sample["answer"])[brand][0][0]))
        else:
            recs = recommendation_candidates(sample["answer"])
        if len(recs) < 3:
            anomalies.append({
                "platform": sample["platform"],
                "question_number": sample["question_number"],
                "question": sample["question"],
                "recommendation_count": len(recs),
                "brands": [r[0] for r in recs],
                "answer_start": sample["answer"][:500],
            })
        for link in sample.get("links", []):
            url = str(link.get("url", "") or "")
            title = clean_text(link.get("title", ""))
            try:
                domain = urlparse(url).netloc.lower()
            except Exception:
                domain = ""
            all_links.append({
                "platform": sample["platform"],
                "question_number": sample["question_number"],
                "track": sample["track"],
                "title": title,
                "url": url,
                "domain": domain,
                "source_type": source_type(url, title),
                "publication_date": infer_date(title, url),
            })
        for brand, rank, _ in recs:
            link = pick_link(sample.get("links", []), brand, sample["question"])
            rows.append({
                "platform": sample["platform"],
                "search_date": sample.get("search_date", ""),
                "question_number": sample["question_number"],
                "track": sample["track"],
                "question": sample["question"],
                "brand": brand,
                "rank": rank,
                "reason": extract_reason(sample["answer"], brand),
                "citation_title": clean_text(link.get("title", "")) if link else "",
                "citation_url": str(link.get("url", "") or "") if link else "",
                "source_type": source_type(link.get("url", ""), link.get("title", "")) if link else "未提供链接",
                "publication_date": infer_date(link.get("title", ""), link.get("url", "")) if link else "未核验",
                "support": preliminary_support(link, brand),
                "conversation_url": sample.get("conversation_url", ""),
                "raw_path": sample["_path"],
            })
    counts = Counter(row["brand"] for row in rows)
    by_track = defaultdict(Counter)
    by_platform = defaultdict(Counter)
    rank_sums = Counter()
    for row in rows:
        by_track[row["track"]][row["brand"]] += 1
        by_platform[row["platform"]][row["brand"]] += 1
        rank_sums[row["brand"]] += row["rank"]
    stats = {
        "sample_count": len(samples),
        "recommendation_row_count": len(rows),
        "brand_count": len(counts),
        "overall": [
            {"brand": brand, "count": count, "average_rank": round(rank_sums[brand] / count, 2)}
            for brand, count in counts.most_common()
        ],
        "tracks": {
            track: [
                {"brand": brand, "count": count}
                for brand, count in counter.most_common(10)
            ]
            for track, counter in by_track.items()
        },
        "platforms": {
            platform: [
                {"brand": brand, "count": count}
                for brand, count in counter.most_common(15)
            ]
            for platform, counter in by_platform.items()
        },
    }
    (OUT / "recommendations.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "all_links.json").write_text(json.dumps(all_links, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "anomalies.json").write_text(json.dumps(anomalies, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "samples": len(samples),
        "recommendation_rows": len(rows),
        "brands": len(counts),
        "anomalies": len(anomalies),
        "top20": stats["overall"][:20],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
