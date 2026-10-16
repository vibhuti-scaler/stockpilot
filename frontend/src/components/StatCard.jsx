export default function StatCard({ label, value, hint, icon, tone = 'neutral' }) {
  return (
    <div className={`stat tone-${tone}`}>
      <div className="stat-icon">{icon}</div>
      <div>
        <small>{label}</small>
        <strong>{value}</strong>
        <span>{hint}</span>
      </div>
    </div>
  );
}
