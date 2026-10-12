import React, { useState, useEffect } from 'react';
import { Satellite, RefreshCw, Radio, Menu } from 'lucide-react';
import type { HealthResponse } from '../types';
import { TelemetryBadge } from './TelemetryBadge';

interface TelemetryHeaderProps {
  health: HealthResponse | null;
  healthLoading: boolean;
  onRefreshHealth: () => void;
  onToggleSidebar?: () => void;
}

export const TelemetryHeader: React.FC<TelemetryHeaderProps> = ({
  health,
  healthLoading,
  onRefreshHealth,
  onToggleSidebar,
}) => {
  const [utcTime, setUtcTime] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setUtcTime(now.toUTCString().replace('GMT', 'UTC'));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const isOnline = health !== null && health.status === 'ok';

  return (
    <header className="h-14 border-b border-slate-800 bg-[#0D1117]/90 backdrop-blur-md sticky top-0 z-40 px-4 sm:px-6 flex items-center justify-between">
      {/* Left: Mobile Toggle & Pluto wordmark */}
      <div className="flex items-center gap-3">
        {onToggleSidebar && (
          <button
            onClick={onToggleSidebar}
            className="md:hidden p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white"
            aria-label="Toggle navigation"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}

        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-cyan-950/60 border border-cyan-800/50 flex items-center justify-center text-[#06B6D4]">
            <Satellite className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono font-bold text-sm tracking-widest text-slate-100">
                PLUTO
              </span>
              <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-cyan-400 border border-slate-700">
                v1.0
              </span>
            </div>
            <span className="text-[10px] text-slate-500 font-mono hidden sm:inline-block">
              EARTH OBSERVATION INTELLIGENCE
            </span>
          </div>
        </div>
      </div>

      {/* Middle: Live UTC Clock */}
      <div className="hidden lg:flex items-center gap-2 font-mono text-xs text-slate-400 bg-[#0A0E1A] px-3 py-1 rounded-lg border border-slate-800">
        <Radio className="w-3.5 h-3.5 text-[#06B6D4] animate-pulse" />
        <span className="text-slate-200 tracking-wider font-semibold">{utcTime || 'UTC CLOCK'}</span>
      </div>

      {/* Right: Telemetry Health & Re-ping */}
      <div className="flex items-center gap-3">
        <TelemetryBadge
          status={isOnline ? 'nominal' : 'offline'}
          label={healthLoading ? 'CONNECTING...' : isOnline ? 'SYSTEM NOMINAL' : 'BACKEND OFFLINE'}
        />

        <button
          onClick={onRefreshHealth}
          disabled={healthLoading}
          title="Refresh Backend Telemetry Link"
          className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-cyan-400 transition disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${healthLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>
    </header>
  );
};
