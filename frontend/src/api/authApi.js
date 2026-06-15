import API from './axios'

export const authApi = {
  register: (data) => API.post('/auth/register/', data),
  login: (data) => API.post('/auth/login/', data),
  logout: () => {
    const refresh = localStorage.getItem('refresh_token')
    return API.post('/auth/logout/', { refresh })
  },
  getProfile: () => API.get('/auth/profile/'),
  updateProfile: (data) => API.put('/auth/profile/', data),
  changePassword: (data) => API.put('/auth/change-password/', data),
  forgotPassword: (data) => API.post('/auth/forgot-password/', data),
  refreshToken: (refresh) => API.post('/auth/token/refresh/', { refresh }),
  setPin: (data) => API.post('/auth/set-pin/', data),
  verifyPin: (data) => API.post('/auth/verify-pin/', data),
}
