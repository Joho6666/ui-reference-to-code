# Aesthetic review — judge the rendered result

Review actual desktop and phone images against the recorded direction, user intent and adopted reference essence. Use existing run IDs, artifact IDs, regions and current source fingerprints from [browser validation](browser-validation.md). A DOM measurement or build success cannot show that a composition feels deliberate. A reviewer can be the implementing Agent or an independent observer; disclose which it was.

Keep a flexible `.ui-design/runs/<run-id>/aesthetic-review-<iteration>.md` beside engineering QA when a persistent report is useful. Link the art-direction record and actual captures; record stage (`hero` or `full-page`), route, widths, source revision and observed regions. Do not add aesthetic fields to QA v2, invent artifact types or send SAFE_DESIGN_WARNING as a machine failure code. Reuse the JSON design-spec artifact's `intent` and per-region `rule` to carry the concise adopted direction into the existing gate; the longer reasoning lives in Markdown. If a capture becomes stale after a repair, replace the review evidence before accepting the revised result.

## Hero Gate

Before expanding a visual landing page, answer from the captures: is there a clear first/second/third focus, an intentional silhouette, type character, meaningful scale contrast, purposeful whitespace, appropriate depth, a resolved main asset, a recognizable motif, originality within the brief and retained reference essence? Inspect the first transition as part of the composition, not as an unrelated card row.

Use `accepted`, `needs-polish` or `unreviewed` as an **Agent/human judgement**. Accept when the central thesis is visible on both devices and no unresolved direction-critical defect remains. The ten review dimensions below should have supported scores of at least 7 when applicable; one weak primary subject is not canceled by a high average. For an intentional flat/no-image direction, document why a dimension is inapplicable rather than fabricating depth or an image. Missing screenshots, uncertain asset or reference essence and low-confidence observations leave the relevant review unreviewed. A known visible failure needs polish. Acceptance covers only the recorded hero scope.

This is an internal review step. It does not ask for user confirmation unless the user requested a design choice or approval. If browser capture is unavailable, continue independent asset/content/code work, report the blocked visual judgement and keep whole-page aesthetic acceptance pending; do not falsely advance the hero review to accepted.

## Aesthetic Critic

For hero and full-page review, answer each question with an observed region and consequence; “none observed” is legitimate, missing evidence is “unknown.”

- What looks generic or AI-generated, and which visual choices cause that reading?
- What lacks hierarchy; which parts are too symmetrical, too safe or conservatively scaled for this direction?
- Where is whitespace uniform, a section without identity, or a heading/body/cards pattern repeating an earlier section?
- Which asset feels provisional or visually weak; where does intended depth or typography character disappear?
- What should be removed, become 2–3× larger, become smaller, or intentionally break the grid — and why? “No change” is valid; these are questions, not automatic edits.

Apply the [Safe Design Detector](aesthetic-intelligence.md#safe-design-detector). Emit SAFE_DESIGN_WARNING only with evidence of several cues and a direction-specific problem. Under E, a faithful source should not be penalized for symmetry or lack of novelty; any aesthetic reservation remains advice, not permission to change the reference. Under F or D, critique the adopted direction rather than rewarding resemblance to an arbitrary popular site.

Every actionable finding needs `finding ID / region / capture evidence / cause / intended relationship / specific change / preservation risk / priority`. Prefer structural repairs over adding decoration: establish the dominant subject, restore a lost ratio, change the crop, reduce competing visual anchors or replace a repeated information layout. Give the two or three changes with the largest visual effect first. Record what was actually removed/recomposed and view fresh captures after changing it; do not close a finding by changing a status alone.

## Independent Aesthetic Score

Use a table, not a new schema. Review **Visual Hierarchy, Composition, Typography, Scale Contrast, Whitespace, Density Rhythm, Depth, Imagery, Originality, Signature Moment**. Record each as `score 0–10 or null / confidence / reason / artifact_id + region_id + concrete observation`, with an explicit inapplicability reason when necessary. Inspect desktop and phone individually where their composition differs; a strong desktop must not hide a weak phone behind one average.

Anchors: 9–10 is a distinctive, coherent and resolved execution of the intended relationship; 7–8 communicates the direction with only minor polish; 4–6 loses an important relationship or has a visible generic/provisional region; 0–3 misses the direction's core subject or reading hierarchy. These are contextual Agent/vision judgments. Confidence low/none, unviewed or stale images, absent comparison, or no useful evidence requires **score null**. Never convert pixel diff into aesthetic quality, auto-score from CSS values, or default every dimension to 8.

Keep **Reference Essence** as a separate explanation and high/medium/low/unknown assessment: why the primary works, whether those relationships survive, and which deliberate adaptations preserve or lose them. It is not a substitute for E fidelity or an extra pixel score. If no primary reference was observed, essence is unknown, not invented. For a user-directed original brief, review the adopted thesis and explicitly note that reference-based essence was unavailable.

## Full page and mobile

Review a scroll sequence of the actual sections, not just isolated crops. Check the planned loud/quiet/dense rhythm and the signature screen. Phone review checks hierarchy, silhouette, scale, whitespace rhythm, crop, intentional tension and the signature element alongside overflow and behavior. A wide desktop scene may need a stacked editorial composition, a different focal crop and reordered visual emphasis; preserve semantic reading order and important content. A smaller version of the desktop is not sufficient evidence of a successful mobile direction.

Deliver the engineering status from `qa_gate.py` **and** the aesthetic verdict for the observed scope. Engineering verified + aesthetic needs-polish means the design still needs work. Engineering verified + aesthetic unreviewed means the visual quality is unknown. An accepted aesthetic report does not override failed preservation, stale evidence or broken interactions. Overall completion requires both the existing engineering conditions and the applicable design review; state any gaps honestly.
