import React from 'react';
import type { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  label: string;
  value: string | number;
  subValue?: string;
  icon: LucideIcon;
  accentColor?: string; // hex or tailwind class
  badge?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  subValue,
  icon: Icon,
  accentColor = '#06B6D4',
  badge,
}) => {
  return (
    <div className="bg-[#0D1117] border border-slate-800 hover:border-slate-700/80 rounded-xl p-5 transition-all shadow-md flex flex-col justify-between relative overflow-hidden group">
      {/* Subtle glowing corner highlight */}
      <div
        className="absolute -top-12 -right-12 w-24 h-24 rounded-full blur-2xl opacity-15 transition group-hover:opacity-25"
        style={{ backgroundColor: accentColor }}
      />

      <div className="flex items-center justify-between mb-3 relative z-10">
        <span className="text-[11px] font-mono tracking-widest text-slate-400 uppercase font-semibold">
          {label}
        </span>
        <div
          className="p-2 rounded-lg border border-slate-800 bg-[#111827] text-slate-300 transition group-hover:text-cyan-400 group-hover:border-cyan-500/40"
        >
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div className="relative z-10">
        <div className="text-2xl sm:text-3xl font-mono font-bold tracking-tight text-slate-100">
          {value}
        </div>
        {subValue && (
          <div className="text-xs text-slate-500 mt-1 flex items-center gap-1.5 font-mono">
            {badge && (
              <span className="px-1.5 py-0.2 rounded bg-slate-800 text-[10px] text-cyan-400 border border-slate-700">
                {badge}
              </span>
            )}
            <span>{subValue}</span>
          </div>
        )}
      </div>
    </div>
  );
};
