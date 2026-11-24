import { getRisk } from '../utils/format';

const RADIUS = 54;
const ARC_LENGTH = Math.PI * RADIUS;
const ARC_PATH = 'M 16 80 A 54 54 0 0 1 124 80';

export default function ScoreGauge({ score = 0, level, compact = false }) {
  const value = Math.max(0, Math.min(100, Number(score) || 0));
  const risk = getRisk(level);
  const filled = (value / 100) * ARC_LENGTH;

  return (
    <div className={`relative ${compact ? 'w-[120px]' : 'w-[176px]'}`}>
      <svg viewBox="0 0 140 96" className="w-full" role="img" aria-label={`Risk score ${value} out of 100`}>
        <path d={ARC_PATH} fill="none" stroke="#E8EDF3" strokeWidth="10" strokeLinecap="round" />
        <path
          d={ARC_PATH}
          fill="none"
          stroke={risk.stroke}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={`${filled} ${ARC_LENGTH}`}
          className="transition-all duration-500"
        />
      </svg>
      <div className="absolute inset-x-0 bottom-0 text-center">
        <div className="text-3xl font-bold tracking-tight text-slate-900 tabular-nums">{value}</div>
        <div className="text-[11px] font-medium uppercase tracking-wider text-slate-400">Risk score</div>
      </div>
    </div>
  );
}
