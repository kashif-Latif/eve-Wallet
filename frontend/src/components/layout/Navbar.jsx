import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { useTheme } from '../../context/ThemeContext'
import ThemeToggle from '../ui/Toggle'
import { HiMenuAlt3, HiX, HiBell, HiLogout, HiUser, HiShieldCheck } from 'react-icons/hi'
import { notificationApi } from '../../api/notificationApi'
import { useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export default function Navbar() {
  const { user, isAdmin, logout } = useAuth()
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [unread, setUnread] = useState(0)

  useEffect(() => {
    if (user) {
      notificationApi.getUnreadCount().then(res => {
        setUnread(res.data?.data?.count || res.data?.count || 0)
      }).catch(() => {})
    }
  }, [user])

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <nav className="sticky top-0 z-40 glass border-b border-gray-200/20 dark:border-slate-700/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          <Link to={user ? '/dashboard' : '/'} className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg gradient-bg flex items-center justify-center">
              <span className="text-white font-bold text-sm">W</span>
            </div>
            <span className="text-lg font-bold gradient-text">DigiWallet</span>
          </Link>

          {user ? (
            <div className="flex items-center gap-3">
              <ThemeToggle />
              <Link to="/notifications" className="relative p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-slate-800 transition">
                <HiBell className="w-5 h-5" />
                {unread > 0 && (
                  <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-red-500 text-white text-[10px] rounded-full flex items-center justify-center">
                    {unread > 9 ? '9+' : unread}
                  </span>
                )}
              </Link>
              {isAdmin && (
                <Link to="/admin" className="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-slate-800 transition text-primary-500">
                  <HiShieldCheck className="w-5 h-5" />
                </Link>
              )}
              <Link to="/profile" className="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-slate-800 transition">
                <HiUser className="w-5 h-5" />
              </Link>
              <button onClick={handleLogout} className="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-slate-800 transition text-red-500">
                <HiLogout className="w-5 h-5" />
              </button>
              <button className="md:hidden p-2" onClick={() => setMobileOpen(!mobileOpen)}>
                {mobileOpen ? <HiX className="w-5 h-5" /> : <HiMenuAlt3 className="w-5 h-5" />}
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <ThemeToggle />
              <Link to="/login" className="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary-500 transition">
                Login
              </Link>
              <Link to="/register" className="btn-primary text-sm !py-2 !px-4">Get Started</Link>
            </div>
          )}
        </div>
      </div>

      <AnimatePresence>
        {mobileOpen && user && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden border-t border-gray-200 dark:border-slate-700"
          >
            <div className="px-4 py-3 space-y-1">
              {[
                { to: '/dashboard', label: 'Dashboard' },
                { to: '/wallet', label: 'Wallet' },
                { to: '/send', label: 'Send Money' },
                { to: '/receive', label: 'Receive Money' },
                { to: '/transactions', label: 'Transactions' },
                { to: '/settings', label: 'Settings' },
              ].map(item => (
                <Link key={item.to} to={item.to} onClick={() => setMobileOpen(false)}
                  className="block px-3 py-2 rounded-lg text-sm hover:bg-gray-100 dark:hover:bg-slate-800 transition">
                  {item.label}
                </Link>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  )
}
