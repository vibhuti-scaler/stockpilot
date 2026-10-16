const NAV = [
  { id: 'dashboard', icon: '▦', label: 'Dashboard' },
  { id: 'products', icon: '◫', label: 'Products' },
  { id: 'suppliers', icon: '◎', label: 'Suppliers' },
  { id: 'movements', icon: '⇅', label: 'Movements' },
];

export default function Sidebar({ view, onNavigate, alerts }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark">S</span>
        <div>
          <b>StockPilot</b>
          <small>Inventory management</small>
        </div>
      </div>

      <nav aria-label="Primary">
        {NAV.map((item) => (
          <button
            key={item.id}
            className={view === item.id ? 'active' : ''}
            onClick={() => onNavigate(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
            {item.id === 'products' && alerts > 0 && <span className="badge">{alerts}</span>}
          </button>
        ))}
      </nav>

      <div className="side-bottom">
        <div className="pipeline-card">
          <strong>Delivery pipeline</strong>
          <div className="pipeline">
            <span>Test</span><i /><span>Build</span><i /><span>Scan</span><i /><span>Deploy</span>
          </div>
          <p>GitHub Actions → GHCR → Helm on EKS</p>
        </div>
        <div className="profile">
          <div className="avatar">VB</div>
          <div>
            <b>Vibhuti Bhatnagar</b>
            <small>24bcs10288 · DevOps Capstone</small>
          </div>
        </div>
      </div>
    </aside>
  );
}
