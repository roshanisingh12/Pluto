import React from 'react';
import type { LucideIcon } from 'lucide-react';
import { Database } from 'lucide-react';

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon: Icon = Database,
  title,
  description,
  actionText,
  onAction,
  className = '',
}) => {
  return (
    <div
      className={`border border-dashed border-slate-800 bg-[#0D1117]/60 rounded-2xl p-10 text-center flex flex-col items-center justify-center space-y-3 ${className}`}
    >
      <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 text-slate-400">
        <Icon className="w-8 h-8 text-[#06B6D4]" />
      </div>
      <h3 className="text-base font-semibold text-slate-200 tracking-wide font-mono uppercase">
        {title}
      </h3>
      <p className="text-xs text-slate-400 max-w-md leading-relaxed">
        {description}
      </p>
      {actionText && onAction && (
        <button
          onClick={onAction}
          className="mt-3 px-4 py-2 rounded-lg bg-[#06B6D4]/10 hover:bg-[#06B6D4]/20 border border-[#06B6D4]/30 hover:border-[#06B6D4]/60 text-[#22D3EE] text-xs font-mono font-semibold transition"
        >
          {actionText}
        </button>
      )}
    </div>
  );
};
