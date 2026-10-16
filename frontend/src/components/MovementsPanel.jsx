import { timeAgo } from '../api.js';

export default function MovementsPanel({ movements, compact = false }) {
  return (
    <div className={`panel ${compact ? 'activity' : ''}`}>
      <div className="panel-head">
        <div>
          <h2>{compact ? 'Recent movements' : 'Stock ledger'}</h2>
          <p className="muted">{compact ? 'Latest warehouse activity.' : `${movements.length} most recent entries.`}</p>
        </div>
      </div>
      {!movements.length && <div className="empty">No stock movements recorded yet.</div>}
      {compact ? (
        movements.map((m) => (
          <div className="activity-row" key={m.id}>
            <span className={`activity-icon ${m.movement_type.toLowerCase()}`}>{m.movement_type === 'IN' ? '↓' : '↑'}</span>
            <div>
              <b>{m.movement_type === 'IN' ? 'Received' : 'Issued'} {m.quantity} × {m.product_name}</b>
              <small>{m.note || m.product_sku} · {timeAgo(m.created_at)}</small>
            </div>
          </div>
        ))
      ) : (
        movements.length > 0 && (
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>When</th><th>Type</th><th>Product</th><th>Quantity</th><th>Note</th></tr>
              </thead>
              <tbody>
                {movements.map((m) => (
                  <tr key={m.id}>
                    <td title={m.created_at}>{timeAgo(m.created_at)}</td>
                    <td><span className={`status ${m.movement_type === 'IN' ? 'in_stock' : 'low_stock'}`}>{m.movement_type}</span></td>
                    <td><b>{m.product_name}</b> <small className="muted">{m.product_sku}</small></td>
                    <td>{m.movement_type === 'IN' ? '+' : '−'}{m.quantity}</td>
                    <td>{m.note || <span className="muted">—</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}
    </div>
  );
}
