import API from './axios'

export const notificationApi = {
  getAll: (params) => API.get('/notifications/', { params }),
  markRead: (id) => API.put(`/notifications/${id}/read/`),
  markAllRead: () => API.put('/notifications/read-all/'),
  getUnreadCount: () => API.get('/notifications/unread-count/'),
}
