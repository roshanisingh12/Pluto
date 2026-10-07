import React, { useState, useEffect, useCallback } from 'react';
import {
  Database,
  Layers,
  HardDrive,
  Cpu,
  RefreshCw,
  Clock,
  Sparkles,
  ArrowRight,
  Compass,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { getStatistics, getImages, loadSampleDataset } from '../api/client';
import type { StatisticsResponse, ImageRecord, DatasetLoadResponse } from '../types';
import { MetricCard } from '../components/MetricCard';
import { ImageCard } from '../components/ImageCard';
import { ImageInspectModal } from '../components/ImageInspectModal';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { ErrorState } from '../components/ErrorState';

interface MissionControlPageProps {
  onCatalogMutated?: () => void;
}

export const MissionControlPage: React.FC<MissionControlPageProps> = ({
  onCatalogMutated,
}) => {
  const [stats, setStats] = useState<StatisticsResponse | null>(null);
  const [recentImages, setRecentImages] = useState<ImageRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Sample load state
  const [loadingSample, setLoadingSample] = useState<boolean>(false);
  const [sampleResult, setSampleResult] = useState<DatasetLoadResponse | null>(null);

  // Selected image for modal
  const [inspectImage, setInspectImage] = useState<ImageRecord | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsRes, imagesRes] = await Promise.all([
        getStatistics(),
        getImages({ limit: 4 }),
      ]);
      setStats(statsRes);
      setRecentImages(imagesRes.items);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load Mission Control data';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleLoadSample = async () => {
    setLoadingSample(true);
    setSampleResult(null);
    try {
      const res = await loadSampleDataset();
      setSampleResult(res);
      await fetchData();
      if (onCatalogMutated) onCatalogMutated();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Sample ingestion failed';
      setError(msg);
    } finally {
      setLoadingSample(false);
    }
  };

  const formatStorageSize = (bytes: number) => {
    if (!bytes) return '0 MB';
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
  };

  // Land type color mapping
  const landColors: Record<string, string> = {
    Forest: '#10B981',
    Water: '#0EA5E9',
    Agriculture: '#84CC16',
    Urban: '#94A3B8',
    Barren_Land: '#F97316',
    Barren: '#F97316',
    Other: '#64748B',
  };

  const activeLandTypesCount = stats
    ? Object.values(stats.land_type_counts).filter((c) => c > 0).length
    : 0;

  return (
    <div className="space-y-8">
      {/* Top Banner / Mission Status */}
      <div className="bg-[#0D1117] border border-slate-800 rounded-2xl p-6 relative overflow-hidden flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-xl">
        <div className="space-y-1.5 relative z-10">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#06B6D4] animate-ping" />
            <span className="text-xs font-mono font-semibold text-[#06B6D4] uppercase tracking-wider">
              ORBITAL SATELLITE MISSION CONTROL
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold font-mono tracking-tight text-white">
            Primary Intelligence Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 max-w-2xl">
            Real-time telemetry, DeepGlobe satellite imagery cataloging, and manual DSA algorithm engine.
          </p>
        </div>

        <div className="flex items-center gap-3 relative z-10 shrink-0">
          <button
            onClick={() => fetchData()}
            disabled={loading}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#111827] border border-slate-800 hover:border-slate-700 text-slate-300 text-xs font-mono transition disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>SYNC DATA</span>
          </button>

          <button
            onClick={handleLoadSample}
            disabled={loadingSample}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#06B6D4] hover:bg-[#22D3EE] text-[#0A0E1A] text-xs font-mono font-bold transition shadow-lg shadow-cyan-950/40 disabled:opacity-50"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{loadingSample ? 'INGESTING...' : 'LOAD SAMPLE DATASET'}</span>
          </button>
        </div>
      </div>

      {/* Dataset Load Notification */}
      {sampleResult && (
        <div className="p-4 rounded-xl bg-cyan-950/40 border border-cyan-800/80 text-cyan-300 text-xs font-mono flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400" />
            <span>
              {sampleResult.message} Newly loaded: <strong>{sampleResult.loaded_count}</strong>. Total in catalog: <strong>{sampleResult.total_catalog_count}</strong>.
            </span>
          </div>
          <button
            onClick={() => setSampleResult(null)}
            className="text-xs text-cyan-400 hover:text-white underline ml-4"
          >
            DISMISS
          </button>
        </div>
      )}

      {/* Error state */}
      {error && !loading && (
        <ErrorState message={error} onRetry={fetchData} />
      )}

      {/* Loading Skeletons */}
      {loading && !stats && (
        <div className="space-y-6">
          <LoadingSkeleton type="metric" count={4} />
          <LoadingSkeleton type="image-grid" count={4} />
        </div>
      )}

      {/* KPI Cards */}
      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            label="Total Images"
            value={stats.total_images}
            subValue="Indexed in ImageHashTable"
            badge="O(1) ACCESS"
            icon={Database}
            accentColor="#06B6D4"
          />

          <MetricCard
            label="Land Types"
            value={`${activeLandTypesCount} / 5`}
            subValue="DeepGlobe Classifications"
            icon={Layers}
            accentColor="#10B981"
          />

          <MetricCard
            label="Dataset Size"
            value={formatStorageSize(stats.storage_stats.total_bytes)}
            subValue={`Avg: ${formatStorageSize(stats.storage_stats.avg_bytes)}`}
            icon={HardDrive}
            accentColor="#3B82F6"
          />

          <MetricCard
            label="Algorithms"
            value="6 MANUAL"
            subValue="Merge, Quick, Bubble, Hashing"
            badge="DSA ENGINE"
            icon={Cpu}
            accentColor="#F59E0B"
          />
        </div>
      )}

      {/* Middle Grid: Land Type Distribution & Telemetry Run */}
      {stats && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Land Type Distribution */}
          <div className="lg:col-span-2 bg-[#0D1117] border border-slate-800 rounded-2xl p-6 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold font-mono uppercase tracking-wider text-slate-200">
                  Land Type Classification Distribution
                </h2>
                <p className="text-xs text-slate-500 font-mono">
                  Spectral classification distribution across active catalog
                </p>
              </div>
              <span className="text-xs font-mono text-cyan-400 bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-800/40">
                {stats.total_images} IMAGES
              </span>
            </div>

            {/* Visual stacked distribution bar */}
            {stats.total_images > 0 ? (
              <div className="space-y-4">
                <div className="h-4 w-full bg-[#0A0E1A] rounded-full overflow-hidden flex border border-slate-800">
                  {Object.entries(stats.land_type_counts).map(([type, count]) => {
                    if (count === 0) return null;
                    const pct = (count / stats.total_images) * 100;
                    const color = landColors[type] || '#64748B';
                    return (
                      <div
                        key={type}
                        style={{ width: `${pct}%`, backgroundColor: color }}
                        title={`${type}: ${count} (${pct.toFixed(1)}%)`}
                        className="h-full transition-all hover:opacity-85"
                      />
                    );
                  })}
                </div>

                {/* Legend and percentage list */}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2">
                  {Object.entries(stats.land_type_counts).map(([type, count]) => {
                    const pct = stats.total_images > 0 ? (count / stats.total_images) * 100 : 0;
                    const color = landColors[type] || '#64748B';
                    return (
                      <div
                        key={type}
                        className="p-3 rounded-xl bg-[#111827] border border-slate-800/80 flex items-center justify-between"
                      >
                        <div className="flex items-center gap-2">
                          <span
                            className="w-2.5 h-2.5 rounded-full shrink-0"
                            style={{ backgroundColor: color }}
                          />
                          <span className="text-xs font-mono text-slate-300">
                            {type.replace('_Land', '')}
                          </span>
                        </div>
                        <div className="text-xs font-mono font-bold text-slate-200">
                          {count}{' '}
                          <span className="text-slate-500 font-normal">
                            ({pct.toFixed(0)}%)
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <div className="py-8 text-center text-xs font-mono text-slate-500">
                NO LAND CLASSIFICATION DATA LOADED YET. CLICK "LOAD SAMPLE DATASET" ABOVE.
              </div>
            )}
          </div>

          {/* Last Algorithm Run / Telemetry Status */}
          <div className="bg-[#0D1117] border border-slate-800 rounded-2xl p-6 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">
                  Algorithm Execution
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                  BENCHMARK TELEMETRY
                </span>
              </div>

              {/* Requirement: Last Algorithm Run empty state */}
              <div className="border border-dashed border-slate-800 rounded-xl p-6 text-center space-y-2 bg-[#0A0E1A]/60">
                <Clock className="w-8 h-8 text-slate-600 mx-auto" />
                <div className="text-xs font-mono font-bold tracking-wider text-slate-400 uppercase">
                  NO ALGORITHM RUN RECORDED
                </div>
                <p className="text-[11px] text-slate-500 font-mono leading-relaxed">
                  Head-to-head algorithm benchmarks (Merge vs Quick vs Bubble Sort) will execute in the Benchmark Arena.
                </p>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-800 text-[11px] font-mono text-slate-500 space-y-2">
              <div className="flex justify-between">
                <span>Active Sort Engine:</span>
                <span className="text-cyan-400">Merge Sort O(n log n)</span>
              </div>
              <div className="flex justify-between">
                <span>Primary Index:</span>
                <span className="text-emerald-400">ImageHashTable O(1)</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Imagery Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold font-mono tracking-tight text-slate-100 uppercase">
              Recent Satellite Imagery
            </h2>
            <p className="text-xs text-slate-500 font-mono">
              Latest images cataloged from DeepGlobe ingestion pipeline
            </p>
          </div>

          <Link
            to="/explorer"
            className="flex items-center gap-1.5 text-xs font-mono text-cyan-400 hover:text-cyan-300 transition"
          >
            <span>Explore All Catalog</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {recentImages.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {recentImages.map((img) => (
              <ImageCard
                key={img.image_id}
                image={img}
                onClick={(selected) => setInspectImage(selected)}
              />
            ))}
          </div>
        ) : (
          !loading && (
            <div className="border border-dashed border-slate-800 rounded-2xl p-10 text-center space-y-3 bg-[#0D1117]/60">
              <Compass className="w-8 h-8 text-slate-600 mx-auto" />
              <div className="text-sm font-mono text-slate-300">
                CATALOG CURRENTLY EMPTY
              </div>
              <p className="text-xs font-mono text-slate-500 max-w-sm mx-auto">
                No imagery records loaded. Click "LOAD SAMPLE DATASET" to populate with real DeepGlobe earth observation tiles.
              </p>
            </div>
          )
        )}
      </div>

      {/* Image Inspection Modal */}
      <ImageInspectModal
        image={inspectImage}
        onClose={() => setInspectImage(null)}
      />
    </div>
  );
};
