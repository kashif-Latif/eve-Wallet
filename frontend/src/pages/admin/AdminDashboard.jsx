import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { analyticsApi } from '../../api/analyticsApi'
import Card from '../../components/ui/Card'
import Spinner from '../../components/ui/Spinner'
import TransactionChart from '../../components/charts/TransactionChart'
import RevenueChart from '../../components/charts/RevenueChart'
import { formatCompactCurrency, formatCurrency } from '../../utils/formatCurrency'
import { HiUsers, HiCreditCard, HiSwitchHorizontal, HiCurrencyDollar } from 'react-icons/hi'

export default function AdminDashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    analyticsApi.getAdminDashboard().then(res => {
      setStats(res.data?.data || res.data)
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  if (loading) return <Spinner />

  const statCards = [
    { label: 'Total Users', value: stats?.total_users || 0, icon: HiUsers, color: 'from-blue-500 to-blue-600', format: false },
    { label: 'Total Wallets', value: stats?.total_wallets || 0, icon: HiCreditCard, color: 'from-green-500 to-green-600', format: false },
    { label: 'Total Transactions', value: stats?.total_transactions || 0, icon: HiSwitchHorizontal, color: 'from-purple-500 to-purple-600', format: false },
    { label: 'Total Revenue', value: stats?.total_revenue || 0, icon: HiCurrencyDollar, color: 'from-orange-500 to-orange-600', format: true },
  ]

  return (
    <div className="section-padding">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold mb-2">Admin Dashboard</h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">System overview and analytics</p>
      </motion.div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {statCards.map((card, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
            <Card>
              <div className="flex items-center gap-4">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${card.color} flex items-center justify-center`}>
                  <card.icon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <p className="text-sm text-gray-500">{card.label}</p>
                  <p className="text-2xl font-bold">{card.format ? formatCompactCurrency(card.value) : card.value}</p>
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <Card>
          <h3 className="font-bold mb-4">Transaction Trends</h3>
          <TransactionChart data={stats?.chart_data} />
        </Card>
        <Card>
          <h3 className="font-bold mb-4">Revenue</h3>
          <RevenueChart data={stats?.revenue_data} />
        </Card>
      </div>
    </div>
  )
}
