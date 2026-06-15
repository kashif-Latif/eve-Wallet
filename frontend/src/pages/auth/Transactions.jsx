import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { transactionApi } from '../../api/transactionApi'
import Card from '../../components/ui/Card'
import Spinner from '../../components/ui/Spinner'
import Badge from '../../components/ui/Badge'
import { formatCurrency } from '../../utils/formatCurrency'
import { formatDateTime } from '../../utils/formatDate'
import { TRANSACTION_TYPES, TRANSACTION_STATUS } from '../../utils/constants'
import { HiSearch, HiFilter, HiArrowUp, HiArrowDown, HiDownload, HiRefresh } from 'react-icons/hi'

const typeIcons = { transfer: HiArrowUp, deposit: HiDownload, withdrawal: HiArrowDown, refund: HiRefresh }

export default function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({ transaction_type: '', status: '', search: '' })

  useEffect(() => {
    const fetch = async () => {
      try {
        const params = {}
        if (filters.transaction_type) params.transaction_type = filters.transaction_type
        if (filters.status) params.status = filters.status
        if (filters.search) params.search = filters.search
        const { data } = await transactionApi.getList(params)
        setTransactions(data?.data?.results || data?.results || data?.data || [])
      } catch (e) { console.error(e) }
      finally { setLoading(false) }
    }
    fetch()
  }, [filters])

  if (loading) return <Spinner />

  return (
    <div className="section-padding">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold mb-2">Transactions</h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">View and manage your transaction history</p>
      </motion.div>

      {/* Filters */}
      <Card className="mb-6 !p-4">
        <div className="flex flex-wrap gap-3 items-center">
          <div className="flex-1 min-w-[200px] relative">
            <HiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input type="text" placeholder="Search transactions..."
              value={filters.search} onChange={e => setFilters({ ...filters, search: e.target.value })}
              className="input-field !pl-9 !py-2 text-sm" />
          </div>
          <select value={filters.transaction_type} onChange={e => setFilters({ ...filters, transaction_type: e.target.value })}
            className="input-field !w-auto !py-2 text-sm">
            <option value="">All Types</option>
            <option value="transfer">Transfer</option>
            <option value="deposit">Deposit</option>
            <option value="withdrawal">Withdrawal</option>
            <option value="refund">Refund</option>
          </select>
          <select value={filters.status} onChange={e => setFilters({ ...filters, status: e.target.value })}
            className="input-field !w-auto !py-2 text-sm">
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </Card>

      {/* Transaction List */}
      {transactions.length > 0 ? (
        <div className="space-y-3">
          {transactions.map((tx, i) => {
            const Icon = typeIcons[tx.transaction_type] || HiArrowUp
            const statusInfo = TRANSACTION_STATUS[tx.status] || TRANSACTION_STATUS.pending
            const isDebit = tx.transaction_type === 'transfer' || tx.transaction_type === 'withdrawal'
            return (
              <motion.div key={tx.id} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.03 }}>
                <Link to={`/transactions/${tx.id}`} className="block">
                  <Card className="!p-4 hover:shadow-lg transition-shadow">
                    <div className="flex items-center gap-4">
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                        isDebit ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
                                 : 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
                      }`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{(TRANSACTION_TYPES[tx.transaction_type]?.label || tx.transaction_type)} {tx.description ? `- ${tx.description}` : ''}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">{formatDateTime(tx.created_at)}</p>
                      </div>
                      <div className="text-right">
                        <p className={`font-bold ${isDebit ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'}`}>
                          {isDebit ? '-' : '+'}{formatCurrency(tx.amount)}
                        </p>
                        <Badge variant={tx.status === 'completed' ? 'success' : tx.status === 'pending' ? 'warning' : 'danger'}>
                          {statusInfo.label}
                        </Badge>
                      </div>
                    </div>
                  </Card>
                </Link>
              </motion.div>
            )
          })}
        </div>
      ) : (
        <Card className="text-center py-12">
          <p className="text-gray-400 text-lg mb-2">No transactions found</p>
          <Link to="/send" className="text-primary-500 hover:underline text-sm">Make your first transfer</Link>
        </Card>
      )}
    </div>
  )
}
