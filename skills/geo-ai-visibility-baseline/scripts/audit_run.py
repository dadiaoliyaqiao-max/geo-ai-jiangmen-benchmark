#!/usr/bin/env python3
"""Audit record completeness, question integrity, and screenshot traceability."""

import argparse
import json
from collections import Counter
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def is_success(status: str) -> bool:
    value = status.strip().lower()
    return value == "success" or value.startswith("success_") or value.startswith("成功")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    manifest = load(run_dir / "manifest.json")
    questions = load(run_dir / manifest.get("questions_file", "questions.json"))
    preferred = manifest.get("preferred_records", {})
    findings = []
    rows = []

    for platform in manifest["platforms"]:
        key, name = platform["key"], platform["name"]
        for q in questions:
            qid = str(q["question_id"])
            relative = preferred.get(f"{key}:{qid}", f"raw/{key}/{qid}.json")
            path = run_dir / relative
            record = None
            if not path.exists():
                findings.append({"severity": "error", "platform": key, "question_id": qid, "issue": "missing raw record", "path": relative})
            else:
                try:
                    record = load(path)
                except Exception as exc:
                    findings.append({"severity": "error", "platform": key, "question_id": qid, "issue": f"invalid JSON: {exc}", "path": relative})
            if record is None:
                rows.append({"platform": name, "question_id": qid, "status": "missing", "raw": relative, "screenshot": ""})
                continue

            if str(record.get("question_id", "")) != qid:
                findings.append({"severity": "error", "platform": key, "question_id": qid, "issue": "question_id mismatch", "path": relative})
            if str(record.get("question", "")) != str(q["question"]):
                findings.append({"severity": "error", "platform": key, "question_id": qid, "issue": "prompt differs from fixed question", "path": relative})
            if not record.get("platform"):
                findings.append({"severity": "error", "platform": key, "question_id": qid, "issue": "missing platform label", "path": relative})
            elif record["platform"] not in {key, name}:
                findings.append({"severity": "warning", "platform": key, "question_id": qid, "issue": "platform label differs", "path": relative})
            status = str(record.get("status", ""))
            if not status:
                findings.append({"severity": "error", "platform": key, "question_id": qid, "issue": "missing status", "path": relative})
            if is_success(status) and not str(record.get("raw_answer", "")).strip():
                findings.append({"severity": "error", "platform": key, "question_id": qid, "issue": "successful record has empty answer", "path": relative})
            for field in ("test_date", "mode", "conversation_url"):
                if is_success(status) and not str(record.get(field, "")).strip():
                    findings.append({"severity": "warning", "platform": key, "question_id": qid, "issue": f"successful record missing {field}", "path": relative})
            screenshot_value = record.get("screenshot") or record.get("screenshot_path") or ""
            screenshot = Path(screenshot_value) if screenshot_value else None
            if screenshot and screenshot.is_absolute():
                screenshot_exists = screenshot.exists()
            elif screenshot:
                screenshot_exists = (run_dir / screenshot).exists() or (run_dir.parents[1] / screenshot).exists()
            else:
                screenshot_exists = False
            if not screenshot_exists:
                findings.append({"severity": "error", "platform": key, "question_id": qid, "issue": "missing screenshot", "path": screenshot_value})
            rows.append({"platform": name, "question_id": qid, "status": status or "unknown", "raw": relative, "screenshot": screenshot_value})

    severity_counts = Counter(x["severity"] for x in findings)
    status_counts = Counter(x["status"] for x in rows)
    audit = {
        "run_id": manifest.get("run_id", run_dir.name),
        "expected_records": len(manifest["platforms"]) * len(questions),
        "audited_records": len(rows),
        "status_counts": dict(status_counts),
        "finding_counts": dict(severity_counts),
        "findings": findings,
        "records": rows,
    }
    output = args.output or run_dir / "analysis" / "completion_audit.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "expected": audit["expected_records"], "errors": severity_counts["error"], "warnings": severity_counts["warning"]}, ensure_ascii=False))
    return 1 if severity_counts["error"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
