// Thin wrapper around the StockPilot REST API. The browser only ever talks to the
// same origin (/api/...); Nginx or the Kubernetes Ingress forwards it to FastAPI.
const API = '/api';

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (response.status === 204) return null;
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = Array.isArray(body.detail)
      ? body.detail.map((d) => `${d.loc?.slice(-1)[0]}: ${d.msg}`).join(', ')
      : body.detail || `Request failed (${response.status})`;
    throw new Error(detail);
  }
  return body;
}

export const api = {
  stats: () => request('/products/stats'),
  products: (params = {}) => {
    const query = new URLSearchParams(Object.entries(params).filter(([, v]) => v)).toString();
    return request(`/products${query ? `?${query}` : ''}`);
  },
  lowStock: () => request('/products/low-stock'),
  createProduct: (payload) => request('/products', { method: 'POST', body: JSON.stringify(payload) }),
  updateProduct: (id, payload) => request(`/products/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteProduct: (id) => request(`/products/${id}`, { method: 'DELETE' }),
  suppliers: () => request('/suppliers'),
  createSupplier: (payload) => request('/suppliers', { method: 'POST', body: JSON.stringify(payload) }),
  deleteSupplier: (id) => request(`/suppliers/${id}`, { method: 'DELETE' }),
  movements: (limit = 12) => request(`/movements?limit=${limit}`),
  createMovement: (payload) => request('/movements', { method: 'POST', body: JSON.stringify(payload) }),
};

export const currency = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
});

export function timeAgo(iso) {
  const diff = Math.max(0, Date.now() - new Date(iso).getTime());
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hr${hours > 1 ? 's' : ''} ago`;
  const days = Math.floor(hours / 24);
  return `${days} day${days > 1 ? 's' : ''} ago`;
}
