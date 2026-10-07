import React, { useState, useEffect } from 'react';
import { X, Calendar, Clock, Maximize2, HardDrive, Tag, Layers, RefreshCw, AlertCircle } from 'lucide-react';
import type { ImageRecord } from '../types';
import { getImage, getImageFileUrl } from '../api/client';
import { LandTypeBadge } from './LandTypeBadge';

interface ImageInspectModalProps {
  image: ImageRecord | null;
  onClose: () => void;
}

export const ImageInspectModal: React.FC<ImageInspectModalProps> = ({
  image,
  onClose,
}) => {
  const [record, setRecord] = useState<ImageRecord | null>(image);
  const [loading, setLoading] = useState<boolean>(false);
  const [imgError, setImgError] = useState<boolean>(false);

  useEffect(() => {
    if (!image) {
      setRecord(null);
      return;
    }

    setRecord(image);
    setImgError(false);
    let isMounted = true;

    async function loadFullDetails() {
      setLoading(true);
      try {
        const full = await getImage(image!.image_id);
        if (isMounted) {
          setRecord(full);
        }
      } catch {
        // Fallback to record already present
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    loadFullDetails();

    return () => {
      isMounted = false;
    };
  }, [image]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!image) return null;

  const current = record || image;
  const fileUrl = getImageFileUrl(current.image_id);

  return (
    <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-[#0D1117] border border-slate-800 rounded-2xl max-w-4xl w-full max-h-[92vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Modal Header */}
        <div className="p-4 sm:px-6 border-b border-slate-800 bg-[#111827]/70 flex items-center justify-between">
          <div className="flex items-center gap-3 min-w-0">
            <span className="font-mono text-xs px-2.5 py-1 rounded bg-cyan-950/70 border border-cyan-800/60 text-[#22D3EE] font-bold">
              {current.image_id}
            </span>
            <div className="min-w-0">
              <h3 className="text-sm font-semibold text-slate-100 truncate max-w-md font-mono" title={current.image_name}>
                {current.image_name}
              </h3>
              <p className="text-[11px] text-slate-400 font-mono">
                Telemetry Inspection &bull; $O(1)$ Hash Table Key Lookup
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {loading && <RefreshCw className="w-4 h-4 text-cyan-400 animate-spin mr-2" />}
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-white transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* Real Stream Image View */}
          <div className="relative aspect-video max-h-[420px] bg-[#0A0E1A] rounded-xl border border-slate-800/80 overflow-hidden flex items-center justify-center">
            {!imgError ? (
              <img
                src={fileUrl}
                alt={current.image_name}
                className="max-h-full max-w-full object-contain"
                onError={() => setImgError(true)}
              />
            ) : (
              <div className="text-center p-6 space-y-2">
                <AlertCircle className="w-8 h-8 text-slate-600 mx-auto" />
                <p className="text-xs text-slate-400 font-mono">
                  Direct image preview stream unavailable.
                </p>
              </div>
            )}
            <div className="absolute top-3 right-3">
              <LandTypeBadge landType={current.land_type} size="md" />
            </div>
          </div>

          {/* Metadata Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
            {/* Land Type */}
            <div className="bg-[#111827] border border-slate-800 p-3 rounded-xl">
              <span className="text-slate-500 text-[10px] uppercase tracking-wider block">Land Classification</span>
              <div className="font-semibold text-slate-200 mt-1 flex items-center gap-1.5">
                <Tag className="w-3.5 h-3.5 text-[#06B6D4]" />
                <span>{current.land_type || 'Unknown'}</span>
              </div>
            </div>

            {/* Date */}
            <div className="bg-[#111827] border border-slate-800 p-3 rounded-xl">
              <span className="text-slate-500 text-[10px] uppercase tracking-wider block">Acquisition Date</span>
              <div className="font-semibold text-slate-200 mt-1 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-[#3B82F6]" />
                <span>{current.date || 'N/A'}</span>
              </div>
            </div>

            {/* Time */}
            <div className="bg-[#111827] border border-slate-800 p-3 rounded-xl">
              <span className="text-slate-500 text-[10px] uppercase tracking-wider block">Acquisition Time</span>
              <div className="font-semibold text-slate-200 mt-1 flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-[#10B981]" />
                <span>{current.time || 'N/A'}</span>
              </div>
            </div>

            {/* Dimensions */}
            <div className="bg-[#111827] border border-slate-800 p-3 rounded-xl">
              <span className="text-slate-500 text-[10px] uppercase tracking-wider block">Dimensions</span>
              <div className="font-semibold text-slate-200 mt-1 flex items-center gap-1.5">
                <Maximize2 className="w-3.5 h-3.5 text-[#22D3EE]" />
                <span>{current.width && current.height ? `${current.width}x${current.height} px` : 'N/A'}</span>
              </div>
            </div>

            {/* Format */}
            <div className="bg-[#111827] border border-slate-800 p-3 rounded-xl">
              <span className="text-slate-500 text-[10px] uppercase tracking-wider block">Image Format</span>
              <div className="font-semibold text-slate-200 mt-1">
                {current.image_format?.toUpperCase() || 'UNKNOWN'}
              </div>
            </div>

            {/* File Size */}
            <div className="bg-[#111827] border border-slate-800 p-3 rounded-xl">
              <span className="text-slate-500 text-[10px] uppercase tracking-wider block">File Size</span>
              <div className="font-semibold text-slate-200 mt-1 flex items-center gap-1.5">
                <HardDrive className="w-3.5 h-3.5 text-[#F59E0B]" />
                <span>{current.file_size_formatted || (current.file_size ? `${current.file_size} B` : 'N/A')}</span>
              </div>
            </div>

            {/* Dominant Coverage */}
            <div className="bg-[#111827] border border-slate-800 p-3 rounded-xl">
              <span className="text-slate-500 text-[10px] uppercase tracking-wider block">Coverage Purity</span>
              <div className="font-semibold text-slate-200 mt-1 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-[#14B8A6]" />
                <span>{current.dominant_percentage || 'N/A'}</span>
              </div>
            </div>

            {/* Source */}
            <div className="bg-[#111827] border border-slate-800 p-3 rounded-xl">
              <span className="text-slate-500 text-[10px] uppercase tracking-wider block">Sensor Mission</span>
              <div className="font-semibold text-slate-200 mt-1 truncate" title={current.source || 'Standard Ingestion'}>
                {current.source || 'Standard Ingestion'}
              </div>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-800 bg-[#111827]/40 flex items-center justify-between text-xs font-mono text-slate-400">
          <div>
            Status: <span className="text-[#10B981]">METADATA NOMINAL</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold border border-slate-700 transition"
          >
            Close Inspection
          </button>
        </div>
      </div>
    </div>
  );
};
