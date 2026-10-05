# Polish Loop Playbook

A reference-driven UI should rarely be accepted after one implementation pass. The first pass proves the direction; later passes resolve proportion, material quality and behavior. Use this playbook for Pinterest replicas, website references and expressive landing pages.

## What the first pass is allowed to prove

The first pass only needs to prove:

- the primary reference is visible in the silhouette;
- the page has a clear first, second and third focus;
- the primary subject and CTA are present;
- desktop and mobile have an intentional composition;
- the implementation can be rebuilt in the current stack.

Do not spend the first pass polishing every card, icon or footer.

## Three repair passes

### Pass 1 — Structure

Compare the reference and implementation at the same route and viewport. Repair the two largest relationships:

- dominant subject scale and position;
- title width, line breaks and type-to-image balance;
- first transition height and section rhythm;
- image crop and intentional grid break;
- mobile reading order and overflow.

Remove generic components before adding decoration. Re-capture both desktop and mobile after the repair.

### Pass 2 — Material

Inspect the actual pixels, not only the DOM:

- are the images from one coherent light and color world?
- does the chosen type have the same authority as the reference?
- do surface, border and accent colors support the subject?
- does a 3D object explain material, place or product behavior?
- are the captions, metadata and CTA labels specific enough to feel authored?

Replace weak assets or simplify the scene. A real, consistent image usually improves the result more than another shader.

### Pass 3 — Behavior

Test the implemented states:

- pointer / touch / scroll response;
- loading and poster fallback for 3D assets;
- mobile menu and keyboard focus;
- reduced motion;
- slow-device behavior and layout stability.

Reduce motion when it competes with reading. Keep one primary animated gesture per scene.

## Difference log

Every repair has one entry:

```md
### P1 — Hero feels like a poster, not a destination
- region: launch-hero
- reference_artifact: primary-reference
- before_artifact: iteration-1-desktop
- observation: title occupies 56% of the left column while the reference gives more weight to the destination image
- visual_impact: product/place identity is delayed and the hero feels typographic rather than cinematic
- repair: reduce display width, enlarge the image crop, move the subject toward the first focal point
- after_artifact: iteration-2-desktop
- severity: Major
- resolved: true
```

Use `Major` for a direction-level problem, `Minor` for a detail that does not change the reading order, and `Critical` when the page cannot communicate its main subject or the interaction is unusable.

## Acceptance gate

Use `accepted` only when all of these are true:

- the reference relationship survives on desktop and mobile;
- no unresolved Major/Critical difference remains;
- the strongest asset is resolved or explicitly marked as provisional;
- the first transition changes rhythm instead of repeating the Hero structure;
- 3D has a clear job and a static mobile/reduced-motion fallback;
- screenshots were viewed after the latest repair;
- engineering QA and aesthetic review are both recorded.

Use `needs-polish` when the structure works but assets, type, crop or rhythm remain visibly provisional. Use `unreviewed` when screenshots or source observation are missing. A passing build never advances this gate.

## Reference distance review

When the result feels weaker than the reference, diagnose the distance in this order:

1. **Asset distance** — source photography, model quality, lighting and crop.
2. **Scale distance** — subject, title and whitespace proportions.
3. **Rhythm distance** — transitions, density changes and scroll pacing.
4. **Type distance** — font character, line breaks, tracking and hierarchy.
5. **Behavior distance** — observed interaction, loading and responsive states.

Fix the earliest large distance first. Do not add animation to compensate for weak assets or add cards to compensate for missing hierarchy.
