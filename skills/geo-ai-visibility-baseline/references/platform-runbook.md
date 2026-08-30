# Platform runbook

Read this reference before browser collection or when a platform becomes blocked.

## Shared preflight

For each platform:

1. Load the official web app in the browser session that contains the user's login.
2. Verify an authenticated account indicator or account history is visible.
3. Start or open a harmless new-conversation state and confirm the prompt box is enabled.
4. Record the available search/deep-thinking controls.
5. Do not submit test prompts until all requested platforms pass preflight.

After any browser/app restart, repeat the checks. If one platform is logged out, keep the other completed data and ask the user to log in only to the affected platform, then recheck all platforms before continuing.

## Per-question state machine

```text
new conversation
  -> exact prompt submitted
  -> generation/search finished
  -> final answer captured
  -> sources captured if exposed
  -> screenshot captured
  -> raw JSON saved
  -> progress updated
  -> next new conversation
```

Do not advance when the saved record lacks the answer or screenshot.

## Doubao

- The web UI may expose search results without a separate search toggle. Record the actual visible mode instead of asserting that联网搜索 was enabled.
- Source links can be numerous and may appear after answer extraction. If the answer was already saved, write a source sidecar rather than modifying the raw answer.
- A CAPTCHA can appear after several new conversations. Preserve the blocked attempt and show the verification page to the user. After it clears, start a clean new conversation for the pending question.
- When prompt text was contaminated, use a new correction directory; never reuse the contaminated chat as the clean retest.

## Tencent Yuanbao

- Prefer联网搜索/深度思考 when the UI exposes them and the test contract requests them.
- The captured page may contain search-planning prose before the final response. Preserve it in `raw_answer`, but exclude the preamble from mention/recommendation analysis.
- Citation counts may be visible while stable target URLs are not. Save the count and an explicit note; leave URL fields empty.
- If extraction captures only a generation-state fragment, recover the completed answer from account history. Preserve both files and point `preferred_records` to the recovered one.

## DeepSeek

- Enable available search/deep-thinking modes only when visible and requested.
- Deduplicate citation URLs while keeping the platform-displayed search-page count separately.
- Do not reject a concise answer merely because it is shorter than other responses. Judge whether it answers the question completely; document an adjudication when needed.
- If the browser DOM exposes multiple assistant blocks, select the final user-visible assistant answer rather than transient status text.

## Retry limits and stopping conditions

- Retry an extraction failure only after confirming the conversation contains a completed answer.
- Use a new conversation for a content retry; never add a corrective follow-up.
- After repeated login/CAPTCHA/rate-limit failure, stop the platform run, record the blocker, and request user action. Other already collected platform data remains valid.
- Never use another public search engine to fabricate the missing platform answer.

## Evidence capture

A screenshot should show enough context to connect platform, question, and answer. Keep the conversation URL in the JSON even when the screenshot is the primary visual proof. Do not store or commit browser profiles, cookies, local storage dumps, tokens, or passwords.
