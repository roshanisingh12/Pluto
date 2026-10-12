import React, { useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import {
  Zap, Play, RotateCcw, CheckCircle2, Trophy, Cpu, Clock, Hash, Layers, AlertTriangle,
} from 'lucide-react';
import { runBenchmark } from '../api/client';
import { ErrorState } from '../components/ErrorState';
import { EmptyState } from '../components/EmptyState';
import type { BenchmarkResponse, BenchmarkItemResponse } from '../types';

const ALGO_META: Record<string, { time: string; space: string; stability: string; color: string }> = {
  'Merge Sort': { time: 'O(n log n)', space: 'O(n)', stability: 'Stable', color: '#06B6D4' },
  'Quick Sort': { time: 'O(n log n) avg', space: 'O(log n)', stability: 'Unstable', color: '#3B82F6' },
  'Bubble Sort': { time: 'O(n²)', space: 'O(1)', stability: 'Stable', color: '#F59E0B' },
};

const ChartTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[#0D1117] border border-slate-700 rounded-xl px-3 py-2 text-xs font-mono shadow-2xl">
      {label && <div className="text-slate-400 mb-1">{label}</div>}
      {payload.map((p: any, i: number) => (
        <div key={i} style={{ color: p.color ?? '#22D3EE' }} className="font-bold">
          {p.name}: {typeof p.value === 'number' ? p.value.toFixed(4) : p.value}
        </div>
      ))}
    </div>
  );
};

function getWinner(results: BenchmarkItemResponse[]): BenchmarkItemResponse | null {
  if (!results.length) return null;
  return results.reduce((best, r) => r.time_ms < best.time_ms ? r : best);
}

function isTied(results: BenchmarkItemResponse[]): boolean {
  if (results.length < 2) return false;
  const sorted = [...results].sort((a, b) => a.time_ms - b.time_ms);
  return Math.abs(sorted[0].time_ms - sorted[1].time_ms) < 0.001;
}

