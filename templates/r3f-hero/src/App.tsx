import { Suspense, lazy, useEffect, useState } from 'react';
import { theme } from './theme';

const HeroScene = lazy(() => import('./scene/HeroScene'));

function webglAvailable() {
  try {
    const c = document.createElement('canvas');
    return !!(c.getContext('webgl2') || c.getContext('webgl'));
  } catch {
    return false;
  }
}

export function App() {
  const { colors, fonts, copy, hero, assets } = theme;
  const [gl, setGl] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const r = document.documentElement.style;
    r.setProperty('--surface', colors.surface);
    r.setProperty('--ink', colors.ink);
    r.setProperty('--muted', colors.muted);
    r.setProperty('--accent', colors.accent);
    r.setProperty('--accent-2', colors.accent2);
    r.setProperty('--font-display', fonts.display);
    r.setProperty('--font-body', fonts.body);
    r.setProperty('--glow-x', hero.subjectSide === 'left' ? '-60%' : hero.subjectSide === 'center' ? '0%' : '30%');
    // lazy: mount WebGL only after first meaningful paint
    const t = requestAnimationFrame(() => setGl(webglAvailable()));
    return () => cancelAnimationFrame(t);
  }, []);

  return (
    <>
      <div className="grain" aria-hidden />
      <header className="nav">
        <span className="brand">{copy.brand}</span>
        <ul>{copy.nav.map((n) => <li key={n}><a href="#">{n}</a></li>)}</ul>
        <a className="pill" href="#">{copy.cta}</a>
      </header>

      <section className={`hero${ready ? ' gl-ready' : ''}`} id="hero" data-region="hero">
        {assets.heroImage && <img className="bgimg" src={assets.heroImage} alt="" aria-hidden />}
        <div className="fallback" aria-hidden />
        {gl && (
          <div className="scene" aria-hidden>
            <Suspense fallback={null}><HeroScene onReady={() => setReady(true)} /></Suspense>
          </div>
        )}
        <div className="copy" data-region="hero-copy">
          <p className="eyebrow">{copy.eyebrow}</p>
          <h1>{copy.headline.map((l, i) => <span key={l} style={{ display: 'block' }}>{i === copy.headline.length - 1 ? <em>{l}</em> : l}</span>)}</h1>
          <p className="sub">{copy.sub}</p>
          <div className="actions">
            <a className="btn" data-cta href="#">{copy.cta} →</a>
            <a className="btn ghost" href="#">{copy.ctaSecondary}</a>
          </div>
        </div>
      </section>

      <section className="marquee" data-region="first-transition" aria-label="Capabilities">
        <div className="marquee-track">
          {[...copy.marquee, ...copy.marquee].map((m, i) => <span key={i}>{m}</span>)}
        </div>
      </section>
    </>
  );
}
