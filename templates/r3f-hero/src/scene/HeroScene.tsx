import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Environment, MeshTransmissionMaterial, MeshDistortMaterial, Float, Lightformer } from '@react-three/drei';
import { useMemo, useRef } from 'react';
import * as THREE from 'three';
import { theme } from '../theme';

const reduced = typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const isMobile = typeof window !== 'undefined' && window.innerWidth < 760;

type Rig = React.RefObject<THREE.Group | null>;

/** One bounded pointer response + slow idle drift, shared by every variant. */
function useRig(group: Rig) {
  useFrame((state, dt) => {
    const g = group.current;
    if (!g) return;
    const { pointerTilt, autoRotate } = theme.scene;
    const tx = reduced ? 0 : state.pointer.y * -pointerTilt;
    const ty = reduced ? 0 : state.pointer.x * pointerTilt + state.clock.elapsedTime * autoRotate;
    g.rotation.x = THREE.MathUtils.damp(g.rotation.x, tx, 4, dt);
    g.rotation.y = THREE.MathUtils.damp(g.rotation.y, ty, 4, dt);
  });
}

/** Soft additive glows: transmission can only refract what sits behind it, and these read as ambient light (not shapes) from the front. */
function glowTexture() {
  const c = document.createElement('canvas');
  c.width = c.height = 256;
  const x = c.getContext('2d')!;
  const g = x.createRadialGradient(128, 128, 0, 128, 128, 128);
  g.addColorStop(0, 'rgba(255,255,255,1)');
  g.addColorStop(0.35, 'rgba(255,255,255,0.45)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  x.fillStyle = g;
  x.fillRect(0, 0, 256, 256);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

function GlassBackdrop() {
  const map = useMemo(glowTexture, []);
  const glow = (color: string, pos: [number, number, number], size: number) => (
    <mesh position={pos}>
      <planeGeometry args={[size, size]} />
      <meshBasicMaterial map={map} color={color} transparent depthWrite={false} blending={THREE.AdditiveBlending} toneMapped={false} />
    </mesh>
  );
  return (
    <group position={[0, 0, -2]}>
      {glow(theme.scene.accent, [-0.9, 0.7, 0], 5.5)}
      {glow('#8f7bff', [1.6, -1.0, 0.1], 5.5)}
      {glow('#ffffff', [0.2, 0.2, 0.2], 3.2)}
    </group>
  );
}

function GlassKnot() {
  const g = useRef<THREE.Group>(null);
  useRig(g);
  return (
    <group ref={g}>
      <GlassBackdrop />
      <mesh>
        <torusKnotGeometry args={[1, 0.34, isMobile ? 128 : 256, isMobile ? 24 : 48]} />
        <MeshTransmissionMaterial
          samples={isMobile ? 4 : 8}
          resolution={isMobile ? 512 : 1024}
          thickness={0.7}
          roughness={0.08}
          transmission={1}
          ior={1.35}
          chromaticAberration={0.06}
          anisotropicBlur={0.2}
          distortion={0.25}
          distortionScale={0.4}
          temporalDistortion={0.1}
          color="#ffffff"
          attenuationColor={theme.scene.accent}
          attenuationDistance={3}
          backside
        />
      </mesh>
    </group>
  );
}

function LiquidBlob() {
  const g = useRef<THREE.Group>(null);
  useRig(g);
  return (
    <group ref={g}>
      <mesh>
        <icosahedronGeometry args={[1.25, isMobile ? 24 : 48]} />
        <MeshDistortMaterial color={theme.scene.accent} distort={0.45} speed={reduced ? 0 : 1.6} roughness={0.12} metalness={0.9} envMapIntensity={1.4} />
      </mesh>
    </group>
  );
}

function OrbitCards() {
  const g = useRef<THREE.Group>(null);
  useRig(g);
  const cards = useMemo(
    () => Array.from({ length: 7 }, (_, i) => ({ a: (i / 7) * Math.PI * 2, y: ((i % 3) - 1) * 0.55, hue: i / 7 })),
    [],
  );
  return (
    <group ref={g}>
      {cards.map((c, i) => (
        <Float key={i} speed={reduced ? 0 : 1.2} rotationIntensity={0.3} floatIntensity={0.6}>
          <mesh position={[Math.cos(c.a) * 1.9, c.y, Math.sin(c.a) * 1.9]} rotation={[0, -c.a + Math.PI / 2, 0]}>
            <boxGeometry args={[1.0, 1.4, 0.04]} />
            <meshPhysicalMaterial color={new THREE.Color().setHSL(0.02 + c.hue * 0.12, 0.8, 0.55)} roughness={0.25} metalness={0.2} clearcoat={1} />
          </mesh>
        </Float>
      ))}
    </group>
  );
}

const variants = { 'glass-knot': GlassKnot, 'liquid-blob': LiquidBlob, 'orbit-cards': OrbitCards } as const;

/** Place + size the subject from the actual viewport so it never crops, whatever the aspect ratio. */
function Placement({ children }: { children: React.ReactNode }) {
  const { viewport } = useThree();
  const { subjectSide, subjectWidth } = theme.hero;
  const mobile = viewport.width < viewport.height * 0.8;
  const target = mobile ? viewport.width * 0.66 : viewport.width * subjectWidth * 0.62; // desired subject width in world units
  const scale = Math.min(target, viewport.height * 0.8) / 3.2;
  const side = subjectSide === 'right' ? 1 : subjectSide === 'left' ? -1 : 0;
  const x = mobile ? 0 : side * (viewport.width / 2 - target / 2 - viewport.width * 0.04);
  const y = mobile ? viewport.height * 0.27 : 0;
  return <group position={[x, y, 0]} scale={scale}>{children}</group>;
}

export default function HeroScene({ onReady }: { onReady?: () => void }) {
  const Subject = variants[theme.scene.variant];
  return (
    <Canvas
      dpr={[1, isMobile ? 1.5 : theme.scene.dprMax]}
      camera={{ position: [0, 0, 6.2], fov: 38 }}
      gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}
      frameloop={reduced ? 'demand' : 'always'}
      onCreated={({ gl }) => {
        gl.setClearColor(0x000000, 0);
        gl.domElement.dataset.ready = 'true';
        onReady?.();
      }}
    >
      <ambientLight intensity={0.35} />
      <Placement>
        <Subject />
      </Placement>
      <Environment resolution={256}>
        {/* studio lightformers: no external HDRI, no network, deterministic look */}
        <Lightformer form="rect" intensity={4} position={[-4, 3, 2]} scale={[6, 3, 1]} color="#ffffff" />
        <Lightformer form="rect" intensity={3} position={[4, -1, 3]} scale={[4, 6, 1]} color={theme.scene.accent} />
        <Lightformer form="ring" intensity={2} position={[0, 4, -4]} scale={5} color="#a99bff" />
      </Environment>
    </Canvas>
  );
}
