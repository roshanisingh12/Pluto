import React, { useEffect, useState } from 'react';
import {
  BarChart, Bar, PieChart, Pie, Cell, Tooltip, ResponsiveContainer, XAxis, YAxis,
  CartesianGrid, LineChart, Line,
} from 'recharts';
import {
  Globe, Database, CheckCircle2, AlertTriangle, HardDrive, Image as ImageIcon,
  BarChart3, PieChart as PieIcon, RefreshCw, Calendar,
} from 'lucide-react';
import { getStatistics } from '../api/client';
import { MetricCard } from '../components/MetricCard';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { ErrorState } from '../components/ErrorState';
import type { StatisticsResponse } from '../types';

const LAND_COLOURS: Record<string, string> = {
  Forest: '#10B981',
  Water: '#0EA5E9',
  Agriculture: '#84CC16',
  Urban: '#94A3B8',
  Barren_Land: '#F97316',
  Other: '#64748B',
};
const FORMAT_COLOURS = ['#06B6D4', '#3B82F6', '#8B5CF6', '#F59E0B', '#EF4444', '#10B981'];

const ChartTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[#0D1117] border border-slate-700 rounded-xl px-3 py-2 text-xs font-mono shadow-2xl">
      {label && <div className="text-slate-400 mb-1">{label}</div>}
      {payload.map((p: any, i: number) => (
        <div key={i} style={{ color: p.color ?? '#22D3EE' }} className="font-bold">
          {p.name}: {p.value}
        </div>
      ))}
    </div>
  );
};

function fmtBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1073741824) return `${(bytes / 1048576).toFixed(2)} MB`;
  return `${(bytes / 1073741824).toFixed(2)} GB`;
}

const Panel: React.FC<{ title: string; subtitle?: string; icon: React.ElementType; children: React.ReactNode }> = ({
  title, subtitle, icon: Icon, children,
}) => (
  <div className="bg-[#0D1117] border border-slate-800 rounded-2xl p-6">
    <div className="flex items-center gap-2 mb-5 border-b border-slate-800/80 pb-3">
      <Icon className="w-4 h-4 text-[#06B6D4]" />
      <span className="text-xs font-mono font-semibold text-slate-300 uppercase tracking-wider">{title}</span>
      {subtitle && <span className="ml-auto text-[11px] font-mono text-slate-500">{subtitle}</span>}
    </div>
    {children}
  </div>
);

