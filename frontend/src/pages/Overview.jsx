import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { BellRing, ChevronRight, ScanLine, ShieldAlert, ShieldCheck, TriangleAlert } from 'lucide-react';
import { analyticsService, familyService } from '../api/services';
import { useFetch } from '../hooks/useFetch';
import PageHeader from '../components/PageHeader';
import StatCard from '../components/StatCard';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import LoadingState from '../components/LoadingState';
import RiskBadge from '../components/RiskBadge';
import ScanDetailModal from '../components/ScanDetailModal';
import { formatRelative, getRisk, toPercent } from '../utils/format';

const PIE_COLORS = {
  safe: '#10b981',
  suspicious: '#f59e0b',
  'high risk': '#ef4444',
};

const tooltipStyle = {
  borderRadius: 12,
  border: '1px solid #E4E9F0',
  boxShadow: '0 10px 30px rgba(15,23,42,0.08)',
  fontSize: 12,
  padding: '8px 12px',
};

function Panel({ title, description, children, className = '' }) {
  return (
    <section className={`fs-card flex flex-col p-5 sm:p-6 ${className}`}>
      <div className="mb-5">
        <h2 className="fs-section-title">{title}</h2>
        {description && <p className="mt-1 text-xs text-slate-400">{description}</p>}
      </div>
      <div className="flex-1">{children}</div>
    </section>
  );
}

