import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { notificationApi } from '../../api/notificationApi'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import Spinner from '../../components/ui/Spinner'
import { timeAgo, formatDateTime } from '../../utils/formatDate'
import { HiBell, HiCheck, HiCheckCircle } from 'react-icons/hi'
import toast from 'react-hot-toast'

export default function Notifications() {
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    notificationApi.getAll().then(res => {
      setNotifications(res.data?.data?.results || res.data?.results || res.data?.data || [])
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const markRead = async (id) => {
    try {
      await notificationApi.markRead(id)
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n))
    } catch {}
  }

  const markAllRead = async () => {
    try {
      await notificationApi.markAllRead()
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })))
      toast.success('All marked as read')
    } catch { toast.error('Failed') }
  }

  if (loading) return <Spinner />

  return (
    <div className="section-padding">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Notifications</h1>
            <p className="text-gray-500 dark:text-gray-400">Stay updated on your wallet activity</p>
          </div>
          <Button variant="secondary" onClick={markAllRead}>
            <HiCheckCircle className="w-4 h-4" /> Mark All Read
          </Button>
        </div>
      </motion.div>

      {notifications.length > 0 ? (
        <div className="space-y-2">
          {notifications.map((n, i) => (
            <motion.div key={n.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03 }}>
              <div className={`flex items-start gap-4 p-4 rounded-xl transition cursor-pointer ${
                n.is_read ? 'bg-white dark:bg-slate-900' : 'bg-primary-50 dark:bg-primary-900/10'
              } hover:shadow-md`} onClick={() => !n.is_read && markRead(n.id)}>
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                  n.is_read ? 'bg-gray-100 dark:bg-slate-800 text-gray-400' : 'bg-primary-100 dark:bg-primary-900/30 text-primary-600'
                }`}>
                  <HiBell className="w-5 h-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className={`font-medium ${n.is_read ? 'text-gray-600 dark:text-gray-400' : ''}`}>{n.title}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">{n.message}</p>
                  <p className="text-xs text-gray-400 mt-1">{timeAgo(n.created_at)}</p>
                </div>
                {!n.is_read && <div className="w-2 h-2 rounded-full bg-primary-500 flex-shrink-0 mt-2" />}
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <Card className="text-center py-12">
          <HiBell className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-400">No notifications yet</p>
        </Card>
      )}
    </div>
  )
}
