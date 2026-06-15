import Navbar from './Navbar'
import Sidebar from './Sidebar'
import MobileNav from './MobileNav'
import { useAuth } from '../../context/AuthContext'
import { Navigate } from 'react-router-dom'

export default function Layout({ children, requireAuth = false, requireAdmin = false }) {
  const { isAuthenticated, isAdmin, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-slate-950">
        <div className="animate-spin h-12 w-12 border-4 border-primary-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  if (requireAuth && !isAuthenticated) return <Navigate to="/login" replace />
  if (requireAdmin && !isAdmin) return <Navigate to="/dashboard" replace />

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-950">
      <Navbar />
      <div className="flex">
        {isAuthenticated && <Sidebar />}
        <main className="flex-1 min-h-[calc(100vh-4rem)] pb-20 md:pb-0">
          {children}
        </main>
      </div>
      {isAuthenticated && <MobileNav />}
    </div>
  )
}
