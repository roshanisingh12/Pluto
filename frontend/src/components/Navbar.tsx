import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Activity, Database, Upload, BarChart3, Satellite } from 'lucide-react';
import type { HealthResponse } from '../types';

interface NavbarProps {
  health: HealthResponse | null;
  healthLoading: boolean;
  onRefreshHealth: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ health, healthLoading, onRefreshHealth }) => {
  const location = useLocation();

  const isOnline = health !== null && health.status === 'ok';

  const navItems = [
    { path: '/', label: 'System Health', icon: Activity },
    { path: '/catalog', label: 'Catalog & Preview', icon: Database },
    { path: '/upload', label: 'Upload Test', icon: Upload },
    { path: '/stats', label: 'Statistics', icon: BarChart3 },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <Satellite className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg tracking-wider text-slate-100">SATIQ</span>
              <span className="text-xs px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-mono">
                PHASE 1
              </span>
            </div>
            <p className="text-xs text-slate-400">Satellite Image Intelligence Platform</p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center space-x-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                id={`nav-${item.label.toLowerCase().replace(/[^a-z0-9]/g, '-')}`}
                className={`flex items-center space-x-2 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  active
                    ? 'bg-slate-800 text-emerald-400 border border-slate-700'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Health status indicator */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onRefreshHealth}
            title="Click to recheck health"
            id="health-status-badge"
            disabled={healthLoading}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-full text-xs font-semibold uppercase tracking-wider border transition-all ${
              healthLoading
                ? 'bg-slate-800/80 border-slate-700 text-slate-400'
                : isOnline
                ? 'bg-emerald-950/60 border-emerald-600/40 text-emerald-400 hover:border-emerald-500'
                : 'bg-rose-950/60 border-rose-600/40 text-rose-400 hover:border-rose-500'
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                healthLoading
                  ? 'bg-slate-400 animate-ping'
                  : isOnline
                  ? 'bg-emerald-400 shadow-[0_0_8px_#34d399]'
                  : 'bg-rose-400 shadow-[0_0_8px_#f87171]'
              }`}
            />
            <span>
              {healthLoading ? 'CHECKING...' : isOnline ? 'SYSTEM ONLINE' : 'BACKEND OFFLINE'}
            </span>
          </button>
        </div>
      </div>
    </header>
  );
};
