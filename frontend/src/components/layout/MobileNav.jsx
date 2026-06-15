import { Link, useLocation } from 'react-router-dom'
import { HiHome, HiCreditCard, HiPaperAirplane, HiDownload, HiSwitchHorizontal } from 'react-icons/hi'

const navItems = [
  { to: '/dashboard', icon: HiHome, label: 'Home' },
  { to: '/wallet', icon: HiCreditCard, label: 'Wallet' },
  { to: '/send', icon: HiPaperAirplane, label: 'Send' },
  { to: '/receive', icon: HiDownload, label: 'Receive' },
  { to: '/transactions', icon: HiSwitchHorizontal, label: 'History' },
]

export default function MobileNav() {
  const location = useLocation()

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 glass border-t border-gray-200/20 dark:border-slate-700/20">
      <div className="flex items-center justify-around py-2">
        {navItems.map(({ to, icon: Icon, label }) => (
          <Link
            key={to}
            to={to}
            className={`flex flex-col items-center gap-0.5 px-3 py-1 rounded-xl transition ${
              location.pathname === to
                ? 'text-primary-500'
                : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'
            }`}
          >
            <Icon className="w-5 h-5" />
            <span className="text-[10px] font-medium">{label}</span>
          </Link>
        ))}
      </div>
    </nav>
  )
}