export const BenchmarkPage: React.FC = () => {
  const [field, setField] = useState('datetime');
  const [ascending, setAscending] = useState(true);
  const [data, setData] = useState<BenchmarkResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [complete, setComplete] = useState(false);

  const handleRun = async () => {
    setLoading(true);
    setError(null);
    setComplete(false);
    try {
      const res = await runBenchmark({ field, ascending });
      setData(res);
      setComplete(true);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Benchmark execution failed');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => { setData(null); setError(null); setComplete(false); };

  const winner = data ? getWinner(data.results) : null;
  const tied = data ? isTied(data.results) : false;

  const timeChartData = data?.results.map(r => ({
    name: r.algorithm,
    'Time (ms)': parseFloat(r.time_ms.toFixed(4)),
    fill: ALGO_META[r.algorithm]?.color ?? '#64748B',
  }));

  const comparisonsChartData = data?.results.map(r => ({
    name: r.algorithm,
    Comparisons: r.comparisons,
    fill: ALGO_META[r.algorithm]?.color ?? '#64748B',
  }));

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#06B6D4]" />
            <span className="text-xs font-mono font-semibold text-[#06B6D4] uppercase tracking-wider">ALGORITHM PERFORMANCE LABORATORY</span>
          </div>
          <h1 className="text-2xl font-bold font-mono tracking-tight text-white mt-1">Benchmark Arena</h1>
          <p className="text-xs text-slate-400 font-mono mt-0.5">Head-to-head empirical comparison of Merge Sort, Quick Sort, and Bubble Sort on real catalog data.</p>
        </div>
        <div className="flex items-center gap-2">
          {data && (
            <button onClick={handleReset} className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-[#0D1117] border border-slate-800 hover:border-slate-700 text-slate-400 text-xs font-mono transition">
              <RotateCcw className="w-3.5 h-3.5" />RESET
            </button>
          )}
          <button
            onClick={handleRun}
            disabled={loading}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#06B6D4] hover:bg-[#22D3EE] text-[#0A0E1A] font-mono font-bold text-xs uppercase tracking-wider transition shadow-lg shadow-cyan-950/40 disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : 'fill-current'}`} />
            {loading ? 'BENCHMARKING...' : 'RUN BENCHMARK'}
          </button>
        </div>
      </div>

      {/* Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-8 bg-[#0D1117] border border-slate-800 rounded-2xl p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <span className="text-xs font-mono font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Cpu className="w-4 h-4 text-[#06B6D4]" />Benchmark Parameters
            </span>
            <span className="text-[11px] font-mono text-cyan-400">POST /api/benchmark</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-400">SORT KEY FIELD</label>
              <select
                value={field}
                onChange={e => setField(e.target.value)}
                className="w-full px-3 py-2.5 bg-[#0A0E1A] border border-slate-800 rounded-xl text-xs font-mono text-slate-200 focus:outline-none focus:border-[#06B6D4] transition"
              >
                <option value="datetime">datetime (Timestamp)</option>
                <option value="image_name">image_name (Filename)</option>
                <option value="land_type">land_type (Classification)</option>
                <option value="image_format">image_format (Format)</option>
                <option value="file_size">file_size (Bytes)</option>
                <option value="image_id">image_id (Primary ID)</option>
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-400">ORDER DIRECTION</label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setAscending(true)}
                  className={`py-2 rounded-xl text-xs font-mono font-semibold border transition ${ascending ? 'bg-cyan-950/40 border-cyan-800/80 text-[#22D3EE]' : 'bg-[#0A0E1A] border-slate-800 text-slate-400 hover:text-slate-200'}`}
                >ASC (&uarr;)</button>
                <button
                  type="button"
                  onClick={() => setAscending(false)}
                  className={`py-2 rounded-xl text-xs font-mono font-semibold border transition ${!ascending ? 'bg-cyan-950/40 border-cyan-800/80 text-[#22D3EE]' : 'bg-[#0A0E1A] border-slate-800 text-slate-400 hover:text-slate-200'}`}
                >DESC (&darr;)</button>
              </div>
            </div>
          </div>
          <div className="bg-[#0A0E1A] border border-slate-800 rounded-xl p-3 text-xs font-mono text-slate-500 flex items-center gap-2">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-500 shrink-0" />
            All three algorithms (Merge Sort, Quick Sort, Bubble Sort) run simultaneously on identical dataset copies using Pluto's pure Python DSA implementations.
          </div>
        </div>

        {/* Algorithm Info Panel */}
        <div className="lg:col-span-4 bg-[#0D1117] border border-slate-800 rounded-2xl p-6 space-y-3">
          <div className="text-xs font-mono font-semibold text-slate-300 uppercase tracking-wider border-b border-slate-800 pb-2 mb-3">
            ALGORITHMS IN ARENA
          </div>
          {Object.entries(ALGO_META).map(([name, meta]) => (
            <div key={name} className="flex items-center gap-3 text-xs font-mono py-1">
              <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: meta.color }} />
              <div className="flex-1">
                <div className="text-slate-300 font-semibold">{name}</div>
                <div className="text-slate-500 text-[10px]">{meta.time} &bull; {meta.stability}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Error */}
      {error && !loading && <ErrorState title="Benchmark Execution Error" message={error} onRetry={handleRun} />}

      {/* Telemetry Dashboard */}
      {data && (
        <div className={`bg-[#0D1117] border rounded-2xl p-6 space-y-6 shadow-xl relative overflow-hidden transition-all ${complete ? 'border-cyan-800/60' : 'border-slate-800'}`}>
          <div className="absolute top-0 right-0 w-80 h-40 bg-cyan-500/5 blur-3xl pointer-events-none" />
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-[#10B981]" />
              <span className="text-sm font-mono font-bold text-slate-100 uppercase tracking-wider">BENCHMARK TELEMETRY</span>
            </div>
            <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-emerald-950/60 text-emerald-400 border border-emerald-800/60 font-semibold">
              BENCHMARK COMPLETE
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 font-mono text-xs">
            {[
              { label: 'BENCHMARK STATUS', value: 'NOMINAL', color: '#10B981' },
              { label: 'DATASET SIZE', value: `${data.dataset_size} items`, color: '#06B6D4' },
              { label: 'ALGORITHMS TESTED', value: `${data.results.length}`, color: '#3B82F6' },
              { label: 'FASTEST', value: tied ? 'TIE' : (winner?.algorithm.split(' ')[0] ?? '—'), color: '#F59E0B' },
              { label: 'BEST TIME', value: winner ? `${winner.time_ms.toFixed(4)} ms` : '—', color: '#22D3EE' },
              { label: 'SORT KEY', value: data.field, color: '#8B5CF6' },
            ].map(cell => (
              <div key={cell.label} className="bg-[#0A0E1A] p-3 rounded-xl border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase block">{cell.label}</span>
                <span className="font-bold mt-1 block truncate" style={{ color: cell.color }}>{cell.value}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Winner Banner */}
      {data && winner && !tied && (
        <div className="bg-gradient-to-r from-amber-950/40 via-[#0D1117] to-[#0D1117] border border-amber-800/60 rounded-2xl p-5 flex items-center gap-4">
          <div className="p-3 rounded-xl bg-amber-950/60 border border-amber-800/50">
            <Trophy className="w-6 h-6 text-amber-400" />
          </div>
          <div>
            <div className="text-xs font-mono text-amber-500 uppercase tracking-wider font-semibold">FASTEST ALGORITHM</div>
            <div className="text-xl font-mono font-bold text-amber-300 mt-0.5">{winner.algorithm}</div>
            <div className="text-xs font-mono text-slate-400 mt-0.5">
              {winner.time_ms.toFixed(4)} ms &bull; {winner.comparisons.toLocaleString()} comparisons &bull; {winner.item_count} items
            </div>
          </div>
          <div className="ml-auto text-right font-mono text-xs text-slate-500 hidden sm:block">
            <div>Time: {ALGO_META[winner.algorithm]?.time ?? '—'}</div>
            <div>Space: {ALGO_META[winner.algorithm]?.space ?? '—'}</div>
            <div>Stability: {ALGO_META[winner.algorithm]?.stability ?? '—'}</div>
          </div>
        </div>
      )}

      {data && tied && (
        <div className="bg-[#0D1117] border border-blue-800/60 rounded-2xl p-5 flex items-center gap-4">
          <Zap className="w-6 h-6 text-blue-400 shrink-0" />
          <div>
            <div className="text-xs font-mono text-blue-400 uppercase tracking-wider font-semibold">EFFECTIVE TIE DETECTED</div>
            <div className="text-sm font-mono text-slate-300 mt-0.5">Two or more algorithms produced effectively identical execution times on this dataset.</div>
          </div>
        </div>
      )}

      {/* Charts */}
      {data && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Execution Time Chart */}
          <div className="bg-[#0D1117] border border-slate-800 rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-5 border-b border-slate-800/80 pb-3">
              <Clock className="w-4 h-4 text-[#06B6D4]" />
              <span className="text-xs font-mono font-semibold text-slate-300 uppercase tracking-wider">Execution Time Comparison</span>
              <span className="ml-auto text-[11px] font-mono text-slate-500">milliseconds (lower = better)</span>
            </div>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={timeChartData} margin={{ top: 4, right: 12, left: 0, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="name" tick={{ fill: '#64748B', fontSize: 10, fontFamily: 'monospace' }} />
                <YAxis tick={{ fill: '#64748B', fontSize: 10, fontFamily: 'monospace' }} />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="Time (ms)" radius={[4, 4, 0, 0]}>
                  {timeChartData?.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Comparisons Chart */}
          <div className="bg-[#0D1117] border border-slate-800 rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-5 border-b border-slate-800/80 pb-3">
              <Hash className="w-4 h-4 text-[#06B6D4]" />
              <span className="text-xs font-mono font-semibold text-slate-300 uppercase tracking-wider">Comparison Count</span>
              <span className="ml-auto text-[11px] font-mono text-slate-500">total element comparisons</span>
            </div>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={comparisonsChartData} margin={{ top: 4, right: 12, left: 0, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="name" tick={{ fill: '#64748B', fontSize: 10, fontFamily: 'monospace' }} />
                <YAxis tick={{ fill: '#64748B', fontSize: 10, fontFamily: 'monospace' }} />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="Comparisons" radius={[4, 4, 0, 0]}>
                  {comparisonsChartData?.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Results Table */}
      {data && (
        <div className="bg-[#0D1117] border border-slate-800 rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-5 border-b border-slate-800/80 pb-3">
            <Layers className="w-4 h-4 text-[#06B6D4]" />
            <span className="text-xs font-mono font-semibold text-slate-300 uppercase tracking-wider">Detailed Comparison Table</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-500 uppercase text-[10px] tracking-wider">
                  <th className="text-left py-2 pr-4">Algorithm</th>
                  <th className="text-right py-2 pr-4">Time (ms)</th>
                  <th className="text-right py-2 pr-4">Time (µs)</th>
                  <th className="text-right py-2 pr-4">Comparisons</th>
                  <th className="text-right py-2 pr-4">Items</th>
                  <th className="text-center py-2 pr-4">Time Complexity</th>
                  <th className="text-center py-2 pr-4">Space</th>
                  <th className="text-center py-2">Stability</th>
                </tr>
              </thead>
              <tbody>
                {data.results.map((r) => {
                  const meta = ALGO_META[r.algorithm];
                  const isWinner = !tied && winner?.algorithm === r.algorithm;
                  return (
                    <tr
                      key={r.algorithm}
                      className={`border-b border-slate-800/50 transition ${isWinner ? 'bg-amber-950/10' : 'hover:bg-[#111827]/50'}`}
                    >
                      <td className="py-3 pr-4">
                        <div className="flex items-center gap-2">
                          {isWinner && <Trophy className="w-3.5 h-3.5 text-amber-400" />}
                          <span className="font-bold" style={{ color: meta?.color ?? '#94A3B8' }}>{r.algorithm}</span>
                        </div>
                      </td>
                      <td className="text-right pr-4 text-[#22D3EE] font-bold">{r.time_ms.toFixed(4)}</td>
                      <td className="text-right pr-4 text-slate-400">{r.time_us.toFixed(2)}</td>
                      <td className="text-right pr-4 text-amber-400 font-bold">{r.comparisons.toLocaleString()}</td>
                      <td className="text-right pr-4 text-slate-300">{r.item_count}</td>
                      <td className="text-center pr-4 text-slate-400">{meta?.time ?? '—'}</td>
                      <td className="text-center pr-4 text-slate-400">{meta?.space ?? '—'}</td>
                      <td className="text-center">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${meta?.stability === 'Stable' ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-800/40' : 'bg-amber-950/60 text-amber-400 border border-amber-800/40'}`}>
                          {meta?.stability ?? '—'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {!data && !loading && !error && (
        <EmptyState
          icon={Zap}
          title="BENCHMARK ARENA READY"
          description="Select a sort field and direction, then click 'RUN BENCHMARK' to simultaneously execute Merge Sort, Quick Sort, and Bubble Sort on the real catalog dataset."
          actionText="INITIATE BENCHMARK"
          onAction={handleRun}
        />
      )}
    </div>
  );
};
