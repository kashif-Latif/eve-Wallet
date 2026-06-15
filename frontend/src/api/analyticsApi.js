import API from './axios'

export const analyticsApi = {
  getDashboard: () => API.get('/analytics/dashboard/'),
  getAdminDashboard: () => API.get('/analytics/admin/dashboard/'),
  getTransactionsChart: (params) => API.get('/analytics/transactions-chart/', { params }),
  getRevenue: (params) => API.get('/analytics/revenue/', { params }),
}
