import React, { useState, useEffect, useCallback } from 'react';
import {
  Search,
  Filter,
  ArrowUpDown,
  LayoutGrid,
  List,
  RefreshCw,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { getImages } from '../api/client';
import type { ImageRecord } from '../types';
import { ImageCard } from '../components/ImageCard';
import { ImageInspectModal } from '../components/ImageInspectModal';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import { Pagination } from '../components/Pagination';

export const ExplorerPage: React.FC = () => {
  const navigate = useNavigate();

  const [images, setImages] = useState<ImageRecord[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters & Search State
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [landType, setLandType] = useState<string>('All');
  const [sortBy, setSortBy] = useState<string>('datetime');
  const [order, setOrder] = useState<'asc' | 'desc'>('desc');
  const [page, setPage] = useState<number>(1);
  const [pageSize] = useState<number>(12);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  // Selected image for modal
  const [inspectImage, setInspectImage] = useState<ImageRecord | null>(null);

  const fetchImages = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getImages({
        page,
        page_size: pageSize,
        search: searchTerm.trim() || undefined,
        land_type: landType !== 'All' ? landType : undefined,
        sort_by: sortBy,
        order: order,
      });
      setImages(res.items);
      setTotal(res.total);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to query imagery catalog';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, searchTerm, landType, sortBy, order]);

  useEffect(() => {
    fetchImages();
  }, [fetchImages]);

  const totalPages = Math.ceil(total / pageSize) || 1;

  return (
    <div className="space-y-6">
      {/* Page Title & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#06B6D4]" />
            <span className="text-xs font-mono font-semibold text-[#06B6D4] uppercase tracking-wider">
              EARTH OBSERVATION CATALOG
            </span>
          </div>
          <h1 className="text-2xl font-bold font-mono tracking-tight text-white mt-1">
            Imagery Explorer
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            Browse and inspect calibrated multispectral satellite tiles with $O(1)$ indexed retrieval.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          {/* View Mode Toggle */}
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

          <button
            onClick={() => fetchImages()}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-[#0D1117] border border-slate-800 hover:border-slate-700 text-slate-300 text-xs font-mono transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>SYNC</span>
          </button>
        </div>
      </div>

      {/* Filter and Query Control Bar */}
      <div className="bg-[#0D1117] border border-slate-800 rounded-2xl p-4 grid grid-cols-1 md:grid-cols-12 gap-3">
        {/* Search Input */}
        <div className="md:col-span-5 relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search by ID, name, date, or classification..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setPage(1);
            }}
            className="w-full pl-9 pr-4 py-2 bg-[#0A0E1A] border border-slate-800 rounded-xl text-xs font-mono text-slate-200 placeholder-slate-600 focus:outline-none focus:border-[#06B6D4] transition"
          />
        </div>

        {/* Land Type Filter */}
        <div className="md:col-span-3 flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-500 shrink-0" />
          <select
            value={landType}
            onChange={(e) => {
              setLandType(e.target.value);
              setPage(1);
            }}
            className="w-full px-3 py-2 bg-[#0A0E1A] border border-slate-800 rounded-xl text-xs font-mono text-slate-200 focus:outline-none focus:border-[#06B6D4] transition"
          >
            <option value="All">All Land Classifications</option>
            <option value="Forest">Forest</option>
            <option value="Water">Water</option>
            <option value="Agriculture">Agriculture</option>
            <option value="Urban">Urban</option>
            <option value="Barren">Barren Land</option>
            <option value="Other">Other</option>
          </select>
        </div>

        {/* Sort Field & Order Direction */}
        <div className="md:col-span-4 flex items-center gap-2">
          <ArrowUpDown className="w-4 h-4 text-slate-500 shrink-0" />
          <select
            value={sortBy}
            onChange={(e) => {
              setSortBy(e.target.value);
              setPage(1);
            }}
            className="w-full px-3 py-2 bg-[#0A0E1A] border border-slate-800 rounded-xl text-xs font-mono text-slate-200 focus:outline-none focus:border-[#06B6D4] transition"
          >
            <option value="datetime">Sort by Date/Time</option>
            <option value="image_name">Sort by Filename</option>
            <option value="file_size">Sort by File Size</option>
            <option value="land_type">Sort by Land Type</option>
            <option value="image_id">Sort by Image ID</option>
          </select>

          <button
            onClick={() => {
              setOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'));
              setPage(1);
            }}
            className="px-2.5 py-2 bg-[#0A0E1A] border border-slate-800 hover:border-slate-700 rounded-xl text-xs font-mono text-slate-300 font-bold uppercase transition"
            title="Toggle sort direction"
          >
            {order}
          </button>
        </div>
      </div>

      {/* Telemetry Status Bar */}
      <div className="flex items-center justify-between text-xs font-mono text-slate-400 px-1">
        <div>
          QUERY RESULTS: <span className="text-[#06B6D4] font-bold">{total}</span> IMAGES IN CATALOG
        </div>
        <div>
          PAGE <span className="text-slate-200 font-bold">{page}</span> OF {totalPages}
        </div>
      </div>

      {/* Loading Skeleton */}
      {loading && (
        <LoadingSkeleton type="image-grid" count={pageSize > 8 ? 8 : pageSize} />
      )}

      {/* Error State */}
      {error && !loading && (
        <ErrorState
          title="Catalog Query Error"
          message={error}
          onRetry={fetchImages}
        />
      )}

      {/* Empty State */}
      {!loading && !error && images.length === 0 && (
        <EmptyState
          title="NO IMAGES FOUND"
          description={
            searchTerm || landType !== 'All'
              ? 'No catalog items match your search or classification filter. Try adjusting your filter parameters.'
              : 'The image catalog is currently empty. Ingest satellite imagery to begin exploration.'
          }
          actionText="NAVIGATE TO INGEST IMAGERY"
          onAction={() => navigate('/ingest')}
        />
      )}

      {/* Images Rendering (Grid or List) */}
      {!loading && !error && images.length > 0 && (
        <>
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {images.map((img) => (
                <ImageCard
                  key={img.image_id}
                  image={img}
                  viewMode="grid"
                  onClick={(selected) => setInspectImage(selected)}
                />
              ))}
            </div>
          ) : (
            <div className="space-y-2.5">
              {images.map((img) => (
                <ImageCard
                  key={img.image_id}
                  image={img}
                  viewMode="list"
                  onClick={(selected) => setInspectImage(selected)}
                />
              ))}
            </div>
          )}

          {/* Pagination Controls */}
          <div className="pt-4">
            <Pagination
              currentPage={page}
              totalPages={totalPages}
              onPageChange={(newPage) => setPage(newPage)}
            />
          </div>
        </>
      )}

      {/* Inspection Modal */}
      <ImageInspectModal
        image={inspectImage}
        onClose={() => setInspectImage(null)}
      />
    </div>
  );
};
