import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { HiHome, HiCreditCard, HiPaperAirplane, HiDownload, HiSwitchHorizontal, HiRefresh, HiBell, HiUser, HiCog, HiShieldCheck, HiUsers, HiClipboardList, HiChartBar } from 'react-icons/hi'

const userLinks = [
  { to: '/dashboard', icon: HiHome, label: 'Dashboard' },
  { to: '/wallet', icon: HiCreditCard, label: 'Wallet' },
  { to: '/send', icon: HiPaperAirplane, label: 'Send' },
  { to: '/receive', icon: HiDownload, label: 'Receive' },
  { to: '/transactions', icon: HiSwitchHorizontal, label: 'Transactions' },
  { to: '/refunds', icon: HiRefresh, label: 'Refunds' },
  { to: '/notifications', icon: HiBell, label: 'Alerts' },
  { to: '/profile', icon: HiUser, label: 'Profile' },
  { to: '/settings', icon: HiCog, label: 'Settings' },
]

const adminLinks = [
  { to: '/admin', icon: HiChartBar, label: 'Dashboard' },
  { to: '/admin/users', icon: HiUsers, label: 'Users' },
  { to: '/admin/wallets', icon: HiCreditCard, label: 'Wallets' },
  { to: '/admin/transactions', icon: HiSwitchHorizontal, label: 'Transactions' },
  { to: '/admin/refunds', icon: HiRefresh, label: 'Refunds' },
  { to: '/admin/audit-logs', icon: HiClipboardList, label: 'Audit Logs' },
]

export default function Sidebar() {
  const { isAdmin } = useAuth()
  const location = useLocation()
  const links = isAdmin ? adminLinks : userLinks

  return (
    <aside className="hidden md:flex flex-col w-64 border-r border-gray-200 dark:border-slate-700 bg-white/50 dark:bg-slate-900/50 backdrop-blur-lg h-[calc(100vh-4rem)] sticky top-16">
      <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
        {links.map(({ to, icon: Icon, label }) => (
          <Link
            key={to}
            to={to}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
              location.pathname === to
                ? 'bg-primary-500/10 text-primary-600 dark:text-primary-400'
                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-slate-800'
            }`}
          >
            <Icon className="w-5 h-5" />
            {label}
          </Link>
        ))}
      </nav>
    </aside>
  )
}