export const AnalyticsPage: React.FC = () => {
  const [stats, setStats] = useState<StatisticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getStatistics();
      setStats(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch analytics data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchStats(); }, []);

  const landTypeData = stats
    ? Object.entries(stats.land_type_counts)
        .filter(([, v]) => v > 0)
        .map(([name, value]) => ({ name, value, fill: LAND_COLOURS[name] ?? '#64748B' }))
    : [];

  const formatData = stats
    ? Object.entries(stats.format_counts)
        .filter(([, v]) => v > 0)
        .map(([name, value], i) => ({ name, value, fill: FORMAT_COLOURS[i % FORMAT_COLOURS.length] }))
    : [];

  const timelineData = stats
    ? Object.entries(stats.timeline_counts)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([date, count]) => ({ date, count }))
    : [];

  const metaData = stats
    ? [
        { name: 'Complete', value: stats.complete_metadata_count, fill: '#10B981' },
        { name: 'Incomplete', value: stats.incomplete_metadata_count, fill: '#F59E0B' },
      ]
    : [];

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#06B6D4]" />
            <span className="text-xs font-mono font-semibold text-[#06B6D4] uppercase tracking-wider">GEOSPATIAL INTELLIGENCE CONSOLE</span>
          </div>
          <h1 className="text-2xl font-bold font-mono tracking-tight text-white mt-1">Analytics</h1>
          <p className="text-xs text-slate-400 font-mono mt-0.5">Real-time catalog statistics, distribution analysis, and storage metrics.</p>
        </div>
        <button
          onClick={fetchStats}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#0D1117] border border-slate-800 hover:border-slate-700 text-slate-300 text-xs font-mono transition disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          REFRESH
        </button>
      </div>

      {loading && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
            {[...Array(5)].map((_, i) => <LoadingSkeleton key={i} className="h-28 rounded-xl" />)}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <LoadingSkeleton className="h-72 rounded-2xl" />
            <LoadingSkeleton className="h-72 rounded-2xl" />
          </div>
        </div>
      )}

      {error && !loading && (
        <ErrorState title="Analytics Load Failed" message={error} onRetry={fetchStats} />
      )}

      {stats && !loading && (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            <MetricCard label="Total Images" value={stats.total_images} icon={Database} accentColor="#06B6D4" subValue="in catalog" />
            <MetricCard label="Complete Metadata" value={stats.complete_metadata_count} icon={CheckCircle2} accentColor="#10B981"
              subValue={`${((stats.complete_metadata_count / (stats.total_images || 1)) * 100).toFixed(1)}% complete`} />
            <MetricCard label="Incomplete" value={stats.incomplete_metadata_count} icon={AlertTriangle} accentColor="#F59E0B" subValue="missing fields" />
            <MetricCard label="Storage Used" value={fmtBytes(stats.storage_stats.total_bytes)} icon={HardDrive} accentColor="#8B5CF6"
              subValue={`avg ${fmtBytes(stats.storage_stats.avg_bytes)}`} />
            <MetricCard label="Land Classes" value={Object.values(stats.land_type_counts).filter(v => v > 0).length} icon={Globe} accentColor="#3B82F6" subValue="active types" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Panel title="Land Type Distribution" subtitle="spectral classification" icon={PieIcon}>
              {landTypeData.length > 0 ? (
                <div className="flex flex-col sm:flex-row items-center gap-4">
                  <ResponsiveContainer width="100%" height={220}>
                    <PieChart>
                      <Pie data={landTypeData} cx="50%" cy="50%" innerRadius={55} outerRadius={90} paddingAngle={3} dataKey="value">
                        {landTypeData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                      </Pie>
                      <Tooltip content={<ChartTooltip />} />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="space-y-2 min-w-[130px]">
                    {landTypeData.map((d) => (
                      <div key={d.name} className="flex items-center gap-2 text-xs font-mono">
                        <span className="w-2.5 h-2.5 rounded-sm shrink-0" style={{ backgroundColor: d.fill }} />
                        <span className="text-slate-400 truncate">{d.name}</span>
                        <span className="ml-auto text-slate-200 font-bold">{d.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="h-48 flex items-center justify-center text-slate-500 text-xs font-mono">No land type data available</div>
              )}
            </Panel>

            <Panel title="Metadata Completeness" subtitle="complete vs incomplete" icon={CheckCircle2}>
              {stats.total_images > 0 ? (
                <div className="flex flex-col sm:flex-row items-center gap-6">
                  <ResponsiveContainer width="100%" height={220}>
                    <PieChart>
                      <Pie data={metaData} cx="50%" cy="50%" innerRadius={55} outerRadius={90} paddingAngle={4} dataKey="value">
                        {metaData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                      </Pie>
                      <Tooltip content={<ChartTooltip />} />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="space-y-4 min-w-[130px]">
                    {metaData.map((d) => (
                      <div key={d.name} className="text-xs font-mono">
                        <div className="flex items-center gap-2">
                          <span className="w-2.5 h-2.5 rounded-sm shrink-0" style={{ backgroundColor: d.fill }} />
                          <span className="text-slate-400">{d.name}</span>
                        </div>
                        <div className="text-slate-100 font-bold text-xl mt-0.5 ml-4">{d.value}</div>
                        <div className="text-slate-500 ml-4">{((d.value / (stats.total_images || 1)) * 100).toFixed(1)}%</div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="h-48 flex items-center justify-center text-slate-500 text-xs font-mono">No metadata statistics available</div>
              )}
            </Panel>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Panel title="Land Type Count Distribution" subtitle="bar chart" icon={BarChart3}>
              {landTypeData.length > 0 ? (
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={landTypeData} margin={{ top: 4, right: 12, left: 0, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                    <XAxis dataKey="name" tick={{ fill: '#64748B', fontSize: 10, fontFamily: 'monospace' }} />
                    <YAxis tick={{ fill: '#64748B', fontSize: 10, fontFamily: 'monospace' }} />
                    <Tooltip content={<ChartTooltip />} />
                    <Bar dataKey="value" name="Images" radius={[4, 4, 0, 0]}>
                      {landTypeData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-48 flex items-center justify-center text-slate-500 text-xs font-mono">No data</div>
              )}
            </Panel>

            <Panel title="Image Format Distribution" subtitle="by extension" icon={ImageIcon}>
              {formatData.length > 0 ? (
                <div className="flex flex-col sm:flex-row items-center gap-4">
                  <ResponsiveContainer width="100%" height={220}>
                    <PieChart>
                      <Pie data={formatData} cx="50%" cy="50%" innerRadius={50} outerRadius={85} paddingAngle={4} dataKey="value">
                        {formatData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                      </Pie>
                      <Tooltip content={<ChartTooltip />} />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="space-y-2 min-w-[120px]">
                    {formatData.map((d) => (
                      <div key={d.name} className="flex items-center gap-2 text-xs font-mono">
                        <span className="w-2.5 h-2.5 rounded-sm shrink-0" style={{ backgroundColor: d.fill }} />
                        <span className="text-slate-400">{d.name}</span>
                        <span className="ml-auto text-slate-200 font-bold">{d.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="h-48 flex items-center justify-center text-slate-500 text-xs font-mono">No format data available</div>
              )}
            </Panel>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Panel title="Acquisition Timeline" subtitle="images by ingestion date" icon={Calendar}>
              {timelineData.length > 0 ? (
                <ResponsiveContainer width="100%" height={240}>
                  <LineChart data={timelineData} margin={{ top: 4, right: 12, left: 0, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                    <XAxis dataKey="date" tick={{ fill: '#64748B', fontSize: 10, fontFamily: 'monospace' }} />
                    <YAxis tick={{ fill: '#64748B', fontSize: 10, fontFamily: 'monospace' }} />
                    <Tooltip content={<ChartTooltip />} />
                    <Line type="monotone" dataKey="count" name="Images" stroke="#06B6D4" strokeWidth={2} dot={{ fill: '#06B6D4', r: 4 }} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-48 flex flex-col items-center justify-center gap-2 text-xs font-mono text-slate-500">
                  <Calendar className="w-8 h-8 opacity-20" />
                  <span className="text-slate-400">Insufficient date metadata for timeline</span>
                  <span className="text-slate-600 text-center max-w-48">Most images in this catalog lack acquisition date metadata.</span>
                </div>
              )}
            </Panel>

            <Panel title="Storage Statistics" subtitle="file size metrics" icon={HardDrive}>
              <div className="space-y-3 font-mono text-xs">
                {[
                  { label: 'Total Storage', value: fmtBytes(stats.storage_stats.total_bytes), color: '#06B6D4' },
                  { label: 'Average File Size', value: fmtBytes(stats.storage_stats.avg_bytes), color: '#3B82F6' },
                  { label: 'Largest File', value: fmtBytes(stats.storage_stats.max_bytes), color: '#F59E0B' },
                  { label: 'Smallest File', value: fmtBytes(stats.storage_stats.min_bytes), color: '#10B981' },
                  { label: 'Files with Size Data', value: `${stats.storage_stats.count_with_size} / ${stats.total_images}`, color: '#8B5CF6' },
                ].map((row) => (
                  <div key={row.label} className="flex items-center justify-between py-2.5 border-b border-slate-800/60 last:border-0">
                    <span className="text-slate-500">{row.label}</span>
                    <span className="font-bold text-sm" style={{ color: row.color }}>{row.value}</span>
                  </div>
                ))}
              </div>
            </Panel>
          </div>
        </>
      )}
    </div>
  );
};
