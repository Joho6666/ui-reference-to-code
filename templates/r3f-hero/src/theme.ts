// The ONLY file a replica normally has to edit for a first pass.
// Fill it from the Replica Card (.ui-design/replica-card.md): every value maps to a card field.
export type SceneVariant = 'glass-knot' | 'liquid-blob' | 'orbit-cards';

export const theme = {
  // color_roles
  colors: {
    surface: '#0b0b0f',
    ink: '#f4f1ea',
    muted: '#8d8a84',
    accent: '#ff5b2e',
    accent2: '#7a5cff',
  },
  // type_hierarchy — fonts are bundled via @fontsource in main.tsx (works offline / behind firewalls); swap per reference
  fonts: {
    display: '"Instrument Serif", "Playfair Display", Georgia, serif',
    body: '"Inter Variable", "Inter", system-ui, sans-serif',
  },
  // hero_silhouette: where the 3D subject sits (percent of hero width) and how big
  hero: {
    subjectSide: 'right' as 'left' | 'right' | 'center',
    subjectWidth: 0.55,
  },
  // scene contract
  scene: {
    variant: 'glass-knot' as SceneVariant,
    accent: '#ff5b2e',
    pointerTilt: 0.35, // radians, bounded pointer response
    autoRotate: 0.12, // 0 disables continuous motion
    dprMax: 2,
  },
  // optional generated/real hero imagery (see references/image-generation.md); '' = none. Path under /public.
  assets: { heroImage: '' },
  // authored copy — replace; never reuse the reference's brand copy
  copy: {
    brand: 'Atelier',
    nav: ['Work', 'Studio', 'Journal', 'Contact'],
    eyebrow: 'Spatial design studio — 2026',
    headline: ['Objects that', 'feel like', 'light.'],
    sub: 'Interfaces with weight, depth and a point of view.',
    cta: 'Start a project',
    ctaSecondary: 'See selected work',
    marquee: ['Identity', 'Interface', 'Motion', 'Spatial', 'Product', 'Direction'],
  },
};
