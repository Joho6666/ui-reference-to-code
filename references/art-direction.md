# Art direction — composition, type, materials and rhythm

Input: scoped brief, selected references, Visual Thesis and Aesthetic DNA. Output: a concise direction and region blueprint before tokens/components. Use one `.ui-design/art-direction.md` when the task needs persistence; a local change can record only its delta. This is flexible design reasoning, not a new machine schema.

## Direction record

Record Visual Thesis, Primary Visual, Composition Strategy, Typography Strategy, Imagery Strategy, Color Strategy, Depth Strategy, Motion Strategy, Section Rhythm, Signature Moment and Anti-Patterns. Link each important choice to a reference observation or brief requirement. State unknowns and alternatives that would materially change the result; resolve routine choices yourself unless the user requested selection first.

Anti-Patterns are specific to this task: for example, repeated equal rounded feature grids, an unsupported blue/purple glow, glass everywhere, centered text in every section, a generic orb or meaningless mesh gradients. These effects are not universally banned; use them when the direction and audience justify them. State what replaces a rejected pattern. Avoid prescribing one fashionable style to every brief.

## Composition Director

Decide visual weight before the component tree. For the hero and each key section, write:

```text
region_id / purpose / reading order
composition silhouette and visual center
dominant element / secondary element / subordinate detail
alignment and weight distribution
negative space / density
visual tension: offset, overlap, crop, bleed or deliberately none
depth: background, middle, foreground, optional floating layer
desktop relationship → mobile recomposition
reference essence preserved / deliberate adaptation
```

Draw a small sketch when relationships are unclear. A grid break should frame the content, not hide CTA text or create accidental document overflow. Clip decorative crops within their own region; preserve semantic reading order, focus rings and touch targets. A foreground object can interrupt a background plane while controls remain stable. Flat design can be intentional; inventing four decorative layers is not an obligation.

## Typography Director

Choose the display voice and body voice, then describe their relationship: grotesk/serif tension, condensed display/neutral prose, humanist UI/technical metadata or another reasoned pairing. Record headline width and desired line breaks, scale ratio to metadata and body, tracking, uppercase strategy, paragraph measure, labels, numerals and micro typography. Short headings can be architectural; long text requires a different measure. Use font size as a means to a relationship, not a universal 64/18/16 recipe.

Verify licensed font availability, actual glyphs, variable axes and fallback metrics before relying on them. For Chinese and multilingual content, inspect punctuation, CJK/Latin pairing and actual wrapping; an uppercase Latin reference does not translate directly to Chinese. Extreme contrast can use small nonessential metadata, but preserve readable essential text and accessible zoom/reflow. Specify desktop and phone line breaks independently; `clamp()` alone does not establish good phone composition.

## Visual Material Director

Determine whether the direction needs an asset with visual weight. A reference led by a person, product photograph, 3D object, complete UI canvas or cinematic video loses its main principle if replaced by a generic circle or gradient. Diagnose **dominant visual missing** before adjusting margins.

Use supplied real assets, authentic project captures, permitted imagery, original generated visuals, illustration, SVG, CSS graphics, 3D or video according to the thesis. SVG/CSS is appropriate when the subject is genuinely graphical; it is not a stand-in for required photography. Define focal point, lighting/material, background relationship, visible scale, aspect ratio and crop for desktop and mobile. A screenshot belongs in an intentional frame with enough detail to understand it, not as a tiny unreadable tile. Track provenance with [research and assets](research-and-assets.md).

Plan a usable asset early in the hero prototype. If the required asset is unavailable, use an explicit provisional alternative, describe the lost essence and leave the imagery/hero review pending where that loss matters. Do not call a placeholder complete. Lazy-load secondary material, bound hero payload, reserve dimensions and provide static/reduced-motion fallbacks where relevant.

## Section Rhythm Director

Before expanding the page, assign each real section a distinct visual job and its transition to the next. An illustrative sequence is Hero LOUD → Intro QUIET → Product DENSE → Statement LOUD → System TECHNICAL → Cases EDITORIAL → CTA QUIET. Labels describe relationships, not mandatory sections or a prescribed sequence. A two-section page needs less notation; product structure and real content decide the section count.

For each section, record weight, density, silhouette, type/imagery role, spacing before/after and mobile treatment. If five successive sections all use title + paragraph + three cards, change the information presentation: a full-width canvas, compact index, editorial feature, process strip or typographic statement when the content supports it. Do not remove real information to manufacture whitespace or vary layouts randomly.

Important landing pages need one **Signature Moment**: an oversized typographic statement, product workspace, photograph, purposeful graph, gallery, 3D scene or another subject tied to the product. State which screen should survive in memory and why. A distinctive static composition is sufficient; a signature does not require animation or 3D.

## Hero First

Implement Nav + Hero + First Transition at the real target widths, including the main asset and authentic essential copy. Capture and inspect both desktop and phone using the existing [browser contract](browser-validation.md), then run [Hero Aesthetic Review](aesthetic-review.md#hero-gate). Use its concrete defects to revise the prototype before duplicating decisions across the page. Do not run the full-page engineering gate on incomplete downstream sections and call the whole site verified.

For a scoped UI repair or dense functional application, prototype the affected region instead of rebuilding the landing page. For E, preserve the supplied geometry and character; critique does not authorize redesign. After the hero decision, reuse its direction while allowing later sections their own rhythm.
