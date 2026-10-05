import { Suspense, lazy, useCallback, useEffect, useRef, useState } from 'react';
import { theme } from './theme';
import { cities } from './data/cities';

const HeroScene = lazy(() => import('./scene/HeroScene'));

function webglAvailable() {
  try {
    const c = document.createElement('canvas');
    return !!(c.getContext('webgl2') || c.getContext('webgl'));
  } catch {
    return false;
  }
}

const pad = (n: number) => String(n).padStart(2, '0');

export function App() {
  const { colors, copy } = theme;
  const [gl, setGl] = useState(false);
  const [ready, setReady] = useState(false);
  const [active, setActive] = useState(0);
  const n = cities.length;
  const go = useCallback((i: number) => setActive(((i % n) + n) % n), [n]);
  const prev = cities[(active - 1 + n) % n];
  const next = cities[(active + 1) % n];
  const city = cities[active];

  useEffect(() => {
    const r = document.documentElement.style;
    r.setProperty('--surface', colors.surface);
    r.setProperty('--surface-2', colors.surface2);
    r.setProperty('--ink', colors.ink);
    r.setProperty('--muted', colors.muted);
    r.setProperty('--accent', colors.accent);
    r.setProperty('--glow', colors.glow);
    r.setProperty('--city', colors.city);
    r.setProperty('--pill', colors.pill);
    // mount WebGL after the first paint; a timer (not rAF) so background/headless tabs still mount it
    const t = window.setTimeout(() => setGl(webglAvailable()), 30);
    return () => window.clearTimeout(t);
  }, []);

  useEffect(() => {
    const key = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight') go(active + 1);
      if (e.key === 'ArrowLeft') go(active - 1);
    };
    window.addEventListener('keydown', key);
    return () => window.removeEventListener('keydown', key);
  }, [active, go]);

  // horizontal swipe on touch devices
  const start = useRef<number | null>(null);

  return (
    <>
      <div className="grain" aria-hidden />
      <header className="nav">
        <span className="brand">{copy.brand}</span>
        <nav aria-label="Primary">
          <ul>{copy.nav.map((l, i) => <li key={l}><a href="#" className={i === 0 ? 'on' : ''}>{l}</a></li>)}</ul>
        </nav>
        <a className="pill" href="#">{copy.navCta}</a>
      </header>

      <section
        className={`hero${ready ? ' gl-ready' : ''}`}
        id="hero"
        data-region="hero"
        onTouchStart={(e) => { start.current = e.touches[0].clientX; }}
        onTouchEnd={(e) => {
          if (start.current == null) return;
          const dx = e.changedTouches[0].clientX - start.current;
          if (Math.abs(dx) > 50) go(active + (dx < 0 ? 1 : -1));
          start.current = null;
        }}
      >
        <div className="fallback" aria-hidden />
        {gl && (
          <div className="scene" aria-hidden data-region="globe">
            <Suspense fallback={null}><HeroScene active={active} onReady={() => setReady(true)} /></Suspense>
          </div>
        )}

        <div className="copy" data-region="hero-copy" aria-live="polite">
          <p className="eyebrow">{copy.eyebrow} <i /> {pad(active + 1)} / {pad(n)}</p>
          <h1 key={city.id} style={{ ['--len' as string]: city.name.length }}><span>{city.name}</span></h1>
          <span className="rule" aria-hidden />
          <p className="sub" key={city.id + 's'}>{city.line}</p>
          <dl className="facts" key={city.id + 'f'}>
            <div><dt>State</dt><dd>{city.state}</dd></div>
            <div><dt>Population</dt><dd>~{city.pop}</dd></div>
            <div><dt>Time zone</dt><dd>{city.tz}</dd></div>
            <div><dt>Coordinates</dt><dd>{Math.abs(city.lat).toFixed(1)}°N {Math.abs(city.lon).toFixed(1)}°W</dd></div>
          </dl>
          <a className="btn" data-cta href="#">{copy.cta}</a>
        </div>

        <div className="side left" data-region="city-prev">
          <button onClick={() => go(active - 1)} aria-label={`Previous city: ${prev.name}`}>
            <span className="orb" aria-hidden />
            <span className="label">{prev.name}</span>
          </button>
        </div>
        <div className="side right" data-region="city-next">
          <button onClick={() => go(active + 1)} aria-label={`Next city: ${next.name}`}>
            <span className="label">{next.name}</span>
            <span className="orb" aria-hidden />
          </button>
        </div>

        <ol className="pips" aria-label="Cities">
          {cities.map((c, i) => (
            <li key={c.id}>
              <button className={i === active ? 'on' : ''} onClick={() => go(i)} aria-label={c.name} aria-current={i === active} />
            </li>
          ))}
        </ol>
      </section>
    </>
  );
}
