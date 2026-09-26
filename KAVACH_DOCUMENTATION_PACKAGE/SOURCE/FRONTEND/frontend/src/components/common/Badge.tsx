import React from 'react';

interface BadgeProps {
  label?: string;
  children?: React.ReactNode;
  type?: 'severity' | 'status' | 'custom';
  variant?: string;
  size?: 'sm' | 'md';
}

export const Badge: React.FC<BadgeProps> = ({ label, children, type = 'status', variant, size = 'md' }) => {
  const content = (typeof children === 'string' ? children : label || '') as string;
  const normalized = (variant || content || '').toUpperCase();
  const sizeClass = size === 'sm' ? 'px-2 py-0.5 text-[10px]' : 'px-2.5 py-1 text-xs';

  let dotColor = 'bg-neutral-400';
  let textColor = 'text-neutral-300';
  let borderColor = 'border-white/[0.08]';
  let bgColor = 'bg-neutral-950/80';

  // Severity indicator colors (Used solely for security meaning)
  if (type === 'severity' || ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'].includes(normalized)) {
    switch (normalized) {
      case 'CRITICAL':
        dotColor = 'bg-rose-500';
        textColor = 'text-rose-400';
        borderColor = 'border-rose-500/30';
        bgColor = 'bg-rose-950/20';
        break;
      case 'HIGH':
        dotColor = 'bg-rose-400';
        textColor = 'text-rose-300';
        borderColor = 'border-rose-500/25';
        bgColor = 'bg-rose-950/15';
        break;
      case 'MEDIUM':
        dotColor = 'bg-amber-400';
        textColor = 'text-amber-300';
        borderColor = 'border-amber-500/25';
        bgColor = 'bg-amber-950/15';
        break;
      case 'LOW':
        dotColor = 'bg-blue-400';
        textColor = 'text-blue-300';
        borderColor = 'border-blue-500/25';
        bgColor = 'bg-blue-950/15';
        break;
      case 'INFO':
        dotColor = 'bg-neutral-400';
        textColor = 'text-neutral-400';
        borderColor = 'border-neutral-700/40';
        bgColor = 'bg-neutral-900/40';
        break;
    }
  } else {
    // Finding & lifecycle status (Minimalist semantics)
    switch (normalized) {
      case 'CONFIRMED':
      case 'RESOLVED':
      case 'ONLINE':
      case 'READY':
      case 'VERIFIED':
        dotColor = 'bg-emerald-400';
        textColor = 'text-emerald-400';
        borderColor = 'border-emerald-500/30';
        bgColor = 'bg-emerald-950/20';
        break;
      case 'POTENTIAL':
      case 'NEEDS REVIEW':
      case 'REQUIRES MANUAL REVIEW':
      case 'MANUAL REVIEW':
        dotColor = 'bg-amber-400';
        textColor = 'text-amber-300';
        borderColor = 'border-amber-500/30';
        bgColor = 'bg-amber-950/15';
        break;
      case 'UNDER ANALYSIS':
      case 'AI ANALYSIS':
        dotColor = 'bg-purple-400 animate-pulse';
        textColor = 'text-purple-300';
        borderColor = 'border-purple-500/30';
        bgColor = 'bg-purple-950/20';
        break;
      case 'VALIDATING':
      case 'RUNNING':
        dotColor = 'bg-cyan-400 animate-pulse';
        textColor = 'text-cyan-300';
        borderColor = 'border-cyan-500/30';
        bgColor = 'bg-cyan-950/20';
        break;
      case 'EVIDENCE AVAILABLE':
      case 'IMPROVED':
        dotColor = 'bg-blue-400';
        textColor = 'text-blue-300';
        borderColor = 'border-blue-500/30';
        bgColor = 'bg-blue-950/15';
        break;
      case 'UNCONFIRMED':
        dotColor = 'bg-neutral-500';
        textColor = 'text-neutral-400';
        borderColor = 'border-white/[0.08]';
        bgColor = 'bg-neutral-900/40';
        break;
      case 'OFFLINE':
      case 'FAILED':
      case 'STILL OBSERVED':
        dotColor = 'bg-rose-500';
        textColor = 'text-rose-400';
        borderColor = 'border-rose-500/30';
        bgColor = 'bg-rose-950/20';
        break;
      default:
        dotColor = 'bg-neutral-400';
        textColor = 'text-neutral-300';
        borderColor = 'border-white/[0.08]';
        bgColor = 'bg-neutral-900/40';
    }
  }

  return (
    <span
      className={`glass-badge border tracking-wide uppercase ${sizeClass} ${bgColor} ${borderColor} ${textColor}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dotColor} shrink-0`} />
      <span>{content}</span>
    </span>
  );
};
