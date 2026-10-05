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

## Aesthetic behavior cases (v3.0)

Run these as realistic skill tasks, with raw artifacts rather than the expected answer. Inspect the output decisions and generated page where applicable; matching phrases in SKILL.md is not a behavior test. Store generated work outside the repository. Aesthetic reports are Agent judgements; a named test case is not a passed evaluation.

| ID | Raw input / context | Observable expectation | Failure signal |
| --- | --- | --- | --- |
| A1 Generic AI SaaS | “做一个 AI Agent 网站。” + available reference/brief | Select or honestly defer primary; concrete thesis, dominant subject and hero prototype before whole-page generation | Default purple glow/orb/glass/three cards without design reasoning; invented reference visit |
| A2 Too Safe | Page with centered hero, equal rounded grids and uniform section spacing | Diagnose combined safe cues; direction-specific structural correction and preserved content | Random decoration, symmetry treated as an automatic defect, or only margin tweaks |
| A3 Reference Essence | Supplied huge-title/tiny-label reference and similar-font/color implementation with compressed scale contrast | Explain the lost proportion and repair it; keep essence distinct from pixel fidelity | Declares faithful because palette/fonts match |
| A4 Missing Visual Asset | Photography-dominant reference, implementation with only gradient | Identify missing dominant subject; plan available material/focal crop or disclose blocking asset | Replaces the photo with a circle and marks imagery complete |
| A5 Section Repetition | Five consecutive heading + paragraph + three-card sections | Give actual section IDs and differentiated information roles/transitions | New colors on the same five grids, content deleted to create whitespace |
| A6 Mobile | Strong desktop composition compressed to phone | Redesign phone hierarchy, crop, wraps and signature; preserve essential content/actions | Only reduces font sizes, checks overflow and calls mobile accepted |

Also verify boundaries: E preserves source decisions, A produces research only, local repairs keep scope, absent screenshots give null scores/unreviewed, a functional dense UI is not forced into an expressive landing page, and a machine verified status cannot override aesthetic needs-polish. Use the [direction example](../examples/aesthetic-direction.md) to check the complete chain without treating its hypothetical observations as evidence.

### v3.0 execution record

2026-10-04: an independent Agent performed all six raw-brief design tasks in isolated local storage without reading this expected-answer table. The outputs addressed scale loss, missing photography, section roles and phone recomposition; unavailable visuals stayed null/unreviewed. This was design reasoning, not six rendered-site passes. The execution exposed an absent no-reference creation route and a stale F instruction to average common rules; both were corrected and rechecked. A paired prototype also exposed the distinction between verbal reference descriptions and actual B screenshots, now explicit in routing.

Two separate Agents used v2.1 and v3.0 respectively for the same personal AI portfolio brief, title, capability content and available material. Both generated only Nav/Hero/First Transition. Ego Lite captured hero and transition at 1440 and 390 CSS px, 1000px height and DPR 1: eight initial images, viewed and registered with the unchanged evidence helper; both runs validated with no artifact issues. HTTP CTA interactions reached the two original anchor targets, with no document overflow at the tested widths.

Night Eye initially rewrote HTTP captures into dark colors. Final light-theme captures rendered the exact self-contained HTML bytes through data URLs in the same Ego Lite page, isolating extension injection; no browser preference or source styling was changed. Data-URL anchor navigation was restricted, so HTTP interaction observations and isolated visual captures are separate evidence, not one end-to-end environment. Independent image review found the v3 mobile sculpture too cropped; v3 then reduced the mobile SVG to the viewport and captured a changed iteration, registered with no evidence issues. No actual reference screenshot exists, so reference essence remains unknown. This single paired generation is exploratory; it cannot establish universal improvement or full-site engineering acceptance. Generated artifacts and detailed critiques remain outside the public skill repository.

## Deterministic suite

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
