export const ROLES = { USER: 'user', ADMIN: 'admin', SUPERADMIN: 'superadmin' }

export const TRANSACTION_TYPES = {
  transfer: { label: 'Transfer', color: 'blue', icon: 'send' },
  deposit: { label: 'Deposit', color: 'green', icon: 'download' },
  withdrawal: { label: 'Withdrawal', color: 'orange', icon: 'upload' },
  refund: { label: 'Refund', color: 'purple', icon: 'rotate' },
}

export const TRANSACTION_STATUS = {
  pending: { label: 'Pending', style: 'status-pending' },
  completed: { label: 'Completed', style: 'status-completed' },
  failed: { label: 'Failed', style: 'status-failed' },
  cancelled: { label: 'Cancelled', style: 'status-cancelled' },
}

export const REFUND_STATUS = {
  pending: { label: 'Pending', style: 'status-pending' },
  approved: { label: 'Approved', style: 'status-completed' },
  rejected: { label: 'Rejected', style: 'status-failed' },
  completed: { label: 'Completed', style: 'status-completed' },
}

export const NAV_ITEMS = [
  { path: '/dashboard', label: 'Dashboard', icon: 'dashboard' },
  { path: '/wallet', label: 'Wallet', icon: 'wallet' },
  { path: '/send', label: 'Send', icon: 'send' },
  { path: '/receive', label: 'Receive', icon: 'receive' },
  { path: '/transactions', label: 'Transactions', icon: 'transactions' },
  { path: '/refunds', label: 'Refunds', icon: 'refund' },
  { path: '/notifications', label: 'Notifications', icon: 'bell' },
  { path: '/profile', label: 'Profile', icon: 'user' },
  { path: '/settings', label: 'Settings', icon: 'settings' },
]

export const ADMIN_NAV_ITEMS = [
  { path: '/admin', label: 'Admin Dashboard', icon: 'admin' },
  { path: '/admin/users', label: 'Users', icon: 'users' },
  { path: '/admin/wallets', label: 'Wallets', icon: 'wallet' },
  { path: '/admin/transactions', label: 'Transactions', icon: 'transactions' },
  { path: '/admin/refunds', label: 'Refunds', icon: 'refund' },
  { path: '/admin/audit-logs', label: 'Audit Logs', icon: 'log' },
]

export const FEE_CONFIG = { rate: 0.015, min: 0.5, max: 25 }

export const calculateFee = (amount) => {
  const fee = amount * FEE_CONFIG.rate
  return Math.min(Math.max(fee, FEE_CONFIG.min), FEE_CONFIG.max)
}
