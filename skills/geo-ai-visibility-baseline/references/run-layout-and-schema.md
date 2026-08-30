# Run layout and record schema

Read this reference when initializing, resuming, or auditing a baseline run.

## Recommended directory contract

```text
work/<slug>_<YYYYMMDD>/
|-- manifest.json
|-- progress.json
|-- questions.json
|-- corrections.json                 optional
|-- raw/
|   |-- <platform-key>/Q01.json
|   `-- <platform-key>_retest/Q01.json
|-- screenshots/
|   |-- <platform-key>/Q01.png
|   `-- <platform-key>_retest/Q01.png
`-- analysis/
    |-- completion_audit.json
    |-- test_records.json
    `-- summary.json
```

Use a new dated directory for a new baseline. Do not mix it with an older baseline.

## Question bank

`questions.json` is an array. Required fields:

```json
{
  "question_id": "Q01",
  "question_number": 1,
  "theme": "Market or project theme",
  "intent_code": "A",
  "intent_name": "Direct recommendation",
  "question": "Exact user prompt"
}
```

Question IDs must be unique. Preserve punctuation and wording exactly.

## Manifest

The initializer writes this minimal shape:

```json
{
  "run_id": "brand_20260830",
  "created_at": "ISO-8601 timestamp",
  "timezone": "Asia/Shanghai",
  "platforms": [
    {"key": "doubao", "name": "豆包"}
  ],
  "questions_file": "questions.json",
  "preferred_records": {
    "doubao:Q05": "raw/doubao_retest/Q05.json"
  }
}
```

`preferred_records` is optional. Add an entry only after preserving the original attempt and documenting why another file supersedes it.

## Raw record

Required for audit:

```json
{
  "test_date": "2026-08-30",
  "platform": "豆包",
  "question_id": "Q01",
  "theme": "江门全屋定制",
  "intent_code": "A",
  "intent_name": "直接推荐型",
  "question": "Exact fixed prompt",
  "status": "success",
  "mode": "Actual mode visible in UI",
  "conversation_url": "https://...",
  "raw_answer": "Complete visible answer",
  "source_count": 12,
  "source_links": [
    {"title": "Source title", "url": "https://example.com/page"}
  ],
  "screenshot": "work/<run>/screenshots/doubao/Q01.png",
  "notes": ""
}
```

Platform capture scripts may use `href`/`text` or `links`; normalize only in analysis. Do not rewrite the raw record solely to make schemas identical.

Allowed status values are project-specific, but distinguish at least `success`, `failed`, `blocked`, and an explicitly adjudicated short/incomplete state.

## Normalized analysis record

`scripts/summarize_records.py` expects an array containing:

- `platform`, `question_id`, `theme`, and `status`;
- `target_mentioned` (or compatibility field `kinwai_mentioned`);
- `target_recommended` (or compatibility field `kinwai_recommended`);
- `target_rank` (or compatibility field `kinwai_rank`);
- `top1`, `top3`, `strength`, and `property_case`;
- `all_recommended_brands` as standardized names;
- `urls`, `domains`, and `source_platforms` when extractable.

Prefer generic `target_*` names in new projects. Compatibility aliases exist only to support the first production run.

## Corrections

For each correction, preserve:

- original path;
- corrected path;
- reason: prompt contamination, extraction failure, recovery, or adjudication;
- timestamp;
- decision about which record is preferred for analysis.

An invalid or CAPTCHA-interrupted attempt remains evidence of the interruption and must not be silently deleted.
