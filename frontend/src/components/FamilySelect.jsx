export default function FamilySelect({
  families = [],
  value = '',
  onChange,
  id = 'family_id',
  label = 'Share with family (optional)',
  helper = 'A family alert is created automatically for suspicious or high-risk results.',
  disabled = false,
}) {
  return (
    <div>
      <label htmlFor={id} className="fs-label">{label}</label>
      <select
        id={id}
        className="fs-input"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled}
      >
        <option value="">Just for me — do not share</option>
        {families.map((family) => (
          <option key={family.id} value={family.id}>
            {family.name}
          </option>
        ))}
      </select>
      {helper && <p className="mt-1.5 text-xs text-slate-400">{helper}</p>}
    </div>
  );
}
