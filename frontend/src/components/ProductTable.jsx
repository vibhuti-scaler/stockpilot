import { currency } from '../api.js';

const FILTERS = [
  ['ALL', 'All'],
  ['IN_STOCK', 'In stock'],
  ['LOW_STOCK', 'Low stock'],
  ['OUT_OF_STOCK', 'Out of stock'],
];

const STATUS_LABEL = { IN_STOCK: 'In stock', LOW_STOCK: 'Low stock', OUT_OF_STOCK: 'Out of stock' };

export default function ProductTable({
  products, loading, filter, onFilter, search, onSearch, onReceive, onIssue, onDelete, compact = false,
}) {
  return (
    <div className="panel">
      <div className="panel-head">
        <div>
          <h2>Products</h2>
          <p className="muted">{products.length} item{products.length === 1 ? '' : 's'} shown</p>
        </div>
        <div className="panel-tools">
          <input
            className="search"
            type="search"
            placeholder="Search name or SKU…"
            value={search}
            onChange={(e) => onSearch(e.target.value)}
            aria-label="Search products"
          />
          <div className="filters" role="tablist">
            {FILTERS.map(([key, label]) => (
              <button
                key={key}
                role="tab"
                aria-selected={filter === key}
                className={filter === key ? 'selected' : ''}
                onClick={() => onFilter(key)}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {loading ? (
        <div className="empty">Loading products…</div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Product</th>
                {!compact && <th>Supplier</th>}
                <th>Stock level</th>
                <th>Unit price</th>
                <th>Status</th>
                <th aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {products.map((p) => {
                const pct = Math.min(100, Math.round((p.quantity / Math.max(p.reorder_level * 3, 1)) * 100));
                return (
                  <tr key={p.id}>
                    <td>
                      <div className="product-cell">
                        <span className={`dot ${p.stock_status.toLowerCase()}`} />
                        <div>
                          <b>{p.name}</b>
                          <small>{p.sku} <span className="chip">{p.category}</span></small>
                        </div>
                      </div>
                    </td>
                    {!compact && <td className="nowrap">{p.supplier_name || <span className="muted">—</span>}</td>}
                    <td>
                      <div className="level">
                        <div className="level-bar"><i className={p.stock_status.toLowerCase()} style={{ width: `${pct}%` }} /></div>
                        <small>{p.quantity} / reorder at {p.reorder_level}</small>
                      </div>
                    </td>
                    <td>{currency.format(p.unit_price)}</td>
                    <td><span className={`status ${p.stock_status.toLowerCase()}`}>{STATUS_LABEL[p.stock_status]}</span></td>
                    <td className="actions">
                      <button className="icon-btn" title="Receive stock (IN)" onClick={() => onReceive(p)}>＋</button>
                      <button className="icon-btn" title="Issue stock (OUT)" onClick={() => onIssue(p)} disabled={p.quantity === 0}>－</button>
                      {!compact && <button className="icon-btn danger" title="Delete product" onClick={() => onDelete(p)}>🗑</button>}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {!products.length && <div className="empty">No products match this filter.</div>}
        </div>
      )}
    </div>
  );
}
