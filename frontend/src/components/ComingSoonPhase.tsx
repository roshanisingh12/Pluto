import React from 'react';
import { ArrowLeft, Clock, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';

interface ComingSoonPhaseProps {
  title: string;
  description: string;
  phase: string;
  features: string[];
}

export const ComingSoonPhase: React.FC<ComingSoonPhaseProps> = ({
  title,
  description,
  phase,
  features,
}) => {
  return (
    <div className="max-w-3xl mx-auto py-12 px-4 space-y-6">
      <div className="bg-[#0D1117] border border-slate-800 rounded-2xl p-8 space-y-6 relative overflow-hidden shadow-xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <span className="p-2 rounded-lg bg-cyan-950/60 border border-cyan-800/60 text-[#06B6D4]">
              <Clock className="w-5 h-5" />
            </span>
            <span className="text-xs font-mono px-2.5 py-1 rounded bg-slate-800 text-cyan-400 border border-slate-700">
              SCHEDULED FOR {phase.toUpperCase()}
            </span>
          </div>
          <span className="text-xs font-mono text-slate-500">PLUTO SPECIFICATION</span>
        </div>

        <div>
          <h1 className="text-2xl font-bold font-mono tracking-tight text-slate-100">
            {title}
          </h1>
          <p className="text-sm text-slate-400 mt-2 leading-relaxed">
            {description}
          </p>
        </div>

        <div className="space-y-3 pt-4 border-t border-slate-800/80">
          <div className="text-xs font-mono uppercase text-slate-400 font-semibold tracking-wider">
            Planned Capabilities:
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {features.map((feat, idx) => (
              <div
                key={idx}
                className="p-3 rounded-xl bg-[#111827] border border-slate-800/80 text-xs font-mono text-slate-300 flex items-center gap-2"
              >
                <ShieldCheck className="w-4 h-4 text-[#06B6D4] shrink-0" />
                <span>{feat}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="pt-4 flex items-center justify-between">
          <Link
            to="/explorer"
            className="flex items-center gap-2 text-xs font-mono text-cyan-400 hover:text-cyan-300 transition"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Return to Imagery Explorer</span>
          </Link>
          <span className="text-[11px] font-mono text-slate-500">
            Phase 1 &amp; Phase 2 foundation active
          </span>
        </div>
      </div>
    </div>
  );
};
