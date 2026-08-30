# Analysis and deliverables

Read this reference when extracting brand visibility, assessing evidence, or building the final workbook/report.

## Target classification

Apply aliases case-insensitively where appropriate, but preserve the exact form that appeared.

- **Mention**: an accepted alias occurs in the final visible answer.
- **Formal recommendation**: the target enters a visible recommendation/candidate list.
- **Rank**: its order in that list. Continue past five when the model supplied more than five candidates.
- **TOP1/TOP3**: rank equals 1 / rank is 1–3.
- **Strength 0**: absent.
- **Strength 1**: mentioned, not recommended.
- **Strength 2**: formally recommended.
- **Strength 3**: recommendation includes explicit preference such as first choice, prioritize, strongly recommend, worth focusing on, or especially suitable.

Negative remarks are a separate flag. Generic buying risks near the target name are not automatically target-specific negatives.

## Project/property association

Count an association only when the answer explicitly says or clearly implies the target served, designed, installed, completed, or has a case in the named project. Recommending the brand to owners of that project is not enough.

Keep two independent fields:

- `property_case`: what the AI claimed;
- evidence result: whether an opened original page supports target + project + service/case.

## Brand normalization

Maintain an alias map from raw names to standard names. Do not merge similarly named companies without evidence. Count the same standardized brand at most once per platform-question record.

Competitor statistics should report recommendation count, average visible rank, platform coverage, main themes/projects, and evidence quality where available.

## Evidence grading

Open original pages when possible. Search-result snippets and AI citation summaries are discovery aids, not proof.

Distinguish brand official websites, government/official institutions, industry associations, authoritative media, maps/reviews, content platforms, industry portals, company directories/encyclopedias, advertorial/reposts/aggregation, and unavailable/no URL.

Suggested support results:

- `supported`: opened page directly supports the claim;
- `partially_supported`: supports brand identity/service but not the full recommendation reason or project claim;
- `unsupported`: opened page contradicts or does not support the linked claim;
- `unverified`: URL missing, inaccessible, or not yet opened.

Do not convert `unverified` to `false`. Flag quantitative superlatives such as “many owners”, “market leader”, or “most cases” unless their source supports the quantity.

## Metrics

Use successful/adjudicated tests as the denominator unless the user defines otherwise:

- mention rate = mentions / valid tests;
- recommendation rate = formal recommendations / valid tests;
- TOP3 rate = TOP3 / valid tests;
- TOP1 rate = TOP1 / valid tests;
- strong recommendation rate = strength-3 / valid tests;
- project association rate = explicit target-project claims / valid tests for that project;
- average rank = mean rank among formally recommended records with visible rank.

Report the counts alongside rates so small denominators remain visible.

## Workbook

When the user does not specify another structure, include raw test detail, theme summary, one sheet per platform, cross-platform comparison, project/property analysis, competitor visibility, AI sources, errors/unverified claims, and GEO priorities.

Keep raw answers intact in the raw sheet. Use formulas for summary counts/rates when practical, bounded to the actual raw range. Add filters, freeze panes, semantic number formats, and conditional formatting. Render every sheet, inspect clipping and chart axes, then scan formula errors.

## Markdown report

Cover execution totals and limitations, overall target visibility, platform differences, generic themes, every project/property, competitors that exceed the target, sources/evidence limitations, errors, and concrete P0/P1/P2 actions.

Every GEO action should identify the target topic, current gap, exact content asset to create, required evidence fields, publication channel, and AI platform to attack. Avoid “increase promotion” or “publish more content” without specifying the asset.

## Final audit

Verify expected record count, preferred raw paths, exact question text, screenshots, correction preservation, workbook sheets/formulas/layout, report sections, ranking language, delivery paths, and absence of secrets.
