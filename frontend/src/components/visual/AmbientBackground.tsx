import React from 'react';

/**
 * AmbientBackground: 5-layer cinematic background replacing old cyber/matrix grid patterns.
 * Provides a deep black void with soft atmospheric illumination and depth.
 */
export const AmbientBackground: React.FC = () => {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden -z-10 select-none bg-[#000000]">
      {/* Pure Solid True Black Base */}
      <div className="absolute inset-0 bg-[#000000]" />
    </div>
  );
};
