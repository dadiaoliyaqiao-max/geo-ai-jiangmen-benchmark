---
name: geo-ai-visibility-baseline
description: Run evidence-preserving brand visibility baselines across logged-in web AI search platforms, including independent prompts, recovery, ranking and citation analysis, screenshots, and audited Excel/Markdown delivery. Use for GEO or AI-search visibility benchmark and retest requests; do not use for generic SEO advice or ordinary web research.
---

# GEO / AI Search Visibility Baseline

Produce a reproducible snapshot of whether selected AI platforms naturally recognize and recommend a target brand. Preserve each platform answer as evidence; never optimize the prompts or reinterpret unsupported claims to improve the result.

## Establish the test contract

Before collecting answers, resolve these inputs from the request or existing project files:

- target brand and every accepted alias;
- platforms in scope;
- fixed question bank, theme, and intent labels;
- run date/timezone and output location;
- definitions for mention, recommendation, rank, TOP1/TOP3, strength, and property/project association;
- required spreadsheet sheets, report sections, screenshots, and filenames.

The question bank is user-configurable before a new run. Let the user create, replace, add, delete, reorder, or rewrite questions in their local copy, then confirm the resulting bank as part of that run's contract. Once collection starts, freeze that version: do not silently rewrite it. If a provided parser changes a frozen prompt, fix the parser, preserve affected attempts, and retest the exact contracted question.

For a new run, read [references/run-layout-and-schema.md](references/run-layout-and-schema.md), then use `scripts/init_run.py` when its directory contract fits. Reuse an existing run when the user asks to resume; do not initialize over it.

## Preflight every platform

Read [references/platform-runbook.md](references/platform-runbook.md) before controlling browser sessions.

1. Open every requested platform and confirm it is genuinely signed in and can start a new conversation. A visible tab alone is not sufficient.
2. Confirm requested search/deep-thinking modes are available. Record the actual mode used; do not claim a mode was enabled when the UI did not expose it.
3. After a browser or app restart, recheck all platforms before resuming collection.
4. If login, CAPTCHA, rate limiting, or a platform error blocks a run, record the attempt as blocked and expose the relevant page to the user. Resume only after the condition clears. Never invent an answer or source to fill a gap.

## Collect independent answers

For every platform-question pair:

- start a genuinely new conversation;
- submit only the fixed question, without the target brand, claimed strengths, projects, or corrective follow-ups;
- wait for generation and search activity to finish;
- save the complete visible answer, conversation URL, mode, source count, extractable source titles/URLs, timestamp, and screenshot before moving on;
- keep source URLs empty when the platform shows citation counts but does not expose stable targets;
- update progress after each saved record.

One question must not influence the next. Do not ask why the brand was omitted, ask the model to reconsider it, or reuse the prior conversation.

Preserve attempts immutably. Corrections, retries, and recovered answers belong in a new directory. Record which file supersedes which in a correction manifest or `manifest.json`; never overwrite the original capture.

## Recover safely

Use bounded retries for extraction failures or incomplete generation. Before retrying, distinguish:

- **answer absent**: retry the same question in a new conversation;
- **answer exists but extraction failed**: recover it from account history when possible;
- **prompt contamination**: run a clean independent retest with the exact fixed prompt;
- **short but complete answer**: preserve it and adjudicate explicitly instead of padding or replacing it;
- **login/CAPTCHA/rate limit**: stop platform execution, retain the failed attempt, and wait for the user or platform state.

## Analyze without upgrading claims

Read [references/analysis-and-deliverables.md](references/analysis-and-deliverables.md) before extracting recommendations or building outputs.

- Analyze the final user-visible answer, not search-planning or reasoning preambles.
- Preserve raw brand names and map them to standard names separately.
- Count a mention when an accepted alias appears in the final answer.
- Count a formal recommendation only when the brand enters a candidate/recommendation list. A background reference is mention-only.
- Derive rank from visible candidate order. Do not force an unranked mention into TOP3.
- Treat “AI says this brand served this project” as an AI claim until an opened original page supports the association.
- Separate confirmed errors, suspected errors, high-risk unsupported claims, and unverified claims.
- Label all rankings as results of this test, never as official market rankings.

Use `scripts/audit_run.py` before analysis. After producing normalized records, use `scripts/summarize_records.py` when the record schema matches.

## Deliver and verify

Build the requested workbook with the spreadsheet skill when available. Keep raw answers separate from analysis, use bounded formulas for summaries, add filters/freeze panes, and render every sheet for visual inspection. Scan formulas for `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`, `#N/A`, `#NUM!`, and `#NULL!`.

The Markdown report should lead with completion counts and core rates, then cover platform differences, themes/projects, competitors, sources, errors, and concrete P0/P1/P2 actions. Report source limitations prominently.

Completion requires:

- every requested platform-question pair accounted for as success, limited, or failed;
- every analyzed record traceable to a raw file and screenshot;
- corrections documented without deleting originals;
- formulas, workbook layout, required report sections, and file paths verified;
- no credentials, cookies, tokens, browser profiles, or `.env` files in deliverables or Git.

Do not commit or push results unless the user asks. When authorized, stage only files in scope and inspect the staged diff before pushing.
