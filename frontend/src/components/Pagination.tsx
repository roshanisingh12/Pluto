import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  className?: string;
}

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  className = '',
}) => {
  if (totalPages <= 1) return null;

  return (
    <div className={`flex items-center justify-center gap-2 font-mono text-xs ${className}`}>
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage <= 1}
        className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-[#0D1117] border border-slate-800 text-slate-300 hover:border-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition"
      >
        <ChevronLeft className="w-4 h-4" />
        <span>PREV</span>
      </button>

      <span className="px-3 py-1.5 rounded-lg bg-[#111827] border border-slate-800 text-slate-200">
        PAGE <span className="text-[#06B6D4] font-bold">{currentPage}</span> / {totalPages}
      </span>

      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage >= totalPages}
        className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-[#0D1117] border border-slate-800 text-slate-300 hover:border-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition"
      >
        <span>NEXT</span>
        <ChevronRight className="w-4 h-4" />
      </button>
    </div>
  );
};
