import API from './axios'

export const walletApi = {
  getMyWallet: () => API.get('/wallets/my-wallet/'),
  getBalance: () => API.get('/wallets/balance/'),
  getTransactions: (params) => API.get('/wallets/transactions/', { params }),
  adminGetAll: (params) => API.get('/wallets/admin/all/', { params }),
  freezeWallet: (id) => API.post(`/wallets/${id}/freeze/`),
  updateLimits: (id, data) => API.post(`/wallets/${id}/update-limits/`, data),
}
