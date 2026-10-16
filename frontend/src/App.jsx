import { useCallback, useEffect, useState } from 'react';
import { api } from './api.js';
import Sidebar from './components/Sidebar.jsx';
import StatCard from './components/StatCard.jsx';
import ProductTable from './components/ProductTable.jsx';
import MovementsPanel from './components/MovementsPanel.jsx';
import SuppliersPanel from './components/SuppliersPanel.jsx';
import ProductModal from './components/ProductModal.jsx';
import StockModal from './components/StockModal.jsx';
import { currency } from './api.js';

const EMPTY_STATS = {
  totalProducts: 0,
  totalUnits: 0,
  lowStock: 0,
  outOfStock: 0,
  inventoryValue: 0,
  suppliers: 0,
  movementsToday: 0,
};

const VIEW_TITLES = {
  dashboard: ['WORKSPACE / OVERVIEW', 'Inventory overview', 'Live stock levels, reorder alerts and the latest warehouse activity.'],
  products: ['WORKSPACE / CATALOGUE', 'Products', 'Every SKU in the catalogue with quantity, reorder level and supplier.'],
  suppliers: ['WORKSPACE / VENDORS', 'Suppliers', 'Vendors that provide the products in this warehouse.'],
  movements: ['WORKSPACE / LEDGER', 'Stock movements', 'Append-only ledger of goods received (IN) and issued (OUT).'],
};

export default function App() {
  const [view, setView] = useState('dashboard');
  const [products, setProducts] = useState([]);
  const [stats, setStats] = useState(EMPTY_STATS);
  const [movements, setMovements] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [filter, setFilter] = useState('ALL');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [toast, setToast] = useState('');
  const [productModal, setProductModal] = useState(false);
  const [stockModal, setStockModal] = useState(null); // { product, type }

  const notify = (message) => {
    setToast(message);
    window.setTimeout(() => setToast(''), 3200);
  };

  const load = useCallback(async () => {
    try {
      setError('');
      const [p, s, m, v] = await Promise.all([
        api.products(),
        api.stats(),
        api.movements(12),
        api.suppliers(),
      ]);
      setProducts(p);
      setStats(s);
      setMovements(m);
      setSuppliers(v);
    } catch (err) {
      setError(err.message === 'Failed to fetch' ? 'Backend unavailable' : err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const timer = window.setInterval(load, 30000);
    return () => window.clearInterval(timer);
  }, [load]);

  const run = async (action, successMessage) => {
    try {
      await action();
      await load();
      if (successMessage) notify(successMessage);
      return true;
    } catch (err) {
      notify(`⚠ ${err.message}`);
      return false;
    }
  };

  const visible = products.filter((p) => {
    const matchesFilter = filter === 'ALL' || p.stock_status === filter;
    const term = search.trim().toLowerCase();
    const matchesSearch =
      !term || p.name.toLowerCase().includes(term) || p.sku.toLowerCase().includes(term);
    return matchesFilter && matchesSearch;
  });

  const [eyebrow, title, subtitle] = VIEW_TITLES[view];

  return (
    <div className="app">
      <Sidebar view={view} onNavigate={setView} alerts={stats.lowStock + stats.outOfStock} />

      <main className="main">
        <header className="page-head">
          <div>
            <p className="eyebrow">{eyebrow}</p>
            <h1>{title}</h1>
            <p className="muted">{subtitle}</p>
          </div>
          <div className="head-actions">
            <button className="ghost" onClick={load} title="Refresh data">↻ Refresh</button>
            <button className="primary" onClick={() => setProductModal(true)}>＋ New product</button>
          </div>
        </header>

        {error && (
          <div className="alert" role="alert">
            ⚠ {error}. Start the backend and PostgreSQL, then refresh.
          </div>
        )}

        {(view === 'dashboard' || view === 'products') && (
          <section className="stats" aria-label="Inventory KPIs">
            <StatCard label="Products" value={stats.totalProducts} hint={`${stats.suppliers} suppliers`} icon="▦" />
            <StatCard label="Units in stock" value={stats.totalUnits.toLocaleString('en-IN')} hint={`${stats.movementsToday} movements in 24h`} icon="◫" />
            <StatCard label="Needs reorder" value={stats.lowStock + stats.outOfStock} hint={`${stats.outOfStock} out of stock`} icon="!" tone={stats.lowStock + stats.outOfStock ? 'warn' : 'ok'} />
            <StatCard label="Inventory value" value={currency.format(stats.inventoryValue)} hint="quantity × unit price" icon="₹" />
          </section>
        )}

        {view === 'dashboard' && (
          <section className="content-grid">
            <ProductTable
              compact
              products={visible}
              loading={loading}
              filter={filter}
              onFilter={setFilter}
              search={search}
              onSearch={setSearch}
              onReceive={(product) => setStockModal({ product, type: 'IN' })}
              onIssue={(product) => setStockModal({ product, type: 'OUT' })}
              onDelete={(product) =>
                window.confirm(`Delete ${product.name}?`) &&
                run(() => api.deleteProduct(product.id), `Deleted ${product.sku}`)
              }
            />
            <div className="side-stack">
              <MovementsPanel movements={movements.slice(0, 6)} compact />
            </div>
          </section>
        )}

        {view === 'products' && (
          <ProductTable
            products={visible}
            loading={loading}
            filter={filter}
            onFilter={setFilter}
            search={search}
            onSearch={setSearch}
            onReceive={(product) => setStockModal({ product, type: 'IN' })}
            onIssue={(product) => setStockModal({ product, type: 'OUT' })}
            onDelete={(product) =>
              window.confirm(`Delete ${product.name}?`) &&
              run(() => api.deleteProduct(product.id), `Deleted ${product.sku}`)
            }
          />
        )}

        {view === 'suppliers' && (
          <SuppliersPanel
            suppliers={suppliers}
            products={products}
            onCreate={(payload) => run(() => api.createSupplier(payload), `Added supplier ${payload.name}`)}
            onDelete={(supplier) =>
              window.confirm(`Delete ${supplier.name}? Its products will be kept without a supplier.`) &&
              run(() => api.deleteSupplier(supplier.id), `Deleted ${supplier.name}`)
            }
          />
        )}

        {view === 'movements' && <MovementsPanel movements={movements} />}

        <footer className="page-foot">
          StockPilot · DevOps Capstone · Vibhuti Bhatnagar (24bcs10288)
        </footer>
      </main>

      {productModal && (
        <ProductModal
          suppliers={suppliers}
          onClose={() => setProductModal(false)}
          onSubmit={async (payload) => {
            const ok = await run(() => api.createProduct(payload), `Created ${payload.sku.toUpperCase()}`);
            if (ok) setProductModal(false);
          }}
        />
      )}

      {stockModal && (
        <StockModal
          product={stockModal.product}
          type={stockModal.type}
          onClose={() => setStockModal(null)}
          onSubmit={async (payload) => {
            const ok = await run(
              () => api.createMovement(payload),
              `${payload.movement_type === 'IN' ? 'Received' : 'Issued'} ${payload.quantity} × ${stockModal.product.sku}`,
            );
            if (ok) setStockModal(null);
          }}
        />
      )}

      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}
