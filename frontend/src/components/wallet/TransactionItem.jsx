import { motion } from 'framer-motion'
import { formatCurrency } from '../../utils/formatCurrency'
import { timeAgo } from '../../utils/formatDate'
import { TRANSACTION_TYPES, TRANSACTION_STATUS } from '../../utils/constants'
import { HiArrowUp, HiArrowDown, HiDownload, HiRefresh } from 'react-icons/hi'
import { Link } from 'react-router-dom'

const typeIcons = {
  transfer: HiArrowUp,
  deposit: HiDownload,
  withdrawal: HiArrowDown,
  refund: HiRefresh,
}

export default function TransactionItem({ transaction, index = 0 }) {
  const typeInfo = TRANSACTION_TYPES[transaction.transaction_type] || TRANSACTION_TYPES.transfer
  const statusInfo = TRANSACTION_STATUS[transaction.status] || TRANSACTION_STATUS.pending
  const Icon = typeIcons[transaction.transaction_type] || HiArrowUp
  const isDebit = transaction.transaction_type === 'transfer' || transaction.transaction_type === 'withdrawal'

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
    >
      <Link
        to={`/transactions/${transaction.id}`}
        className="flex items-center gap-4 p-4 rounded-xl hover:bg-gray-50 dark:hover:bg-slate-800/50 transition"
      >
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
          isDebit ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
                   : 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
        }`}>
          <Icon className="w-5 h-5" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
            {typeInfo.label}
            {transaction.description ? ` - ${transaction.description}` : ''}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">{timeAgo(transaction.created_at)}</p>
        </div>
        <div className="text-right">
          <p className={`text-sm font-semibold ${isDebit ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'}`}>
            {isDebit ? '-' : '+'}{formatCurrency(transaction.amount)}
          </p>
          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium ${statusInfo.style}`}>
            {statusInfo.label}
          </span>
        </div>
      </Link>
    </motion.div>
  )
}
