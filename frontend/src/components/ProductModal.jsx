export default function ProductModal({ suppliers, onClose, onSubmit }) {
  const submit = (e) => {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    onSubmit({
      sku: f.get('sku').trim(),
      name: f.get('name').trim(),
      category: f.get('category').trim() || 'General',
      quantity: Number(f.get('quantity') || 0),
      reorder_level: Number(f.get('reorder_level') || 10),
      unit_price: Number(f.get('unit_price') || 0),
      supplier_id: f.get('supplier_id') ? Number(f.get('supplier_id')) : null,
    });
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <form className="modal" onSubmit={submit} onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <div>
            <p className="eyebrow">CREATE PRODUCT</p>
            <h2>Add a product to the catalogue</h2>
          </div>
          <button type="button" className="close" onClick={onClose} aria-label="Close">×</button>
        </div>
        <div className="form-row">
          <label>SKU<input name="sku" required placeholder="ELC-1004" pattern="[A-Za-z0-9\-]{2,40}" /></label>
          <label>Category<input name="category" placeholder="Electronics" defaultValue="General" /></label>
        </div>
        <label>Product name<input name="name" required placeholder="e.g. 27-inch Monitor" /></label>
        <div className="form-row three">
          <label>Opening quantity<input name="quantity" type="number" min="0" defaultValue="0" /></label>
          <label>Reorder level<input name="reorder_level" type="number" min="0" defaultValue="10" /></label>
          <label>Unit price (₹)<input name="unit_price" type="number" min="0" step="0.01" defaultValue="0" /></label>
        </div>
        <label>
          Supplier
          <select name="supplier_id" defaultValue="">
            <option value="">— No supplier —</option>
            {suppliers.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </label>
        <button className="primary full">Create product</button>
      </form>
    </div>
  );
}
