import React, { useRef, useEffect } from "react";
import * as THREE from "three";

interface CinematicEarthProps {
  size: number;
  className?: string;
}

// ── Geographic Land Mask Constants ───────────────────────────────────────────
const GLOBE_RADIUS = 0.96;
const CANDIDATE_POINTS = 52000; // Dense, continuous continent coverage
const LAND_THRESHOLD = 60; // 0=ocean, 255=land in earth-land-mask.png
const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5)); // ~2.399963 rad

/**
 * CinematicEarth — Pure Sovereign Geographic Monochrome 3D Earth Globe
 *
 * Visual Rules:
 * - Pure Black Background (#000000)
 * - LAND = 100% Pure White Crisp Dots (#ffffff) tracing actual continents & coastlines
 * - Zero Color Tint — No blue, cyan, or green tint
 * - OCEANS = Completely empty (no dots)
 * - Zero Geolocation / Zero Location Prompts (Never asks browser for location)
 * - Interactive pointer drag with smooth inertia damping & subtle auto-spin
 */
export const CinematicEarth: React.FC<CinematicEarthProps> = ({
  size,
  className = "",
}) => {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount || size <= 0) return;

    // ── WebGL Capability Check ────────────────────────────────────────────────
    const testCanvas = document.createElement("canvas");
    const gl =
      testCanvas.getContext("webgl2") ||
      testCanvas.getContext("webgl") ||
      testCanvas.getContext("experimental-webgl");
    if (!gl) {
      canvas2DFallback(mount, size);
      return;
    }

    // ── Three.js Renderer ─────────────────────────────────────────────────────
    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      powerPreference: "high-performance",
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(size, size);
    renderer.setClearColor(0x000000, 0);

    const canvas = renderer.domElement;
    canvas.style.display = "block";
    canvas.style.width = `${size}px`;
    canvas.style.height = `${size}px`;
    canvas.style.cursor = "grab";
    canvas.style.userSelect = "none";
    canvas.style.touchAction = "none";
    mount.appendChild(canvas);

    // ── Scene & Camera ────────────────────────────────────────────────────────
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
    camera.position.set(0, 0, 3.0);

    // ── Root Earth Group (Rotates during spin & drag) ─────────────────────────
    const earthGroup = new THREE.Group();
    earthGroup.rotation.x = 0.22; // Natural ~12.6° axial tilt
    earthGroup.rotation.y = -(78.9629 * Math.PI) / 180; // Start facing India (~78.96° E, Indian Subcontinent)
    scene.add(earthGroup);

    // ── 1. Inner Pure Black Sphere (Opaque body) ───────────────────────────────
    const innerSphereGeo = new THREE.SphereGeometry(GLOBE_RADIUS * 0.995, 48, 48);
    const innerSphereMat = new THREE.MeshBasicMaterial({
      color: 0x000000,
      depthWrite: true,
    });
    const innerSphere = new THREE.Mesh(innerSphereGeo, innerSphereMat);
    earthGroup.add(innerSphere);

    // ── 2. Pure White Land Dots Buffer Geometry ───────────────────────────────
    const dotGeo = new THREE.BufferGeometry();
    const dotMat = new THREE.PointsMaterial({
      size: 0.016,
      vertexColors: true,
      transparent: true,
      opacity: 0.95,
      sizeAttenuation: true,
      depthWrite: false,
    });
    const landPointsMesh = new THREE.Points(dotGeo, dotMat);
    earthGroup.add(landPointsMesh);

    // ── Fibonacci Sphere Land Sampling (Pure White) ───────────────────────────
    const generateFromLandMask = (
      maskData: Uint8ClampedArray,
      maskW: number,
      maskH: number
    ) => {
      const positions: number[] = [];
      const colors: number[] = [];

      for (let i = 0; i < CANDIDATE_POINTS; i++) {
        const y = 1 - (i / (CANDIDATE_POINTS - 1)) * 2; // -1 to +1
        const radiusAtY = Math.sqrt(Math.max(0, 1 - y * y));
        const theta = GOLDEN_ANGLE * i;

        const x = Math.cos(theta) * radiusAtY;
        const z = Math.sin(theta) * radiusAtY;

        // Spherical -> Equirectangular Coordinates
        const lat = Math.asin(Math.max(-1, Math.min(1, y))) * (180 / Math.PI);
        const lon = Math.atan2(x, z) * (180 / Math.PI);

        // Map lat/lon to texture pixel (u: 0..1, v: 0..1)
        const u = (lon + 180) / 360;
        const v = (90 - lat) / 180;

        const px = Math.min(maskW - 1, Math.max(0, Math.floor(u * maskW)));
        const py = Math.min(maskH - 1, Math.max(0, Math.floor(v * maskH)));
        const pixelIdx = (py * maskW + px) * 4;

        // Sample Red channel of high-contrast land mask
        const brightness = maskData[pixelIdx];

        if (brightness > LAND_THRESHOLD) {
          positions.push(x * GLOBE_RADIUS, y * GLOBE_RADIUS, z * GLOBE_RADIUS);
          // Pure White (1.0, 1.0, 1.0) — Zero Color Tint
          colors.push(1.0, 1.0, 1.0);
        }
      }

      dotGeo.setAttribute(
        "position",
        new THREE.Float32BufferAttribute(positions, 3)
      );
      dotGeo.setAttribute(
        "color",
        new THREE.Float32BufferAttribute(colors, 3)
      );
      dotGeo.computeBoundingSphere();
    };

    // Load High-Contrast Land Mask
    const maskImg = new Image();
    maskImg.crossOrigin = "anonymous";
    maskImg.src = "/earth-land-mask.png";

    maskImg.onload = () => {
      try {
        const offscreen = document.createElement("canvas");
        const w = maskImg.naturalWidth || 2048;
        const h = maskImg.naturalHeight || 1024;
        offscreen.width = w;
        offscreen.height = h;
        const ctx = offscreen.getContext("2d", { willReadFrequently: true });
        if (ctx) {
          ctx.drawImage(maskImg, 0, 0, w, h);
          const raw = ctx.getImageData(0, 0, w, h).data;
          generateFromLandMask(raw, w, h);
        }
      } catch (err) {
        console.warn("[CinematicEarth] Local land mask sample fallback active:", err);
      }
    };

    maskImg.onerror = () => {
      console.warn("[CinematicEarth] /earth-land-mask.png not found, mathematical model active");
    };

    // ── Pointer Drag & Auto-Rotation ──────────────────────────────────────────
    const AUTO_SPIN_SPEED = 0.0009;
    const DRAG_FACTOR = 0.005;
    const DAMPING = 0.92;
    const MAX_PITCH = Math.PI / 2.2;

    let isDragging = false;
    let dragStartX = 0;
    let dragStartY = 0;
    let lastMouseX = 0;
    let lastMouseY = 0;
    let velocityX = 0;
    let velocityY = 0;

    const onPointerDown = (e: PointerEvent) => {
      isDragging = true;
      dragStartX = e.clientX;
      dragStartY = e.clientY;
      lastMouseX = e.clientX;
      lastMouseY = e.clientY;
      velocityX = 0;
      velocityY = 0;
      canvas.style.cursor = "grabbing";
      try {
        canvas.setPointerCapture(e.pointerId);
      } catch {
        /* Ignore */
      }
    };

    const onPointerMove = (e: PointerEvent) => {
      if (!isDragging) return;
      const dx = e.clientX - lastMouseX;
      const dy = e.clientY - lastMouseY;

      earthGroup.rotation.y += dx * DRAG_FACTOR;
      earthGroup.rotation.x = Math.max(
        -MAX_PITCH,
        Math.min(MAX_PITCH, earthGroup.rotation.x + dy * DRAG_FACTOR)
      );

      velocityX = dx * 0.003;
      velocityY = dy * 0.003;
      lastMouseX = e.clientX;
      lastMouseY = e.clientY;
    };

    const onPointerUp = (e: PointerEvent) => {
      isDragging = false;
      canvas.style.cursor = "grab";
      try {
        canvas.releasePointerCapture(e.pointerId);
      } catch {
        /* Ignore */
      }
    };

    canvas.addEventListener("pointerdown", onPointerDown);
    canvas.addEventListener("pointermove", onPointerMove);
    canvas.addEventListener("pointerup", onPointerUp);
    canvas.addEventListener("pointercancel", onPointerUp);

    // ── Animation Loop ────────────────────────────────────────────────────────
    let animationId = 0;
    let isRunning = true;

    const animate = () => {
      if (!isRunning) return;
      animationId = requestAnimationFrame(animate);

      if (!isDragging) {
        velocityX *= DAMPING;
        velocityY *= DAMPING;
        earthGroup.rotation.y += velocityX + AUTO_SPIN_SPEED;
        earthGroup.rotation.x = Math.max(
          -MAX_PITCH,
          Math.min(MAX_PITCH, earthGroup.rotation.x + velocityY)
        );
      }

      renderer.render(scene, camera);
    };

    const onVisibilityChange = () => {
      if (document.hidden) {
        isRunning = false;
        cancelAnimationFrame(animationId);
      } else {
        isRunning = true;
        animate();
      }
    };

    document.addEventListener("visibilitychange", onVisibilityChange);
    animate();

    // ── Cleanup ───────────────────────────────────────────────────────────────
    return () => {
      isRunning = false;
      cancelAnimationFrame(animationId);
      document.removeEventListener("visibilitychange", onVisibilityChange);

      canvas.removeEventListener("pointerdown", onPointerDown);
      canvas.removeEventListener("pointermove", onPointerMove);
      canvas.removeEventListener("pointerup", onPointerUp);
      canvas.removeEventListener("pointercancel", onPointerUp);

      innerSphereGeo.dispose();
      innerSphereMat.dispose();
      dotGeo.dispose();
      dotMat.dispose();
      renderer.dispose();

      if (mount.contains(canvas)) {
        mount.removeChild(canvas);
      }
    };
  }, [size]);

  return (
    <div
      ref={mountRef}
      className={className}
      style={{
        width: size,
        height: size,
        overflow: "visible",
        flexShrink: 0,
        position: "relative",
      }}
      aria-label="Interactive 3D Sovereign Earth Globe (Monochrome White)"
    />
  );
};

