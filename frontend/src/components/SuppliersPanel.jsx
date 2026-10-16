import { useState } from 'react';

export default function SuppliersPanel({ suppliers, products, onCreate, onDelete }) {
  const [form, setForm] = useState({ name: '', contact_email: '', phone: '', city: '' });

  const submit = async (e) => {
    e.preventDefault();
    const ok = await onCreate(form);
    if (ok) setForm({ name: '', contact_email: '', phone: '', city: '' });
  };

  const countFor = (id) => products.filter((p) => p.supplier_id === id).length;

  return (
    <section className="content-grid">
      <div className="panel">
        <div className="panel-head">
          <div>
            <h2>Suppliers</h2>
            <p className="muted">{suppliers.length} vendor{suppliers.length === 1 ? '' : 's'}</p>
          </div>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Name</th><th>Contact</th><th>City</th><th>Products</th><th aria-label="Actions" /></tr>
            </thead>
            <tbody>
              {suppliers.map((s) => (
                <tr key={s.id}>
                  <td><b>{s.name}</b></td>
                  <td>{s.contact_email || '—'}<br /><small className="muted">{s.phone}</small></td>
                  <td>{s.city || '—'}</td>
                  <td><span className="chip">{countFor(s.id)}</span></td>
                  <td className="actions"><button className="icon-btn danger" title="Delete supplier" onClick={() => onDelete(s)}>🗑</button></td>
                </tr>
              ))}
            </tbody>
          </table>
          {!suppliers.length && <div className="empty">No suppliers yet. Add one on the right.</div>}
        </div>
      </div>

      <form className="panel form-panel" onSubmit={submit}>
        <div className="panel-head">
          <div>
            <h2>Add supplier</h2>
            <p className="muted">POST /api/suppliers</p>
          </div>
        </div>
        <div className="form-body">
          <label>Name<input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g. Nimbus Electronics" /></label>
          <label>Email<input type="email" value={form.contact_email} onChange={(e) => setForm({ ...form, contact_email: e.target.value })} placeholder="orders@vendor.example" /></label>
          <label>Phone<input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} placeholder="+91 …" /></label>
          <label>City<input value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} placeholder="Bengaluru" /></label>
          <button className="primary full">Save supplier</button>
        </div>
      </form>
    </section>
  );
}
