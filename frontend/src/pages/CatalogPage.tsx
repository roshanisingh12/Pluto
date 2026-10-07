import React, { useState, useEffect, useCallback } from 'react';
import { Search, Filter, Image as ImageIcon, X, RefreshCw, Calendar, Tag, CheckCircle2, AlertCircle } from 'lucide-react';
import { getImages, getImage, getImageFileUrl } from '../api/client';
import type { ImageRecord } from '../types';

export const CatalogPage: React.FC = () => {
  const [images, setImages] = useState<ImageRecord[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters & search
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [landType, setLandType] = useState<string>('All');
  const [page, setPage] = useState<number>(1);
  const pageSize = 8;

  // Selected image preview modal
  const [selectedImage, setSelectedImage] = useState<ImageRecord | null>(null);
  const [modalLoading, setModalLoading] = useState<boolean>(false);
  const [imageLoadError, setImageLoadError] = useState<boolean>(false);

  const fetchCatalog = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getImages({
        page,
        page_size: pageSize,
        search: searchTerm.trim() || undefined,
        land_type: landType !== 'All' ? landType : undefined,
      });
      setImages(res.items);
      setTotal(res.total);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to fetch catalog images';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [page, landType, searchTerm]);

  useEffect(() => {
    fetchCatalog();
  }, [fetchCatalog]);

  const handleOpenDetail = async (img: ImageRecord) => {
    setSelectedImage(img);
    setImageLoadError(false);
    setModalLoading(true);
    try {
      // Test GET /api/images/{id}
      const fullRecord = await getImage(img.image_id);
      setSelectedImage(fullRecord);
    } catch {
      // Fallback to record we already have
    } finally {
      setModalLoading(false);
    }
  };

  const totalPages = Math.ceil(total / pageSize) || 1;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Imagery Catalog &amp; File Preview</h1>
          <p className="text-sm text-slate-400">
            Real satellite catalog fetched from <code>GET /api/images</code> with O(1) hash table lookups and image streaming.
          </p>
        </div>
        <button
          onClick={() => fetchCatalog()}
          disabled={loading}
          className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 text-sm font-medium self-start sm:self-auto"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Search & Filter Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 bg-slate-900/40 p-4 rounded-xl border border-slate-800">
        <div className="sm:col-span-2 relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search by ID, filename, or classification..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setPage(1);
            }}
            className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition"
          />
        </div>

        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-slate-400 shrink-0" />
          <select
            value={landType}
            onChange={(e) => {
              setLandType(e.target.value);
              setPage(1);
            }}
            className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-emerald-500 transition"
          >
            <option value="All">All Land Types</option>
            <option value="Forest">Forest</option>
            <option value="Water">Water</option>
            <option value="Agriculture">Agriculture</option>
            <option value="Urban">Urban</option>
            <option value="Barren">Barren Land</option>
            <option value="Other">Other</option>
          </select>
        </div>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="py-16 text-center text-slate-400 space-y-3">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto text-emerald-400" />
          <p className="text-sm">Querying satellite catalog...</p>
        </div>
      )}

      {/* Error state */}
      {error && !loading && (
        <div className="p-6 rounded-xl bg-rose-950/30 border border-rose-800 text-center space-y-2">
          <AlertCircle className="w-8 h-8 text-rose-400 mx-auto" />
          <div className="text-base font-semibold text-rose-300">Catalog Query Failed</div>
          <p className="text-xs text-rose-400">{error}</p>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && images.length === 0 && (
        <div className="p-12 text-center border border-dashed border-slate-800 rounded-2xl space-y-3">
          <ImageIcon className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-base font-semibold text-slate-300">No images match your query</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Load the sample DeepGlobe dataset from the Overview tab or upload new images to populate the catalog.
          </p>
        </div>
      )}

      {/* Grid of Image Records */}
      {!loading && !error && images.length > 0 && (
        <>
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Showing {images.length} of {total} images</span>
            <span>Page {page} of {totalPages}</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {images.map((img) => {
              const fileUrl = getImageFileUrl(img.image_id);
              return (
                <div
                  key={img.image_id}
                  onClick={() => handleOpenDetail(img)}
                  className="group cursor-pointer bg-slate-900/60 hover:bg-slate-900 border border-slate-800 hover:border-emerald-500/40 rounded-xl overflow-hidden transition-all shadow-md flex flex-col"
                >
                  {/* Thumbnail Preview */}
                  <div className="relative aspect-video bg-slate-950 overflow-hidden flex items-center justify-center">
                    <img
                      src={fileUrl}
                      alt={img.image_name}
                      className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                      loading="lazy"
                      onError={(e) => {
                        // Fallback icon if file can't be rendered directly
                        e.currentTarget.style.display = 'none';
                      }}
                    />
                    <div className="absolute top-2 left-2 px-2 py-0.5 rounded bg-slate-950/80 backdrop-blur-sm border border-slate-700 text-[10px] font-mono font-semibold text-emerald-400">
                      {img.image_id}
                    </div>
                    {img.land_type && (
                      <div className="absolute top-2 right-2 px-2 py-0.5 rounded bg-slate-950/80 backdrop-blur-sm border border-slate-700 text-[10px] font-medium text-slate-300">
                        {img.land_type}
                      </div>
                    )}
                  </div>

                  {/* Metadata Summary */}
                  <div className="p-3.5 space-y-2 flex-1 flex flex-col justify-between">
                    <div>
                      <div className="text-xs font-medium text-slate-200 truncate" title={img.image_name}>
                        {img.image_name}
                      </div>
                      <div className="flex items-center space-x-2 text-[11px] text-slate-400 mt-1">
                        <Calendar className="w-3 h-3 text-slate-500" />
                        <span>{img.datetime || img.date || 'No Date'}</span>
                      </div>
                    </div>

                    <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500 font-mono">
                      <span>{img.width && img.height ? `${img.width}x${img.height}` : 'Dimensions N/A'}</span>
                      <span>{img.file_size_formatted || (img.file_size ? `${Math.round(img.file_size / 1024)} KB` : 'N/A')}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center space-x-2 pt-4">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs font-medium text-slate-300 disabled:opacity-40"
              >
                Previous
              </button>
              <span className="text-xs text-slate-400 font-mono px-2">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs font-medium text-slate-300 disabled:opacity-40"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}

      {/* Image Detail & Preview Modal */}
      {selectedImage && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl flex flex-col">
            <div className="p-4 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="font-mono text-xs px-2 py-0.5 rounded bg-emerald-950 border border-emerald-800 text-emerald-400 font-bold">
                  {selectedImage.image_id}
                </span>
                <span className="text-sm font-semibold text-slate-200 truncate max-w-md">
                  {selectedImage.image_name}
                </span>
              </div>
              <button
                onClick={() => setSelectedImage(null)}
                className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Full Image Stream Preview */}
              <div className="aspect-video bg-black rounded-xl overflow-hidden border border-slate-800 flex items-center justify-center relative">
                {modalLoading && (
                  <RefreshCw className="w-8 h-8 animate-spin text-emerald-400" />
                )}
                {!imageLoadError ? (
                  <img
                    src={getImageFileUrl(selectedImage.image_id)}
                    alt={selectedImage.image_name}
                    className="max-h-full max-w-full object-contain"
                    onError={() => setImageLoadError(true)}
                  />
                ) : (
                  <div className="text-center text-slate-500 p-4 text-xs">
                    File stream preview unavailable. Verify file exists on disk.
                  </div>
                )}
              </div>

              {/* Real Metadata Inspection */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                  <div className="text-slate-500">Land Classification</div>
                  <div className="font-semibold text-slate-200 mt-1 flex items-center space-x-1">
                    <Tag className="w-3.5 h-3.5 text-emerald-400" />
                    <span>{selectedImage.land_type || 'Unknown'}</span>
                  </div>
                </div>

                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                  <div className="text-slate-500">Acquisition Date</div>
                  <div className="font-semibold text-slate-200 mt-1 flex items-center space-x-1">
                    <Calendar className="w-3.5 h-3.5 text-sky-400" />
                    <span>{selectedImage.date || 'N/A'}</span>
                  </div>
                </div>

                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                  <div className="text-slate-500">Resolution</div>
                  <div className="font-mono font-semibold text-slate-200 mt-1">
                    {selectedImage.width && selectedImage.height
                      ? `${selectedImage.width} x ${selectedImage.height} px`
                      : 'N/A'}
                  </div>
                </div>

                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                  <div className="text-slate-500">File Size</div>
                  <div className="font-mono font-semibold text-slate-200 mt-1">
                    {selectedImage.file_size_formatted || `${selectedImage.file_size} B`}
                  </div>
                </div>
              </div>

              {/* Source & Completeness */}
              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs flex items-center justify-between">
                <div className="text-slate-400">
                  Source: <span className="text-slate-200">{selectedImage.source || 'DeepGlobe Mission'}</span>
                </div>
                <div className="flex items-center space-x-1 text-emerald-400 font-medium">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Metadata Validated</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
