import React, { useState } from 'react';
import {
  ArrowDownUp,
  Play,
  RotateCcw,
  Cpu,
  CheckCircle2,
  LayoutGrid,
  List,
} from 'lucide-react';
import { useSort } from '../hooks/useSort';
import { ImageCard } from '../components/ImageCard';
import { ImageInspectModal } from '../components/ImageInspectModal';
import { ErrorState } from '../components/ErrorState';
import { EmptyState } from '../components/EmptyState';
import type { ImageRecord } from '../types';

export const SortLabPage: React.FC = () => {
  const [algorithm, setAlgorithm] = useState<'Merge Sort' | 'Quick Sort' | 'Bubble Sort'>('Merge Sort');
  const [field, setField] = useState<string>('datetime');
  const [ascending, setAscending] = useState<boolean>(true);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  const [inspectImage, setInspectImage] = useState<ImageRecord | null>(null);

  const { data, loading, error, executeSort, reset } = useSort();

  const handleRunSort = async () => {
    try {
      await executeSort({
        algorithm,
        field,
        ascending,
      });
    } catch {
      // Error handled in hook state
    }
  };

  const getComplexity = (algo: string) => {
    switch (algo) {
      case 'Merge Sort':
        return { time: 'O(n log n)', space: 'O(n)', stability: 'Stable', type: 'Divide & Conquer' };
      case 'Quick Sort':
        return { time: 'O(n log n) avg', space: 'O(log n)', stability: 'Unstable', type: 'Partitioning' };
      case 'Bubble Sort':
        return { time: 'O(n²)', space: 'O(1)', stability: 'Stable', type: 'Comparison Exchange' };
      default:
        return { time: 'O(n log n)', space: 'O(1)', stability: 'Unknown', type: 'Sorting' };
    }
  };

  const currentComplexity = getComplexity(algorithm);

  return (
    <div className="space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#06B6D4]" />
            <span className="text-xs font-mono font-semibold text-[#06B6D4] uppercase tracking-wider">
              ALGORITHMIC EXECUTION ENGINE
            </span>
          </div>
          <h1 className="text-2xl font-bold font-mono tracking-tight text-white mt-1">
            Sort Lab
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            Execute manual Merge Sort, Quick Sort, and Bubble Sort on catalog imagery without library abstractions.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {data && (
            <button
              onClick={reset}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-[#0D1117] border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-200 text-xs font-mono transition"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>RESET</span>
            </button>
          )}

          <button
            onClick={handleRunSort}
            disabled={loading}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#06B6D4] hover:bg-[#22D3EE] text-[#0A0E1A] font-mono font-bold text-xs uppercase tracking-wider transition shadow-lg shadow-cyan-950/40 disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : 'fill-current'}`} />
            <span>{loading ? 'EXECUTING SORT...' : 'RUN SORT'}</span>
          </button>
        </div>
      </div>

      {/* Control Panel & Theory Specs */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Controls Form */}
        <div className="lg:col-span-8 bg-[#0D1117] border border-slate-800 rounded-2xl p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <span className="text-xs font-mono font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Cpu className="w-4 h-4 text-[#06B6D4]" />
              <span>Algorithm Parameters</span>
            </span>
            <span className="text-[11px] font-mono text-cyan-400">POST /api/sort</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Algorithm Selector */}
            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-400">SORT ALGORITHM</label>
              <select
                value={algorithm}
                onChange={(e) => setAlgorithm(e.target.value as any)}
                className="w-full px-3 py-2.5 bg-[#0A0E1A] border border-slate-800 rounded-xl text-xs font-mono text-slate-200 focus:outline-none focus:border-[#06B6D4] transition"
              >
                <option value="Merge Sort">Merge Sort (O(n log n))</option>
                <option value="Quick Sort">Quick Sort (Partitioning)</option>
                <option value="Bubble Sort">Bubble Sort (O(n²))</option>
              </select>
            </div>

            {/* Field Selector */}
            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-400">SORT KEY FIELD</label>
              <select
                value={field}
                onChange={(e) => setField(e.target.value)}
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

            {/* Direction */}
            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-400">ORDER DIRECTION</label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setAscending(true)}
                  className={`py-2 rounded-xl text-xs font-mono font-semibold border transition ${
                    ascending
                      ? 'bg-cyan-950/40 border-cyan-800/80 text-[#22D3EE]'
                      : 'bg-[#0A0E1A] border-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  ASC (&uarr;)
                </button>
                <button
                  type="button"
                  onClick={() => setAscending(false)}
                  className={`py-2 rounded-xl text-xs font-mono font-semibold border transition ${
                    !ascending
                      ? 'bg-cyan-950/40 border-cyan-800/80 text-[#22D3EE]'
                      : 'bg-[#0A0E1A] border-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  DESC (&darr;)
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Algorithm Complexity Specs Box */}
        <div className="lg:col-span-4 bg-[#0D1117] border border-slate-800 rounded-2xl p-6 flex flex-col justify-between space-y-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">
                THEORETICAL SPECS
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950/50 text-cyan-400 border border-cyan-800/50">
                {algorithm}
              </span>
            </div>
            <div className="text-sm font-mono font-bold text-slate-200">
              {currentComplexity.type}
            </div>
          </div>

          <div className="space-y-2.5 font-mono text-xs">
            <div className="flex justify-between py-1 border-b border-slate-800/80">
              <span className="text-slate-500">Time Complexity:</span>
              <span className="text-[#22D3EE] font-bold">{currentComplexity.time}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/80">
              <span className="text-slate-500">Aux Space:</span>
              <span className="text-slate-300">{currentComplexity.space}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/80">
              <span className="text-slate-500">Stability:</span>
              <span className={currentComplexity.stability === 'Stable' ? 'text-emerald-400' : 'text-amber-400'}>
                {currentComplexity.stability}
              </span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-500">Implementation:</span>
              <span className="text-slate-400">Pure Python / No Built-ins</span>
            </div>
          </div>
        </div>
      </div>

      {/* Error state */}
      {error && !loading && (
        <ErrorState
          title="Algorithm Execution Error"
          message={error}
          onRetry={handleRunSort}
        />
      )}

      {/* Real Execution Telemetry Panel */}
      {data && (
        <div className="bg-[#0D1117] border border-cyan-800/50 rounded-2xl p-6 space-y-6 shadow-xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-32 bg-cyan-500/5 blur-3xl pointer-events-none" />

          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-[#10B981]" />
              <span className="text-sm font-mono font-bold text-slate-100 uppercase tracking-wider">
                EXECUTION TELEMETRY &bull; {data.algorithm.toUpperCase()}
              </span>
            </div>
            <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-emerald-950/60 text-emerald-400 border border-emerald-800/60 font-semibold">
              STATUS: NOMINAL
            </span>
          </div>

          {/* Telemetry Metric Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 font-mono text-xs">
            <div className="bg-[#0A0E1A] p-3 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase block">ALGORITHM</span>
              <span className="text-slate-200 font-bold mt-1 block truncate">{data.algorithm}</span>
            </div>

            <div className="bg-[#0A0E1A] p-3 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase block">SORT FIELD</span>
              <span className="text-[#06B6D4] font-bold mt-1 block truncate">{data.field}</span>
            </div>

            <div className="bg-[#0A0E1A] p-3 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase block">DIRECTION</span>
              <span className="text-slate-200 font-bold mt-1 block">{data.order}</span>
            </div>

            <div className="bg-[#0A0E1A] p-3 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase block">ITEMS SORTED</span>
              <span className="text-slate-200 font-bold mt-1 block">{data.total_count}</span>
            </div>

            <div className="bg-[#0A0E1A] p-3 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase block">COMPARISONS</span>
              <span className="text-[#F59E0B] font-bold mt-1 block">{data.comparisons.toLocaleString()}</span>
            </div>

            <div className="bg-[#0A0E1A] p-3 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase block">EXECUTION TIME</span>
              <span className="text-[#10B981] font-bold mt-1 block">{data.time_ms.toFixed(3)} ms</span>
            </div>
          </div>
        </div>
      )}

      {/* Results Section */}
      {data && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold font-mono tracking-tight text-slate-100 uppercase">
                Ranked Sorting Results ({data.total_count} Records)
              </h2>
              <p className="text-xs text-slate-500 font-mono">
                Sorted by <span className="text-cyan-400">{data.field}</span> in <span className="text-slate-300">{data.order.toLowerCase()}</span> sequence.
              </p>
            </div>

            <div className="flex items-center bg-[#0D1117] border border-slate-800 rounded-lg p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-1.5 rounded-md transition ${
                  viewMode === 'grid'
                    ? 'bg-slate-800 text-cyan-400'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title="Grid View"
              >
                <LayoutGrid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-1.5 rounded-md transition ${
                  viewMode === 'list'
                    ? 'bg-slate-800 text-cyan-400'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title="List View"
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>

          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {data.results.map((img, idx) => (
                <div key={img.image_id} className="relative group">
                  <div className="absolute top-2 left-2 z-10 px-2 py-0.5 rounded bg-cyan-950/90 text-cyan-300 border border-cyan-800/80 font-mono text-[10px] font-bold">
                    #{idx + 1}
                  </div>
                  <ImageCard
                    image={img}
                    onClick={(selected) => setInspectImage(selected)}
                  />
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-2">
              {data.results.map((img, idx) => (
                <div key={img.image_id} className="flex items-center gap-3">
                  <span className="w-8 text-center font-mono text-xs text-slate-500 font-bold shrink-0">
                    #{idx + 1}
                  </span>
                  <div className="flex-1">
                    <ImageCard
                      image={img}
                      viewMode="list"
                      onClick={(selected) => setInspectImage(selected)}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Initial Empty State before running sort */}
      {!data && !loading && !error && (
        <EmptyState
          icon={ArrowDownUp}
          title="AWAITING SORT EXECUTION"
          description="Select an algorithm (Merge Sort, Quick Sort, Bubble Sort), target metadata key, and direction above, then click 'RUN SORT' to trigger live execution."
          actionText="TRIGGER INITIAL SORT"
          onAction={handleRunSort}
        />
      )}

      {/* Image Inspection Modal */}
      <ImageInspectModal
        image={inspectImage}
        onClose={() => setInspectImage(null)}
      />
    </div>
  );
};
