import React, { useRef, useEffect, useState, useCallback, useMemo } from 'react';

interface Point3D {
  x: number;
  y: number;
  z: number;
}

interface Node3D extends Point3D {
  label: string;
  active?: boolean;
}

interface Arc3D {
  from: Node3D;
  to: Node3D;
  progress: number;
  speed: number;
}

interface InteractiveGlobeProps {
  className?: string;
  size?: number;
  onNodeClick?: (node: Node3D) => void;
}

/**
 * InteractiveGlobe: High-performance, digital cybersecurity point-cloud globe.
 * - Deep black, bright white, soft graphite, subtle metallic light.
 * - Heavy, smooth auto-rotation.
 * - Cursor parallax reaction.
 * - Drag-to-rotate with velocity & inertia damping.
 * - Tab sleep and prefers-reduced-motion support.
 */
export const InteractiveGlobe: React.FC<InteractiveGlobeProps> = ({
  className = '',
  size = 560,
  onNodeClick
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const isDraggingRef = useRef(false);
  const lastMouseRef = useRef({ x: 0, y: 0 });
  const velocityRef = useRef({ x: 0, y: 0 });
  const anglesRef = useRef({ x: 0.22, y: 0 });
  const hoverParallaxRef = useRef({ x: 0, y: 0 });
  const animFrameRef = useRef<number>(0);
  const [isHovered, setIsHovered] = useState(false);
  const [isGrabbing, setIsGrabbing] = useState(false);

  // Generate scientific point cloud
  const { points, nodes, arcs } = useMemo(() => {
    const pts: Point3D[] = [];
    const radius = 1;

    // 1. Point Cloud Grid (Fibonacci sphere distribution for uniform, elegant dots)
    const totalDots = 720;
    const phi = Math.PI * (3 - Math.sqrt(5)); // Golden angle

    for (let i = 0; i < totalDots; i++) {
      const y = 1 - (i / (totalDots - 1)) * 2; // y goes from 1 to -1
      const radiusAtY = Math.sqrt(1 - y * y);
      const theta = phi * i;

      const x = Math.cos(theta) * radiusAtY;
      const z = Math.sin(theta) * radiusAtY;

      pts.push({ x: x * radius, y: y * radius, z: z * radius });
    }

    // 2. Curated Global Security Telemetry Nodes
    const nds: Node3D[] = [
      { x: 0.52, y: 0.62, z: 0.58, label: 'Frankfurt Core', active: true },
      { x: 0.18, y: 0.74, z: 0.65, label: 'London Edge', active: false },
      { x: -0.68, y: 0.54, z: 0.49, label: 'US-East Vault', active: true },
      { x: -0.84, y: 0.42, z: 0.35, label: 'US-West Gateway', active: false },
      { x: 0.88, y: 0.38, z: 0.26, label: 'Tokyo Sensor', active: true },
      { x: 0.72, y: 0.21, z: 0.66, label: 'Singapore Hub', active: true },
      { x: 0.65, y: 0.35, z: 0.67, label: 'Mumbai Node', active: true },
      { x: 0.81, y: -0.52, z: 0.27, label: 'Sydney Probe', active: false },
      { x: -0.42, y: -0.38, z: 0.82, label: 'São Paulo Sensor', active: false },
      { x: 0.15, y: 0.05, z: 0.98, label: 'Accra Edge', active: false }
    ];

    // Normalize node vectors onto sphere surface
    nds.forEach((n) => {
      const len = Math.sqrt(n.x * n.x + n.y * n.y + n.z * n.z);
      n.x /= len;
      n.y /= len;
      n.z /= len;
    });

    // 3. Network Connection Paths (Security inspection routes)
    const arcList: Arc3D[] = [
      { from: nds[0], to: nds[2], progress: 0.2, speed: 0.006 },
      { from: nds[1], to: nds[6], progress: 0.5, speed: 0.005 },
      { from: nds[2], to: nds[3], progress: 0.8, speed: 0.008 },
      { from: nds[3], to: nds[4], progress: 0.1, speed: 0.006 },
      { from: nds[4], to: nds[5], progress: 0.4, speed: 0.007 },
      { from: nds[5], to: nds[6], progress: 0.7, speed: 0.005 },
      { from: nds[6], to: nds[0], progress: 0.9, speed: 0.006 },
      { from: nds[5], to: nds[8], progress: 0.3, speed: 0.006 }
    ];

    return { points: pts, nodes: nds, arcs: arcList };
  }, []);

  // Project 3D vector to 2D screen coordinate
  const project = useCallback(
    (
      p: Point3D,
      rotX: number,
      rotY: number,
      scale: number,
      cx: number,
      cy: number
    ) => {
      // Rotation around Y (Yaw)
      const cosY = Math.cos(rotY);
      const sinY = Math.sin(rotY);
      const x1 = p.x * cosY - p.z * sinY;
      const z1 = p.z * cosY + p.x * sinY;

      // Rotation around X (Pitch)
      const cosX = Math.cos(rotX);
      const sinX = Math.sin(rotX);
      const y2 = p.y * cosX - z1 * sinX;
      const z2 = z1 * cosX + p.y * sinX;

      // Perspective scale factor
      const fov = 3.2;
      const factor = fov / (fov + z2);

      return {
        x: cx + x1 * scale * factor,
        y: cy - y2 * scale * factor,
        z: z2,
        scale: factor
      };
    },
    []
  );

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let isRunning = true;

    // Respect reduced motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const baseAutoRotSpeed = prefersReducedMotion ? 0 : 0.0016;

    const render = () => {
      if (!isRunning) return;

      const dpr = window.devicePixelRatio || 1;
      const width = canvas.clientWidth;
      const height = canvas.clientHeight;

      if (canvas.width !== width * dpr || canvas.height !== height * dpr) {
        canvas.width = width * dpr;
        canvas.height = height * dpr;
      }

      ctx.save();
      ctx.scale(dpr, dpr);
      ctx.clearRect(0, 0, width, height);

      const cx = width * 0.48;
      const cy = height * 0.5;
      const globeRadius = Math.min(width, height) * 0.44;

      // Inertia Physics & Velocity damping
      if (!isDraggingRef.current) {
        velocityRef.current.x *= 0.94;
        velocityRef.current.y *= 0.94;

        anglesRef.current.y += velocityRef.current.x;
        anglesRef.current.x += velocityRef.current.y;

        // Auto-rotation when not dragging
        anglesRef.current.y += baseAutoRotSpeed;

        // Soft stabilizing spring for pitch tilt
        anglesRef.current.x += (0.2 - anglesRef.current.x) * 0.02;
      }

      // Parallax adjustment
      const currentRotX = anglesRef.current.x + hoverParallaxRef.current.y * 0.05;
      const currentRotY = anglesRef.current.y + hoverParallaxRef.current.x * 0.05;

      // 1. Atmosphere Radial Glow (Digital metallic aura)
      const auraGrad = ctx.createRadialGradient(cx, cy, globeRadius * 0.75, cx, cy, globeRadius * 1.25);
      auraGrad.addColorStop(0, 'rgba(255, 255, 255, 0.035)');
      auraGrad.addColorStop(0.6, 'rgba(255, 255, 255, 0.012)');
      auraGrad.addColorStop(1, 'transparent');
      ctx.fillStyle = auraGrad;
      ctx.beginPath();
      ctx.arc(cx, cy, globeRadius * 1.25, 0, Math.PI * 2);
      ctx.fill();

      // 2. Subtle Outer Orbital Ring
      ctx.save();
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.06)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.ellipse(cx, cy, globeRadius * 1.12, globeRadius * 0.38, currentRotX * 0.4, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();

      // 3. Render Great-Circle Network Arcs
      arcs.forEach((arc: Arc3D) => {
        arc.progress = (arc.progress + arc.speed) % 1;

        const pFrom = project(arc.from, currentRotX, currentRotY, globeRadius, cx, cy);
        const pTo = project(arc.to, currentRotX, currentRotY, globeRadius, cx, cy);

        // Render curve if either end is visible
        if (pFrom.z > -0.3 || pTo.z > -0.3) {
          const midX = (pFrom.x + pTo.x) / 2;
          const midY = (pFrom.y + pTo.y) / 2 - 28 * Math.max(0.2, (pFrom.z + pTo.z + 2) / 4);

          ctx.beginPath();
          ctx.moveTo(pFrom.x, pFrom.y);
          ctx.quadraticCurveTo(midX, midY, pTo.x, pTo.y);
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
          ctx.lineWidth = 1;
          ctx.stroke();

          // Traveling Telemetry Packet
          const t = arc.progress;
          const packetX = (1 - t) * (1 - t) * pFrom.x + 2 * (1 - t) * t * midX + t * t * pTo.x;
          const packetY = (1 - t) * (1 - t) * pFrom.y + 2 * (1 - t) * t * midY + t * t * pTo.y;

          ctx.beginPath();
          ctx.arc(packetX, packetY, 1.8, 0, Math.PI * 2);
          ctx.fillStyle = '#ffffff';
          ctx.shadowColor = 'rgba(255, 255, 255, 0.8)';
          ctx.shadowBlur = 6;
          ctx.fill();
          ctx.shadowBlur = 0;
        }
      });

      // 4. Render Uniform Scientific Point Cloud
      points.forEach((pt: Point3D) => {
        const pr = project(pt, currentRotX, currentRotY, globeRadius, cx, cy);

        // Depth Cueing (Front points are bright white; back points fade smoothly into black)
        const depthAlpha = Math.max(0.08, (pr.z + 1) / 2);
        const dotRadius = Math.max(0.6, (pr.z + 1.2) * 1.05);

        ctx.beginPath();
        ctx.arc(pr.x, pr.y, dotRadius, 0, Math.PI * 2);

        if (pr.z > 0.3) {
          ctx.fillStyle = `rgba(255, 255, 255, ${depthAlpha * 0.95})`;
        } else if (pr.z > 0) {
          ctx.fillStyle = `rgba(220, 220, 230, ${depthAlpha * 0.7})`;
        } else {
          ctx.fillStyle = `rgba(120, 120, 135, ${depthAlpha * 0.35})`;
        }
        ctx.fill();
      });

      // 5. Render Active Security Telemetry Nodes
      nodes.forEach((node: Node3D) => {
        const pr = project(node, currentRotX, currentRotY, globeRadius, cx, cy);

        if (pr.z > -0.15) {
          const alpha = Math.max(0.2, (pr.z + 1) / 2);

          // Node Halo / Ring
          ctx.beginPath();
          ctx.arc(pr.x, pr.y, 4.5 * pr.scale, 0, Math.PI * 2);
          ctx.strokeStyle = `rgba(255, 255, 255, ${alpha * 0.6})`;
          ctx.lineWidth = 1;
          ctx.stroke();

          // Node Center Dot
          ctx.beginPath();
          ctx.arc(pr.x, pr.y, 2.2 * pr.scale, 0, Math.PI * 2);
          ctx.fillStyle = node.active ? '#ffffff' : 'rgba(200, 200, 210, 0.8)';
          ctx.shadowColor = node.active ? 'rgba(255, 255, 255, 0.9)' : 'transparent';
          ctx.shadowBlur = 8;
          ctx.fill();
          ctx.shadowBlur = 0;

          // Node Micro-Label (Crisp technical typography)
          if (pr.z > 0.4) {
            ctx.font = '9px "JetBrains Mono", monospace';
            ctx.fillStyle = `rgba(255, 255, 255, ${alpha * 0.85})`;
            ctx.fillText(node.label, pr.x + 8, pr.y + 3);
          }
        }
      });

      ctx.restore();
      animFrameRef.current = requestAnimationFrame(render);
    };

    // Tab visibility handling (pause to eliminate idle CPU)
    const handleVisibilityChange = () => {
      if (document.hidden) {
        isRunning = false;
        cancelAnimationFrame(animFrameRef.current);
      } else {
        isRunning = true;
        animFrameRef.current = requestAnimationFrame(render);
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    animFrameRef.current = requestAnimationFrame(render);

    return () => {
      isRunning = false;
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      cancelAnimationFrame(animFrameRef.current);
    };
  }, [project, points, nodes, arcs]);

  // Pointer Drag & Interaction Handlers
  const handlePointerDown = (e: React.PointerEvent) => {
    isDraggingRef.current = true;
    setIsGrabbing(true);
    lastMouseRef.current = { x: e.clientX, y: e.clientY };
    velocityRef.current = { x: 0, y: 0 };
    (e.target as HTMLElement).setPointerCapture(e.pointerId);
  };

  const handlePointerMove = (e: React.PointerEvent) => {
    if (isDraggingRef.current) {
      const deltaX = e.clientX - lastMouseRef.current.x;
      const deltaY = e.clientY - lastMouseRef.current.y;

      anglesRef.current.y += deltaX * 0.005;
      anglesRef.current.x += deltaY * 0.005;

      velocityRef.current = {
        x: deltaX * 0.0035,
        y: deltaY * 0.0035
      };

      lastMouseRef.current = { x: e.clientX, y: e.clientY };
    } else if (containerRef.current) {
      // Subtle Parallax Tilt on Hover
      const rect = containerRef.current.getBoundingClientRect();
      const normX = (e.clientX - rect.left) / rect.width - 0.5;
      const normY = (e.clientY - rect.top) / rect.height - 0.5;
      hoverParallaxRef.current = { x: normX, y: normY };
    }
  };

  const handlePointerUp = (e: React.PointerEvent) => {
    isDraggingRef.current = false;
    setIsGrabbing(false);
    try {
      (e.target as HTMLElement).releasePointerCapture(e.pointerId);
    } catch {
      // Ignore
    }
  };

  return (
    <div
      ref={containerRef}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onPointerCancel={handlePointerUp}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        hoverParallaxRef.current = { x: 0, y: 0 };
      }}
      className={`relative select-none touch-none transition-all duration-300 ${
        isGrabbing ? 'cursor-grabbing' : 'cursor-grab'
      } ${className}`}
      style={{ width: size, height: size }}
      title="Interactive Cyber Globe: Click and drag to rotate the global security telemetry surface"
    >
      <canvas
        ref={canvasRef}
        className="w-full h-full block pointer-events-none"
      />

      {/* Micro-Telemetry Badge Overlay */}
      <div className="absolute bottom-4 left-6 pointer-events-none flex items-center gap-3">
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-black/60 border border-white/10 backdrop-blur-md">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-[10px] font-mono text-neutral-300 font-semibold uppercase tracking-wider">
            Telemetry Stream
          </span>
        </div>
        <span className="text-[10px] font-mono text-neutral-500">
          Drag to inspect
        </span>
      </div>
    </div>
  );
};
