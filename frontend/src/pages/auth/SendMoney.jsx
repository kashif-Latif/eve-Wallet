import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { transactionApi } from '../../api/transactionApi'
import { useAuth } from '../../context/AuthContext'
import Card from '../../components/ui/Card'
import Input from '../../components/ui/Input'
import Button from '../../components/ui/Button'
import Modal from '../../components/ui/Modal'
import PinInput from '../../components/ui/PinInput'
import { formatCurrency } from '../../utils/formatCurrency'
import { calculateFee, FEE_CONFIG } from '../../utils/constants'
import toast from 'react-hot-toast'

export default function SendMoney() {
  const { user } = useAuth()
  const [form, setForm] = useState({ receiver_wallet_number: '', amount: '', description: '' })
  const [loading, setLoading] = useState(false)
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [pinOpen, setPinOpen] = useState(false)
  const [pinToken, setPinToken] = useState('')
  const [errors, setErrors] = useState({})

  const amount = parseFloat(form.amount) || 0
  const fee = calculateFee(amount)
  const total = amount + fee

  const validate = () => {
    const errs = {}
    if (!form.receiver_wallet_number.trim()) errs.receiver_wallet_number = 'Wallet number is required'
    else if (form.receiver_wallet_number.trim().length < 10) errs.receiver_wallet_number = 'Invalid wallet number'
    if (!form.amount || amount <= 0) errs.amount = 'Enter a valid amount'
    if (amount < 1) errs.amount = 'Minimum amount is $1'
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleProceed = () => {
    if (!validate()) return
    // If user has PIN set, show PIN input first
    if (user?.pin_set) {
      setPinOpen(true)
    } else {
      setConfirmOpen(true)
    }
  }

  const handlePinVerified = (token) => {
    setPinToken(token)
    setPinOpen(false)
    setConfirmOpen(true)
  }

  const handleSend = async () => {
    setLoading(true)
    try {
      const payload = {
        receiver_wallet_number: form.receiver_wallet_number.trim(),
        amount: form.amount,
        description: form.description,
      }
      if (pinToken) {
        payload.pin_verification_token = pinToken
      }
      await transactionApi.sendMoney(payload)
      toast.success(`Sent ${formatCurrency(amount)} successfully!`)
      setForm({ receiver_wallet_number: '', amount: '', description: '' })
      setPinToken('')
      setConfirmOpen(false)
    } catch (err) {
      const msg = err.response?.data?.message || err.response?.data?.pin_verification_token?.[0] || 'Transfer failed'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="section-padding max-w-2xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold mb-2">Send Money</h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">Transfer funds to any DigiWallet user instantly</p>
      </motion.div>

      {/* PIN Not Set Warning */}
      {user && !user.pin_set && (
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
          className="mb-6 p-4 rounded-xl bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-primary-100 dark:bg-primary-900/40 flex items-center justify-center flex-shrink-0">
              <svg className="w-4 h-4 text-primary-600 dark:text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium text-primary-700 dark:text-primary-300">Set Your Transaction PIN</p>
              <p className="text-xs text-primary-600 dark:text-primary-400 mt-0.5">
                Secure your transactions by setting a 4-digit PIN. Go to Settings to set it up.
              </p>
            </div>
          </div>
        </motion.div>
      )}

      <Card>
        <div className="space-y-5">
          <Input label="Recipient Wallet Number" value={form.receiver_wallet_number}
            onChange={e => setForm({ ...form, receiver_wallet_number: e.target.value })}
            error={errors.receiver_wallet_number} placeholder="Enter 12-digit wallet number" />

          <div>
            <Input label="Amount (USD)" type="number" value={form.amount}
              onChange={e => setForm({ ...form, amount: e.target.value })}
              error={errors.amount} placeholder="0.00" min="1" step="0.01" />
            {amount > 0 && (
              <div className="mt-3 p-3 rounded-xl bg-primary-50 dark:bg-primary-900/10 space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Transfer Amount</span>
                  <span>{formatCurrency(amount)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Fee ({(FEE_CONFIG.rate * 100).toFixed(1)}%)</span>
                  <span>{formatCurrency(fee)}</span>
                </div>
                <div className="flex justify-between font-bold pt-1 border-t border-primary-200 dark:border-primary-800">
                  <span>Total</span>
                  <span className="text-primary-600 dark:text-primary-400">{formatCurrency(total)}</span>
                </div>
              </div>
            )}
          </div>

          <Input label="Description (Optional)" value={form.description}
            onChange={e => setForm({ ...form, description: e.target.value })}
            placeholder="What's this for?" />

          <Button onClick={handleProceed} className="w-full" disabled={amount <= 0}>
            {user?.pin_set ? 'Enter PIN & Send' : 'Send'} {amount > 0 ? formatCurrency(total) : 'Money'}
          </Button>
        </div>
      </Card>

      {/* PIN Input Modal */}
      <PinInput
        isOpen={pinOpen}
        onClose={() => setPinOpen(false)}
        onVerified={handlePinVerified}
        title="Confirm Transaction"
      />

      {/* Confirmation Modal */}
      <Modal isOpen={confirmOpen} onClose={() => setConfirmOpen(false)} title="Confirm Transfer">
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-primary-50 dark:bg-primary-900/10 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">To</span>
              <span className="font-mono">{form.receiver_wallet_number}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Amount</span>
              <span>{formatCurrency(amount)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Fee</span>
              <span>{formatCurrency(fee)}</span>
            </div>
            <div className="flex justify-between font-bold pt-2 border-t border-primary-200 dark:border-primary-800">
              <span>Total</span>
              <span className="text-primary-600">{formatCurrency(total)}</span>
            </div>
          </div>

          {pinToken && (
            <div className="flex items-center gap-2 text-sm text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-900/10 p-2 rounded-lg">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
              PIN verified
            </div>
          )}

          <div className="flex gap-3">
            <Button variant="secondary" onClick={() => { setConfirmOpen(false); setPinToken('') }} className="flex-1">Cancel</Button>
            <Button onClick={handleSend} loading={loading} className="flex-1">Confirm & Send</Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
