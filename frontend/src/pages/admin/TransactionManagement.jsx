import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { transactionApi } from '../../api/transactionApi'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Spinner from '../../components/ui/Spinner'
import { formatCurrency } from '../../utils/formatCurrency'
import { formatDateTime } from '../../utils/formatDate'
import { TRANSACTION_STATUS } from '../../utils/constants'

export default function TransactionManagement() {
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    transactionApi.adminGetAll().then(res => {
      setTransactions(res.data?.data?.results || res.data?.results || res.data?.data || [])
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  if (loading) return <Spinner />

  return (
    <div className="section-padding">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold mb-6">Transaction Management</h1>
      </motion.div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 dark:border-slate-700">
                <th className="text-left py-3 px-4 font-medium text-gray-500">Ref #</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Type</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Amount</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Fee</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Status</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Date</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map(tx => {
                const statusInfo = TRANSACTION_STATUS[tx.status] || TRANSACTION_STATUS.pending
                return (
                  <tr key={tx.id} className="border-b border-gray-100 dark:border-slate-800 hover:bg-gray-50 dark:hover:bg-slate-800/50">
                    <td className="py-3 px-4 font-mono text-xs">{tx.reference_number}</td>
                    <td className="py-3 px-4 capitalize">{tx.transaction_type}</td>
                    <td className="py-3 px-4 font-medium">{formatCurrency(tx.amount)}</td>
                    <td className="py-3 px-4 text-gray-500">{formatCurrency(tx.fee)}</td>
                    <td className="py-3 px-4"><Badge variant={tx.status === 'completed' ? 'success' : tx.status === 'pending' ? 'warning' : 'danger'}>{statusInfo.label}</Badge></td>
                    <td className="py-3 px-4 text-gray-500 text-xs">{formatDateTime(tx.created_at)}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
          {transactions.length === 0 && <p className="text-center py-8 text-gray-400">No transactions found</p>}
        </div>
      </Card>
    </div>
  )
}
