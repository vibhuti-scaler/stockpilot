export default function StockModal({ product, type, onClose, onSubmit }) {
  const receiving = type === 'IN';
  const submit = (e) => {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    onSubmit({
      product_id: product.id,
      movement_type: type,
      quantity: Number(f.get('quantity')),
      note: f.get('note').trim(),
    });
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <form className="modal" onSubmit={submit} onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <div>
            <p className="eyebrow">{receiving ? 'RECEIVE STOCK (IN)' : 'ISSUE STOCK (OUT)'}</p>
            <h2>{product.name}</h2>
            <p className="muted">{product.sku} · currently {product.quantity} in stock</p>
          </div>
          <button type="button" className="close" onClick={onClose} aria-label="Close">×</button>
        </div>
        <label>
          Quantity
          <input name="quantity" type="number" min="1" max={receiving ? 1000000 : product.quantity} defaultValue="1" required autoFocus />
        </label>
        <label>
          Note
          <input name="note" placeholder={receiving ? 'Purchase order number' : 'Issued to…'} />
        </label>
        <button className={`primary full ${receiving ? '' : 'warn'}`}>
          {receiving ? 'Record receipt' : 'Record issue'}
        </button>
      </form>
    </div>
  );
}
