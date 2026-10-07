import React, { useState } from 'react';
import {
  Download,
  FolderOpen,
  CheckCircle2,
  AlertTriangle,
  Play,
  FileText,
} from 'lucide-react';
import { getExportCsvUrl, organizeImages } from '../api/client';
import type { OrganizeResponse } from '../types';

const LAND_COLOURS: Record<string, string> = {
  Forest: '#10B981',
  Water: '#0EA5E9',
  Agriculture: '#84CC16',
  Urban: '#94A3B8',
  Barren_Land: '#F97316',
  Other: '#64748B',
};

export const ExportPage: React.FC = () => {
  /* CSV Export state */
  const [csvLoading, setCsvLoading] = useState(false);
  const [csvSuccess, setCsvSuccess] = useState(false);
  const [csvError, setCsvError] = useState<string | null>(null);

  /* Organise state */
  const [orgLoading, setOrgLoading] = useState(false);
  const [orgResult, setOrgResult] = useState<OrganizeResponse | null>(null);
  const [orgError, setOrgError] = useState<string | null>(null);

  const handleExportCsv = async () => {
    setCsvLoading(true);
    setCsvSuccess(false);
    setCsvError(null);
    try {
      const url = getExportCsvUrl();
      const response = await fetch(url);
      if (!response.ok) {
        const text = await response.text();
        let msg = 'CSV export failed';
        try { msg = JSON.parse(text)?.detail ?? msg; } catch { /* keep default */ }
        throw new Error(msg);
      }
      const blob = await response.blob();
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'satellite_imagery_metadata.csv';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(link.href);
      setCsvSuccess(true);
    } catch (err: unknown) {
      setCsvError(err instanceof Error ? err.message : 'Failed to export CSV');
    } finally {
      setCsvLoading(false);
    }
  };

  const handleOrganize = async () => {
    setOrgLoading(true);
    setOrgResult(null);
    setOrgError(null);
    try {
      const res = await organizeImages();
      setOrgResult(res);
    } catch (err: unknown) {
      setOrgError(err instanceof Error ? err.message : 'Organization failed');
    } finally {
      setOrgLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#06B6D4]" />
          <span className="text-xs font-mono font-semibold text-[#06B6D4] uppercase tracking-wider">DATA MANAGEMENT OPERATIONS</span>
        </div>
        <h1 className="text-2xl font-bold font-mono tracking-tight text-white mt-1">Export &amp; Organize</h1>
        <p className="text-xs text-slate-400 font-mono mt-0.5">Export catalog metadata as CSV and organize imagery files by land classification.</p>
      </div>

      {/* -- CSV Export Card -- */}
      <div className="bg-[#0D1117] border border-slate-800 rounded-2xl p-6 space-y-5">
        <div className="flex items-center gap-2 border-b border-slate-800/80 pb-3">
          <FileText className="w-4 h-4 text-[#06B6D4]" />
          <span className="text-xs font-mono font-semibold text-slate-300 uppercase tracking-wider">Metadata CSV Export</span>
          <span className="ml-auto text-[11px] font-mono text-cyan-400">GET /api/export/csv</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div className="space-y-3 text-xs font-mono text-slate-400">
            <p>Downloads a structured CSV file of all catalog image records and their extracted metadata fields.</p>
            <div className="space-y-1.5">
              {['image_id', 'image_name', 'date', 'time', 'land_type', 'image_format', 'file_size', 'width', 'height', 'source', 'dominant_percentage'].map(f => (
                <div key={f} className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-800" />
                  <span className="text-slate-500">{f}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="flex flex-col justify-between gap-4">
            <div className="bg-[#0A0E1A] border border-slate-800 rounded-xl p-4 text-xs font-mono space-y-1.5">
              <div className="text-slate-500">Output filename</div>
              <div className="text-cyan-300 font-bold">satellite_imagery_metadata.csv</div>
              <div className="text-slate-500 mt-2">Format</div>
              <div className="text-slate-300">UTF-8 CSV with header row</div>
            </div>

            <button
              onClick={handleExportCsv}
              disabled={csvLoading}
              className="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-[#06B6D4] hover:bg-[#22D3EE] text-[#0A0E1A] font-mono font-bold text-xs uppercase tracking-wider transition shadow-lg shadow-cyan-950/40 disabled:opacity-50"
            >
              <Download className={`w-4 h-4 ${csvLoading ? 'animate-bounce' : ''}`} />
              {csvLoading ? 'EXPORTING...' : 'EXPORT CSV'}
            </button>

            {csvSuccess && (
              <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 bg-emerald-950/30 border border-emerald-800/50 rounded-xl p-3">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                CSV downloaded successfully
              </div>
            )}

            {csvError && (
              <div className="flex items-center gap-2 text-xs font-mono text-red-400 bg-red-950/30 border border-red-800/50 rounded-xl p-3">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                {csvError}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* -- Organize Card -- */}
      <div className="bg-[#0D1117] border border-slate-800 rounded-2xl p-6 space-y-5">
        <div className="flex items-center gap-2 border-b border-slate-800/80 pb-3">
          <FolderOpen className="w-4 h-4 text-[#06B6D4]" />
          <span className="text-xs font-mono font-semibold text-slate-300 uppercase tracking-wider">Filesystem Organization</span>
          <span className="ml-auto text-[11px] font-mono text-cyan-400">POST /api/organize</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div className="space-y-3 text-xs font-mono text-slate-400">
            <p>Physically copies satellite image files into land classification subfolders on disk. The operation is non-destructive — original files are preserved.</p>
            <div className="bg-[#0A0E1A] border border-slate-800 rounded-xl p-4 space-y-2">
              <div className="text-slate-500 mb-2">Destination structure:</div>
              {['Organized/Forest/', 'Organized/Water/', 'Organized/Agriculture/', 'Organized/Urban/', 'Organized/Barren_Land/', 'Organized/Other/'].map(f => (
                <div key={f} className="flex items-center gap-2 text-slate-400">
                  <FolderOpen className="w-3 h-3 text-amber-600" />
                  <span>{f}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="flex flex-col justify-between gap-4">
            <div className="bg-[#0A0E1A] border border-amber-800/30 rounded-xl p-4 text-xs font-mono space-y-1.5 text-amber-400/80">
              <AlertTriangle className="w-4 h-4 mb-2" />
              <div>Files are <strong>copied</strong>, not moved. The original image store is unchanged.</div>
              <div className="text-slate-500 mt-1">Filename collisions are handled automatically.</div>
            </div>

            <button
              onClick={handleOrganize}
              disabled={orgLoading}
              className="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-slate-700 hover:bg-slate-600 text-slate-100 font-mono font-bold text-xs uppercase tracking-wider transition disabled:opacity-50"
            >
              <Play className={`w-4 h-4 ${orgLoading ? 'animate-spin' : 'fill-current'}`} />
              {orgLoading ? 'ORGANIZING...' : 'ORGANIZE FILESYSTEM'}
            </button>

            {orgError && (
              <div className="flex items-center gap-2 text-xs font-mono text-red-400 bg-red-950/30 border border-red-800/50 rounded-xl p-3">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                {orgError}
              </div>
            )}
          </div>
        </div>

        {/* Organize Result */}
        {orgResult && (
          <div className={`border rounded-2xl p-5 space-y-4 mt-2 ${orgResult.success ? 'border-emerald-800/50 bg-emerald-950/10' : 'border-red-800/50 bg-red-950/10'}`}>
            <div className="flex items-center gap-2">
              {orgResult.success
                ? <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                : <AlertTriangle className="w-5 h-5 text-red-400" />}
              <span className="text-sm font-mono font-bold text-slate-100 uppercase tracking-wider">
                {orgResult.success ? 'ORGANIZATION COMPLETE' : 'ORGANIZATION ENCOUNTERED ERRORS'}
              </span>
              <span className="ml-auto text-xs font-mono text-emerald-400 bg-emerald-950/50 border border-emerald-800/50 px-2.5 py-1 rounded-full">
                {orgResult.total_copied} files copied
              </span>
            </div>

            {/* Category Breakdown */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 font-mono text-xs">
              {Object.entries(orgResult.category_counts).map(([cat, count]) => (
                <div key={cat} className="bg-[#0A0E1A] border border-slate-800 rounded-xl p-3 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-sm shrink-0" style={{ backgroundColor: LAND_COLOURS[cat] ?? '#64748B' }} />
                  <span className="text-slate-400 truncate">{cat}</span>
                  <span className="ml-auto text-slate-200 font-bold">{count}</span>
                </div>
              ))}
            </div>

            {orgResult.errors.length > 0 && (
              <div className="space-y-1">
                <div className="text-xs font-mono text-amber-400 font-semibold">WARNINGS / ERRORS ({orgResult.errors.length})</div>
                {orgResult.errors.slice(0, 5).map((e, i) => (
                  <div key={i} className="text-xs font-mono text-slate-500 flex items-start gap-2">
                    <AlertTriangle className="w-3 h-3 text-amber-600 mt-0.5 shrink-0" />
                    {e}
                  </div>
                ))}
                {orgResult.errors.length > 5 && (
                  <div className="text-xs font-mono text-slate-600">...and {orgResult.errors.length - 5} more</div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
