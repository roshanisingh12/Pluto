import React from 'react';

export type TelemetryStatus = 'nominal' | 'advisory' | 'critical' | 'offline' | 'active';

interface TelemetryBadgeProps {
  status: TelemetryStatus;
  label?: string;
  pulse?: boolean;
  className?: string;
}

export const TelemetryBadge: React.FC<TelemetryBadgeProps> = ({
  status,
  label,
  pulse = true,
  className = '',
}) => {
  let bg = 'bg-[#10B981]/10';
  let border = 'border-[#10B981]/30';
  let text = 'text-[#10B981]';
  let dot = 'bg-[#10B981]';
  let defaultLabel = 'SYSTEM NOMINAL';

  switch (status) {
    case 'nominal':
      bg = 'bg-[#10B981]/10';
      border = 'border-[#10B981]/30';
      text = 'text-[#10B981]';
      dot = 'bg-[#10B981]';
      defaultLabel = 'SYSTEM NOMINAL';
      break;
    case 'advisory':
      bg = 'bg-[#F59E0B]/10';
      border = 'border-[#F59E0B]/30';
      text = 'text-[#F59E0B]';
      dot = 'bg-[#F59E0B]';
      defaultLabel = 'ADVISORY';
      break;
    case 'critical':
    case 'offline':
      bg = 'bg-[#EF4444]/10';
      border = 'border-[#EF4444]/30';
      text = 'text-[#EF4444]';
      dot = 'bg-[#EF4444]';
      defaultLabel = 'BACKEND OFFLINE';
      break;
    case 'active':
      bg = 'bg-[#06B6D4]/10';
      border = 'border-[#06B6D4]/30';
      text = 'text-[#06B6D4]';
      dot = 'bg-[#06B6D4]';
      defaultLabel = 'ACTIVE';
      break;
  }

  return (
    <span
      className={`inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-mono font-semibold tracking-wider uppercase border ${bg} ${border} ${text} ${className}`}
    >
      <span className="relative flex h-2 w-2">
        {pulse && (
          <span
            className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${dot}`}
          />
        )}
        <span className={`relative inline-flex rounded-full h-2 w-2 ${dot}`} />
      </span>
      <span>{label || defaultLabel}</span>
    </span>
  );
};
