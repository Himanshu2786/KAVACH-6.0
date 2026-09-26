import React, { useRef, useEffect, useState, useMemo } from 'react';
import * as THREE from 'three';
import { Globe, Map, RotateCcw, ZoomIn, ZoomOut, Play, Pause, MapPin } from 'lucide-react';
import { WorldEvent } from '../../types';

interface WorldMonitorGeospatialViewProps {
  events: WorldEvent[];
  selectedEventId: string | null;
  correlations: any[];
  onSelectEvent: (eventId: string) => void;
}

const GLOBE_RADIUS = 1.0;
const CANDIDATE_POINTS = 45000;
const LAND_THRESHOLD = 60;
const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));

/**
 * WorldMonitorGeospatialView — Sovereign 2D / 3D Geospatial Layer
 *
 * Rules:
 * - 100% Pure Monochrome White Land Dots & Outlines (#ffffff) on Pure Black (#000000)
 * - Zero Color Tint on the globe body
 * - Functional Threat Pins positioned accurately at (lat, lon) with severity indicators
 * - Smooth 3D raycasting, auto-spin, and 2D equirectangular projection
 */
export const WorldMonitorGeospatialView: React.FC<WorldMonitorGeospatialViewProps> = ({
  events,
  selectedEventId,
  correlations,
  onSelectEvent,
}) => {
  const [viewMode, setViewMode] = useState<'3d' | '2d'>('3d');
  const [autoRotate, setAutoRotate] = useState<boolean>(true);
  const [zoomLevel, setZoomLevel] = useState<number>(1.0);
  const [hoveredEvent, setHoveredEvent] = useState<WorldEvent | null>(null);
  const [tooltipPos, setTooltipPos] = useState<{ x: number; y: number } | null>(null);

  const mountRef = useRef<HTMLDivElement>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const earthGroupRef = useRef<THREE.Group | null>(null);
  const targetRotationRef = useRef<{ x: number; y: number } | null>(null);

  // Filter events with valid geographic coordinates
  const geoEvents = useMemo(() => {
    return events.filter(
      (e) =>
        e.location &&
        e.location.has_coordinates &&
        e.location.latitude != null &&
        e.location.longitude != null
    );
  }, [events]);

  const selectedEvent = useMemo(() => {
    return geoEvents.find((e) => e.id === selectedEventId) || null;
  }, [geoEvents, selectedEventId]);

  // Rotate 3D globe to face newly selected event
  useEffect(() => {
    if (viewMode === '3d' && selectedEvent && selectedEvent.location.latitude != null && selectedEvent.location.longitude != null) {
      const lat = selectedEvent.location.latitude;
      const lon = selectedEvent.location.longitude;
      const targetY = -(lon * Math.PI) / 180;
      const targetX = Math.max(-0.6, Math.min(0.6, (lat * Math.PI) / 180 * 0.5));
      targetRotationRef.current = { x: targetX, y: targetY };
    }
  }, [selectedEvent, viewMode]);

  // ── 3D THREE.JS MONOCHROME GLOBE ENGINE ─────────────────────────────────────
  useEffect(() => {
    if (viewMode !== '3d') return;
    const mount = mountRef.current;
    if (!mount) return;

    const width = mount.clientWidth || 800;
    const height = Math.round(width / 2.05458);

    // WebGL Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(width, height);
    renderer.setClearColor(0x000000, 0);

    const canvas = renderer.domElement;
    canvas.style.display = 'block';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.aspectRatio = '2.05458 / 1';
    canvas.style.cursor = 'grab';
    mount.innerHTML = '';
    mount.appendChild(canvas);

    // Scene & Camera (exact 2.05458 : 1 aspect ratio)
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(38, width / height, 0.1, 100);

    camera.position.set(0, 0, 3.2 / zoomLevel);
    cameraRef.current = camera;

    // Earth Root Group
    const earthGroup = new THREE.Group();
    earthGroup.rotation.x = 0.22; // Natural ~12.6° axial tilt
    earthGroup.rotation.y = -(78.9629 * Math.PI) / 180; // Start facing India (~78.96° E, Indian Subcontinent)
    earthGroupRef.current = earthGroup;
    scene.add(earthGroup);

    // 1. Inner Pure Black Core Sphere
    const innerSphereGeo = new THREE.SphereGeometry(GLOBE_RADIUS * 0.995, 48, 48);
    const innerSphereMat = new THREE.MeshBasicMaterial({ color: 0x000000, depthWrite: true });
    const innerSphere = new THREE.Mesh(innerSphereGeo, innerSphereMat);
    earthGroup.add(innerSphere);

    // 2. Pure White Land Dots
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

    // Load Land Mask Texture
    const maskImg = new Image();
    maskImg.crossOrigin = 'anonymous';
    maskImg.src = '/earth-land-mask.png';

    maskImg.onload = () => {
      try {
        const offscreen = document.createElement('canvas');
        const w = maskImg.naturalWidth || 2048;
        const h = maskImg.naturalHeight || 1024;
        offscreen.width = w;
        offscreen.height = h;
        const ctx = offscreen.getContext('2d', { willReadFrequently: true });
        if (ctx) {
          ctx.drawImage(maskImg, 0, 0, w, h);
          const raw = ctx.getImageData(0, 0, w, h).data;
          
          const positions: number[] = [];
          const colors: number[] = [];

          for (let i = 0; i < CANDIDATE_POINTS; i++) {
            const y = 1 - (i / (CANDIDATE_POINTS - 1)) * 2;
            const radiusAtY = Math.sqrt(Math.max(0, 1 - y * y));
            const theta = GOLDEN_ANGLE * i;

            const x = Math.cos(theta) * radiusAtY;
            const z = Math.sin(theta) * radiusAtY;

            const lat = Math.asin(Math.max(-1, Math.min(1, y))) * (180 / Math.PI);
            const lon = Math.atan2(x, z) * (180 / Math.PI);

            const u = (lon + 180) / 360;
            const v = (90 - lat) / 180;

            const px = Math.min(w - 1, Math.max(0, Math.floor(u * w)));
            const py = Math.min(h - 1, Math.max(0, Math.floor(v * h)));
            const pixelIdx = (py * w + px) * 4;

            if (raw[pixelIdx] > LAND_THRESHOLD) {
              positions.push(x * GLOBE_RADIUS, y * GLOBE_RADIUS, z * GLOBE_RADIUS);
              // 100% Pure White — Zero Color Tint
              colors.push(1.0, 1.0, 1.0);
            }
          }

          dotGeo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
          dotGeo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
          dotGeo.computeBoundingSphere();
        }
      } catch (err) {
        console.warn('[WorldMonitorGlobe] Land mask load notice:', err);
      }
    };

    // ── Incident Threat Pins in 3D ───────────────────────────────────────────
    const pinMeshes: { mesh: THREE.Mesh; hitMesh: THREE.Mesh; event: WorldEvent }[] = [];
    const pinGroup = new THREE.Group();
    earthGroup.add(pinGroup);

    geoEvents.forEach((ev) => {
      const lat = ev.location.latitude!;
      const lon = ev.location.longitude!;
      const isCorrelated = correlations.some((c) => c.event_id === ev.id);
      const isSelected = ev.id === selectedEventId;

      const latRad = (lat * Math.PI) / 180;
      const lonRad = (lon * Math.PI) / 180;
      const rPin = GLOBE_RADIUS * 1.015;

      const y = Math.sin(latRad) * rPin;
      const rRing = Math.cos(latRad) * rPin;
      const x = Math.sin(lonRad) * rRing;
      const z = Math.cos(lonRad) * rRing;

      // Color coding
      const pinColor = isCorrelated ? 0x38bdf8 : ev.severity === 'CRITICAL' ? 0xf87171 : 0xfb923c;

      // Pin Core Dot
      const pinGeo = new THREE.SphereGeometry(isSelected ? 0.032 : 0.024, 16, 16);
      const pinMat = new THREE.MeshBasicMaterial({ color: pinColor });
      const pinMesh = new THREE.Mesh(pinGeo, pinMat);
      pinMesh.position.set(x, y, z);
      pinGroup.add(pinMesh);

      // Pulsing Halo Ring
      const ringGeo = new THREE.RingGeometry(0.024, isSelected ? 0.075 : 0.05, 32);
      const ringMat = new THREE.MeshBasicMaterial({
        color: pinColor,
        transparent: true,
        opacity: 0.6,
        side: THREE.DoubleSide,
      });
      const ringMesh = new THREE.Mesh(ringGeo, ringMat);
      ringMesh.position.set(x * 1.002, y * 1.002, z * 1.002);
      ringMesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), new THREE.Vector3(x, y, z).normalize());
      pinGroup.add(ringMesh);

      // Invisible Hit Sphere for Raycasting
      const hitGeo = new THREE.SphereGeometry(0.08, 12, 12);
      const hitMat = new THREE.MeshBasicMaterial({ visible: false });
      const hitMesh = new THREE.Mesh(hitGeo, hitMat);
      hitMesh.position.set(x, y, z);
      hitMesh.userData = { eventId: ev.id, event: ev };
      pinGroup.add(hitMesh);

      pinMeshes.push({ mesh: pinMesh, hitMesh, event: ev });
    });

    // ── Interaction: Dragging, Raycasting & Auto-Rotation ─────────────────────
    let isDragging = false;
    let hasDragged = false;
    let dragStartX = 0;
    let dragStartY = 0;
    let lastMouseX = 0;
    let lastMouseY = 0;
    let velocityX = 0;
    let velocityY = 0;
    const raycaster = new THREE.Raycaster();

    const onPointerDown = (e: PointerEvent) => {
      isDragging = true;
      hasDragged = false;
      dragStartX = e.clientX;
      dragStartY = e.clientY;
      lastMouseX = e.clientX;
      lastMouseY = e.clientY;
      velocityX = 0;
      velocityY = 0;
      canvas.style.cursor = 'grabbing';
      targetRotationRef.current = null;
    };

    const onPointerMove = (e: PointerEvent) => {
      const rect = canvas.getBoundingClientRect();
      const mouseX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      const mouseY = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      if (isDragging) {
        const dx = e.clientX - lastMouseX;
        const dy = e.clientY - lastMouseY;
        if (Math.hypot(e.clientX - dragStartX, e.clientY - dragStartY) > 5) {
          hasDragged = true;
        }

        earthGroup.rotation.y += dx * 0.005;
        earthGroup.rotation.x = Math.max(-1.4, Math.min(1.4, earthGroup.rotation.x + dy * 0.005));

        velocityX = dx * 0.003;
        velocityY = dy * 0.003;
        lastMouseX = e.clientX;
        lastMouseY = e.clientY;
        setHoveredEvent(null);
      } else {
        raycaster.setFromCamera(new THREE.Vector2(mouseX, mouseY), camera);
        const hitObjects = pinMeshes.map((p) => p.hitMesh);
        const intersects = raycaster.intersectObjects(hitObjects, false);

        if (intersects.length > 0) {
          const hit = intersects[0].object;
          const ev = hit.userData.event as WorldEvent;
          canvas.style.cursor = 'pointer';
          setHoveredEvent(ev);
          setTooltipPos({ x: e.clientX - rect.left, y: e.clientY - rect.top });
        } else {
          canvas.style.cursor = 'grab';
          setHoveredEvent(null);
        }
      }
    };

    const onPointerUp = (e: PointerEvent) => {
      isDragging = false;
      canvas.style.cursor = 'grab';

      if (!hasDragged) {
        const rect = canvas.getBoundingClientRect();
        const mouseX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        const mouseY = -((e.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(new THREE.Vector2(mouseX, mouseY), camera);
        const hitObjects = pinMeshes.map((p) => p.hitMesh);
        const intersects = raycaster.intersectObjects(hitObjects, false);

        if (intersects.length > 0) {
          const hit = intersects[0].object;
          const evId = hit.userData.eventId as string;
          if (evId) {
            onSelectEvent(evId);
          }
        }
      }
    };

    canvas.addEventListener('pointerdown', onPointerDown);
    canvas.addEventListener('pointermove', onPointerMove);
    canvas.addEventListener('pointerup', onPointerUp);
    canvas.addEventListener('pointercancel', onPointerUp);

    // ── Animation Loop ───────────────────────────────────────────────────────
    let animId = 0;
    let isRunning = true;
    let animTime = 0;

    const animate = () => {
      if (!isRunning) return;
      animId = requestAnimationFrame(animate);
      animTime += 0.016;

      if (targetRotationRef.current) {
        const tr = targetRotationRef.current;
        earthGroup.rotation.y += (tr.y - earthGroup.rotation.y) * 0.06;
        earthGroup.rotation.x += (tr.x - earthGroup.rotation.x) * 0.06;
        if (
          Math.abs(tr.y - earthGroup.rotation.y) < 0.005 &&
          Math.abs(tr.x - earthGroup.rotation.x) < 0.005
        ) {
          targetRotationRef.current = null;
        }
      } else if (!isDragging) {
        velocityX *= 0.92;
        velocityY *= 0.92;
        earthGroup.rotation.y += velocityX + (autoRotate ? 0.001 : 0);
        earthGroup.rotation.x = Math.max(-1.4, Math.min(1.4, earthGroup.rotation.x + velocityY));
      }

      const pulseScale = 1.0 + 0.2 * Math.sin(animTime * 3.5);
      pinMeshes.forEach(({ mesh }) => {
        mesh.scale.set(pulseScale, pulseScale, pulseScale);
      });

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!mount) return;
      const w = mount.clientWidth || 800;
      const h = Math.round(w / 2.05458);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      isRunning = false;
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', handleResize);
      canvas.removeEventListener('pointerdown', onPointerDown);
      canvas.removeEventListener('pointermove', onPointerMove);
      canvas.removeEventListener('pointerup', onPointerUp);
      canvas.removeEventListener('pointercancel', onPointerUp);
      renderer.dispose();
      innerSphereGeo.dispose();
      innerSphereMat.dispose();
      dotGeo.dispose();
      dotMat.dispose();
    };
  }, [viewMode, geoEvents, correlations, selectedEventId, autoRotate, zoomLevel]);

  // Update 3D Camera Zoom
  useEffect(() => {
    if (cameraRef.current) {
      cameraRef.current.position.set(0, 0, 3.2 / zoomLevel);
      cameraRef.current.updateProjectionMatrix();
    }
  }, [zoomLevel]);

  // Equirectangular 2D coordinate conversion (exact 1:2.05458 aspect ratio)
  const project2D = (lat: number, lon: number) => {
    const x = ((lon + 180) / 360) * 1027.29;
    const y = ((90 - lat) / 180) * 500;
    return { x, y };
  };

  return (
    <div className="space-y-3 select-none">
      {/* Top Map Action Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-white/[0.02] border border-white/[0.06] p-2 rounded-xl backdrop-blur-sm font-mono text-xs">
        {/* View Mode Toggle: 3D Globe vs 2D World Map */}
        <div className="flex items-center gap-1 bg-black/80 p-1 rounded-lg border border-white/[0.08]">
          <button
            onClick={() => setViewMode('3d')}
            className={`px-3 py-1.5 rounded-md flex items-center gap-1.5 font-bold transition-all cursor-pointer ${
              viewMode === '3d'
                ? 'bg-white text-black shadow-md'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            <Globe className="w-3.5 h-3.5" />
            3D Globe
          </button>
          <button
            onClick={() => setViewMode('2d')}
            className={`px-3 py-1.5 rounded-md flex items-center gap-1.5 font-bold transition-all cursor-pointer ${
              viewMode === '2d'
                ? 'bg-white text-black shadow-md'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            <Map className="w-3.5 h-3.5" />
            2D Map
          </button>
        </div>

        {/* Status indicator */}
        <div className="flex items-center gap-3 text-neutral-400 text-[11px]">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            {geoEvents.length} Geospatial Threat Points
          </span>
          <span className="text-neutral-600">|</span>
          <span>Ratio: 1:2.05458</span>
        </div>

        {/* View Controls (Rotation, Zoom, Reset) */}
        <div className="flex items-center gap-1.5">
          {viewMode === '3d' && (
            <button
              onClick={() => setAutoRotate((r) => !r)}
              className={`p-1.5 rounded-lg border transition-colors cursor-pointer ${
                autoRotate
                  ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30'
                  : 'bg-white/[0.04] text-neutral-400 border-white/[0.08] hover:text-white'
              }`}
              title={autoRotate ? 'Pause Rotation' : 'Auto Rotate'}
            >
              {autoRotate ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            </button>
          )}

          <button
            onClick={() => setZoomLevel((z) => Math.min(2.0, z + 0.2))}
            className="p-1.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-neutral-300 hover:text-white transition-colors cursor-pointer"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={() => setZoomLevel((z) => Math.max(0.6, z - 0.2))}
            className="p-1.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-neutral-300 hover:text-white transition-colors cursor-pointer"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={() => {
              setZoomLevel(1.0);
              if (earthGroupRef.current) {
                earthGroupRef.current.rotation.x = 0.22;
                earthGroupRef.current.rotation.y = -(78.9629 * Math.PI) / 180;
              }
              targetRotationRef.current = null;
            }}
            className="p-1.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-neutral-300 hover:text-white transition-colors cursor-pointer"
            title="Reset View (Focus India)"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Canvas Display Container (Pure Black Background with 1:2.05458 ratio) */}
      <div
        className="relative w-full bg-[#000000] rounded-2xl border border-white/[0.08] overflow-hidden shadow-2xl flex items-center justify-center"
        style={{ aspectRatio: '2.05458 / 1' }}
      >
        {/* ── 3D VIEW CONTAINER ── */}
        {viewMode === '3d' && (
          <div ref={mountRef} className="w-full h-full flex items-center justify-center" style={{ aspectRatio: '2.05458 / 1' }} />
        )}

        {/* ── 2D VIEW CONTAINER (Authentic Monochrome Equirectangular World Map) ── */}
        {viewMode === '2d' && (
          <div className="w-full h-full relative overflow-hidden flex items-center justify-center bg-[#000000]" style={{ aspectRatio: '2.05458 / 1' }}>
            <WorldMap2DCanvas
              events={geoEvents}
              selectedEventId={selectedEventId}
              correlations={correlations}
              zoomLevel={zoomLevel}
              onSelectEvent={onSelectEvent}
              onHoverEvent={(ev, pos) => {
                setHoveredEvent(ev);
                setTooltipPos(pos);
              }}
            />
          </div>
        )}

        {/* Hover / Raycast Tooltip */}
        {hoveredEvent && (
          <div
            className="absolute z-30 pointer-events-none p-3 rounded-xl bg-black/95 border border-white/20 shadow-2xl backdrop-blur-md max-w-xs transition-all duration-75 text-xs font-mono select-none"
            style={{
              left: tooltipPos ? `${Math.min(tooltipPos.x + 10, 500)}px` : '20px',
              top: tooltipPos ? `${Math.max(tooltipPos.y - 40, 20)}px` : '20px',
            }}
          >
            <div className="flex items-center justify-between gap-2 border-b border-white/[0.08] pb-1.5 mb-1.5">
              <span className="text-white font-bold flex items-center gap-1 text-[11px]">
                <MapPin className="w-3 h-3 text-cyan-400" />
                {hoveredEvent.location.city}, {hoveredEvent.location.country}
              </span>
              <span
                className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                  hoveredEvent.severity === 'CRITICAL'
                    ? 'bg-red-500/20 text-red-400'
                    : 'bg-orange-500/20 text-orange-400'
                }`}
              >
                {hoveredEvent.severity}
              </span>
            </div>
            <p className="text-white font-semibold text-xs leading-snug line-clamp-2">{hoveredEvent.title}</p>
            <div className="flex items-center justify-between gap-2 text-[10px] text-neutral-400 mt-1.5 pt-1 border-t border-white/[0.04]">
              <span>Source: {hoveredEvent.source}</span>
              <span className="text-cyan-300 font-bold">Click to inspect</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// ── 2D MONOCHROME WORLD MAP CANVAS COMPONENT (1:2.05458 ASPECT RATIO) ───────────────────
interface WorldMap2DCanvasProps {
  events: WorldEvent[];
  selectedEventId: string | null;
  correlations: any[];
  zoomLevel: number;
  onSelectEvent: (id: string) => void;
  onHoverEvent: (ev: WorldEvent | null, pos: { x: number; y: number } | null) => void;
}

const WorldMap2DCanvas: React.FC<WorldMap2DCanvasProps> = ({
  events,
  selectedEventId,
  correlations,
  zoomLevel,
  onSelectEvent,
  onHoverEvent,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Map coordinate system: width:height = 2.05458 : 1
  const MAP_H = 500;
  const MAP_W = 1027.29; // 500 * 2.05458

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = MAP_W * dpr;
    canvas.height = MAP_H * dpr;
    ctx.scale(dpr, dpr);

    // 1. Deep Black Background
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, MAP_W, MAP_H);

    // 2. Graticule Lat/Lon Grid (Monochrome White)
    ctx.lineWidth = 0.5;
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';

    // Longitude lines (every 30 degrees)
    for (let lon = -180; lon <= 180; lon += 30) {
      const x = ((lon + 180) / 360) * MAP_W;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, MAP_H);
      ctx.stroke();
    }

    // Latitude lines (every 30 degrees)
    for (let lat = -90; lat <= 90; lat += 30) {
      const y = ((90 - lat) / 180) * MAP_H;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(MAP_W, y);
      ctx.stroke();
    }

    // 3. Equator & Prime Meridian (Prominent Monochrome White Dashes)
    ctx.lineWidth = 1;
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
    ctx.setLineDash([4, 4]);

    // Equator (y = 250)
    ctx.beginPath();
    ctx.moveTo(0, MAP_H / 2);
    ctx.lineTo(MAP_W, MAP_H / 2);
    ctx.stroke();

    // Prime Meridian (x = 500)
    ctx.beginPath();
    ctx.moveTo(MAP_W / 2, 0);
    ctx.lineTo(MAP_W / 2, MAP_H);
    ctx.stroke();
    ctx.setLineDash([]); // Reset line dash

    // 4. Sample and Render Real Land Dots from /earth-land-mask.png
    const maskImg = new Image();
    maskImg.crossOrigin = 'anonymous';
    maskImg.src = '/earth-land-mask.png';

    const drawLand = (imgData: ImageData, imgW: number, imgH: number) => {
      const raw = imgData.data;
      const stepX = 3.5;
      const stepY = 3.5;
      const dotRadius = 1.2;

      ctx.fillStyle = '#ffffff';

      for (let x = 0; x < MAP_W; x += stepX) {
        const u = x / MAP_W;
        const px = Math.min(imgW - 1, Math.max(0, Math.floor(u * imgW)));

        for (let y = 0; y < MAP_H; y += stepY) {
          const v = y / MAP_H;
          const py = Math.min(imgH - 1, Math.max(0, Math.floor(v * imgH)));
          const pixelIdx = (py * imgW + px) * 4;

          if (raw[pixelIdx] > 55) {
            ctx.beginPath();
            ctx.arc(x, y, dotRadius, 0, Math.PI * 2);
            ctx.fill();
          }
        }
      }
    };

    const processMask = () => {
      try {
        const offscreen = document.createElement('canvas');
        const w = maskImg.naturalWidth || 2048;
        const h = maskImg.naturalHeight || 1024;
        offscreen.width = w;
        offscreen.height = h;
        const offCtx = offscreen.getContext('2d', { willReadFrequently: true });
        if (offCtx) {
          offCtx.drawImage(maskImg, 0, 0, w, h);
          const imgData = offCtx.getImageData(0, 0, w, h);
          drawLand(imgData, w, h);
        }
      } catch (err) {
        console.warn('[WorldMap2D] Land mask sampling fallback:', err);
      }
    };

    if (maskImg.complete && maskImg.naturalWidth > 0) {
      processMask();
    } else {
      maskImg.onload = processMask;
    }
  }, []);

  const project2D = (lat: number, lon: number) => {
    const x = ((lon + 180) / 360) * MAP_W;
    const y = ((90 - lat) / 180) * MAP_H;
    return { x, y };
  };

  return (
    <div
      ref={containerRef}
      className="relative w-full h-full flex items-center justify-center select-none overflow-hidden cursor-default"
    >
      <div
        className="relative w-full h-full flex items-center justify-center"
        style={{
          aspectRatio: '2.05458 / 1',
          transform: zoomLevel !== 1 ? `scale(${zoomLevel})` : undefined,
          transformOrigin: 'center center',
        }}
      >
        {/* Canvas World Map Layer (Pure White Monochrome Dots) */}
        <canvas
          ref={canvasRef}
          className="w-full h-full block"
          style={{ width: '100%', height: '100%', aspectRatio: '2.05458 / 1' }}
        />

        {/* SVG Interactive Incident Threat Pins Layer */}
        <svg
          viewBox={`0 0 ${MAP_W} ${MAP_H}`}
          className="absolute inset-0 w-full h-full pointer-events-auto"
        >
          {events.map((ev) => {
            const { x, y } = project2D(ev.location.latitude!, ev.location.longitude!);
            const isSelected = ev.id === selectedEventId;
            const isCorrelated = correlations.some((c) => c.event_id === ev.id);
            const pinColor = isCorrelated ? '#38bdf8' : ev.severity === 'CRITICAL' ? '#f87171' : '#fb923c';

            return (
              <g
                key={ev.id}
                className="cursor-pointer group"
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectEvent(ev.id);
                }}
                onMouseEnter={(e) => {
                  const rect = e.currentTarget.getBoundingClientRect();
                  onHoverEvent(ev, { x: rect.left, y: rect.top });
                }}
                onMouseLeave={() => onHoverEvent(null, null)}
              >
                {/* Outer Radar Ping */}
                <circle
                  cx={x}
                  cy={y}
                  r={isSelected ? 20 : 12}
                  fill={pinColor}
                  fillOpacity="0.25"
                  className="animate-ping"
                />

                {/* Core Pin Dot */}
                <circle
                  cx={x}
                  cy={y}
                  r={isSelected ? 8 : 5}
                  fill={pinColor}
                  stroke="#000000"
                  strokeWidth="2"
                />

                {/* City / Country Label */}
                <text
                  x={x + 10}
                  y={y + 4}
                  fill="#ffffff"
                  fontSize="11"
                  fontFamily="monospace"
                  fontWeight="bold"
                  className="drop-shadow-[0_2px_4px_rgba(0,0,0,0.95)] select-none pointer-events-none"
                >
                  {ev.location.city}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
};
