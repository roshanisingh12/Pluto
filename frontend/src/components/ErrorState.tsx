import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Telemetry Error',
  message,
  onRetry,
  className = '',
}) => {
  return (
    <div
      className={`border border-[#EF4444]/40 bg-[#EF4444]/5 rounded-2xl p-6 text-center flex flex-col items-center justify-center space-y-3 ${className}`}
    >
      <div className="p-3 rounded-xl bg-[#EF4444]/10 border border-[#EF4444]/30 text-[#EF4444]">
        <AlertTriangle className="w-6 h-6" />
      </div>
      <div className="text-sm font-semibold font-mono tracking-wider uppercase text-rose-400">
        {title}
      </div>
      <p className="text-xs text-rose-300/80 max-w-lg leading-relaxed font-mono">
        {message}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-2 flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-slate-900 border border-slate-700 hover:border-slate-500 text-slate-200 text-xs font-mono font-medium transition"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>RETRY TELEMETRY LINK</span>
        </button>
      )}
    </div>
  );
};
