import React, { useState, useRef, useEffect, useCallback } from "react";
import { ArrowRight, Globe, FileCheck2, Lock, Check } from "lucide-react";
import { useApp } from "../context/AppContext";
import { AuthorizationModal } from "../components/common/AuthorizationModal";
import { CinematicEarth } from "../components/visual/CinematicEarth";

/**
 * HomePage
 *
 * Layout:
 *   - Fills 100% of parent (App.tsx gives it flex-1, h-full, overflow-hidden)
 *   - overflow: hidden on root — no scroll
 *   - Globe size = min(containerH * 0.95, containerW * 0.72)
 *     This ensures:
 *       · Top/bottom fit vertically (97% of h)
 *       · Right curved edge stays in left ~40% of screen (0.72W * 0.55 ≈ 0.40W)
 *   - Globe left position: -globeSize * 0.45 → 55% visible, 45% clipped LEFT only
 *   - Content panel starts at 41% from left
 */
export const HomePage: React.FC = () => {
  const { navigate, activeAssessment } = useApp();
  const [targetUrl, setTargetUrl] = useState("https://www.worldmonitor.app");
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [urlError, setUrlError] = useState("");
  const [globeSize, setGlobeSize] = useState(0);

  const rootRef = useRef<HTMLDivElement>(null);

  const measureSize = useCallback(() => {
    const el = rootRef.current;
    if (!el) return;
    const h = el.clientHeight;
    const w = el.clientWidth;
    if (h <= 0 || w <= 0) return;
    // Size by height (fills ~95% vertically)
    const byH = Math.round(h * 0.95);
    // Size by width: visible 55% of globe must sit in left 41% of screen
    // globeSize * 0.55 <= w * 0.41  →  globeSize <= w * 0.746
    const byW = Math.round(w * 0.72);
    setGlobeSize(Math.min(byH, byW));
  }, []);

  useEffect(() => {
    measureSize();
    const ro = new ResizeObserver(measureSize);
    if (rootRef.current) ro.observe(rootRef.current);
    return () => ro.disconnect();
  }, [measureSize]);

  const handleAssess = (e: React.FormEvent) => {
    e.preventDefault();
    if (
      !targetUrl.trim() ||
      (!targetUrl.startsWith("http://") && !targetUrl.startsWith("https://"))
    ) {
      setUrlError("Enter a valid URL starting with http:// or https://");
      return;
    }
    setUrlError("");
    setShowAuthModal(true);
  };

  const handleAuthConfirmed = () => {
    setShowAuthModal(false);
    setTimeout(() => navigate("new-assessment"), 400);
  };

  return (
    <>
      {/* Root: fills all space below Navbar. overflow:hidden clips left globe edge */}
      <div
        ref={rootRef}
        className="relative w-full h-full"
        style={{ overflow: "hidden", minHeight: 0 }}
      >

        {/* ── Globe — far-left, 55% visible ─────────────────────────────────
            top:50% + translateY(-50%) = vertical centre.
            left: -globeSize*0.45 = 45% pushed off left edge of screen.
            z-index 1 (above bg, below content).                           */}
        {globeSize > 0 && (
          <div
            style={{
              position: "absolute",
              top: "50%",
              left: -globeSize * 0.45,
              transform: "translateY(-50%)",
              width: globeSize,
              height: globeSize,
              zIndex: 1,
              pointerEvents: "auto",
            }}
          >
            <CinematicEarth size={globeSize} />
          </div>
        )}

        {/* ── Left-edge fade: background bleeds over globe left ─────────── */}
        <div
          aria-hidden="true"
          style={{
            position: "absolute",
            inset: "0 auto 0 0",
            width: "5vw",
            background: "linear-gradient(to right, #000000 30%, transparent)",
            zIndex: 2,
            pointerEvents: "none",
          }}
        />

        {/* ── Content panel — right side ─────────────────────────────────── */}
        <div
          style={{
            position: "absolute",
            top: 0,
            bottom: 0,
            left: "41%",
            right: 0,
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            paddingLeft: "3vw",
            paddingRight: "4vw",
            paddingTop: "12px",
            paddingBottom: "12px",
            zIndex: 10,
          }}
        >
          <div style={{ display: "flex", flexDirection: "column", gap: "20px", maxWidth: "520px", width: "100%" }}>

            {/* Enterprise Badge */}
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                padding: "4px 12px",
                borderRadius: "9999px",
                background: "rgba(255,255,255,0.04)",
                border: "1px solid rgba(255,255,255,0.10)",
                fontSize: "11px",
                fontFamily: "monospace",
                color: "#d4d4d8",
                alignSelf: "flex-start",
              }}
            >
              <span
                style={{
                  width: 6, height: 6, borderRadius: "50%",
                  background: "#34d399",
                  animation: "pulse 2s cubic-bezier(0.4,0,0.6,1) infinite",
                  flexShrink: 0,
                }}
              />
              KAVACH Enterprise VAPT
              <span style={{ color: "#52525b" }}>/</span>
              <span style={{ color: "#a1a1aa" }}>Evidence-First Security</span>
            </div>

            {/* Brand */}
            <div>
              <h1
                style={{
                  fontSize: "clamp(2.5rem, 5vw, 3.75rem)",
                  fontWeight: 900,
                  letterSpacing: "-0.04em",
                  color: "#ffffff",
                  lineHeight: 1,
                  margin: "0 0 8px 0",
                }}
              >
                KAVACH
              </h1>
              <h2
                style={{
                  fontSize: "clamp(1rem, 2.2vw, 1.4rem)",
                  fontWeight: 600,
                  color: "#e4e4e7",
                  lineHeight: 1.3,
                  margin: "0 0 10px 0",
                  letterSpacing: "-0.02em",
                }}
              >
                Security Assessment.{" "}
                <span style={{ color: "#71717a" }}>Backed by Evidence.</span>
              </h2>
              <p
                style={{
                  fontSize: "14px",
                  color: "#71717a",
                  lineHeight: 1.6,
                  maxWidth: "360px",
                  margin: 0,
                }}
              >
                Authorized, evidence-first security assessment for the World Monitor
                platform. Every finding SHA-256 hashed.
              </p>
            </div>

            {/* CTA Buttons */}
            <div style={{ display: "flex", flexWrap: "wrap", gap: "10px", alignItems: "center" }}>
              <button onClick={() => setShowAuthModal(true)} className="btn-primary">
                Start Assessment
                <ArrowRight style={{ width: 14, height: 14 }} />
              </button>
              <button onClick={() => navigate("url-check")} className="btn-secondary">
                <Globe style={{ width: 14, height: 14 }} />
                URL Security Check
              </button>
              <button onClick={() => navigate("evidence")} className="btn-secondary">
                <FileCheck2 style={{ width: 14, height: 14 }} />
                Evidence Vault
              </button>
            </div>

            {/* URL Input */}
            <div
              style={{
                borderRadius: "12px",
                padding: "16px",
                background: "rgba(14,14,18,0.76)",
                backdropFilter: "blur(24px)",
                WebkitBackdropFilter: "blur(24px)",
                border: "1px solid rgba(255,255,255,0.10)",
                boxShadow: "0 8px 32px rgba(0,0,0,0.55)",
              }}
            >
              <div
                style={{
                  display: "flex", justifyContent: "space-between",
                  alignItems: "center", marginBottom: "10px",
                  fontSize: "11px", fontFamily: "monospace",
                }}
              >
                <span style={{ display: "flex", alignItems: "center", gap: 6, color: "#ffffff", fontWeight: 600 }}>
                  <Lock style={{ width: 11, height: 11, color: "#a1a1aa" }} />
                  Authorized Target URL
                </span>
                <span style={{ color: "#52525b" }}>Read-Only Inspection</span>
              </div>
              <form onSubmit={handleAssess} style={{ display: "flex", gap: "8px" }}>
                <input
                  id="url-input-field"
                  type="text"
                  value={targetUrl}
                  onChange={(e) => { setTargetUrl(e.target.value); if (urlError) setUrlError(""); }}
                  placeholder="https://example.com"
                  style={{
                    flex: 1,
                    padding: "10px 12px",
                    borderRadius: "8px",
                    background: "rgba(0,0,0,0.6)",
                    border: "1px solid rgba(255,255,255,0.10)",
                    color: "#ffffff",
                    fontFamily: "monospace",
                    fontSize: "13px",
                    outline: "none",
                  }}
                />
                <button type="submit" className="btn-primary" style={{ padding: "10px 16px", fontSize: "13px", flexShrink: 0 }}>
                  Assess
                </button>
              </form>
              {urlError && (
                <p style={{ fontSize: "11px", color: "#fb7185", fontFamily: "monospace", marginTop: "6px" }}>
                  {urlError}
                </p>
              )}
              <div
                style={{
                  display: "flex", justifyContent: "space-between", alignItems: "center",
                  marginTop: "12px", paddingTop: "10px",
                  borderTop: "1px solid rgba(255,255,255,0.06)",
                  fontSize: "11px", fontFamily: "monospace", color: "#71717a",
                }}
              >
                <div style={{ display: "flex", gap: "14px" }}>
                  <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
                    <Check style={{ width: 11, height: 11, color: "#34d399" }} /> No destructive checks
                  </span>
                  <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
                    <Check style={{ width: 11, height: 11, color: "#34d399" }} /> SHA-256 hashed
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => { setTargetUrl("https://www.worldmonitor.app"); setUrlError(""); }}
                  style={{
                    background: "none", border: "none", cursor: "pointer",
                    color: "#71717a", fontFamily: "monospace", fontSize: "11px",
                    textDecoration: "underline", textUnderlineOffset: "3px",
                    padding: 0,
                  }}
                  onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = "#ffffff"; }}
                  onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = "#71717a"; }}
                >
                  Use Demo Target
                </button>
              </div>
            </div>

            {/* System Status */}
            <div
              style={{
                borderRadius: "12px",
                padding: "12px 16px",
                background: "rgba(12,12,16,0.62)",
                backdropFilter: "blur(16px)",
                WebkitBackdropFilter: "blur(16px)",
                border: "1px solid rgba(255,255,255,0.07)",
                display: "flex",
                alignItems: "center",
                gap: "12px",
                flexWrap: "wrap",
              }}
            >
              <div style={{ fontSize: "10px", fontFamily: "monospace", flex: "1 1 auto", minWidth: 0 }}>
                <span style={{ color: "#52525b", display: "block" }}>TARGET</span>
                <span style={{ color: "#ffffff", fontWeight: 600, display: "block", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {activeAssessment?.name || "World Monitor"}
                </span>
              </div>
              <div style={{ width: 1, height: 28, background: "rgba(255,255,255,0.07)", flexShrink: 0 }} />
              <div style={{ fontSize: "10px", fontFamily: "monospace", flexShrink: 0 }}>
                <span style={{ color: "#52525b", display: "block" }}>POSTURE</span>
                <span style={{ color: "#34d399", fontWeight: 600 }}>65 / 100</span>
              </div>
              <div style={{ width: 1, height: 28, background: "rgba(255,255,255,0.07)", flexShrink: 0 }} />
              <div style={{ fontSize: "10px", fontFamily: "monospace", flexShrink: 0 }}>
                <span style={{ color: "#52525b", display: "block" }}>FINDINGS</span>
                <span style={{ color: "#ffffff", fontWeight: 600 }}>07 Tracked</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "11px", fontFamily: "monospace", color: "#34d399", fontWeight: 600, marginLeft: "auto", flexShrink: 0 }}>
                <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#34d399", flexShrink: 0, animation: "pulse 2s ease-in-out infinite" }} />
                SYSTEM READY
              </div>
            </div>

            {/* Drag hint */}
            <p style={{ fontSize: "10px", fontFamily: "monospace", color: "#3f3f46", textAlign: "center", margin: 0, userSelect: "none" }}>
              ← Drag the Earth to rotate
            </p>

          </div>
        </div>

      </div>

      <AuthorizationModal
        isOpen={showAuthModal}
        targetUrl={targetUrl}
        onConfirm={handleAuthConfirmed}
        onClose={() => setShowAuthModal(false)}
      />
    </>
  );
};
