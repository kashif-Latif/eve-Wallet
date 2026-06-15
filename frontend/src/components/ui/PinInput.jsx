import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { HiLockClosed, HiX } from 'react-icons/hi'
import Button from './Button'
import toast from 'react-hot-toast'

export default function PinInput({ isOpen, onClose, onVerified, title = 'Enter PIN to Confirm' }) {
  const [pin, setPin] = useState(['', '', '', ''])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const inputRefs = [useRef(), useRef(), useRef(), useRef()]

  useEffect(() => {
    if (isOpen) {
      setPin(['', '', '', ''])
      setError('')
      setTimeout(() => inputRefs[0].current?.focus(), 100)
    }
  }, [isOpen])

  const handleChange = (index, value) => {
    if (!/^\d*$/.test(value)) return
    const newPin = [...pin]
    newPin[index] = value.slice(-1)
    setPin(newPin)
    setError('')
    if (value && index < 3) {
      inputRefs[index + 1].current?.focus()
    }
  }

  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !pin[index] && index > 0) {
      inputRefs[index - 1].current?.focus()
    }
  }

  const handlePaste = (e) => {
    e.preventDefault()
    const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 4)
    if (pastedData.length > 0) {
      const newPin = [...pin]
      for (let i = 0; i < 4; i++) {
        newPin[i] = pastedData[i] || ''
      }
      setPin(newPin)
      const nextEmpty = pastedData.length < 4 ? pastedData.length : 3
      inputRefs[nextEmpty].current?.focus()
    }
  }

  const handleSubmit = async () => {
    const pinString = pin.join('')
    if (pinString.length !== 4) {
      setError('Please enter all 4 digits')
      return
    }

    setLoading(true)
    setError('')

    try {
      const { authApi } = await import('../../api/authApi')
      const res = await authApi.verifyPin({ pin: pinString })
      const token = res.data?.data?.verification_token || res.data?.verification_token
      if (onVerified) onVerified(token)
      onClose()
    } catch (err) {
      const msg = err.response?.data?.message || err.response?.data?.pin?.[0] || 'Incorrect PIN'
      setError(msg)
      toast.error(msg)
      setPin(['', '', '', ''])
      setTimeout(() => inputRefs[0].current?.focus(), 100)
    } finally {
      setLoading(false)
    }
  }

  const pinComplete = pin.every(d => d !== '')

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={onClose}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 30 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 30 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="glass-card max-w-sm w-full relative z-10 !p-8 text-center"
          >
            <button onClick={onClose} className="absolute top-4 right-4 p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-700 transition">
              <HiX className="w-5 h-5 text-gray-400" />
            </button>

            <div className="w-16 h-16 rounded-2xl gradient-bg flex items-center justify-center mx-auto mb-5">
              <HiLockClosed className="w-8 h-8 text-white" />
            </div>

            <h3 className="text-xl font-bold mb-1">{title}</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-8">
              Enter your 4-digit PIN to confirm this transaction
            </p>

            <div className="flex justify-center gap-3 mb-6">
              {pin.map((digit, i) => (
                <motion.div
                  key={i}
                  animate={digit ? { scale: [1, 1.1, 1] } : {}}
                  transition={{ duration: 0.15 }}
                >
                  <input
                    ref={inputRefs[i]}
                    type="password"
                    inputMode="numeric"
                    maxLength={1}
                    value={digit}
                    onChange={(e) => handleChange(i, e.target.value)}
                    onKeyDown={(e) => handleKeyDown(i, e)}
                    onPaste={handlePaste}
                    className="pin-input-box"
                  />
                </motion.div>
              ))}
            </div>

            {error && (
              <motion.p
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-red-500 text-sm mb-4"
              >
                {error}
              </motion.p>
            )}

            <Button onClick={handleSubmit} loading={loading} disabled={!pinComplete} className="w-full">
              Confirm & Send
            </Button>

            <p className="text-xs text-gray-400 mt-4">
              PIN verification is required for your security
            </p>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
}
