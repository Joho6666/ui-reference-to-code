# Browser capture and QA

The browser tool owns navigation and interaction; this skill owns the capture contract. Use any available runtime, but do not treat a DOM snapshot as a screenshot or a script recording as an observed design. Keep one capture per URL, route, viewport, DPR, theme, state and scroll position.

## Run and evidence setup

A multi-round task stores its immutable artifacts below `.ui-design/runs/<run-id>/`. Create the run before editing so the initial selected source files establish a baseline:

```sh
python3 scripts/evidence.py create-run --project . --url http://localhost:3000/
python3 scripts/evidence.py list --run .ui-design/runs/<run-id>
```

`project_revision` contains HEAD (when available), a `dirty` indicator and SHA-256 hashes for the selected files. The default selection is tracked and non-ignored untracked project files, excluding `.git`, `.ui-design`, caches and OS metadata. `--files` selects a deliberate subset. Dirty work is supported; any change to HEAD or a selected file invalidates evidence. Changes outside a selected subset do not.

Capture the page in the browser, view the screenshot, then register it. Screenshot files are copied into the run and become immutable. A capture receipt can be exported by the browser adapter or assembled from browser-reported values:

```json
{
  "run_id": "the-run-folder-name",
  "iteration": 1,
  "url": "http://localhost:3000/",
  "route": "/",
  "viewport": [1440, 900],
  "dpr": 1,
  "theme": "light",
  "state": "default",
  "scroll": [0, 0],
  "captured_at": "2026-10-04T12:00:00Z",
  "source_revision": "fingerprint returned by evidence.py snapshot helper",
  "regions": {"hero": [0, 0, 1440, 620]}
}
```

Read the run fingerprint with `python3 scripts/evidence.py snapshot --run ...`; compare it before and after the capture. Register with `scripts/evidence.py add --run ... --path capture.png --id impl-desktop --type screenshot --role implementation --capture capture.json --observer agent --iteration 1`. Use `observer human` for a screenshot a person actually inspected; `unobserved` keeps the bytes but cannot support a visual score. An implementation receipt must use the current run fingerprint. Reference artifacts can use external source revisions but must still be present in the run. `regions` are named design regions with pixel-space `[x,y,width,height]` rectangles in the image; use the same IDs in the design spec, component map, captures, QA and differences.

Capture `viewport` in CSS pixels and verify the PNG pixels are exactly `viewport × DPR`. Do not silently resize screenshots. A reference from a different route can be compared only through an explicitly shared `region_id` and the same `viewport`, DPR, theme, state and scroll. Pixel Fidelity requires reference screenshots for the compared desktop and mobile regions. F Inspiration compares a design spec to the implementation and does not score pixel similarity.

## Preserve scope and record checks

Before edits, write `.ui-design/runs/<run-id>/preservation.json` with only relevant routes, links, API contracts, copy, data fields and functional behaviors. For D, an empty list is insufficient. For B/C with no existing contract, an explicit reason can describe why no baseline applies. Register versioned `check-result` JSON artifacts; each item check names the baseline item, repeats its expected value, records the observed value, a boolean outcome and the actual check method. For interactions use `browser-interaction`; for content/links use the observed DOM or a source-specific test. Command checks record the actual command and exit status. These result files and browser actions remain declarations from the executing environment, not cryptographic attestations.

## Compare and repair

QA v2 is stored as `.ui-design/runs/<run-id>/qa-<iteration>.json`; its `browser.desktop/mobile`, score evidence, comparison and difference fields reference registered artifact IDs. A resolved Critical/Major difference points to a later, changed implementation screenshot, with the same capture conditions and a recorded review. Keep earlier QA iterations in the run; the gate does not allow an unresolved serious difference to disappear from later reports.

Run `python3 scripts/qa_gate.py .ui-design/runs/<run-id>/qa-<iteration>.json`. Exit codes: 0 verified, 1 needs-repair, 2 unverified, 3 invalid report. A score below 7 or a failed content/function check needs repair. Missing, stale, unobserved or unsupported evidence is unverified. Include recognized failure codes from the QA v2 schema to explain unavailable reference, browser, font or assets and regressions.

`python3 scripts/visual_diff.py reference.png implementation.png --output diff.png` optionally uses Pillow. It refuses mismatched pixel dimensions and can crop a declared region. Its changed-pixel ratio and bounding box are evidence for investigation, not a design score. Without Pillow, compare the inspected images manually; run/PNG validation and the QA gate use only Python's standard library.

See [contracts.json](../schemas/contracts.json), [QA example](../examples/qa-unverified.json) and [visual scoring](visual-fidelity.md). A valid schema or gate result verifies file identity and stated conditions, not whether a person actually looked at the image, whether the design is good, or whether a check-result is truthful.
