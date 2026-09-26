import React, { useRef } from 'react';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  glow?: 'cyan' | 'red' | 'green' | 'amber' | 'none';
  glassLevel?: 1 | 2 | 3 | 4;
  onClick?: () => void;
}

/**
 * GlassCard: Modern iOS-inspired layered glass panel.
 * Uses physical material layering with dynamic cursor light tracking and hairline borders.
 */
export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  className = '',
  title,
  subtitle,
  icon,
  action,
  glow = 'none',
  glassLevel = 2,
  onClick
}) => {
  const cardRef = useRef<HTMLDivElement | null>(null);

  const glowStyles = {
    cyan: 'border-white/20 shadow-[0_8px_32px_rgba(0,0,0,0.7),0_0_24px_rgba(255,255,255,0.06)]',
    red: 'border-rose-500/25 shadow-[0_8px_32px_rgba(0,0,0,0.7),0_0_24px_rgba(244,63,94,0.08)]',
    green: 'border-emerald-500/25 shadow-[0_8px_32px_rgba(0,0,0,0.7),0_0_24px_rgba(16,185,129,0.08)]',
    amber: 'border-amber-500/25 shadow-[0_8px_32px_rgba(0,0,0,0.7),0_0_24px_rgba(245,158,11,0.08)]',
    none: 'border-white/[0.08] hover:border-white/18'
  }[glow];

  const levelClass = `glass-level-${glassLevel}`;

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    cardRef.current.style.setProperty('--mouse-x', `${x}px`);
    cardRef.current.style.setProperty('--mouse-y', `${y}px`);
  };

  return (
    <div
      ref={cardRef}
      onClick={onClick}
      onMouseMove={handleMouseMove}
      className={`${levelClass} rounded-xl p-5 ${glowStyles} ${
        onClick ? 'cursor-pointer' : ''
      } ${className}`}
    >
      {(title || action) && (
        <div className="flex items-center justify-between pb-3.5 mb-4 border-b border-white/[0.06]">
          <div className="flex items-center space-x-2.5">
            {icon && <div className="text-white shrink-0">{icon}</div>}
            <div>
              {title && <h3 className="text-sm font-semibold tracking-tight text-white">{title}</h3>}
              {subtitle && <p className="text-xs text-neutral-400 mt-0.5">{subtitle}</p>}
            </div>
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      {children}
    </div>
  );
};
