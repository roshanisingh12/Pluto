import React, { useState, useEffect } from 'react';
import { RefreshCw, HardDrive, AlertTriangle, Layers, PieChart } from 'lucide-react';
import { getStatistics } from '../api/client';
import type { StatisticsResponse } from '../types';

export const StatisticsPage: React.FC = () => {
  const [stats, setStats] = useState<StatisticsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getStatistics();
      setStats(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to fetch catalog statistics';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Catalog Statistics &amp; Analytics</h1>
          <p className="text-sm text-slate-400">
            Real catalog metrics computed by the Python backend via <code>GET /api/statistics</code>.
          </p>
        </div>
        <button
          onClick={fetchStats}
          disabled={loading}
          className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 text-sm font-medium self-start sm:self-auto"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {loading && (
        <div className="py-16 text-center text-slate-400 space-y-3">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto text-emerald-400" />
          <p className="text-sm">Calculating dataset statistics...</p>
        </div>
      )}

      {error && !loading && (
        <div className="p-6 rounded-xl bg-rose-950/30 border border-rose-800 text-center space-y-2">
          <AlertTriangle className="w-8 h-8 text-rose-400 mx-auto" />
          <div className="text-base font-semibold text-rose-300">Statistics Calculation Failed</div>
          <p className="text-xs text-rose-400">{error}</p>
        </div>
      )}

      {stats && !loading && (
        <div className="space-y-6">
          {/* Top Key Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5">
              <span className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Total Imagery</span>
              <div className="text-3xl font-bold font-mono text-slate-100 mt-2">{stats.total_images}</div>
              <p className="text-[11px] text-slate-400 mt-1">Catalog items</p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5">
              <span className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Complete Metadata</span>
              <div className="text-3xl font-bold font-mono text-emerald-400 mt-2">{stats.complete_metadata_count}</div>
              <p className="text-[11px] text-slate-400 mt-1">All fields present</p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5">
              <span className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Incomplete Metadata</span>
              <div className="text-3xl font-bold font-mono text-amber-400 mt-2">{stats.incomplete_metadata_count}</div>
              <p className="text-[11px] text-slate-400 mt-1">Pending user review</p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5">
              <span className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Total Storage Size</span>
              <div className="text-2xl font-bold font-mono text-sky-400 mt-2">
                {formatBytes(stats.storage_stats.total_bytes)}
              </div>
              <p className="text-[11px] text-slate-400 mt-1">
                Avg: {formatBytes(stats.storage_stats.avg_bytes)}
              </p>
            </div>
          </div>

          {/* Breakdown cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Land Classification Distribution */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
              <h3 className="text-sm font-semibold text-slate-200 mb-4 flex items-center space-x-2">
                <Layers className="w-4 h-4 text-emerald-400" />
                <span>Land Classification Distribution</span>
              </h3>
              <div className="space-y-3">
                {Object.entries(stats.land_type_counts).map(([type, count]) => {
                  const pct = stats.total_images > 0 ? (count / stats.total_images) * 100 : 0;
                  return (
                    <div key={type} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-slate-300 font-medium">{type}</span>
                        <span className="text-slate-400 font-mono">
                          {count} ({pct.toFixed(0)}%)
                        </span>
                      </div>
                      <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                        <div
                          className="bg-emerald-500 h-2 rounded-full transition-all"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Image Format Distribution & Storage */}
            <div className="space-y-6">
              <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
                <h3 className="text-sm font-semibold text-slate-200 mb-4 flex items-center space-x-2">
                  <PieChart className="w-4 h-4 text-sky-400" />
                  <span>Image Format Distribution</span>
                </h3>
                <div className="grid grid-cols-3 gap-2">
                  {Object.entries(stats.format_counts).map(([fmt, count]) => (
                    <div key={fmt} className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-center">
                      <div className="text-xs text-slate-500 font-mono">{fmt}</div>
                      <div className="text-lg font-bold text-slate-200 font-mono mt-0.5">{count}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
                <h3 className="text-sm font-semibold text-slate-200 mb-4 flex items-center space-x-2">
                  <HardDrive className="w-4 h-4 text-purple-400" />
                  <span>Filesystem Storage Breakdown</span>
                </h3>
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <span className="text-slate-500">Min File Size</span>
                    <div className="font-mono text-slate-200 mt-1 font-semibold">
                      {formatBytes(stats.storage_stats.min_bytes)}
                    </div>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <span className="text-slate-500">Max File Size</span>
                    <div className="font-mono text-slate-200 mt-1 font-semibold">
                      {formatBytes(stats.storage_stats.max_bytes)}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
