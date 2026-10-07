import React, { useState } from 'react';
import {
  Filter,
  Play,
  RotateCcw,
  CheckCircle2,
  Calendar,
  Layers,
  FileCode,
  LayoutGrid,
  List,
  Sparkles,
} from 'lucide-react';
import { useFilter } from '../hooks/useFilter';
import { ImageCard } from '../components/ImageCard';
import { ImageInspectModal } from '../components/ImageInspectModal';
import { ErrorState } from '../components/ErrorState';
import { EmptyState } from '../components/EmptyState';
import { Pagination } from '../components/Pagination';
import type { ImageRecord } from '../types';

export const FiltersPage: React.FC = () => {
  const [selectedLandType, setSelectedLandType] = useState<string>('All');
  const [selectedFormat, setSelectedFormat] = useState<string>('All');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');

  const [page, setPage] = useState<number>(1);
  const pageSize = 12;
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  const [inspectImage, setInspectImage] = useState<ImageRecord | null>(null);

  const { data, loading, error, executeFilter, reset } = useFilter();

  const handleApplyFilters = async () => {
    setPage(1);
    try {
      await executeFilter({
        land_type: selectedLandType !== 'All' ? selectedLandType : null,
        image_format: selectedFormat !== 'All' ? selectedFormat : null,
        start_date: startDate.trim() || null,
        end_date: endDate.trim() || null,
      });
    } catch {
      // Handled in hook state
    }
  };

  const handleResetFilters = () => {
    setSelectedLandType('All');
    setSelectedFormat('All');
    setStartDate('');
    setEndDate('');
    reset();
  };

  const landTypeChips = [
    { label: 'All Classes', value: 'All', color: '#64748B' },
    { label: 'Forest', value: 'Forest', color: '#10B981' },
    { label: 'Water', value: 'Water', color: '#0EA5E9' },
    { label: 'Agriculture', value: 'Agriculture', color: '#84CC16' },
    { label: 'Urban', value: 'Urban', color: '#94A3B8' },
    { label: 'Barren Land', value: 'Barren', color: '#F97316' },
  ];

  const formatOptions = ['All', 'JPG', 'JPEG', 'PNG', 'TIFF', 'WEBP'];

  // Pagination on returned filtered array
  const allResults = data?.results || [];
  const totalMatches = allResults.length;
  const totalPages = Math.ceil(totalMatches / pageSize) || 1;
  const paginatedResults = allResults.slice((page - 1) * pageSize, page * pageSize);

  return (
    <div className="space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#06B6D4]" />
            <span className="text-xs font-mono font-semibold text-[#06B6D4] uppercase tracking-wider">
              MULTI-CRITERIA PREDICATE ENGINE
            </span>
          </div>
          <h1 className="text-2xl font-bold font-mono tracking-tight text-white mt-1">
            Smart Filters
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            Execute single-pass $O(n)$ predicate filtering across land classification, image format, and acquisition dates.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {data && (
            <button
              onClick={handleResetFilters}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-[#0D1117] border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-200 text-xs font-mono transition"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>RESET</span>
            </button>
          )}

          <button
            onClick={handleApplyFilters}
            disabled={loading}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#06B6D4] hover:bg-[#22D3EE] text-[#0A0E1A] font-mono font-bold text-xs uppercase tracking-wider transition shadow-lg shadow-cyan-950/40 disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : 'fill-current'}`} />
            <span>{loading ? 'APPLYING FILTERS...' : 'APPLY FILTERS'}</span>
          </button>
        </div>
      </div>

      {/* Predicate Pipeline Concept Banner */}
      <div className="bg-[#0D1117] border border-slate-800 rounded-2xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono">
        <div className="flex items-center gap-2 text-slate-400">
          <Sparkles className="w-4 h-4 text-[#06B6D4]" />
          <span>Predicate Evaluation:</span>
        </div>
        <div className="flex items-center gap-2 text-slate-300 font-bold">
          <span className="px-2.5 py-1 rounded bg-[#111827] border border-slate-800 text-slate-400">Catalog Record</span>
          <span className="text-cyan-400">&rarr;</span>
          <span className="px-2.5 py-1 rounded bg-[#111827] border border-cyan-800/60 text-cyan-300">Predicate Conditions (P_land &and; P_fmt &and; P_date)</span>
          <span className="text-cyan-400">&rarr;</span>
          <span className="px-2.5 py-1 rounded bg-emerald-950/50 border border-emerald-800/60 text-emerald-300">Matching Set</span>
        </div>
        <span className="text-[10px] text-slate-500">SINGLE-PASS O(n)</span>
      </div>

      {/* Filter Chips & Inputs Panel */}
      <div className="bg-[#0D1117] border border-slate-800 rounded-2xl p-6 space-y-6">
        {/* Land Type Filter Chips */}
        <div className="space-y-3">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400">
            <span className="flex items-center gap-1.5 font-semibold uppercase text-slate-300">
              <Layers className="w-3.5 h-3.5 text-[#06B6D4]" />
              <span>Land Classification Filter Chips</span>
            </span>
            <span>ACTIVE: <strong className="text-cyan-400">{selectedLandType}</strong></span>
          </div>

          <div className="flex flex-wrap gap-2">
            {landTypeChips.map((chip) => {
              const isSelected = selectedLandType === chip.value;
              return (
                <button
                  key={chip.value}
                  type="button"
                  onClick={() => setSelectedLandType(chip.value)}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-mono border transition-all ${
                    isSelected
                      ? 'bg-cyan-950/40 border-cyan-500/80 text-cyan-200 shadow-md shadow-cyan-950/30'
                      : 'bg-[#0A0E1A] border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                  }`}
                >
                  <span
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: chip.color }}
                  />
                  <span>{chip.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Format & Date Range Row */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 border-t border-slate-800/80">
          {/* Image Format */}
          <div className="space-y-1.5">
            <label className="text-xs font-mono text-slate-400 flex items-center gap-1.5">
              <FileCode className="w-3.5 h-3.5 text-sky-400" />
              <span>IMAGE FORMAT EXTENSION</span>
            </label>
            <select
              value={selectedFormat}
              onChange={(e) => setSelectedFormat(e.target.value)}
              className="w-full px-3 py-2.5 bg-[#0A0E1A] border border-slate-800 rounded-xl text-xs font-mono text-slate-200 focus:outline-none focus:border-[#06B6D4] transition"
            >
              {formatOptions.map((fmt) => (
                <option key={fmt} value={fmt}>
                  {fmt === 'All' ? 'All Formats' : fmt}
                </option>
              ))}
            </select>
          </div>

          {/* Start Date */}
          <div className="space-y-1.5">
            <label className="text-xs font-mono text-slate-400 flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-emerald-400" />
              <span>START DATE (MIN BOUND)</span>
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-3 py-2 bg-[#0A0E1A] border border-slate-800 rounded-xl text-xs font-mono text-slate-200 focus:outline-none focus:border-[#06B6D4] transition"
            />
          </div>

          {/* End Date */}
          <div className="space-y-1.5">
            <label className="text-xs font-mono text-slate-400 flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-emerald-400" />
              <span>END DATE (MAX BOUND)</span>
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full px-3 py-2 bg-[#0A0E1A] border border-slate-800 rounded-xl text-xs font-mono text-slate-200 focus:outline-none focus:border-[#06B6D4] transition"
            />
          </div>
        </div>
      </div>

      {/* Error state */}
      {error && !loading && (
        <ErrorState
          title="Filter Predicate Error"
          message={error}
          onRetry={handleApplyFilters}
        />
      )}

      {/* Filter Telemetry Panel */}
      {data && (
        <div className="bg-[#0D1117] border border-cyan-800/50 rounded-2xl p-6 space-y-6 shadow-xl relative overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-[#10B981]" />
              <span className="text-sm font-mono font-bold text-slate-100 uppercase tracking-wider">
                PREDICATE EVALUATION TELEMETRY
              </span>
            </div>
            <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-emerald-950/60 text-emerald-400 border border-emerald-800/60 font-semibold">
              EVALUATION COMPLETE
            </span>
          </div>

          {/* Telemetry Metric Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
            <div className="bg-[#0A0E1A] p-3 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase block">RECORDS MATCHED</span>
              <span className="text-[#10B981] font-bold mt-1 block text-lg">{data.matches_count}</span>
            </div>

            <div className="bg-[#0A0E1A] p-3 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase block">PREDICATE COMPARISONS</span>
              <span className="text-[#F59E0B] font-bold mt-1 block text-lg">{data.comparisons.toLocaleString()}</span>
            </div>

            <div className="bg-[#0A0E1A] p-3 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase block">EXECUTION SCAN TIME</span>
              <span className="text-[#22D3EE] font-bold mt-1 block text-lg">{data.time_ms.toFixed(3)} ms</span>
            </div>

            <div className="bg-[#0A0E1A] p-3 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase block">ACTIVE CRITERIA</span>
              <span className="text-slate-200 font-bold mt-1 block text-xs truncate">
                {selectedLandType} &bull; {selectedFormat}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Filtered Results */}
      {data && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold font-mono tracking-tight text-slate-100 uppercase">
                Filtered Imagery Results ({data.matches_count} Records)
              </h2>
              <p className="text-xs text-slate-500 font-mono">
                Showing page {page} of {totalPages}
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

          {paginatedResults.length > 0 ? (
            <>
              {viewMode === 'grid' ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {paginatedResults.map((img) => (
                    <ImageCard
                      key={img.image_id}
                      image={img}
                      onClick={(selected) => setInspectImage(selected)}
                    />
                  ))}
                </div>
              ) : (
                <div className="space-y-2">
                  {paginatedResults.map((img) => (
                    <ImageCard
                      key={img.image_id}
                      image={img}
                      viewMode="list"
                      onClick={(selected) => setInspectImage(selected)}
                    />
                  ))}
                </div>
              )}

              {/* Pagination */}
              <div className="pt-4">
                <Pagination
                  currentPage={page}
                  totalPages={totalPages}
                  onPageChange={(newPage) => setPage(newPage)}
                />
              </div>
            </>
          ) : (
            <div className="border border-dashed border-slate-800 bg-[#0D1117]/60 rounded-2xl p-10 text-center space-y-2 font-mono text-xs text-slate-500">
              <div className="font-bold text-slate-300 uppercase">NO IMAGES MATCH CRITERIA</div>
              <p>Try broadening your land classification chips, format selector, or date range.</p>
            </div>
          )}
        </div>
      )}

      {/* Initial Empty State before applying filters */}
      {!data && !loading && !error && (
        <EmptyState
          icon={Filter}
          title="AWAITING PREDICATE CRITERIA"
          description="Select land classification chips, format, or date boundary bounds above, then click 'APPLY FILTERS' to scan the catalog."
          actionText="EVALUATE PREDICATES NOW"
          onAction={handleApplyFilters}
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
