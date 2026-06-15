import API from './axios'

export const refundApi = {
  requestRefund: (data) => API.post('/refunds/request/', data),
  getMyRefunds: (params) => API.get('/refunds/my-refunds/', { params }),
  getAll: (params) => API.get('/refunds/', { params }),
  process: (id, data) => API.post(`/refunds/${id}/process/`, data),
  complete: (id) => API.post(`/refunds/${id}/complete/`),
}
