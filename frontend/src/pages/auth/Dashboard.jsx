import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuth } from '../../context/AuthContext'
import { walletApi } from '../../api/walletApi'
import { transactionApi } from '../../api/transactionApi'
import { analyticsApi } from '../../api/analyticsApi'
import Card from '../../components/ui/Card'
import Spinner from '../../components/ui/Spinner'
import WalletCard from '../../components/wallet/WalletCard'
import TransactionItem from '../../components/wallet/TransactionItem'
import TransactionChart from '../../components/charts/TransactionChart'
import { HiPaperAirplane, HiDownload, HiCurrencyDollar, HiTrendingUp, HiArrowRight } from 'react-icons/hi'
import { formatCurrency } from '../../utils/formatCurrency'

export default function Dashboard() {
  const { user } = useAuth()
  const [wallet, setWallet] = useState(null)
  const [transactions, setTransactions] = useState([])
  const [chartData, setChartData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetch = async () => {
      try {
        const [walletRes, txRes, chartRes] = await Promise.allSettled([
          walletApi.getMyWallet(),
          transactionApi.getList({ page_size: 5 }),
          analyticsApi.getTransactionsChart(),
        ])
        if (walletRes.status === 'fulfilled') setWallet(walletRes.value.data?.data || walletRes.value.data)
        if (txRes.status === 'fulfilled') {
          const d = txRes.value.data
          setTransactions(d?.data?.results || d?.results || d?.data || [])
        }
        if (chartRes.status === 'fulfilled') setChartData(chartRes.value.data?.data || chartRes.value.data)
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [])

  if (loading) return <Spinner />

  const quickActions = [
    { to: '/send', icon: HiPaperAirplane, label: 'Send', color: 'from-blue-500 to-blue-600' },
    { to: '/receive', icon: HiDownload, label: 'Receive', color: 'from-green-500 to-green-600' },
    { to: '/wallet', icon: HiCurrencyDollar, label: 'Deposit', color: 'from-purple-500 to-purple-600' },
    { to: '/transactions', icon: HiTrendingUp, label: 'History', color: 'from-orange-500 to-orange-600' },
  ]

  return (
    <div className="section-padding">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold mb-1">Welcome, {user?.first_name || user?.username}!</h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">Here's your wallet overview</p>
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <WalletCard wallet={wallet} />

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {quickActions.map((action, i) => (
              <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 + i * 0.05 }}>
                <Link to={action.to} className="flex flex-col items-center gap-2 p-4 glass-card !p-4 hover:scale-[1.02] transition-transform">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${action.color} flex items-center justify-center`}>
                    <action.icon className="w-6 h-6 text-white" />
                  </div>
                  <span className="text-sm font-medium">{action.label}</span>
                </Link>
              </motion.div>
            ))}
          </div>

          <Card>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold">Transaction Activity</h3>
            </div>
            <TransactionChart data={chartData} />
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold">Recent Transactions</h3>
              <Link to="/transactions" className="text-sm text-primary-500 hover:underline flex items-center gap-1">
                View All <HiArrowRight className="w-3 h-3" />
              </Link>
            </div>
            {transactions.length > 0 ? (
              <div className="space-y-1 -mx-4">
                {transactions.slice(0, 5).map((tx, i) => (
                  <TransactionItem key={tx.id} transaction={tx} index={i} />
                ))}
              </div>
            ) : (
              <p className="text-gray-400 text-sm text-center py-8">No transactions yet</p>
            )}
          </Card>

          <Card>
            <h3 className="font-bold mb-3">Quick Info</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Wallet Status</span>
                <span className={`font-medium ${wallet?.is_active ? 'text-green-500' : 'text-red-500'}`}>
                  {wallet?.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Daily Limit</span>
                <span className="font-medium">{formatCurrency(wallet?.daily_limit)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Monthly Limit</span>
                <span className="font-medium">{formatCurrency(wallet?.monthly_limit)}</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
