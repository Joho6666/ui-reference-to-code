# Aesthetic intelligence — choose and interpret

Use this layer before turning a visual reference into tokens. Judge a reference against the user's audience, content, desired character and task mode. Novelty alone is not quality; expressive choices still need readable content, usable controls and an appropriate tone.

## Taste Curator

Start from a diagnosed design problem, not a list of famous brands. Use [research and assets](research-and-assets.md) to choose sources and record actual observations. A small shortlist is enough once the decision is supported; do not collect pages to fill a quota.

For each serious candidate, record observed strength, weakness, relevance and implementation value. Examine visual distinctiveness, composition strength, typography character, scale contrast, imagery quality, section rhythm and originality. Use concrete evidence such as a crop, heading proportion or transition; unknown sections stay unknown. Do not give thumbnail-only candidates a confident whole-page rating. Prefer a decisive, contextually appropriate reference over averaging unrelated strong fragments.

Select one **Primary Reference** for the scoped direction. It owns composition, type personality, scale, whitespace, depth, rhythm and motif. Secondary references can supply a named crop, material or local treatment; functional references supply navigation, states or product structure. A 70 / 20 / 10 influence description is a useful illustration, not a measurable blend or fixed quota. If a secondary contradicts the primary, reject it or document the deliberate local exception. A user-selected E reference stays authoritative even if the curator dislikes it; explain constraints and preserve its essence.

If research is unavailable, use an actually supplied reference. If none exists, label the working direction as **proposed, reference pending** and use the brief to make progress; never invent a visited source or claim reference essence was checked. Research-only A stops at curation and actionable direction. A functional application can use a compact direction grounded in its existing system; novelty must not obstruct dense work.

## Visual Thesis

Before visual implementation, write one sentence that makes at least these choices concrete: dominant subject, composition, type character, scale relationship and emotional character. “Modern, premium, clean” is insufficient. The sentence should let another designer anticipate the silhouette.

Example, not a default style: “A paper-like AI portfolio where an oversized editorial headline leads into one black workflow canvas, tiny technical labels provide a secondary voice, and a broad empty margin keeps the first screen deliberate.” A fashion portfolio, education site or operations dashboard requires its own thesis. Carry user choices forward rather than reselecting the aesthetic at every turn.

## Aesthetic DNA and Reference Essence

Record these relationships before precise sizes; use proportions and measured/estimated labels from [decomposition](reference-decomposition.md).

| Relationship | Question that changes a design decision |
| --- | --- |
| Visual hierarchy | Where does the eye go first, second and third? What must remain subordinate? |
| Dominant visual | What occupies the most visual weight: type, photograph, product canvas, object or something else? |
| Composition silhouette | Centered, left/right-heavy, asymmetric, diagonal, full-bleed, split or layered — and why? |
| Scale contrast | What is the relationship of display to labels and body? Does the headline claim half a viewport or sit inside a card? |
| Typography personality | Grotesk, editorial serif, condensed, wide, geometric, humanist, industrial, technical, fashion or raw; how does display differ from body? |
| Negative space | Where is space deliberately large; where is compression necessary? |
| Density rhythm | Which parts are empty, dense, declarative or editorial? |
| Visual tension | Is there an intentional crop, overlap, offset or grid break? What stabilizes it? A lack of tension can be appropriate. |
| Depth | What sits in background, middle, foreground or floating layer? Which layers are truly necessary? |
| Imagery language | Photography, 3D, illustration, real UI, product mockup, video or original artwork; why this medium? |
| Signature motif | Which one screen or recurring gesture should be recognizable later? |
| Emotional temperature | Research lab, human workshop, editorial fashion, playful learning, industrial, raw, cinematic or another specific tone? |

**Reference Essence** states the causal reason the chosen reference works, not its palette inventory. Example: “A headline claims nearly half the viewport while metadata stays tiny, creating poster-like authority.” A 108px adapted headline may preserve that relationship better than an exact font paired with a conservative 64px heading. Compare the relationship in actual captures; pixel difference and essence are separate judgements. Under F, retain the adopted principles while designing an original page. Under E, essence supplements matched fidelity rather than replacing it.

## Safe Design Detector

Inspect the proposed blueprint and later screenshots for repeated centered sections, identical max-width silhouettes, same-sized cards, rounded corners everywhere, uniform spacing, over-perfect alignment, no dominant subject, no meaningful depth/crop, repeated heading + paragraph + three cards and entirely predictable choices. Record concrete region IDs and observed repetitions.

When several cues suppress hierarchy or identity in an expressive landing page, report **SAFE_DESIGN_WARNING** with the causal problem and a structural correction. Example: “hero and three following sections have the same width and weight; turn the hero into a type-led poster, reduce the introduction, and replace the second card grid with a wide product canvas.” It is a critic finding, not a Python failure code. Symmetry, flatness or consistency alone is not a defect; do not inject overlap, larger text or irregular spacing into a restrained product UI merely to clear this warning.

The next artifact is [Art Direction](art-direction.md), not a list of CSS decorations. For a complete illustrative chain, see [the direction example](../examples/aesthetic-direction.md).
