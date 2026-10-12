import React, { useState } from 'react';
import {
  UploadCloud,
  FileCheck,
  AlertTriangle,
  RefreshCw,
  Sparkles,
  Info,
  CheckCircle2,
  FileCode,
  HardDrive,
} from 'lucide-react';
import { uploadImages, loadSampleDataset } from '../api/client';
import type { UploadResponse, DatasetLoadResponse } from '../types';
import { ImageCard } from '../components/ImageCard';
import { ImageInspectModal } from '../components/ImageInspectModal';
import type { ImageRecord } from '../types';

export const IngestPage: React.FC = () => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Sample dataset loading
  const [sampleLoading, setSampleLoading] = useState<boolean>(false);
  const [sampleResult, setSampleResult] = useState<DatasetLoadResponse | null>(null);

  // Selected image for inspection
  const [inspectImage, setInspectImage] = useState<ImageRecord | null>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setSelectedFiles(Array.from(e.dataTransfer.files));
      setUploadResult(null);
      setUploadError(null);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFiles(Array.from(e.target.files));
      setUploadResult(null);
      setUploadError(null);
    }
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;
    setUploading(true);
    setUploadError(null);
    setUploadResult(null);

    try {
      const res = await uploadImages(selectedFiles);
      setUploadResult(res);
      setSelectedFiles([]);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Imagery upload failed';
      setUploadError(msg);
    } finally {
      setUploading(false);
    }
  };

  const handleLoadSamples = async () => {
    setSampleLoading(true);
    setSampleResult(null);
    try {
      const res = await loadSampleDataset();
      setSampleResult(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Sample dataset load failed';
      setUploadError(msg);
    } finally {
      setSampleLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#06B6D4]" />
            <span className="text-xs font-mono font-semibold text-[#06B6D4] uppercase tracking-wider">
              DATA INGESTION PIPELINE
            </span>
          </div>
          <h1 className="text-2xl font-bold font-mono tracking-tight text-white mt-1">
            Ingest Satellite Imagery
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            Direct multipart upload with automated header inspection, MIME verification, and hash indexing.
          </p>
        </div>

        <button
          onClick={handleLoadSamples}
          disabled={sampleLoading}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-500 hover:to-teal-500 text-[#0A0E1A] text-xs font-mono font-bold transition shadow-lg shadow-cyan-950/40 disabled:opacity-50 self-start sm:self-auto"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>{sampleLoading ? 'LOADING SAMPLES...' : 'LOAD SAMPLE DATASET'}</span>
        </button>
      </div>

      {/* Visual Pipeline Banner */}
      <div className="bg-[#0D1117] border border-slate-800 rounded-2xl p-5 space-y-3">
        <div className="flex items-center justify-between text-xs font-mono">
          <span className="text-slate-400 font-semibold uppercase tracking-wider">
            Ingestion Pipeline Architecture
          </span>
          <span className="text-cyan-400">AUTOMATED &bull; ZERO LATENCY</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-center text-xs font-mono">
          <div className="p-3 rounded-xl bg-[#111827] border border-slate-800">
            <div className="text-[10px] text-slate-500">STAGE 1</div>
            <div className="font-bold text-slate-200 mt-0.5">UPLOAD</div>
            <div className="text-[10px] text-slate-400 mt-1">Multipart Stream</div>
          </div>
          <div className="p-3 rounded-xl bg-[#111827] border border-slate-800">
            <div className="text-[10px] text-slate-500">STAGE 2</div>
            <div className="font-bold text-[#06B6D4] mt-0.5">VALIDATE</div>
            <div className="text-[10px] text-slate-400 mt-1">MIME &amp; Headers</div>
          </div>
          <div className="p-3 rounded-xl bg-[#111827] border border-slate-800">
            <div className="text-[10px] text-slate-500">STAGE 3</div>
            <div className="font-bold text-[#3B82F6] mt-0.5">EXTRACT METADATA</div>
            <div className="text-[10px] text-slate-400 mt-1">Regex &amp; Pillow</div>
          </div>
          <div className="p-3 rounded-xl bg-[#111827] border border-slate-800">
            <div className="text-[10px] text-slate-500">STAGE 4</div>
            <div className="font-bold text-[#F59E0B] mt-0.5">INDEX</div>
            <div className="text-[10px] text-slate-400 mt-1">ImageHashTable O(1)</div>
          </div>
          <div className="p-3 rounded-xl bg-[#111827] border border-emerald-800/60 bg-emerald-950/20 col-span-2 sm:col-span-1">
            <div className="text-[10px] text-emerald-500">STAGE 5</div>
            <div className="font-bold text-[#10B981] mt-0.5">READY</div>
            <div className="text-[10px] text-emerald-400 mt-1">Catalog Ready</div>
          </div>
        </div>
      </div>

      {/* Dataset Load Notification */}
      {sampleResult && (
        <div className="p-4 rounded-xl bg-cyan-950/40 border border-cyan-800/80 text-cyan-300 text-xs font-mono flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" />
            <span>
              {sampleResult.message} Added: <strong>{sampleResult.loaded_count}</strong>. Total catalog count: <strong>{sampleResult.total_catalog_count}</strong>.
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

      {/* Drag & Drop Upload Zone */}
      <div className="space-y-4">
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-2xl p-10 text-center transition-all flex flex-col items-center justify-center space-y-4 ${
            isDragging
              ? 'border-[#06B6D4] bg-cyan-950/30 shadow-xl'
              : 'border-slate-800 bg-[#0D1117] hover:border-slate-700'
          }`}
        >
          <div className="p-4 rounded-2xl bg-[#111827] border border-slate-800 text-cyan-400">
            <UploadCloud className="w-10 h-10 animate-bounce" />
          </div>

          <div>
            <h2 className="text-base font-bold font-mono tracking-tight text-slate-200">
              Drag &amp; drop satellite imagery files here
            </h2>
            <p className="text-xs font-mono text-slate-500 mt-1 max-w-md mx-auto">
              Supports TIFF, GeoTIFF, PNG, JPG, and WEBP formats up to 50 MB per file.
            </p>
          </div>

          <label className="cursor-pointer">
            <span className="px-5 py-2.5 rounded-xl bg-[#111827] hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-mono font-semibold transition">
              Select Files from Computer
            </span>
            <input
              type="file"
              multiple
              accept=".jpg,.jpeg,.png,.tiff,.tif,.webp,.bmp"
              onChange={handleFileSelect}
              className="hidden"
            />
          </label>
        </div>

        {/* Selected files preview & action */}
        {selectedFiles.length > 0 && (
          <div className="bg-[#0D1117] border border-slate-800 rounded-2xl p-5 space-y-4">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400">
              <span>QUEUED FILES FOR INGESTION: <strong className="text-white">{selectedFiles.length}</strong></span>
              <button
                onClick={() => setSelectedFiles([])}
                className="text-rose-400 hover:text-rose-300 underline"
              >
                Clear Queue
              </button>
            </div>

            <div className="max-h-48 overflow-y-auto space-y-2 pr-1 font-mono text-xs">
              {selectedFiles.map((file, idx) => (
                <div
                  key={idx}
                  className="p-2.5 rounded-xl bg-[#0A0E1A] border border-slate-800/80 flex items-center justify-between text-slate-300"
                >
                  <div className="flex items-center gap-2 truncate">
                    <FileCode className="w-4 h-4 text-cyan-400 shrink-0" />
                    <span className="truncate">{file.name}</span>
                  </div>
                  <span className="text-slate-500 text-[11px] shrink-0 ml-3">
                    {(file.size / 1024).toFixed(1)} KB
                  </span>
                </div>
              ))}
            </div>

            <button
              onClick={handleUpload}
              disabled={uploading}
              className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-[#06B6D4] hover:bg-[#22D3EE] text-[#0A0E1A] font-mono font-bold text-xs uppercase tracking-wider transition shadow-lg shadow-cyan-950/40 disabled:opacity-50"
            >
              {uploading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>EXECUTING INGESTION PIPELINE...</span>
                </>
              ) : (
                <>
                  <FileCheck className="w-4 h-4" />
                  <span>PROCESS &amp; INDEX {selectedFiles.length} IMAGES</span>
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {/* Upload Error Notification */}
      {uploadError && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800 text-rose-300 text-xs font-mono flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{uploadError}</span>
          </div>
          <button
            onClick={() => setUploadError(null)}
            className="text-xs text-rose-400 hover:text-white underline ml-4"
          >
            DISMISS
          </button>
        </div>
      )}

      {/* Upload Results Display */}
      {uploadResult && (
        <div className="bg-[#0D1117] border border-slate-800 rounded-2xl p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div className="flex items-center gap-2 text-[#10B981] font-mono font-bold text-sm">
              <CheckCircle2 className="w-5 h-5" />
              <span>INGESTION COMPLETED: {uploadResult.uploaded_count} IMAGES INDEXED</span>
            </div>
            <span className="text-xs font-mono text-slate-500">HTTP 200 OK</span>
          </div>

          {uploadResult.errors.length > 0 && (
            <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-800/80 text-rose-300 text-xs font-mono space-y-1.5">
              <div className="font-bold flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-rose-400" />
                <span>Validation Rejections:</span>
              </div>
              <ul className="list-disc list-inside space-y-1 text-rose-300/90">
                {uploadResult.errors.map((err, i) => (
                  <li key={i}>{err}</li>
                ))}
              </ul>
            </div>
          )}

          {uploadResult.images.length > 0 && (
            <div className="space-y-3">
              <div className="text-xs font-mono font-semibold text-slate-400 uppercase tracking-wider">
                Newly Indexed Images:
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                {uploadResult.images.map((img) => (
                  <ImageCard
                    key={img.image_id}
                    image={img}
                    onClick={(selected) => setInspectImage(selected)}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Ingestion Guidelines & Convention Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Filename Convention Info */}
        <div className="bg-[#0D1117] border border-slate-800 rounded-2xl p-6 space-y-4">
          <div className="flex items-center gap-2 text-cyan-400 font-mono text-xs font-semibold uppercase">
            <Info className="w-4 h-4" />
            <span>Filename Convention Standards</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed font-mono">
            Pluto automatically extracts date, timestamp, and land classification metadata when filenames adhere to the standardized format:
          </p>
          <div className="p-3 rounded-xl bg-[#0A0E1A] border border-slate-800 font-mono text-xs text-[#22D3EE] select-all">
            YYYY-MM-DD_HH-MM_LandType.ext
          </div>
          <div className="text-[11px] font-mono text-slate-500 space-y-1">
            <div>Example: <span className="text-slate-300">2026-01-15_14-30_Forest.jpg</span></div>
            <div>Supported Land Types: Forest, Water, Agriculture, Urban, Barren</div>
          </div>
        </div>

        {/* Technical Constraints */}
        <div className="bg-[#0D1117] border border-slate-800 rounded-2xl p-6 space-y-4">
          <div className="flex items-center gap-2 text-slate-300 font-mono text-xs font-semibold uppercase">
            <HardDrive className="w-4 h-4 text-emerald-400" />
            <span>Storage &amp; Security Specs</span>
          </div>
          <div className="space-y-2 text-xs font-mono text-slate-400">
            <div className="flex justify-between py-1 border-b border-slate-800/80">
              <span className="text-slate-500">Max File Size:</span>
              <span className="text-slate-200">50 MB per image</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/80">
              <span className="text-slate-500">Image Readers:</span>
              <span className="text-slate-200">Pillow PIL Decoder</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/80">
              <span className="text-slate-500">Path Traversal Protection:</span>
              <span className="text-emerald-400">Strict Subpath Containment</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-500">Catalog Storage:</span>
              <span className="text-cyan-400">Memory + ImageHashTable</span>
            </div>
          </div>
        </div>
      </div>

      {/* Modal */}
      <ImageInspectModal
        image={inspectImage}
        onClose={() => setInspectImage(null)}
      />
    </div>
  );
};
