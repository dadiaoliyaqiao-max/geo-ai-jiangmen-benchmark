#!/usr/bin/env python3
"""Initialize a dated, evidence-preserving GEO visibility run directory."""

import argparse
import datetime as dt
import json
import re
import shutil
from pathlib import Path


def parse_platform(value: str) -> dict:
    if ":" in value:
        key, name = value.split(":", 1)
    else:
        key = name = value
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", key):
        raise argparse.ArgumentTypeError(f"invalid platform key: {key}")
    return {"key": key, "name": name}


def load_questions(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError("questions file must be a non-empty JSON array")
    required = {"question_id", "question_number", "theme", "intent_code", "intent_name", "question"}
    seen = set()
    for index, item in enumerate(data, 1):
        missing = required - set(item)
        if missing:
            raise ValueError(f"question {index} missing: {', '.join(sorted(missing))}")
        qid = str(item["question_id"])
        if qid in seen:
            raise ValueError(f"duplicate question_id: {qid}")
        seen.add(qid)
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--slug", required=True, help="lowercase run slug without date")
    parser.add_argument("--date", required=True, help="YYYYMMDD")
    parser.add_argument("--timezone", default="Asia/Shanghai")
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--platform", action="append", type=parse_platform, required=True, help="key or key:display name")
    args = parser.parse_args()

    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", args.slug):
        parser.error("--slug must use lowercase letters, digits, underscore, or hyphen")
    try:
        dt.datetime.strptime(args.date, "%Y%m%d")
        questions = load_questions(args.questions.resolve())
    except ValueError as exc:
        parser.error(str(exc))

    run_id = f"{args.slug}_{args.date}"
    run_dir = args.workspace.resolve() / "work" / run_id
    if run_dir.exists():
        parser.error(f"run directory already exists: {run_dir}")

    for platform in args.platform:
        (run_dir / "raw" / platform["key"]).mkdir(parents=True, exist_ok=False)
        (run_dir / "screenshots" / platform["key"]).mkdir(parents=True, exist_ok=False)
    (run_dir / "analysis").mkdir(parents=True, exist_ok=False)
    shutil.copyfile(args.questions.resolve(), run_dir / "questions.json")

    created_at = dt.datetime.now(dt.timezone.utc).astimezone().isoformat()
    manifest = {
        "run_id": run_id,
        "created_at": created_at,
        "timezone": args.timezone,
        "platforms": args.platform,
        "questions_file": "questions.json",
        "preferred_records": {},
    }
    progress = {
        "initialized_at": created_at,
        "expected_questions_per_platform": len(questions),
        "platforms": {p["key"]: {"completed": 0, "failed": 0, "blocked": 0, "next_question": questions[0]["question_id"]} for p in args.platform},
        "blockers": [],
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (run_dir / "progress.json").write_text(json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run_dir": str(run_dir), "questions": len(questions), "platforms": len(args.platform)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
