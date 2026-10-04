# UI 灵感到落地 · UI Reference to Code

A reusable Codex skill for turning browser-found design references into clear design decisions, polished web interfaces, and browser-verified results.

## What it does

- Researches a small, purposeful set of references from sites such as Pinterest, Behance, Spline, Semi Design, and Apache ECharts.
- Converts observations into actionable guidance: what to borrow, where it belongs, and how to implement it.
- Routes work to available design skills and MCP tools only when useful.
- Supports three modes: research only, implement/redesign, and continue polishing an existing page.
- Tracks asset provenance, data definitions, responsive behavior, accessibility, performance, and visual verification.

## Install

Copy this repository's contents into your Codex skills folder:

```sh
mkdir -p ~/.codex/skills/ui-reference-to-code
cp -R . ~/.codex/skills/ui-reference-to-code/
```

Restart or start a new Codex conversation if the skill is not immediately available.

## Use

```text
$ui-reference-to-code
Study these references and improve the UI of my existing website.
Preserve its content and working features. Check desktop and mobile in a browser.
References: https://...
```

For research only, say so explicitly. The skill will return sources and implementation guidance without changing code.

## Repository layout

- `SKILL.md`: workflow entry point and task modes.
- `agents/openai.yaml`: Codex skill metadata.
- `references/research-and-assets.md`: reference research and asset tracking.
- `references/tool-routing.md`: design skills, browser, Semi MCP, ECharts, Spline, and publishing.
- `references/review-and-handoff.md`: visual/behavior review and handoff.
- `references/joho-case-study.md`: a concrete case study that informed the workflow.

The workflow is adaptable to the current project's audience, stack, tools, and visual direction; the JOHO case study is an example rather than a default design prescription.
