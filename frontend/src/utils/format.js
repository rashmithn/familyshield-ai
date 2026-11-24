export const RISK_LEVELS = {
  safe: {
    label: 'Safe',
    badge: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
    dot: 'bg-emerald-500',
    stroke: '#10b981',
    bar: 'bg-emerald-500',
  },
  suspicious: {
    label: 'Suspicious',
    badge: 'bg-amber-50 text-amber-700 ring-amber-200',
    dot: 'bg-amber-500',
    stroke: '#f59e0b',
    bar: 'bg-amber-500',
  },
  high_risk: {
    label: 'High risk',
    badge: 'bg-red-50 text-red-700 ring-red-200',
    dot: 'bg-red-500',
    stroke: '#ef4444',
    bar: 'bg-red-500',
  },
};

export const getRisk = (level) => RISK_LEVELS[level] || RISK_LEVELS.suspicious;

export const SEVERITY_STYLES = {
  low: 'bg-slate-100 text-slate-600 ring-slate-200',
  medium: 'bg-amber-50 text-amber-700 ring-amber-200',
  high: 'bg-red-50 text-red-700 ring-red-200',
};

export function getErrorMessage(error, fallback = 'Something went wrong. Please try again.') {
  const data = error?.response?.data;
  if (typeof data === 'string' && data.trim()) return data.trim();
  if (data?.message && typeof data.message === 'string') return data.message;

  let detail = data?.detail;
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => (typeof item === 'string' ? item : item?.msg))
      .filter(Boolean);
    if (messages.length) return messages.join(' ');
  }
  if (typeof detail === 'string' && detail.trim()) return detail.trim();
  if (detail && typeof detail === 'object') {
    const messages = Object.values(detail).flat().filter(Boolean);
    if (messages.length) return messages.join(' ');
  }
  if (error?.message === 'Network Error') return 'Cannot reach the server. Check your connection and try again.';
  if (error?.code === 'ECONNABORTED') return 'The server took too long to respond. Please try again.';
  if (error?.message && !error?.response) return error.message;
  return fallback;
}

export function formatDate(value, options = { month: 'short', day: 'numeric', year: 'numeric' }) {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '—';
  return new Intl.DateTimeFormat('en-IN', options).format(date);
}

export function formatDateTime(value) {
  return formatDate(value, { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' });
}

export function formatRelative(value) {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '—';
  const seconds = Math.max(0, Math.floor((Date.now() - date.getTime()) / 1000));
  if (seconds < 60) return 'Just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days === 1) return 'Yesterday';
  if (days < 7) return `${days}d ago`;
  return formatDate(value, { month: 'short', day: 'numeric' });
}

export function toPercent(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '—';
  const n = Number(value);
  return `${Math.round(n <= 1 && n > 0 ? n * 100 : n)}%`;
}

export function humanizeKey(key) {
  return String(key)
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export function formatDetailValue(value) {
  if (value === null || value === undefined || value === '') return '—';
  if (Array.isArray(value)) return value.map(formatDetailValue).join(', ');
  if (typeof value === 'object') return JSON.stringify(value);
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  return String(value);
}

export function initials(name) {
  const parts = String(name || '').trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return 'FS';
  return (parts[0][0] + (parts.length > 1 ? parts[parts.length - 1][0] : '')).toUpperCase();
}

export function pluralize(count, singular, plural = `${singular}s`) {
  return `${count} ${count === 1 ? singular : plural}`;
}
