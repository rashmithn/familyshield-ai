import { getRisk } from '../utils/format';

export default function RiskBadge({ level, score, className = '' }) {
  const risk = getRisk(level);
  return (
    <span className={`fs-badge ${risk.badge} ${className}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${risk.dot}`} />
      {risk.label}
      {typeof score === 'number' && <span className="font-semibold tabular-nums opacity-70">{score}/100</span>}
    </span>
  );
}
