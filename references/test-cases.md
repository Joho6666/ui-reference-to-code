# Skill behavior and evidence tests

Test observable behavior and meaningful invariants. Report the actual execution level; test fixtures and DOM runs are not screenshots or complete visual acceptance.

## Routing cases

| ID | User input / context | Expected behavior | Failure signal |
| --- | --- | --- | --- |
| T1 | “参考 Linear 首页，把我的 SaaS 首页设计得更现代，但不要复制。” | C+F; existing target project becomes D+website+F | Copies brand/assets or misses original design intent |
| T2 | Supplied screenshot: “尽量还原。” | B+E, evidence-labelled specs and matched comparison | Invented timing or self-score instead of capture |
| T3 | Existing Vue page: “参考 Stripe 改一下，功能别动。” | D+website, preserve routes/API/content and Vue | Removes content, replaces stack without reason |
| T4 | “找几个作品集参考，不写代码。” | A, traceable source observations only | Edits project, installs UI, publishes |
| T5 | “继续优化上一次的页面。” with record | Resume after checking record and source state | Reuses stale capture |
| T6 | Multiple pages from one source | Shared tokens with recorded page variants | Conflicting duplicated systems |
| T7 | Desktop source only | Mark mobile adaptation as such | Claims mobile pixel fidelity |

## Deterministic tests

```sh
python3 -m unittest discover -s tests -v
```

The suite uses small synthetic PNG files to exercise helper/gate invariants; those files are not screenshots from a browser. Tests cover corrupt/missing files, hashes, path escape, PNG CRC and dimensions, revision staleness, evidence references, score confidence, preservation checks, difference repair history, matched E conditions, F scoring semantics, CLI exit codes and the optional image diff.

## Real browser evaluation harness

`tests/browser_evaluation.mjs` is an optional Ego Lite adapter for two isolated static fixtures. It captures the reference and implementation at desktop/mobile sizes, exercises search and the CTA, records preservation checks, detects an intentionally overflowing mobile CTA, repairs it, and captures the changed page again. Browser interaction and screenshot observation are separate: register/mark image observations only after actually reviewing the captured files. A failure to capture must remain unverified.

To run it, start the fixture HTTP server and prepare an output directory with `tests/browser_evaluation.py`. The Ego adapter uses the runtime already supplied by Ego Lite, not a skill-level browser dependency. `browser_evaluation.py assemble <output>` produces QA reports and calls the real gate. It does not automate visual judgement or manufacture screenshot observations. Record any tool/runtime limitation and the resulting gate status.

## v2.1 record

The deterministic suite and CI check schemas, evidence bytes, selected revisions, and QA decisions. It cannot attest that a browser generated the capture, a person actually viewed the image, or that a semantic observation/score is honest. Record genuine browser fixture execution separately from synthetic tests; planned/unavailable runs must not be presented as end-to-end passes.

### Current Ego Lite execution record

2026-10-04: both isolated fixtures were opened in Ego Lite Chromium. The portfolio fixture ran at 1200 CSS px, returned 1 / 0 / 2 / 1 for four real search events, kept its document within the viewport, and navigated the CTA to `#contact`. The responsive fixture ran at 390 CSS px; its initial CTA was 560px wide and made the document 584px wide. After changing the CTA to wrap, a later live DOM measurement showed a 295px CTA and 390px document. Ego Lite's `Page.captureScreenshot` timed out repeatedly, including a direct CDP capture attempt. These are real-browser functional and DOM checks, not screenshot E2E or visual acceptance; the gate keeps the repair unverified until current screenshots can be captured, inspected and registered.
