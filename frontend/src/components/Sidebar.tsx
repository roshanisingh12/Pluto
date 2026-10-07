import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Gauge,
  Compass,
  UploadCloud,
  ArrowDownUp,
  Search,
  Filter,
  BarChart3,
  Zap,
  FolderArchive,
  BookOpen,
  X,
  Layers,
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const navItems = [
  { path: '/', label: 'Mission Control', icon: Gauge, phase: 'Phase 2' },
  { path: '/explorer', label: 'Imagery Explorer', icon: Compass, phase: 'Phase 2' },
  { path: '/ingest', label: 'Ingest Imagery', icon: UploadCloud, phase: 'Phase 2' },
  { path: '/sort-lab', label: 'Sort Lab', icon: ArrowDownUp, phase: 'Phase 3' },
  { path: '/search-lab', label: 'Search Lab', icon: Search, phase: 'Phase 3' },
  { path: '/smart-filters', label: 'Smart Filters', icon: Filter, phase: 'Phase 3' },
  { path: '/analytics', label: 'Analytics', icon: BarChart3, phase: 'Phase 4' },
  { path: '/benchmark-arena', label: 'Benchmark Arena', icon: Zap, phase: 'Phase 4' },
  { path: '/export-organize', label: 'Export & Organize', icon: FolderArchive, phase: 'Phase 4' },
  { path: '/dsa-academy', label: 'DSA Academy', icon: BookOpen, phase: 'Phase 4' },
];

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm md:hidden"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 md:z-30 w-[240px] bg-[#0D1117] border-r border-slate-800 flex flex-col transition-transform duration-300 md:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Sidebar Header / Logo */}
        <div className="h-14 border-b border-slate-800 px-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-sm bg-[#06B6D4]" />
            <span className="font-mono text-xs font-bold tracking-widest text-slate-200">
              MISSION CONTROL
            </span>
          </div>

          <button
            onClick={onClose}
            className="md:hidden p-1 rounded-lg text-slate-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation list */}
        <div className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
          <div className="px-3 py-1 text-[10px] font-mono uppercase tracking-wider text-slate-500 font-semibold">
            PRIMARY MODULES
          </div>

          {navItems.slice(0, 3).map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? 'border-l-2 border-[#06B6D4] bg-cyan-950/25 text-[#22D3EE] font-semibold'
                      : 'border-l-2 border-transparent text-slate-400 hover:text-slate-200 hover:bg-[#111827]'
                  }`
                }
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}

          <div className="pt-4 px-3 py-1 text-[10px] font-mono uppercase tracking-wider text-slate-500 font-semibold">
            DSA &amp; INTELLIGENCE
          </div>

          {navItems.slice(3).map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? 'border-l-2 border-[#06B6D4] bg-cyan-950/25 text-[#22D3EE] font-semibold'
                      : 'border-l-2 border-transparent text-slate-400 hover:text-slate-200 hover:bg-[#111827]'
                  }`
                }
              >
                <div className="flex items-center gap-3 min-w-0">
                  <Icon className="w-4 h-4 shrink-0 text-slate-500" />
                  <span className="truncate">{item.label}</span>
                </div>
                <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-slate-800/80 text-slate-500 border border-slate-700/50">
                  {item.phase}
                </span>
              </NavLink>
            );
          })}
        </div>

        {/* Sidebar Footer */}
        <div className="p-3 border-t border-slate-800 bg-[#0A0E1A]/40 text-[11px] font-mono text-slate-500 flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-[#06B6D4]" />
            <span>DEEPGLOBE v1</span>
          </div>
          <span className="text-[#10B981]">ONLINE</span>
        </div>
      </aside>
    </>
  );
};
