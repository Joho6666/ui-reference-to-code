# Template Replica Playbook

Use this playbook when a UI task asks for a Pinterest reference, a reusable visual template, or a close recreation of a design work.

## Replica Card

Copy this block into `.ui-design/replica-card.md` and fill it from observed evidence:

```yaml
template_name: ""
primary_url: ""
primary_role: "hero composition / editorial rhythm / product presentation"
page_type: ""
observed_viewport: "measured / estimated / unknown"
hero_silhouette: ""
grid: "container, columns, overlap, alignment"
type_hierarchy: "display, body, metadata, line breaks"
image_crop: "subject scale, focal point, crop and background"
color_roles: "surface, ink, accent, image treatment"
motion: "observed / inferred / unknown"
mobile_transformation: "reorder, stack, crop, or alternate composition"
unknowns: []
adaptation_boundary: "what is borrowed as a relationship and what becomes original"
```

## Rule extraction

Turn the card into rules that a frontend developer can implement. Good rules contain a measurable relationship and an intended effect:

| Area | Weak note | Usable rule |
| --- | --- | --- |
| Hero | Large product | Product occupies 42–48% of the desktop hero width and sits 8–12% above the text baseline. |
| Type | Editorial heading | Display heading stays within 3 lines; body copy remains below 420px wide. |
| Image | Nice photo | Subject stays on the right third with 15% breathing room and one dominant light direction. |
| Rhythm | Interesting sections | First transition changes from split hero to asymmetric image grid; no repeated three-card row. |
| Motion | Has 3D | One pointer or touch response changes depth by a small bounded amount; reduced motion shows the final state. |

Write at least five rules covering silhouette, type, image, rhythm and mobile. Mark measurements as measured or estimated. Do not invent hidden CSS values from a screenshot.

## Reference roles

- **Primary template**: owns the hero silhouette, visual hierarchy and first transition.
- **Secondary craft reference**: owns one local quality such as product photography, typography or motion.
- **Functional reference**: owns navigation, form feedback, filtering or purchase flow.

Only the primary template should influence the whole page. A Pinterest pin can guide a relationship or mood; a real website is needed to claim a working interaction.

## Replica loop

1. Capture the primary reference and inspect it before coding.
2. Build Header + Hero + First Transition in the current stack.
3. Capture the same route at desktop and mobile sizes.
4. Score each screenshot on hierarchy, composition, type, scale contrast, whitespace, density rhythm, depth, imagery, originality and signature moment.
5. Repair the two largest visual problems. Prefer changing proportions, crop, type width or section rhythm before adding decoration.
6. Capture again and record `before artifact`, `after artifact`, `observation`, `visual impact` and `repair`.
7. Expand the remaining page only after the hero gate reaches `accepted` or a documented `needs-polish` handoff.

## Pattern library entry

After a successful task, add one compact entry to `.ui-design/pattern-library.md`:

```md
## [Template name]
- Use for: [page types]
- Hero rule: [relationship]
- Transition rule: [relationship]
- Mobile rule: [recomposition]
- Tokens: [type / spacing / color / radius]
- Components: [local mappings]
- Avoid: [specific combinations that looked generic]
- Verified at: [viewport and route]
```

This library stores relationships and tested implementation choices. It does not store scraped site assets, brand copy or a promise that every future project should use the same look.
