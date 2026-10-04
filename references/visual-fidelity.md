# Visual fidelity and scoring

Compare only a source the task actually adopted: a reference screenshot for Pixel Fidelity (E), or an explicit adopted design spec for Inspiration (F). Assign consistent `region_id` values through spec → component map → capture → difference. Compare matched viewport, DPR, theme, state and scroll conditions. A region may be mapped across routes only when its region ID and the comparison observation make that scope explicit.

## Pixel signal

Optional `scripts/visual_diff.py` checks image sizes, reports changed-pixel ratio and changed bounding box, and saves a red difference image. A region crop is optional. The script never resizes, aligns, masks, or chooses a pass threshold for the page. Dynamic content, font rendering, animation and image crops can affect its signal; explain those conditions and visually inspect the compared images.

## QA v2 scores

Each score has `applicable`, `score`, `confidence`, `reason` and structured `evidence` references (`artifact_id`, `region_id`, `observation`). Default B/C/D dimensions are layout, typography, color, component, responsive and interaction. E uses geometry, typography, visual, composition, responsive and interaction. F uses consistency, hierarchy, usability, responsive, interaction and content. Run E and F in separate scoped QA reports if a task explicitly needs both.

Scores below 7/10 need repair. Confidence `low` or `none`, missing image observation, or no useful evidence requires `score: null`; do not use a high score with low confidence. Applicable desktop/mobile captures, real check results, scoped preservation checks, current revisions, and region comparisons must all be linked. Unknown source animation or interaction remains unknown; test implemented behavior without claiming it matches an unobserved source.

Score anchors: 9–10 meets the scoped intent with evidence and only negligible issues; 7–8 meets key structure and behavior, with minor limitations; 4–6 has a visible major issue or incomplete state; 0–3 misses a core goal or interaction. These values require agent/human visual reasoning and are never calculated from pixel-diff percentages.

Difference records include a stable ID, severity, region, expected and observed results, source and implementation artifacts, and resolution proof. Critical/Major unresolved defects need repair. A resolution must link to a later implementation screenshot whose bytes changed, whose iteration and capture time are later, whose review is recorded, and whose viewport/DPR/theme/state/scroll and region match the original. Keep the prior iteration as history.
