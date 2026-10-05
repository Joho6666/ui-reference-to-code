import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { useTexture } from '@react-three/drei';
import { Suspense, useEffect, useMemo, useRef } from 'react';
import * as THREE from 'three';
import { theme } from '../theme';
import { cities } from '../data/cities';

const reduced = typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const DEG = Math.PI / 180;
const TILT = 56 * DEG; // where the active city sits on the visible cap (0 = facing camera, 90 = at the top)

/** Same parametrisation as THREE.SphereGeometry, so markers line up with the equirectangular textures. */
function surfacePoint(lat: number, lon: number, r = 1) {
  const la = lat * DEG, lo = lon * DEG;
  return new THREE.Vector3(r * Math.cos(la) * Math.cos(lo), r * Math.sin(la), -r * Math.cos(la) * Math.sin(lo));
}

/** Rotation that brings (lat, lon) to elevation TILT above the camera axis, north up. */
function focusQuaternion(lat: number, lon: number) {
  return new THREE.Quaternion().setFromEuler(new THREE.Euler(lat * DEG - TILT, -Math.PI / 2 - lon * DEG, 0, 'XYZ'));
}

const globeVertex = /* glsl */ `
  varying vec2 vUv; varying vec3 vN; varying vec3 vV;
  void main() {
    vUv = uv;
    vN = normalize(mat3(modelMatrix) * normal);
    vec4 wp = modelMatrix * vec4(position, 1.0);
    vV = normalize(cameraPosition - wp.xyz);
    gl_Position = projectionMatrix * viewMatrix * wp;
  }`;

const globeFragment = /* glsl */ `
  uniform sampler2D uDay; uniform sampler2D uNight; uniform sampler2D uSpec;
  uniform vec3 uSun; uniform vec3 uGlow; uniform vec3 uCity;
  varying vec2 vUv; varying vec3 vN; varying vec3 vV;
  void main() {
    vec3 n = normalize(vN);
    vec3 day = texture2D(uDay, vUv).rgb;
    vec3 lights = texture2D(uNight, vUv).rgb;
    float spec = texture2D(uSpec, vUv).r;
    float ndl = dot(n, normalize(uSun));
    float dayMix = smoothstep(-0.12, 0.5, ndl);

    // night side: deep blue base + warm city lights, boosted so US metros read as constellations
    vec3 nightCol = day * vec3(0.012, 0.028, 0.07) + lights * uCity * 2.6 + pow(lights, vec3(2.0)) * 1.4;
    // day side: lit terrain + ocean sun glint
    vec3 refl = reflect(-normalize(uSun), n);
    float glint = pow(max(dot(refl, normalize(vV)), 0.0), 140.0) * spec * 0.45;
    vec3 dayCol = day * (0.12 + 1.15 * max(ndl, 0.0)) + glint * vec3(0.7, 0.85, 1.0);
    vec3 col = mix(nightCol, dayCol, dayMix);

    // fresnel rim: the blue atmospheric edge from the reference, present on both sides
    float f = pow(1.0 - max(dot(n, normalize(vV)), 0.0), 4.5);
    col += uGlow * f * (0.35 + 0.9 * dayMix);
    gl_FragColor = vec4(col, 1.0);
    #include <colorspace_fragment>
  }`;

const atmoVertex = /* glsl */ `
  varying vec3 vNormal;
  void main() { vNormal = normalize(normalMatrix * normal); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`;

// Back-faced shell: glow is strongest at the globe's silhouette and fades to nothing at the shell's edge.
const atmoFragment = /* glsl */ `
  uniform vec3 uGlow; varying vec3 vNormal;
  void main() {
    float d = max(-dot(vNormal, vec3(0.0, 0.0, 1.0)), 0.0);
    float g = pow(smoothstep(0.0, 0.5, d), 2.2);
    gl_FragColor = vec4(uGlow * g * 1.15, g);
    #include <colorspace_fragment>
  }`;

function Marker({ lat, lon, active }: { lat: number; lon: number; active: boolean }) {
  const ring = useRef<THREE.Mesh>(null);
  const core = useRef<THREE.Mesh>(null);
  const pos = useMemo(() => surfacePoint(lat, lon, 1.004), [lat, lon]);
  const quat = useMemo(() => {
    const o = new THREE.Object3D();
    o.position.copy(pos);
    o.lookAt(pos.clone().multiplyScalar(2)); // +z of the disc faces outward
    return o.quaternion.clone();
  }, [pos]);
  useFrame((s) => {
    const t = s.clock.elapsedTime;
    if (core.current) core.current.scale.setScalar(THREE.MathUtils.damp(core.current.scale.x, active ? 1.9 : 0.8, 6, 0.016));
    if (ring.current) {
      const m = ring.current.material as THREE.MeshBasicMaterial;
      if (!active) { m.opacity = 0; return; }
      const k = reduced ? 0.5 : (t * 0.7) % 1;
      ring.current.scale.setScalar(1 + k * 5);
      m.opacity = (1 - k) * 0.85;
    }
  });
  return (
    <group position={pos} quaternion={quat}>
      <mesh ref={core}>
        <circleGeometry args={[0.0075, 24]} />
        <meshBasicMaterial color="#fff2d6" toneMapped={false} />
      </mesh>
      <mesh>
        <circleGeometry args={[0.022, 24]} />
        <meshBasicMaterial color={theme.colors.city} transparent opacity={active ? 0.55 : 0.28} blending={THREE.AdditiveBlending} depthWrite={false} toneMapped={false} />
      </mesh>
      <mesh ref={ring}>
        <ringGeometry args={[0.02, 0.0215, 48]} />
        <meshBasicMaterial color={theme.colors.city} transparent opacity={0} blending={THREE.AdditiveBlending} depthWrite={false} toneMapped={false} />
      </mesh>
    </group>
  );
}

