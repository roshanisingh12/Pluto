import React from 'react';

interface LoadingSkeletonProps {
  type?: 'card' | 'table-row' | 'metric' | 'image-grid';
  count?: number;
  className?: string;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  type = 'card',
  count,
  className = '',
}) => {
  // If a custom className is passed without a specific container type, render a direct skeleton block
  if (className && count === undefined && type === 'card') {
    return (
      <div className={`bg-[#0D1117] border border-slate-800/80 animate-pulse ${className}`} />
    );
  }

  const effectiveCount = count ?? 4;
  const items = Array.from({ length: effectiveCount });

  if (type === 'metric') {
    return (
      <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 ${className}`}>
        {items.map((_, i) => (
          <div
            key={i}
            className="bg-[#0D1117] border border-slate-800/80 rounded-xl p-5 animate-pulse space-y-3"
          >
            <div className="h-3 w-24 bg-slate-800 rounded" />
            <div className="h-8 w-16 bg-slate-800 rounded" />
            <div className="h-2.5 w-32 bg-slate-800/60 rounded" />
          </div>
        ))}
      </div>
    );
  }

  if (type === 'image-grid') {
    return (
      <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 ${className}`}>
        {items.map((_, i) => (
          <div
            key={i}
            className="bg-[#0D1117] border border-slate-800/80 rounded-xl overflow-hidden animate-pulse flex flex-col"
          >
            <div className="aspect-video bg-slate-800/70" />
            <div className="p-3.5 space-y-2.5">
              <div className="h-3.5 bg-slate-800 rounded w-3/4" />
              <div className="h-2.5 bg-slate-800/60 rounded w-1/2" />
              <div className="pt-2 border-t border-slate-800/60 flex justify-between">
                <div className="h-2.5 bg-slate-800/60 rounded w-16" />
                <div className="h-2.5 bg-slate-800/60 rounded w-12" />
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className={`space-y-3 ${className}`}>
      {items.map((_, i) => (
        <div
          key={i}
          className="h-16 bg-[#0D1117] border border-slate-800/80 rounded-xl animate-pulse"
        />
      ))}
    </div>
  );
};
