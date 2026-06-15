import { motion } from 'framer-motion'
import { formatCurrency } from '../../utils/formatCurrency'

export default function BalanceDisplay({ amount, label = 'Balance', size = 'lg' }) {
  const sizes = {
    sm: 'text-xl',
    md: 'text-2xl',
    lg: 'text-4xl',
  }

  return (
    <div>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">{label}</p>
      <motion.p
        key={amount}
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`${sizes[size]} font-bold text-gray-900 dark:text-white`}
      >
        {formatCurrency(amount)}
      </motion.p>
    </div>
  )
}
