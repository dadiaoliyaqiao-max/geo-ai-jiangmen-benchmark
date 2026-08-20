import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_samples():
    samples = []
    for path in sorted((ROOT / "work" / "raw").glob("*/q*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        data["_path"] = str(path.relative_to(ROOT))
        samples.append(data)
    return samples


def candidate_lines(text):
    patterns = [
        r"^\s*第\s*[1-5一二三四五]\s*(?:名|推荐|位)?[：:\s-]*(.+)$",
        r"^\s*[1-5一二三四五]\s*[.、）):：]\s*(.+)$",
        r"^\s*(?:首选|优先推荐|推荐品牌|品牌)[一二三四五1-5]?[：:\s-]+(.+)$",
        r"^\s*#{1,4}\s*[1-5一二三四五]?[.、\s-]*(.+)$",
    ]
    out = []
    for raw in text.splitlines():
        line = re.sub(r"\s+", " ", raw).strip()
        if not line or len(line) > 120:
            continue
        for pat in patterns:
            match = re.match(pat, line, re.I)
            if match:
                out.append(match.group(1).strip())
                break
    return out


def main():
    samples = load_samples()
    print(f"samples={len(samples)}")
    counts = Counter()
    examples = {}
    for sample in samples:
        text = str(sample.get("messages", ["", ""])[1])
        for line in candidate_lines(text):
            key = re.split(r"[（(｜|—–\-：:]", line, 1)[0].strip()
            key = re.sub(r"^(?:推荐|首选|优先|备选)\s*", "", key)
            key = key[:40]
            if 1 < len(key) <= 40:
                counts[key] += 1
                examples.setdefault(
                    key,
                    (sample.get("platform"), sample.get("question_number"), line),
                )
    for key, count in counts.most_common(150):
        platform, question, line = examples[key]
        print(f"{count:>3}\t{key}\t{platform} q{question:02}\t{line}")


if __name__ == "__main__":
    main()
