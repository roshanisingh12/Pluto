import React, { useState } from 'react';
import { Database, CheckCircle2, AlertTriangle, RefreshCw, Layers, Cpu } from 'lucide-react';
import { loadSampleDataset } from '../api/client';
import type { HealthResponse, DatasetLoadResponse } from '../types';

interface OverviewPageProps {
  health: HealthResponse | null;
  healthLoading: boolean;
  healthError: string | null;
  onRefreshHealth: () => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({
  health,
  healthLoading,
  healthError,
  onRefreshHealth,
}) => {
  const [loadingDataset, setLoadingDataset] = useState(false);
  const [datasetResult, setDatasetResult] = useState<DatasetLoadResponse | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const isOnline = health !== null && health.status === 'ok';
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  const handleLoadSamples = async () => {
    setLoadingDataset(true);
    setActionError(null);
    try {
      const res = await loadSampleDataset();
      setDatasetResult(res);
      onRefreshHealth();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load sample dataset';
      setActionError(msg);
    } finally {
      setLoadingDataset(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Top Hero Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-emerald-950/40 border border-slate-800 rounded-2xl p-6 sm:p-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Phase 1 Foundation
              </span>
              <span className="text-xs text-slate-400 font-mono">VITE_API_BASE_URL: {apiBaseUrl}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
              System Health &amp; Backend Integration
            </h1>
            <p className="text-sm text-slate-400 mt-1 max-w-2xl">
              Verifying live communication between React + TypeScript + Vite frontend and the FastAPI backend,
              connecting existing Python metadata services and pure DSA algorithms.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={onRefreshHealth}
              disabled={healthLoading}
              id="btn-recheck-health"
              className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium border border-slate-700 transition disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${healthLoading ? 'animate-spin' : ''}`} />
              <span>Ping Health</span>
            </button>
            <button
              onClick={handleLoadSamples}
              disabled={loadingDataset || !isOnline}
              id="btn-load-dataset"
              className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium transition shadow-lg shadow-emerald-900/40 disabled:opacity-50"
            >
              <Database className="w-4 h-4" />
              <span>{loadingDataset ? 'Loading Samples...' : 'Load Sample Dataset'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Health Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Main Status */}
        <div
          id="status-card-health"
          className={`rounded-xl border p-6 transition-all ${
            healthLoading
              ? 'bg-slate-900/50 border-slate-800'
              : isOnline
              ? 'bg-emerald-950/20 border-emerald-800/60 shadow-lg shadow-emerald-950/30'
              : 'bg-rose-950/20 border-rose-800/60 shadow-lg shadow-rose-950/30'
          }`}
        >
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">
              Connection Status
            </span>
            {isOnline ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            ) : (
              <AlertTriangle className="w-5 h-5 text-rose-400" />
            )}
          </div>
          <div className="text-2xl font-bold tracking-wider mb-2">
            {healthLoading ? (
              <span className="text-slate-400">CHECKING...</span>
            ) : isOnline ? (
              <span className="text-emerald-400">SYSTEM ONLINE</span>
            ) : (
              <span className="text-rose-400">BACKEND OFFLINE</span>
            )}
          </div>
          <p className="text-xs text-slate-400">
            {isOnline
              ? `FastAPI responded from ${apiBaseUrl}/api/health`
              : healthError || 'Backend unreachable. Verify FastAPI server is running on HOST:PORT.'}
          </p>
        </div>

        {/* Catalog Count */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">
              Cataloged Images
            </span>
            <Database className="w-5 h-5 text-sky-400" />
          </div>
          <div className="text-3xl font-mono font-bold text-slate-100 mb-1">
            {health ? health.catalog_count : '—'}
          </div>
          <p className="text-xs text-slate-400">
            Indexed in memory &amp; ImageHashTable O(1)
          </p>
        </div>

        {/* Backend Info */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">
              Backend Version
            </span>
            <Cpu className="w-5 h-5 text-purple-400" />
          </div>
          <div className="text-lg font-semibold text-slate-100 mb-1">
            {health ? `${health.app}` : 'FastAPI REST Layer'}
          </div>
          <p className="text-xs text-slate-400 font-mono">
            Version: {health ? health.version : 'Unknown'}
          </p>
        </div>
      </div>

      {/* Dataset Load Notification */}
      {datasetResult && (
        <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-800 text-emerald-300 text-sm flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            <span>
              {datasetResult.message} Newly loaded: <strong>{datasetResult.loaded_count}</strong>. Total in catalog: <strong>{datasetResult.total_catalog_count}</strong>.
            </span>
          </div>
          <button
            onClick={() => setDatasetResult(null)}
            className="text-xs text-emerald-400 hover:text-emerald-200 underline ml-4"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Action Error Notification */}
      {actionError && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800 text-rose-300 text-sm flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
            <span>{actionError}</span>
          </div>
          <button
            onClick={() => setActionError(null)}
            className="text-xs text-rose-400 hover:text-rose-200 underline ml-4"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Architecture Flow Card */}
      <div className="bg-slate-900/30 border border-slate-800 rounded-xl p-6">
        <h3 className="text-base font-semibold text-slate-200 mb-4 flex items-center space-x-2">
          <Layers className="w-5 h-5 text-emerald-400" />
          <span>Integrated Pipeline Architecture</span>
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 text-center">
          <div className="p-4 rounded-lg bg-slate-900 border border-slate-800">
            <div className="text-xs font-semibold text-emerald-400">FRONTEND</div>
            <div className="text-sm font-bold text-slate-200 mt-1">React + TS + Vite</div>
            <div className="text-xs text-slate-400 mt-1">Tailwind + Axios</div>
          </div>
          <div className="flex items-center justify-center text-slate-600 font-mono">&rarr;</div>
          <div className="p-4 rounded-lg bg-slate-900 border border-slate-800">
            <div className="text-xs font-semibold text-sky-400">API GATEWAY</div>
            <div className="text-sm font-bold text-slate-200 mt-1">FastAPI Backend</div>
            <div className="text-xs text-slate-400 mt-1">CORS &bull; Pydantic</div>
          </div>
          <div className="flex items-center justify-center text-slate-600 font-mono">&rarr;</div>
          <div className="p-4 rounded-lg bg-slate-900 border border-slate-800">
            <div className="text-xs font-semibold text-purple-400">DOMAIN ENGINE</div>
            <div className="text-sm font-bold text-slate-200 mt-1">Python Services &amp; DSA</div>
            <div className="text-xs text-slate-400 mt-1">Merge/Quick &bull; Hashing</div>
          </div>
        </div>
      </div>
    </div>
  );
};
