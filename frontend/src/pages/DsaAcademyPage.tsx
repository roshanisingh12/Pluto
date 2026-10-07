import React, { useEffect, useState } from 'react';
import {
  BookOpen, ChevronDown, ChevronRight, Cpu, Search, Database, Filter, Hash, Zap, AlertCircle,
} from 'lucide-react';
import { getDsaInfo } from '../api/client';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { ErrorState } from '../components/ErrorState';
import type { DsaInfoResponse } from '../types';

/* -- colour helpers -- */
const ALGO_COLOURS: Record<string, { accent: string; border: string; bg: string }> = {
  merge_sort:     { accent: '#06B6D4', border: 'border-cyan-800/60',   bg: 'bg-cyan-950/20' },
  quick_sort:     { accent: '#3B82F6', border: 'border-blue-800/60',   bg: 'bg-blue-950/20' },
  bubble_sort:    { accent: '#F59E0B', border: 'border-amber-800/60',  bg: 'bg-amber-950/20' },
  linear_search:  { accent: '#10B981', border: 'border-emerald-800/60', bg: 'bg-emerald-950/20' },
  binary_search:  { accent: '#8B5CF6', border: 'border-violet-800/60', bg: 'bg-violet-950/20' },
};

/* -- Complexity Badge -- */
const Badge: React.FC<{ label: string; value: string; color: string }> = ({ label, value, color }) => (
  <div className="bg-[#0A0E1A] border border-slate-800 rounded-xl p-3 text-xs font-mono">
    <div className="text-slate-500 uppercase text-[10px] tracking-wider mb-1">{label}</div>
    <div className="font-bold" style={{ color }}>{value}</div>
  </div>
);

/* -- Collapsible Card -- */
const AlgoCard: React.FC<{
  id: string;
  name: string;
  info: any;
  defaultOpen?: boolean;
}> = ({ id, name, info, defaultOpen }) => {
  const [open, setOpen] = useState(defaultOpen ?? false);
  const colour = ALGO_COLOURS[id] ?? { accent: '#06B6D4', border: 'border-slate-800', bg: 'bg-[#0D1117]' };

  const tc = info.time_complexity as any;
  const best = tc?.best ?? '—';
  const avg = tc?.average ?? '—';
  const worst = tc?.worst ?? '—';
  const stability = info.stability ?? (info.stable === true ? 'Stable' : info.stable === false ? 'Unstable' : '—');

  return (
    <div className={`border ${colour.border} rounded-2xl overflow-hidden transition-all`}>
      <button
        onClick={() => setOpen(!open)}
        className={`w-full flex items-center gap-3 px-5 py-4 text-left ${colour.bg} hover:brightness-110 transition`}
      >
        <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: colour.accent }} />
        <span className="font-mono font-bold text-sm text-slate-100 flex-1">{name}</span>
        <div className="flex items-center gap-3 font-mono text-[11px] text-slate-500">
          <span>{tc?.average ?? '—'}</span>
          <span className={stability === 'Stable' ? 'text-emerald-400' : stability === 'Unstable' ? 'text-amber-400' : 'text-slate-500'}>{stability}</span>
        </div>
        {open ? <ChevronDown className="w-4 h-4 text-slate-500" /> : <ChevronRight className="w-4 h-4 text-slate-500" />}
      </button>

      {open && (
        <div className="px-5 pb-5 pt-4 bg-[#0D1117] space-y-4 border-t border-slate-800/50">
          {/* Complexity grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <Badge label="Best Case" value={best} color="#10B981" />
            <Badge label="Average Case" value={avg} color={colour.accent} />
            <Badge label="Worst Case" value={worst} color="#F59E0B" />
            <Badge label="Space" value={info.space_complexity ?? '—'} color="#8B5CF6" />
          </div>

          {/* Stability + Paradigm */}
          <div className="flex flex-wrap gap-2 font-mono text-xs">
            {stability !== '—' && (
              <span className={`px-3 py-1 rounded-full text-[11px] font-semibold border ${stability === 'Stable' ? 'bg-emerald-950/50 text-emerald-400 border-emerald-800/50' : 'bg-amber-950/50 text-amber-400 border-amber-800/50'}`}>
                {stability}
              </span>
            )}
            {info.paradigm && (
              <span className="px-3 py-1 rounded-full text-[11px] font-semibold border border-slate-700 bg-slate-800/50 text-slate-300">
                {info.paradigm}
              </span>
            )}
          </div>

          {/* Description */}
          {info.description && (
            <p className="text-xs font-mono text-slate-400 leading-relaxed">{info.description}</p>
          )}

          {/* Project Application */}
          <div className="bg-[#0A0E1A] border border-slate-800 rounded-xl p-4">
            <div className="text-[10px] font-mono uppercase tracking-wider text-slate-500 mb-1.5">HOW SATIQ USES THIS</div>
            <p className="text-xs font-mono text-slate-300 leading-relaxed">{info.project_application}</p>
          </div>
        </div>
      )}
    </div>
  );
};

