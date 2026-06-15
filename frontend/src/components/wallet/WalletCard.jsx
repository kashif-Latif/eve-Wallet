import { motion } from 'framer-motion'
import { formatCurrency } from '../../utils/formatCurrency'
import { HiCheck, HiDuplicate } from 'react-icons/hi'
import { useState } from 'react'

export default function WalletCard({ wallet }) {
  const [copied, setCopied] = useState(false)

  const copyWalletNumber = () => {
    navigator.clipboard.writeText(wallet?.wallet_number || '')
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="relative overflow-hidden rounded-2xl p-6 gradient-bg text-white"
    >
      <div className="absolute top-0 right-0 w-40 h-40 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2" />
      <div className="absolute bottom-0 left-0 w-32 h-32 bg-white/10 rounded-full translate-y-1/2 -translate-x-1/2" />
      <div className="relative z-10">
        <p className="text-sm text-white/80 mb-1">Total Balance</p>
        <motion.h2
          key={wallet?.balance}
          initial={{ scale: 1.05 }}
          animate={{ scale: 1 }}
          className="text-3xl sm:text-4xl font-bold mb-4"
        >
          {formatCurrency(wallet?.balance)}
        </motion.h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-white/70">Wallet:</span>
          <span className="font-mono text-sm tracking-wider">{wallet?.wallet_number}</span>
          <button onClick={copyWalletNumber} className="p-1 rounded hover:bg-white/20 transition">
            {copied ? <HiCheck className="w-4 h-4 text-green-300" /> : <HiDuplicate className="w-4 h-4" />}
          </button>
        </div>
        {wallet?.is_frozen && (
          <div className="mt-3 inline-flex items-center px-3 py-1 bg-red-500/30 rounded-full text-sm">
            FROZEN
          </div>
        )}
      </div>
    </motion.div>
  )
}
