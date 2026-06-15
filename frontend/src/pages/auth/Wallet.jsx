import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { walletApi } from '../../api/walletApi'
import { transactionApi } from '../../api/transactionApi'
import Card from '../../components/ui/Card'
import Spinner from '../../components/ui/Spinner'
import WalletCard from '../../components/wallet/WalletCard'
import TransactionItem from '../../components/wallet/TransactionItem'
import Button from '../../components/ui/Button'
import Modal from '../../components/ui/Modal'
import Input from '../../components/ui/Input'
import toast from 'react-hot-toast'
import { formatCurrency } from '../../utils/formatCurrency'

export default function Wallet() {
  const [wallet, setWallet] = useState(null)
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [depositOpen, setDepositOpen] = useState(false)
  const [depositAmount, setDepositAmount] = useState('')
  const [depositing, setDepositing] = useState(false)

  const fetchWallet = async () => {
    try {
      const [walletRes, txRes] = await Promise.allSettled([
        walletApi.getMyWallet(),
        walletApi.getTransactions(),
      ])
      if (walletRes.status === 'fulfilled') setWallet(walletRes.value.data?.data || walletRes.value.data)
      if (txRes.status === 'fulfilled') {
        const d = txRes.value.data
        setTransactions(d?.data?.results || d?.results || d?.data || [])
      }
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchWallet() }, [])

  const handleDeposit = async () => {
    if (!depositAmount || parseFloat(depositAmount) <= 0) {
      toast.error('Enter a valid amount')
      return
    }
    setDepositing(true)
    try {
      await transactionApi.deposit({ amount: depositAmount })
      toast.success(`Deposited ${formatCurrency(depositAmount)}!`)
      setDepositOpen(false)
      setDepositAmount('')
      fetchWallet()
    } catch (err) {
      toast.error(err.response?.data?.message || 'Deposit failed')
    } finally { setDepositing(false) }
  }

  if (loading) return <Spinner />

  const dailyUsed = wallet ? (wallet.daily_limit - (wallet.daily_remaining || wallet.daily_limit)) : 0
  const monthlyUsed = wallet ? (wallet.monthly_limit - (wallet.monthly_remaining || wallet.monthly_limit)) : 0

  return (
    <div className="section-padding">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold mb-6">My Wallet</h1>
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <WalletCard wallet={wallet} />
          <div className="flex gap-3">
            <Button onClick={() => setDepositOpen(true)}>
              Deposit Money
            </Button>
          </div>
          <Card>
            <h3 className="font-bold mb-4">Transaction History</h3>
            {transactions.length > 0 ? (
              <div className="space-y-1 -mx-4">
                {transactions.slice(0, 10).map((tx, i) => (
                  <TransactionItem key={tx.id} transaction={tx} index={i} />
                ))}
              </div>
            ) : (
              <p className="text-gray-400 text-center py-8">No transactions yet</p>
            )}
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <h3 className="font-bold mb-4">Limits</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-500">Daily</span>
                  <span>{formatCurrency(dailyUsed)} / {formatCurrency(wallet?.daily_limit)}</span>
                </div>
                <div className="h-2 bg-gray-200 dark:bg-slate-700 rounded-full overflow-hidden">
                  <div className="h-full bg-primary-500 rounded-full transition-all"
                    style={{ width: `${Math.min((dailyUsed / (wallet?.daily_limit || 1)) * 100, 100)}%` }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-500">Monthly</span>
                  <span>{formatCurrency(monthlyUsed)} / {formatCurrency(wallet?.monthly_limit)}</span>
                </div>
                <div className="h-2 bg-gray-200 dark:bg-slate-700 rounded-full overflow-hidden">
                  <div className="h-full bg-secondary-500 rounded-full transition-all"
                    style={{ width: `${Math.min((monthlyUsed / (wallet?.monthly_limit || 1)) * 100, 100)}%` }} />
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>

      <Modal isOpen={depositOpen} onClose={() => setDepositOpen(false)} title="Deposit Money">
        <div className="space-y-4">
          <Input label="Amount" type="number" value={depositAmount} onChange={e => setDepositAmount(e.target.value)}
            placeholder="Enter amount" min="0.01" step="0.01" />
          {depositAmount && (
            <p className="text-sm text-gray-500">You will receive: {formatCurrency(depositAmount)}</p>
          )}
          <Button onClick={handleDeposit} loading={depositing} className="w-full">Confirm Deposit</Button>
        </div>
      </Modal>
    </div>
  )
}