export default function Overview() {
  const { data, loading, error, reload } = useFetch(analyticsService.overview, []);
  const { data: families } = useFetch(familyService.list, []);
  const [selectedScan, setSelectedScan] = useState(null);

  if (loading) {
    return (
      <>
        <PageHeader title="Overview" description="Loading your safety snapshot…" />
        <div className="fs-card"><LoadingState label="Loading your dashboard…" /></div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <PageHeader title="Overview" />
        <div className="fs-card"><ErrorState error={error} onRetry={reload} title="Could not load your overview" /></div>
      </>
    );
  }

  const trend = Array.isArray(data?.weekly_trend) ? data.weekly_trend : [];
  const categories = Array.isArray(data?.categories) ? data.categories : [];
  const distribution = Array.isArray(data?.risk_distribution) ? data.risk_distribution : [];
  const familyActivity = Array.isArray(data?.family_activity) ? data.family_activity : [];
  const recentScans = Array.isArray(data?.recent_scans) ? data.recent_scans : [];
  const totalScans = data?.total_scans ?? 0;

  const isEmpty =
    totalScans === 0 &&
    !trend.some((day) => Number(day.scans) > 0) &&
    !categories.length &&
    !familyActivity.length &&
    !recentScans.length;

  return (
    <>
      <PageHeader
        eyebrow="Overview"
        title="Your safety at a glance"
        description={
          data?.scope
            ? `Showing ${data.scope}. Figures come from completed scans and family alerts.`
            : 'Figures come from completed scans and family alerts.'
        }
        actions={
          <Link to="/app/scanner" className="fs-btn-primary">
            <ScanLine className="h-4 w-4" /> New scan
          </Link>
        }
      />

      {isEmpty ? (
        <div className="fs-card">
          <EmptyState
            icon={ScanLine}
            title="No scans yet"
            description="Once you check a message or link, your results and trends will appear here."
            action={
              <Link to="/app/scanner" className="fs-btn-primary">Scan your first message</Link>
            }
          />
        </div>
      ) : (
        <div className="space-y-5">
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 xl:grid-cols-5">
            <StatCard label="Total scans" value={totalScans} hint={`Average risk score ${toPercent(data?.average_risk_score)}`} icon={ScanLine} />
            <StatCard label="High risk" value={data?.high_risk ?? 0} hint="Needs attention" icon={ShieldAlert} tone="red" />
            <StatCard label="Suspicious" value={data?.suspicious ?? 0} hint="Worth a closer look" icon={TriangleAlert} tone="amber" />
            <StatCard label="Safe" value={data?.safe ?? 0} hint="No obvious indicators" icon={ShieldCheck} tone="emerald" />
            <StatCard
              label="Unread alerts"
              value={data?.unread_alerts ?? 0}
              hint={`${data?.shared_alerts ?? 0} alerts shared`}
              icon={BellRing}
              tone="navy"
            />
          </div>

          <div className="grid gap-5 lg:grid-cols-3">
            <Panel title="Scan activity" description="Checks completed over the last 7 days" className="lg:col-span-2">
              {trend.length ? (
                <div className="h-[260px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={trend} margin={{ top: 8, right: 8, left: -24, bottom: 0 }}>
                      <defs>
                        <linearGradient id="scansFill" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#1e3656" stopOpacity={0.22} />
                          <stop offset="100%" stopColor="#1e3656" stopOpacity={0.01} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid vertical={false} stroke="#EEF2F7" strokeDasharray="3 3" />
                      <XAxis dataKey="label" tickLine={false} axisLine={false} tick={{ fill: '#94A3B8', fontSize: 11 }} dy={8} />
                      <YAxis allowDecimals={false} tickLine={false} axisLine={false} tick={{ fill: '#94A3B8', fontSize: 11 }} />
                      <Tooltip contentStyle={tooltipStyle} formatter={(value, name) => [value, name === 'scans' ? 'Scans' : 'High risk']} />
                      <Area type="monotone" dataKey="scans" stroke="#223A5B" strokeWidth={2} fill="url(#scansFill)" dot={false} activeDot={{ r: 4 }} />
                      <Area type="monotone" dataKey="high_risk" stroke="#EF4444" strokeWidth={2} fill="transparent" dot={false} activeDot={{ r: 4 }} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <p className="py-16 text-center text-sm text-slate-400">No activity in the last 7 days.</p>
              )}
            </Panel>

            <Panel title="Risk distribution" description="How results were classified">
              {distribution.length ? (
                <>
                  <div className="h-[210px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie data={distribution} dataKey="value" nameKey="name" innerRadius={58} outerRadius={84} paddingAngle={3} stroke="none">
                          {distribution.map((entry) => (
                            <Cell key={entry.name} fill={PIE_COLORS[String(entry.name).toLowerCase()] || '#94A3B8'} />
                          ))}
                        </Pie>
                        <Tooltip contentStyle={tooltipStyle} formatter={(value) => [value, 'Scans']} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <ul className="mt-2 space-y-2">
                    {distribution.map((entry) => (
                      <li key={entry.name} className="flex items-center justify-between text-xs">
                        <span className="flex items-center gap-2 text-slate-600">
                          <span
                            className="h-2 w-2 rounded-full"
                            style={{ backgroundColor: PIE_COLORS[String(entry.name).toLowerCase()] || '#94A3B8' }}
                          />
                          {entry.name}
                        </span>
                        <span className="font-semibold text-slate-800 tabular-nums">{entry.value}</span>
                      </li>
                    ))}
                  </ul>
                </>
              ) : (
                <p className="py-16 text-center text-sm text-slate-400">No classified results yet.</p>
              )}
            </Panel>
          </div>

          <div className="grid gap-5 lg:grid-cols-2">
            <Panel title="Most common categories" description="What your scans were about">
              {categories.length ? (
                <div className="h-[260px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={categories} layout="vertical" margin={{ top: 4, right: 16, left: 8, bottom: 4 }}>
                      <CartesianGrid horizontal={false} stroke="#EEF2F7" strokeDasharray="3 3" />
                      <XAxis type="number" allowDecimals={false} tickLine={false} axisLine={false} tick={{ fill: '#94A3B8', fontSize: 11 }} />
                      <YAxis
                        type="category"
                        dataKey="name"
                        width={130}
                        tickLine={false}
                        axisLine={false}
                        tick={{ fill: '#64748B', fontSize: 11 }}
                      />
                      <Tooltip contentStyle={tooltipStyle} formatter={(value) => [value, 'Scans']} cursor={{ fill: '#F8FAFC' }} />
                      <Bar dataKey="count" fill="#0F766E" radius={[0, 6, 6, 0]} barSize={18} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <p className="py-16 text-center text-sm text-slate-400">No categories recorded yet.</p>
              )}
            </Panel>

            <Panel title="Family activity" description="Checks shared with each family">
              {familyActivity.length ? (
                <div className="overflow-x-auto fs-scroll">
                  <table className="w-full min-w-[360px] text-left text-sm">
                    <thead>
                      <tr className="border-b border-line text-[11px] uppercase tracking-wide text-slate-400">
                        <th className="pb-2.5 font-medium">Family</th>
                        <th className="pb-2.5 text-right font-medium">Scans</th>
                        <th className="pb-2.5 text-right font-medium">High risk</th>
                        <th className="pb-2.5 text-right font-medium">Members</th>
                      </tr>
                    </thead>
                    <tbody>
                      {familyActivity.map((row) => (
                        <tr key={row.family_name} className="border-b border-line/60 last:border-0">
                          <td className="py-3 font-medium text-slate-700">{row.family_name}</td>
                          <td className="py-3 text-right tabular-nums text-slate-600">{row.scans}</td>
                          <td className="py-3 text-right tabular-nums text-red-600">{row.high_risk}</td>
                          <td className="py-3 text-right tabular-nums text-slate-600">{row.members}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="py-16 text-center text-sm text-slate-400">No shared family activity yet.</p>
              )}
            </Panel>
          </div>

          <Panel title="Recent scans" description="Your latest checks">
            {recentScans.length ? (
              <ul className="divide-y divide-line">
                {recentScans.map((scan) => (
                  <li key={scan.id}>
                    <button
                      type="button"
                      onClick={() => setSelectedScan(scan)}
                      className="flex w-full items-center gap-3 py-3.5 text-left transition hover:bg-slate-50/70"
                    >
                      <span className={`h-8 w-1 shrink-0 rounded-full ${getRisk(scan.risk_level).bar}`} />
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium text-slate-800">{scan.category || 'Scan result'}</p>
                        <p className="mt-0.5 text-xs text-slate-400">
                          {scan.scan_type === 'url' ? 'Link check' : 'Message check'} · {formatRelative(scan.created_at)}
                        </p>
                      </div>
                      <RiskBadge level={scan.risk_level} />
                      <ChevronRight className="h-4 w-4 shrink-0 text-slate-300" />
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="py-16 text-center text-sm text-slate-400">No recent scans to show.</p>
            )}
          </Panel>
        </div>
      )}

      {selectedScan && (
        <ScanDetailModal
          scanId={selectedScan.id}
          initialScan={selectedScan}
          families={families || []}
          onClose={() => setSelectedScan(null)}
        />
      )}
    </>
  );
}
