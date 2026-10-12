import React, { useState } from 'react';
import { UploadCloud, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';
import { uploadImages } from '../api/client';
import type { UploadResponse } from '../types';

export const UploadPage: React.FC = () => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState<boolean>(false);
  const [result, setResult] = useState<UploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files));
      setResult(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;
    setUploading(true);
    setError(null);
    setResult(null);

    try {
      const res = await uploadImages(selectedFiles);
      setResult(res);
      setSelectedFiles([]);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Upload failed';
      setError(msg);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">Upload Satellite Imagery</h1>
        <p className="text-sm text-slate-400">
          Tests <code>POST /api/upload</code>. Validates MIME types, extracts date/time/land type from filenames, calculates dimensions via Pillow, and indexes into the hash table.
        </p>
      </div>

      {/* Upload Pipeline Indicator */}
      <div className="bg-slate-900/40 p-4 rounded-xl border border-slate-800 text-xs">
        <div className="text-slate-400 font-semibold mb-2 uppercase tracking-wider text-[11px]">
          Pluto Upload Pipeline Flow
        </div>
        <div className="flex flex-wrap items-center gap-2 text-slate-300 font-mono">
          <span className="px-2.5 py-1 rounded bg-slate-800 border border-slate-700">1. UPLOAD</span>
          <span className="text-slate-600">&rarr;</span>
          <span className="px-2.5 py-1 rounded bg-slate-800 border border-slate-700">2. VALIDATE</span>
          <span className="text-slate-600">&rarr;</span>
          <span className="px-2.5 py-1 rounded bg-slate-800 border border-slate-700">3. EXTRACT METADATA</span>
          <span className="text-slate-600">&rarr;</span>
          <span className="px-2.5 py-1 rounded bg-slate-800 border border-slate-700">4. INDEX HASH TABLE</span>
          <span className="text-slate-600">&rarr;</span>
          <span className="px-2.5 py-1 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-bold">5. READY</span>
        </div>
      </div>

      {/* Upload Card */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-6">
        <div className="border-2 border-dashed border-slate-800 hover:border-slate-700 rounded-xl p-8 text-center bg-slate-950/40 transition">
          <UploadCloud className="w-12 h-12 text-slate-500 mx-auto mb-3" />
          <p className="text-sm font-medium text-slate-200">
            Select satellite image files to test backend upload
          </p>
          <p className="text-xs text-slate-500 mt-1">
            Supported: .jpg, .jpeg, .png, .tiff, .tif, .webp (Standard pattern: <code>YYYY-MM-DD_HH-MM_LandType.ext</code>)
          </p>

          <label className="mt-4 inline-block">
            <span className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg cursor-pointer border border-slate-700 transition">
              Browse Files
            </span>
            <input
              type="file"
              multiple
              accept=".jpg,.jpeg,.png,.tiff,.tif,.webp,.bmp"
              onChange={handleFileChange}
              className="hidden"
            />
          </label>
        </div>

        {/* Selected files preview */}
        {selectedFiles.length > 0 && (
          <div className="space-y-3">
            <div className="text-xs font-semibold text-slate-400">
              Selected Files ({selectedFiles.length}):
            </div>
            <div className="max-h-40 overflow-y-auto space-y-1.5 p-2 bg-slate-950 rounded-lg border border-slate-800 text-xs">
              {selectedFiles.map((f, idx) => (
                <div key={idx} className="flex items-center justify-between text-slate-300">
                  <span className="truncate">{f.name}</span>
                  <span className="text-slate-500 font-mono shrink-0 ml-2">
                    {(f.size / 1024).toFixed(1)} KB
                  </span>
                </div>
              ))}
            </div>

            <button
              onClick={handleUpload}
              disabled={uploading}
              className="w-full flex items-center justify-center space-x-2 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold transition disabled:opacity-50"
            >
              {uploading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Processing &amp; Indexing...</span>
                </>
              ) : (
                <>
                  <UploadCloud className="w-4 h-4" />
                  <span>Execute Upload to Backend</span>
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {/* Results */}
      {result && (
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex items-center space-x-2 text-emerald-400 text-sm font-semibold">
            <CheckCircle2 className="w-5 h-5" />
            <span>Upload Processed: {result.uploaded_count} images successfully indexed.</span>
          </div>

          {result.errors.length > 0 && (
            <div className="p-3 bg-rose-950/40 border border-rose-800 rounded-lg text-xs text-rose-300 space-y-1">
              <div className="font-semibold flex items-center space-x-1">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>Upload Warnings / Errors:</span>
              </div>
              <ul className="list-disc list-inside">
                {result.errors.map((err, i) => (
                  <li key={i}>{err}</li>
                ))}
              </ul>
            </div>
          )}

          {result.images.length > 0 && (
            <div className="space-y-2">
              <div className="text-xs font-semibold text-slate-400">Indexed Image Records:</div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {result.images.map((img) => (
                  <div key={img.image_id} className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs">
                    <div className="flex items-center justify-between font-mono">
                      <span className="text-emerald-400 font-bold">{img.image_id}</span>
                      <span className="text-slate-400">{img.land_type}</span>
                    </div>
                    <div className="text-slate-300 truncate mt-1">{img.image_name}</div>
                    <div className="text-slate-500 mt-1">
                      {img.width}x{img.height} px &bull; {img.file_size_formatted}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800 text-rose-300 text-xs flex items-center space-x-2">
          <AlertTriangle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};
