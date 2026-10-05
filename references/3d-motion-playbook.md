# 3D and Motion Playbook

Use this reference when a page needs a product model, landscape scene, shader, scroll choreography or pointer interaction.

## Source roles

| Source | Use it for | Evidence boundary |
| --- | --- | --- |
| ThreeUI | Ready-to-adapt Three.js heroes, shaders, 3D assets, buttons and source patterns | Public pages show catalog and rendered examples. MCP templates/source require the site's eligible Pro access. |
| Three.js examples | Canonical implementation details for loaders, materials, postprocessing, controls and performance | Use the example and docs for API behavior; do not treat a gallery screenshot as a product requirement. |
| Spline Library / Community | Editable scenes, camera, materials and interaction ideas | Check each asset's license and export path before embedding. |
| Codrops | Experimental interaction patterns, shaders, transitions and art direction | Treat demos as interaction references; rebuild the relationship in the project's stack. |
| Awwwards / SiteInspire / Land-book | Whole-page rhythm, scroll pacing, navigation and section transitions | Use as composition references, not as proof of implementation behavior. |
| GSAP / Motion / Theatre.js | Animation timing, scroll state and controlled choreography | Preserve reduced-motion and avoid adding motion only because a demo has it. |

## Choose the 3D implementation

- **CSS 3D**: one product image or card, small depth shift, no mesh or camera needs. Best fallback and easiest mobile path.
- **Three.js / React Three Fiber**: a real model, camera, material or shader is central to the product story. Keep one scene, one camera and one focal interaction.
- **Spline**: a designer-editable scene is needed and the current environment exposes an authorized Spline MCP or embed/export path. Record the scene ID, export method and fallback screenshot.
- **ThreeUI adaptation**: use a public example to reproduce a pattern; use MCP/source only when the runtime confirms access. Never claim a ThreeUI template was integrated when only its screenshot was observed.

## Scene contract

Before coding, write:

```yaml
scene_goal: "what the 3D element explains"
subject: "one product, landscape or object"
camera: "static / orbit / scroll-controlled"
materials: "matte / glass / metal / paper / water"
interaction: "one bounded pointer, touch or scroll response"
performance_budget: "target fps, asset size, device fallback"
mobile_fallback: "static image / CSS silhouette / simplified scene"
reduced_motion: "final state with no continuous motion"
asset_license: "source, author, license, export path"
```

## Motion rules

1. Give the 3D element a job: orientation, material explanation, spatial story or product comparison.
2. Use one focal response per scene. Do not combine continuous rotation, particles, cursor trails and pinned scroll by default.
3. Animate `transform`, camera position or shader uniforms within bounded ranges; do not move layout-critical text with JavaScript.
4. Load models lazily after the first meaningful paint and show a stable poster or CSS fallback while loading.
5. Respect `prefers-reduced-motion`; show the final camera/material state and keep controls usable by keyboard or touch.
6. Test at mobile width, reduced motion and a slow device profile before accepting the effect.

## Review checklist

Record `scene goal`, `asset source`, `observed interaction`, `implementation`, `fallback`, `mobile result`, `reduced-motion result`, `load cost` and `license status`. Score the effect on clarity, material quality, hierarchy, restraint, performance and fallback quality. A technically impressive scene fails the review when it competes with the page's main message.