/* -- Viva Q&A -- */
const VivaItem: React.FC<{ q: string; a: string; idx: number }> = ({ q, a, idx }) => {
  const [open, setOpen] = useState(false);
  return (
    <div className="border border-slate-800 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-3 px-4 py-3 text-left bg-[#0D1117] hover:bg-[#111827] transition"
      >
        <span className="text-[11px] font-mono font-bold text-cyan-500 shrink-0 w-6">Q{idx}</span>
        <span className="text-xs font-mono text-slate-300 flex-1 text-left">{q.replace(/^Q\d+:\s*/, '')}</span>
        {open ? <ChevronDown className="w-3.5 h-3.5 text-slate-500 shrink-0" /> : <ChevronRight className="w-3.5 h-3.5 text-slate-500 shrink-0" />}
      </button>
      {open && (
        <div className="px-4 pb-4 pt-3 bg-[#0A0E1A] border-t border-slate-800/50">
          <p className="text-xs font-mono text-slate-400 leading-relaxed">{a}</p>
        </div>
      )}
    </div>
  );
};

/* -- Main -- */
export const DsaAcademyPage: React.FC = () => {
  const [info, setInfo] = useState<DsaInfoResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<'sorting' | 'searching' | 'structures' | 'viva'>('sorting');

  const fetchInfo = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getDsaInfo();
      setInfo(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load DSA information');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchInfo(); }, []);

  const tabs = [
    { id: 'sorting' as const, label: 'Sorting', icon: Cpu },
    { id: 'searching' as const, label: 'Searching', icon: Search },
    { id: 'structures' as const, label: 'Data Structures', icon: Database },
    { id: 'viva' as const, label: 'Viva Q&A', icon: BookOpen },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#06B6D4]" />
          <span className="text-xs font-mono font-semibold text-[#06B6D4] uppercase tracking-wider">TECHNICAL MISSION KNOWLEDGE CENTER</span>
        </div>
        <h1 className="text-2xl font-bold font-mono tracking-tight text-white mt-1">DSA Academy</h1>
        <p className="text-xs text-slate-400 font-mono mt-0.5">Algorithms, data structures, and viva examination reference for the SATIQ DSA implementation.</p>
      </div>

      {loading && (
        <div className="space-y-4">
          <LoadingSkeleton className="h-12 rounded-2xl" />
          {[...Array(3)].map((_, i) => <LoadingSkeleton key={i} className="h-20 rounded-xl" />)}
        </div>
      )}

      {error && !loading && <ErrorState title="DSA Info Load Failed" message={error} onRetry={fetchInfo} />}

      {info && !loading && (
        <>
          {/* Tab Bar */}
          <div className="flex flex-wrap gap-2 bg-[#0D1117] border border-slate-800 rounded-2xl p-2">
            {tabs.map(t => {
              const Icon = t.icon;
              return (
                <button
                  key={t.id}
                  onClick={() => setTab(t.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-mono font-semibold transition ${
                    tab === t.id
                      ? 'bg-[#0A0E1A] border border-cyan-800/60 text-[#22D3EE]'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {t.label}
                </button>
              );
            })}
          </div>

          {/* -- Sorting -- */}
          {tab === 'sorting' && (
            <div className="space-y-4">
              <div className="text-xs font-mono text-slate-500 flex items-center gap-2">
                <Cpu className="w-3.5 h-3.5 text-[#06B6D4]" />
                SATIQ implements three manual sorting algorithms. Click an algorithm to expand.
              </div>
              <AlgoCard id="merge_sort"  name="Merge Sort"  info={info.sorting.merge_sort}  defaultOpen />
              <AlgoCard id="quick_sort"  name="Quick Sort"  info={info.sorting.quick_sort}  />
              <AlgoCard id="bubble_sort" name="Bubble Sort" info={info.sorting.bubble_sort} />
            </div>
          )}

          {/* -- Searching -- */}
          {tab === 'searching' && (
            <div className="space-y-4">
              <div className="text-xs font-mono text-slate-500 flex items-center gap-2">
                <Search className="w-3.5 h-3.5 text-[#06B6D4]" />
                SATIQ implements two manual searching algorithms. Click to expand.
              </div>
              <AlgoCard id="linear_search" name="Linear Search" info={info.searching.linear_search} defaultOpen />
              <AlgoCard id="binary_search" name="Binary Search" info={info.searching.binary_search} />
            </div>
          )}

          {/* -- Data Structures -- */}
          {tab === 'structures' && (
            <div className="space-y-6">
              {/* Hash Table */}
              <div className="bg-[#0D1117] border border-cyan-800/40 rounded-2xl p-6 space-y-4">
                <div className="flex items-center gap-2 border-b border-slate-800/80 pb-3">
                  <Hash className="w-4 h-4 text-cyan-400" />
                  <span className="text-sm font-mono font-bold text-slate-100">{info.hashing.name}</span>
                  <span className="ml-auto text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950/50 text-cyan-400 border border-cyan-800/50">Hash Table</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-mono">
                  <div className="space-y-2">
                    <div className="flex justify-between py-1.5 border-b border-slate-800/50"><span className="text-slate-500">Structure</span><span className="text-slate-300">{info.hashing.structure}</span></div>
                    <div className="flex justify-between py-1.5 border-b border-slate-800/50"><span className="text-slate-500">Collision Resolution</span><span className="text-slate-300">{info.hashing.collision_resolution}</span></div>
                    <div className="flex justify-between py-1.5 border-b border-slate-800/50"><span className="text-slate-500">Load Factor Threshold</span><span className="text-cyan-400 font-bold">{info.hashing.load_factor_threshold}</span></div>
                    <div className="flex justify-between py-1.5"><span className="text-slate-500">Space Complexity</span><span className="text-slate-300">{info.hashing.space_complexity}</span></div>
                  </div>
                  <div className="space-y-2">
                    <div className="text-slate-500 text-[10px] uppercase tracking-wider mb-2">Time Complexity</div>
                    {Object.entries(info.hashing.time_complexity).map(([op, cases]: [string, any]) => (
                      <div key={op} className="flex items-center gap-2 py-1.5 border-b border-slate-800/50 last:border-0">
                        <span className="text-slate-400 capitalize w-14">{op}</span>
                        <span className="text-emerald-400">avg: {cases.average}</span>
                        <span className="text-amber-400 ml-auto">worst: {cases.worst}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="bg-[#0A0E1A] border border-slate-800 rounded-xl p-4">
                  <div className="text-[10px] font-mono uppercase tracking-wider text-slate-500 mb-1.5">HASH FUNCTION</div>
                  <code className="text-xs font-mono text-cyan-300">{info.hashing.hash_function}</code>
                </div>
                <div className="bg-[#0A0E1A] border border-slate-800 rounded-xl p-4">
                  <div className="text-[10px] font-mono uppercase tracking-wider text-slate-500 mb-1.5">HOW SATIQ USES THIS</div>
                  <p className="text-xs font-mono text-slate-300 leading-relaxed">{info.hashing.project_application}</p>
                </div>
              </div>

              {/* Dynamic Array */}
              <div className="bg-[#0D1117] border border-blue-800/40 rounded-2xl p-6 space-y-4">
                <div className="flex items-center gap-2 border-b border-slate-800/80 pb-3">
                  <Zap className="w-4 h-4 text-blue-400" />
                  <span className="text-sm font-mono font-bold text-slate-100">Dynamic Array (Python list)</span>
                  <span className="ml-auto text-[10px] font-mono px-2 py-0.5 rounded bg-blue-950/50 text-blue-400 border border-blue-800/50">List</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <Badge label="Access" value="O(1)" color="#10B981" />
                  <Badge label="Search" value="O(n)" color="#06B6D4" />
                  <Badge label="Insert (end)" value="O(1) amortized" color="#3B82F6" />
                  <Badge label="Space" value="O(n)" color="#8B5CF6" />
                </div>
                <div className="bg-[#0A0E1A] border border-slate-800 rounded-xl p-4">
                  <div className="text-[10px] font-mono uppercase tracking-wider text-slate-500 mb-1.5">HOW SATIQ USES THIS</div>
                  <p className="text-xs font-mono text-slate-300 leading-relaxed">
                    The image catalog is maintained as a dynamic Python list (dynamic array) of ImageRecord objects. All sorting and searching algorithms iterate over this list. The list auto-resizes on insertion, enabling O(1) amortized appends when new images are uploaded or sample datasets are loaded.
                  </p>
                </div>
              </div>

              {/* Predicate Filtering */}
              <div className="bg-[#0D1117] border border-emerald-800/40 rounded-2xl p-6 space-y-4">
                <div className="flex items-center gap-2 border-b border-slate-800/80 pb-3">
                  <Filter className="w-4 h-4 text-emerald-400" />
                  <span className="text-sm font-mono font-bold text-slate-100">{info.filtering.name}</span>
                  <span className="ml-auto text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/50 text-emerald-400 border border-emerald-800/50">Filter</span>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <Badge label="Time Complexity" value={info.filtering.time_complexity} color="#10B981" />
                  <Badge label="Space Complexity" value={info.filtering.space_complexity} color="#8B5CF6" />
                </div>
                <div className="bg-[#0A0E1A] border border-slate-800 rounded-xl p-4 font-mono text-xs space-y-2">
                  <div className="text-[10px] uppercase tracking-wider text-slate-500 mb-2">PREDICATE PIPELINE</div>
                  {['Image Records (n items)', 'Predicate Conditions (P_land ? P_fmt ? P_date)', 'Matching Records (k matches)'].map((step, i, arr) => (
                    <React.Fragment key={step}>
                      <div className="text-slate-300 px-3 py-2 bg-[#111827] border border-slate-800 rounded-lg">{step}</div>
                      {i < arr.length - 1 && <div className="text-cyan-500 text-center">?</div>}
                    </React.Fragment>
                  ))}
                </div>
                <div className="bg-[#0A0E1A] border border-slate-800 rounded-xl p-4">
                  <div className="text-[10px] font-mono uppercase tracking-wider text-slate-500 mb-1.5">HOW SATIQ USES THIS</div>
                  <p className="text-xs font-mono text-slate-300 leading-relaxed">{info.filtering.purpose}</p>
                </div>
              </div>
            </div>
          )}

          {/* -- Viva Q&A -- */}
          {tab === 'viva' && (
            <div className="space-y-4">
              <div className="text-xs font-mono text-slate-500 flex items-center gap-2">
                <AlertCircle className="w-3.5 h-3.5 text-amber-500" />
                {info.viva_questions.length} viva examination questions. Click to reveal answers.
              </div>
              <div className="space-y-2">
                {info.viva_questions.map((vq, i) => (
                  <VivaItem key={i} q={vq.q} a={vq.a} idx={i + 1} />
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
