import React from 'react';

interface LandTypeBadgeProps {
  landType: string | null | undefined;
  className?: string;
  size?: 'sm' | 'md';
}

export const LandTypeBadge: React.FC<LandTypeBadgeProps> = ({
  landType,
  className = '',
  size = 'sm',
}) => {
  const norm = (landType || 'Unknown').trim();
  const lower = norm.toLowerCase().replace(/_/g, ' ');

  let bg = 'bg-slate-800/80';
  let text = 'text-slate-300';
  let border = 'border-slate-700/60';
  let dot = 'bg-slate-400';

  if (lower.includes('forest')) {
    bg = 'bg-emerald-950/60';
    text = 'text-emerald-400';
    border = 'border-emerald-800/60';
    dot = 'bg-[#10B981]';
  } else if (lower.includes('water')) {
    bg = 'bg-sky-950/60';
    text = 'text-sky-400';
    border = 'border-sky-800/60';
    dot = 'bg-[#0EA5E9]';
  } else if (lower.includes('agri')) {
    bg = 'bg-lime-950/60';
    text = 'text-lime-400';
    border = 'border-lime-800/60';
    dot = 'bg-[#84CC16]';
  } else if (lower.includes('urban')) {
    bg = 'bg-slate-800/60';
    text = 'text-slate-300';
    border = 'border-slate-700/60';
    dot = 'bg-[#94A3B8]';
  } else if (lower.includes('barren')) {
    bg = 'bg-orange-950/60';
    text = 'text-orange-400';
    border = 'border-orange-800/60';
    dot = 'bg-[#F97316]';
  }

  const padding = size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded font-mono font-medium border ${bg} ${text} ${border} ${padding} ${className}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dot} shrink-0`} />
      <span>{norm}</span>
    </span>
  );
};
