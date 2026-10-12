import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TelemetryHeader } from './TelemetryHeader';
import type { HealthResponse } from '../types';

interface LayoutProps {
  health: HealthResponse | null;
  healthLoading: boolean;
  onRefreshHealth: () => void;
}

export const Layout: React.FC<LayoutProps> = ({
  health,
  healthLoading,
  onRefreshHealth,
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#0A0E1A] text-slate-100 flex">
      {/* 240px Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main Content Area */}
      <div className="flex-1 md:pl-[240px] flex flex-col min-w-0">
        <TelemetryHeader
          health={health}
          healthLoading={healthLoading}
          onRefreshHealth={onRefreshHealth}
          onToggleSidebar={() => setSidebarOpen(true)}
        />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>

        <footer className="h-10 border-t border-slate-800/80 bg-[#0D1117]/60 px-6 flex items-center justify-between text-[11px] font-mono text-slate-500">
          <div>PLUTO MISSION CONTROL &bull; EARTH OBSERVATION PLATFORM</div>
          <div className="hidden sm:block">PHASE 2 &bull; CORE MISSION CONTROL UI</div>
        </footer>
      </div>
    </div>
  );
};
