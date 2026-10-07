import React, { useState } from 'react';
import {
  Search,
  Play,
  RotateCcw,
  CheckCircle2,
  Cpu,
  Info,
  LayoutGrid,
  List,
} from 'lucide-react';
import { useSearch } from '../hooks/useSearch';
import { ImageCard } from '../components/ImageCard';
import { ImageInspectModal } from '../components/ImageInspectModal';
import { ErrorState } from '../components/ErrorState';
import { EmptyState } from '../components/EmptyState';
import type { ImageRecord } from '../types';

export const SearchLabPage: React.FC = () => {
  const [algorithm, setAlgorithm] = useState<'Linear Search' | 'Binary Search'>('Linear Search');
  const [field, setField] = useState<string>('land_type');
  const [query, setQuery] = useState<string>('Forest');
  const [findAll, setFindAll] = useState<boolean>(true);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  const [inspectImage, setInspectImage] = useState<ImageRecord | null>(null);

  const { data, loading, error, executeSearch, reset } = useSearch();

  const handleRunSearch = async () => {
    if (!query.trim()) return;
    try {
      await executeSearch({
        algorithm,
        field,
        query: query.trim(),
        find_all: findAll,
      });
    } catch {
      // Handled in hook state
    }
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#06B6D4]" />
            <span className="text-xs font-mono font-semibold text-[#06B6D4] uppercase tracking-wider">
              RETRIEVAL COMPLEXITY LABORATORY
            </span>
          </div>
          <h1 className="text-2xl font-bold font-mono tracking-tight text-white mt-1">
            Search Lab
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            Execute manual Linear Search $O(n)$ and Binary Search $O(\log n)$ with exact comparison counters.
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
            onClick={handleRunSearch}
            disabled={loading || !query.trim()}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#06B6D4] hover:bg-[#22D3EE] text-[#0A0E1A] font-mono font-bold text-xs uppercase tracking-wider transition shadow-lg shadow-cyan-950/40 disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : 'fill-current'}`} />
            <span>{loading ? 'EXECUTING SEARCH...' : 'RUN SEARCH'}</span>
          </button>
        </div>
      </div>

      {/* Control Panel & Theory Specs */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Search Parameter Form */}
        <div className="lg:col-span-8 bg-[#0D1117] border border-slate-800 rounded-2xl p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <span className="text-xs font-mono font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Cpu className="w-4 h-4 text-[#06B6D4]" />
              <span>Search Parameters</span>
            </span>
            <span className="text-[11px] font-mono text-cyan-400">POST /api/search</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Algorithm Selector */}
            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-400">ALGORITHM</label>
              <select
                value={algorithm}
                onChange={(e) => setAlgorithm(e.target.value as any)}
                className="w-full px-3 py-2.5 bg-[#0A0E1A] border border-slate-800 rounded-xl text-xs font-mono text-slate-200 focus:outline-none focus:border-[#06B6D4] transition"
              >
                <option value="Linear Search">Linear Search O(n)</option>
                <option value="Binary Search">Binary Search O(log n)</option>
              </select>
            </div>

            {/* Field Selector */}
            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-400">SEARCH FIELD</label>
              <select
                value={field}
                onChange={(e) => setField(e.target.value)}
                className="w-full px-3 py-2.5 bg-[#0A0E1A] border border-slate-800 rounded-xl text-xs font-mono text-slate-200 focus:outline-none focus:border-[#06B6D4] transition"
              >
                <option value="land_type">land_type (Classification)</option>
                <option value="image_id">image_id (Primary ID)</option>
                <option value="image_name">image_name (Filename)</option>
                <option value="image_format">image_format (Format)</option>
                <option value="date">date (YYYY-MM-DD)</option>
                <option value="datetime">datetime (Timestamp)</option>
              </select>
            </div>

            {/* Target Query Input */}
            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-400">QUERY STRING</label>
              <div className="relative">
                <input
                  type="text"
                  placeholder="e.g. Forest, Water, SAT001"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleRunSearch()}
                  className="w-full px-3 py-2.5 bg-[#0A0E1A] border border-slate-800 rounded-xl text-xs font-mono text-slate-200 focus:outline-none focus:border-[#06B6D4] transition"
                />
              </div>
            </div>
          </div>

          {/* Toggle Find All Matches */}
          <div className="flex items-center justify-between pt-2">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={findAll}
                onChange={(e) => setFindAll(e.target.checked)}
                className="rounded border-slate-800 bg-[#0A0E1A] text-[#06B6D4] focus:ring-0"
              />
              <span className="text-xs font-mono text-slate-300">
                Find All Matching Occurrences (gather duplicates)
              </span>
            </label>

            {algorithm === 'Binary Search' && (
              <span className="text-[11px] font-mono text-emerald-400 flex items-center gap-1">
                <Info className="w-3.5 h-3.5" />
                Pre-condition: Auto-sorted via Merge Sort
              </span>
            )}
          </div>
        </div>

        {/* Algorithm Theory Box */}
        <div className="lg:col-span-4 bg-[#0D1117] border border-slate-800 rounded-2xl p-6 flex flex-col justify-between space-y-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">
                SEARCH THEORETICAL SPECS
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950/50 text-cyan-400 border border-cyan-800/50">
                {algorithm}
              </span>
            </div>
            <div className="text-sm font-mono font-bold text-slate-200">
              {algorithm === 'Binary Search' ? 'Logarithmic Halving' : 'Sequential Iteration'}
            </div>
          </div>

          <div className="space-y-2.5 font-mono text-xs">
            <div className="flex justify-between py-1 border-b border-slate-800/80">
              <span className="text-slate-500">Best Case:</span>
              <span className="text-emerald-400 font-bold">O(1)</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/80">
              <span className="text-slate-500">Average Case:</span>
              <span className="text-[#22D3EE] font-bold">
                {algorithm === 'Binary Search' ? 'O(log n)' : 'O(n)'}
              </span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/80">
              <span className="text-slate-500">Worst Case:</span>
              <span className="text-slate-300 font-bold">
                {algorithm === 'Binary Search' ? 'O(log n)' : 'O(n)'}
              </span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-500">Pre-sorted Requirement:</span>
              <span className={algorithm === 'Binary Search' ? 'text-amber-400 font-semibold' : 'text-slate-400'}>
                {algorithm === 'Binary Search' ? 'YES (Auto Merge-Sorted)' : 'NO'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Error state */}
      {error && !loading && (
        <ErrorState
          title="Search Execution Error"
          message={error}
          onRetry={handleRunSearch}
        />
      )}

      {/* Telemetry Panel */}
      {data && (
        <div className="bg-[#0D1117] border border-cyan-800/50 rounded-2xl p-6 space-y-6 shadow-xl relative overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-[#10B981]" />
              <span className="text-sm font-mono font-bold text-slate-100 uppercase tracking-wider">
                SEARCH TELEMETRY &bull; {data.algorithm.toUpperCase()}
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
              <span className="text-[10px] text-slate-500 uppercase block">TARGET QUERY</span>
              <span className="text-[#06B6D4] font-bold mt-1 block truncate">{data.query}</span>
            </div>

            <div className="bg-[#0A0E1A] p-3 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase block">SEARCH FIELD</span>
              <span className="text-slate-200 font-bold mt-1 block truncate">{data.field}</span>
            </div>

            <div className="bg-[#0A0E1A] p-3 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase block">MATCHES FOUND</span>
              <span className="text-[#10B981] font-bold mt-1 block">{data.matches_count}</span>
            </div>

            <div className="bg-[#0A0E1A] p-3 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase block">COMPARISONS</span>
              <span className="text-[#F59E0B] font-bold mt-1 block">{data.comparisons.toLocaleString()}</span>
            </div>

            <div className="bg-[#0A0E1A] p-3 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase block">EXECUTION TIME</span>
              <span className="text-[#22D3EE] font-bold mt-1 block">{data.time_ms.toFixed(3)} ms</span>
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
                Matching Search Results ({data.matches_count} Images)
              </h2>
              <p className="text-xs text-slate-500 font-mono">
                Matched key <span className="text-cyan-400">{data.field}</span> = <span className="text-slate-300">"{data.query}"</span> using <span className="text-slate-300">{data.algorithm}</span>.
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

          {data.results.length > 0 ? (
            viewMode === 'grid' ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {data.results.map((img) => (
                  <ImageCard
                    key={img.image_id}
                    image={img}
                    onClick={(selected) => setInspectImage(selected)}
                  />
                ))}
              </div>
            ) : (
              <div className="space-y-2">
                {data.results.map((img) => (
                  <ImageCard
                    key={img.image_id}
                    image={img}
                    viewMode="list"
                    onClick={(selected) => setInspectImage(selected)}
                  />
                ))}
              </div>
            )
          ) : (
            <div className="border border-dashed border-slate-800 bg-[#0D1117]/60 rounded-2xl p-10 text-center space-y-2 font-mono text-xs text-slate-500">
              <div className="font-bold text-slate-300 uppercase">NO MATCHES RETURNED</div>
              <p>No catalog records matched the query condition "{data.query}" for field {data.field}.</p>
            </div>
          )}
        </div>
      )}

      {/* Initial Empty State before search run */}
      {!data && !loading && !error && (
        <EmptyState
          icon={Search}
          title="AWAITING SEARCH QUERY"
          description="Select an algorithm (Linear Search or Binary Search), attribute field, and search value above, then click 'RUN SEARCH'."
          actionText="EXECUTE TARGET SEARCH"
          onAction={handleRunSearch}
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
