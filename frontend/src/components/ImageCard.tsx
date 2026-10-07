import React, { useState } from 'react';
import { Calendar, FileCode, HardDrive, Eye } from 'lucide-react';
import type { ImageRecord } from '../types';
import { getImageFileUrl } from '../api/client';
import { LandTypeBadge } from './LandTypeBadge';

interface ImageCardProps {
  image: ImageRecord;
  onClick: (image: ImageRecord) => void;
  viewMode?: 'grid' | 'list';
}

export const ImageCard: React.FC<ImageCardProps> = ({
  image,
  onClick,
  viewMode = 'grid',
}) => {
  const [imgError, setImgError] = useState(false);
  const fileUrl = getImageFileUrl(image.image_id);

  if (viewMode === 'list') {
    return (
      <div
        onClick={() => onClick(image)}
        className="group cursor-pointer bg-[#0D1117] hover:bg-[#111827] border border-slate-800/80 hover:border-cyan-500/40 rounded-xl p-3 flex items-center justify-between gap-4 transition-all"
      >
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-14 h-14 rounded-lg bg-[#0A0E1A] border border-slate-800 overflow-hidden shrink-0 relative flex items-center justify-center">
            {!imgError ? (
              <img
                src={fileUrl}
                alt={image.image_name}
                loading="lazy"
                onError={() => setImgError(true)}
                className="w-full h-full object-cover transition-transform group-hover:scale-105"
              />
            ) : (
              <FileCode className="w-5 h-5 text-slate-600" />
            )}
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold text-[#06B6D4] bg-cyan-950/40 px-1.5 py-0.5 rounded border border-cyan-800/40">
                {image.image_id}
              </span>
              <span className="text-sm font-medium text-slate-200 truncate group-hover:text-white" title={image.image_name}>
                {image.image_name}
              </span>
            </div>
            <div className="flex items-center gap-3 text-xs text-slate-400 mt-1 font-mono">
              <span className="flex items-center gap-1">
                <Calendar className="w-3 h-3 text-slate-500" />
                {image.datetime || image.date || 'NO DATE'}
              </span>
              <span className="text-slate-600">&bull;</span>
              <span>{image.image_format?.toUpperCase() || 'JPG'}</span>
              <span className="text-slate-600">&bull;</span>
              <span>{image.file_size_formatted || (image.file_size ? `${Math.round(image.file_size / 1024)} KB` : 'N/A')}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <LandTypeBadge landType={image.land_type} />
          <button className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 group-hover:text-cyan-400 group-hover:border-cyan-500/40 transition">
            <Eye className="w-4 h-4" />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      onClick={() => onClick(image)}
      className="group cursor-pointer bg-[#0D1117] hover:bg-[#111827] border border-slate-800/80 hover:border-cyan-500/40 rounded-xl overflow-hidden transition-all shadow-md flex flex-col justify-between"
    >
      {/* Thumbnail area */}
      <div className="relative aspect-video bg-[#0A0E1A] overflow-hidden flex items-center justify-center">
        {!imgError ? (
          <img
            src={fileUrl}
            alt={image.image_name}
            loading="lazy"
            onError={() => setImgError(true)}
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
          />
        ) : (
          <div className="flex flex-col items-center justify-center text-slate-600 text-[11px] gap-1 font-mono">
            <FileCode className="w-6 h-6" />
            <span>FILE ON DISK</span>
          </div>
        )}

        {/* Overlay Badges */}
        <div className="absolute top-2 left-2 px-1.5 py-0.5 rounded bg-[#0A0E1A]/85 backdrop-blur-sm border border-slate-800 text-[10px] font-mono font-bold text-[#06B6D4]">
          {image.image_id}
        </div>
        <div className="absolute top-2 right-2">
          <LandTypeBadge landType={image.land_type} size="sm" />
        </div>
      </div>

      {/* Content */}
      <div className="p-3.5 space-y-2.5 flex-1 flex flex-col justify-between">
        <div>
          <div
            className="text-xs font-semibold text-slate-200 truncate group-hover:text-cyan-300 transition"
            title={image.image_name}
          >
            {image.image_name}
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-slate-400 mt-1 font-mono">
            <Calendar className="w-3 h-3 text-slate-500" />
            <span>{image.datetime || image.date || 'NO DATE'}</span>
          </div>
        </div>

        <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400 font-mono">
          <span className="flex items-center gap-1 text-slate-400">
            <FileCode className="w-3 h-3 text-slate-600" />
            {image.image_format?.toUpperCase() || 'JPG'}
          </span>
          <span className="flex items-center gap-1 text-slate-400">
            <HardDrive className="w-3 h-3 text-slate-600" />
            {image.file_size_formatted || (image.file_size ? `${Math.round(image.file_size / 1024)} KB` : 'N/A')}
          </span>
        </div>
      </div>
    </div>
  );
};
