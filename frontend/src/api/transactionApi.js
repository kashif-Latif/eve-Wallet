import API from './axios'

export const transactionApi = {
  sendMoney: (data) => API.post('/transactions/send/', data),
  deposit: (data) => API.post('/transactions/deposit/', data),
  getList: (params) => API.get('/transactions/', { params }),
  getDetail: (id) => API.get(`/transactions/${id}/`),
  cancel: (id) => API.post(`/transactions/${id}/cancel/`),
  adminGetAll: (params) => API.get('/transactions/admin/all/', { params }),
}
