import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { transactionApi } from '../../api/transactionApi'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import Spinner from '../../components/ui/Spinner'
import Modal from '../../components/ui/Modal'
import { formatCurrency } from '../../utils/formatCurrency'
import { formatDateTime } from '../../utils/formatDate'
import { TRANSACTION_TYPES, TRANSACTION_STATUS } from '../../utils/constants'
import { HiArrowLeft, HiArrowUp, HiArrowDown, HiDownload, HiRefresh } from 'react-icons/hi'
import toast from 'react-hot-toast'

const typeIcons = { transfer: HiArrowUp, deposit: HiDownload, withdrawal: HiArrowDown, refund: HiRefresh }

export default function TransactionDetail() {
  const { id } = useParams()
  const [transaction, setTransaction] = useState(null)
  const [loading, setLoading] = useState(true)
  const [cancelOpen, setCancelOpen] = useState(false)
  const [cancelling, setCancelling] = useState(false)

  useEffect(() => {
    transactionApi.getDetail(id).then(res => {
      setTransaction(res.data?.data || res.data)
    }).catch(() => toast.error('Transaction not found'))
    .finally(() => setLoading(false))
  }, [id])

  const handleCancel = async () => {
    setCancelling(true)
    try {
      await transactionApi.cancel(id)
      toast.success('Transaction cancelled')
      setTransaction(prev => ({ ...prev, status: 'cancelled' }))
      setCancelOpen(false)
    } catch (err) {
      toast.error(err.response?.data?.message || 'Cancel failed')
    } finally { setCancelling(false) }
  }

  if (loading) return <Spinner />
  if (!transaction) return <div className="section-padding text-center"><p>Transaction not found</p></div>

  const typeInfo = TRANSACTION_TYPES[transaction.transaction_type] || {}
  const statusInfo = TRANSACTION_STATUS[transaction.status] || TRANSACTION_STATUS.pending
  const Icon = typeIcons[transaction.transaction_type] || HiArrowUp
  const isDebit = transaction.transaction_type === 'transfer' || transaction.transaction_type === 'withdrawal'

  const details = [
    { label: 'Reference Number', value: transaction.reference_number },
    { label: 'Type', value: typeInfo.label || transaction.transaction_type },
    { label: 'Amount', value: formatCurrency(transaction.amount) },
    { label: 'Fee', value: formatCurrency(transaction.fee) },
    { label: 'Status', value: statusInfo.label },
    { label: 'Description', value: transaction.description || 'N/A' },
    { label: 'Date', value: formatDateTime(transaction.created_at) },
  ]

  return (
    <div className="section-padding max-w-2xl mx-auto">
      <Link to="/transactions" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-primary-500 mb-6">
        <HiArrowLeft className="w-4 h-4" /> Back to Transactions
      </Link>

      <Card className="text-center !p-8 mb-6">
        <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 ${
          isDebit ? 'bg-red-100 dark:bg-red-900/30 text-red-600' : 'bg-green-100 dark:bg-green-900/30 text-green-600'
        }`}>
          <Icon className="w-8 h-8" />
        </div>
        <p className={`text-3xl font-bold ${isDebit ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'}`}>
          {isDebit ? '-' : '+'}{formatCurrency(transaction.amount)}
        </p>
        <Badge variant={transaction.status === 'completed' ? 'success' : transaction.status === 'pending' ? 'warning' : 'danger'} className="mt-2">
          {statusInfo.label}
        </Badge>
      </Card>

      <Card>
        <h3 className="font-bold mb-4">Transaction Details</h3>
        <div className="space-y-3">
          {details.map(({ label, value }) => (
            <div key={label} className="flex justify-between py-2 border-b border-gray-100 dark:border-slate-800 last:border-0">
              <span className="text-gray-500 text-sm">{label}</span>
              <span className="font-medium text-sm text-right">{value}</span>
            </div>
          ))}
        </div>
      </Card>

      {transaction.status === 'pending' && (
        <div className="mt-6">
          <Button variant="danger" onClick={() => setCancelOpen(true)} className="w-full">Cancel Transaction</Button>
        </div>
      )}

      <Modal isOpen={cancelOpen} onClose={() => setCancelOpen(false)} title="Cancel Transaction">
        <p className="text-gray-500 mb-4">Are you sure you want to cancel this transaction? This action cannot be undone.</p>
        <div className="flex gap-3">
          <Button variant="secondary" onClick={() => setCancelOpen(false)} className="flex-1">No, Keep It</Button>
          <Button variant="danger" onClick={handleCancel} loading={cancelling} className="flex-1">Yes, Cancel</Button>
        </div>
      </Modal>
    </div>
  )
}