function Stars() {
  const geo = useMemo(() => {
    const n = 1400;
    const p = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) {
      const u = Math.random() * 2 - 1, a = Math.random() * Math.PI * 2, r = 40 + Math.random() * 20;
      const s = Math.sqrt(1 - u * u);
      p.set([r * s * Math.cos(a), r * u, -Math.abs(r * s * Math.sin(a)) - 5], i * 3);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(p, 3));
    return g;
  }, []);
  return (
    <points geometry={geo}>
      <pointsMaterial color="#cfe0ff" size={0.12} sizeAttenuation transparent opacity={0.75} depthWrite={false} />
    </points>
  );
}

function Globe({ active, onReady }: { active: number; onReady?: () => void }) {
  const { viewport, gl } = useThree();
  const [day, night, spec, clouds] = useTexture([
    '/textures/earth_day_4096.jpg',
    '/textures/earth_night_4096.jpg',
    '/textures/earth_specular_2048.jpg',
    '/textures/earth_clouds_1024.png',
  ]);
  useMemo(() => {
    for (const t of [day, night, spec, clouds]) {
      t.colorSpace = THREE.SRGBColorSpace;
      t.anisotropy = Math.min(8, gl.capabilities.getMaxAnisotropy());
    }
    spec.colorSpace = THREE.NoColorSpace;
  }, [day, night, spec, clouds, gl]);

  const spin = useRef<THREE.Group>(null);
  const cloudsRef = useRef<THREE.Mesh>(null);
  const target = useMemo(() => focusQuaternion(cities[active].lat, cities[active].lon), [active]);
  const uniforms = useMemo(
    () => ({
      uDay: { value: day }, uNight: { value: night }, uSpec: { value: spec },
      uSun: { value: new THREE.Vector3(-0.8, 0.35, -0.45) },
      uGlow: { value: new THREE.Color(theme.colors.glow) },
      uCity: { value: new THREE.Color(theme.colors.city) },
    }),
    [day, night, spec],
  );
  const atmo = useMemo(() => ({ uGlow: { value: new THREE.Color('#4aa3ff') } }), []);

  useEffect(() => { gl.domElement.dataset.ready = 'true'; onReady?.(); }, [onReady, gl]);
  useEffect(() => { if (reduced && spin.current) spin.current.quaternion.copy(target); }, [target]);

  useFrame((state, dt) => {
    const g = spin.current;
    if (!g) return;
    if (!reduced) g.quaternion.slerp(target, 1 - Math.exp(-2.6 * dt));
    if (cloudsRef.current && !reduced) cloudsRef.current.rotation.y += dt * 0.004;
    // one bounded pointer response: the whole planet leans a few degrees toward the cursor
    if (!reduced) {
      g.parent!.rotation.y = THREE.MathUtils.damp(g.parent!.rotation.y, state.pointer.x * 0.06, 3, dt);
      g.parent!.rotation.x = THREE.MathUtils.damp(g.parent!.rotation.x, -state.pointer.y * 0.04, 3, dt);
    }
  });

  // stage: the planet rises from the bottom edge like the reference (about 30% of the height is visible)
  const mobile = viewport.width < viewport.height * 0.8;
  const r = mobile ? viewport.width * 0.78 : Math.min(viewport.width * 0.4, viewport.height * 0.95);
  const visible = mobile ? 0.44 : 0.32;
  const y = -viewport.height / 2 + viewport.height * visible - r;

  return (
    <>
      <Stars />
      <group position={[0, y, 0]} scale={r}>
        <group>
          <group ref={spin}>
            <mesh>
              <sphereGeometry args={[1, 128, 128]} />
              <shaderMaterial vertexShader={globeVertex} fragmentShader={globeFragment} uniforms={uniforms} />
            </mesh>
            <mesh ref={cloudsRef}>
              <sphereGeometry args={[1.012, 96, 96]} />
              <meshBasicMaterial map={clouds} alphaMap={clouds} transparent opacity={0.32} depthWrite={false} color="#cfe3ff" />
            </mesh>
            {cities.map((c, i) => <Marker key={c.id} lat={c.lat} lon={c.lon} active={i === active} />)}
          </group>
        </group>
        <mesh scale={1.16}>
          <sphereGeometry args={[1, 96, 96]} />
          <shaderMaterial vertexShader={atmoVertex} fragmentShader={atmoFragment} uniforms={atmo} side={THREE.BackSide} transparent blending={THREE.AdditiveBlending} depthWrite={false} />
        </mesh>
      </group>
    </>
  );
}

export default function HeroScene({ active, onReady }: { active: number; onReady?: () => void }) {
  return (
    <Canvas
      dpr={[1, 2]}
      camera={{ position: [0, 0, 6], fov: 32 }}
      gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}
      frameloop={reduced ? 'demand' : 'always'}
      onCreated={({ gl }) => { gl.setClearColor(0x000000, 0); }}
    >
      <Suspense fallback={null}>
        <Globe active={active} onReady={onReady} />
      </Suspense>
    </Canvas>
  );
}
