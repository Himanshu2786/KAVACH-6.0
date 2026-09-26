import React, { useEffect } from 'react';

/**
 * CursorLight: High-performance pointer tracking for iOS glass surface reflections.
 * Batched to display refresh rate via requestAnimationFrame with zero lag.
 */
export const CursorLight: React.FC = () => {
  useEffect(() => {
    let rafId: number;
    let latestX = window.innerWidth / 2;
    let latestY = window.innerHeight / 2;

    const onMouseMove = (e: MouseEvent) => {
      latestX = e.clientX;
      latestY = e.clientY;

      cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(() => {
        document.documentElement.style.setProperty('--mouse-x', `${latestX}px`);
        document.documentElement.style.setProperty('--mouse-y', `${latestY}px`);
      });
    };

    window.addEventListener('mousemove', onMouseMove, { passive: true });
    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      cancelAnimationFrame(rafId);
    };
  }, []);

  return null;
};
