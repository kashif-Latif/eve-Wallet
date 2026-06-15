import { Routes, Route, Navigate } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import Layout from './components/layout/Layout'
import Toast from './components/ui/Toast'

// Public
import Home from './pages/public/Home'
import Login from './pages/public/Login'
import Register from './pages/public/Register'

// Auth
import Dashboard from './pages/auth/Dashboard'
import Wallet from './pages/auth/Wallet'
import SendMoney from './pages/auth/SendMoney'
import ReceiveMoney from './pages/auth/ReceiveMoney'
import Transactions from './pages/auth/Transactions'
import TransactionDetail from './pages/auth/TransactionDetail'
import RefundRequests from './pages/auth/RefundRequests'
import Notifications from './pages/auth/Notifications'
import Profile from './pages/auth/Profile'
import Settings from './pages/auth/Settings'

// Admin
import AdminDashboard from './pages/admin/AdminDashboard'
import UserManagement from './pages/admin/UserManagement'
import WalletManagement from './pages/admin/WalletManagement'
import TransactionManagement from './pages/admin/TransactionManagement'
import RefundManagement from './pages/admin/RefundManagement'
import AuditLogs from './pages/admin/AuditLogs'

function App() {
  return (
    <>
      <Toast />
      <AnimatePresence mode="wait">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Layout><Home /></Layout>} />
          <Route path="/login" element={<Layout><Login /></Layout>} />
          <Route path="/register" element={<Layout><Register /></Layout>} />

          {/* Authenticated Routes */}
          <Route path="/dashboard" element={<Layout requireAuth><Dashboard /></Layout>} />
          <Route path="/wallet" element={<Layout requireAuth><Wallet /></Layout>} />
          <Route path="/send" element={<Layout requireAuth><SendMoney /></Layout>} />
          <Route path="/receive" element={<Layout requireAuth><ReceiveMoney /></Layout>} />
          <Route path="/transactions" element={<Layout requireAuth><Transactions /></Layout>} />
          <Route path="/transactions/:id" element={<Layout requireAuth><TransactionDetail /></Layout>} />
          <Route path="/refunds" element={<Layout requireAuth><RefundRequests /></Layout>} />
          <Route path="/notifications" element={<Layout requireAuth><Notifications /></Layout>} />
          <Route path="/profile" element={<Layout requireAuth><Profile /></Layout>} />
          <Route path="/settings" element={<Layout requireAuth><Settings /></Layout>} />

          {/* Admin Routes */}
          <Route path="/admin" element={<Layout requireAuth requireAdmin><AdminDashboard /></Layout>} />
          <Route path="/admin/users" element={<Layout requireAuth requireAdmin><UserManagement /></Layout>} />
          <Route path="/admin/wallets" element={<Layout requireAuth requireAdmin><WalletManagement /></Layout>} />
          <Route path="/admin/transactions" element={<Layout requireAuth requireAdmin><TransactionManagement /></Layout>} />
          <Route path="/admin/refunds" element={<Layout requireAuth requireAdmin><RefundManagement /></Layout>} />
          <Route path="/admin/audit-logs" element={<Layout requireAuth requireAdmin><AuditLogs /></Layout>} />

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AnimatePresence>
    </>
  )
}

export default App