// ── 2D Canvas Fallback (Monochrome White) ─────────────────────────────────────
function canvas2DFallback(mount: HTMLDivElement, size: number): void {
  const canvas = document.createElement("canvas");
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  canvas.width = size * dpr;
  canvas.height = size * dpr;
  canvas.style.width = `${size}px`;
  canvas.style.height = `${size}px`;
  mount.appendChild(canvas);

  const ctx = canvas.getContext("2d");
  if (!ctx) return;
  ctx.scale(dpr, dpr);

  const cx = size / 2;
  const cy = size / 2;
  const rSphere = size * 0.45;

  ctx.beginPath();
  ctx.arc(cx, cy, rSphere, 0, Math.PI * 2);
  ctx.fillStyle = "#000000";
  ctx.fill();

  const sampleLand: [number, number][] = [
    [0.32, 0.3], [0.35, 0.28], [0.3, 0.35], [0.34, 0.42], // North America
    [0.4, 0.58], [0.42, 0.65], [0.43, 0.72], // South America
    [0.52, 0.28], [0.55, 0.32], [0.58, 0.3], // Europe
    [0.53, 0.48], [0.56, 0.55], [0.54, 0.62], // Africa
    [0.65, 0.35], [0.72, 0.32], [0.78, 0.38], // Asia
    [0.68, 0.45], [0.7, 0.48], // India & SE Asia
    [0.76, 0.65], [0.8, 0.68], // Australia
  ];

  ctx.fillStyle = "#ffffff";
  for (const [px, py] of sampleLand) {
    const x = cx + (px - 0.5) * rSphere * 1.8;
    const y = cy + (py - 0.5) * rSphere * 1.8;
    ctx.beginPath();
    ctx.arc(x, y, Math.max(1.5, size / 160), 0, Math.PI * 2);
    ctx.fill();
  }
}
