import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { authApi } from '../../api/authApi'
import Card from '../../components/ui/Card'
import Button from '../../components/ui/Button'
import toast from 'react-hot-toast'
import { HiLockClosed, HiCheck } from 'react-icons/hi'

export default function SetPin({ onSuccess }) {
  const [step, setStep] = useState(1) // 1=enter, 2=confirm
  const [pin, setPin] = useState(['', '', '', ''])
  const [confirmPin, setConfirmPin] = useState(['', '', '', ''])
  const [loading, setLoading] = useState(false)
  const inputRefs = [useRef(), useRef(), useRef(), useRef()]
  const confirmRefs = [useRef(), useRef(), useRef(), useRef()]

  useEffect(() => {
    if (step === 1) setTimeout(() => inputRefs[0].current?.focus(), 100)
    else setTimeout(() => confirmRefs[0].current?.focus(), 100)
  }, [step])

  const handleChange = (index, value, isConfirm = false) => {
    if (!/^\d*$/.test(value)) return
    const currentPin = isConfirm ? [...confirmPin] : [...pin]
    currentPin[index] = value.slice(-1)

    if (isConfirm) setConfirmPin(currentPin)
    else setPin(currentPin)

    const refs = isConfirm ? confirmRefs : inputRefs
    if (value && index < 3) {
      refs[index + 1].current?.focus()
    }
  }

  const handleKeyDown = (index, e, isConfirm = false) => {
    const refs = isConfirm ? confirmRefs : inputRefs
    const currentPin = isConfirm ? confirmPin : pin
    if (e.key === 'Backspace' && !currentPin[index] && index > 0) {
      refs[index - 1].current?.focus()
    }
  }

  const handleContinue = () => {
    if (pin.some(d => !d)) {
      toast.error('Please enter all 4 digits')
      return
    }
    setStep(2)
  }

  const handleSubmit = async () => {
    const pinStr = pin.join('')
    const confirmStr = confirmPin.join('')

    if (confirmStr !== pinStr) {
      toast.error('PINs do not match. Try again.')
      setConfirmPin(['', '', '', ''])
      setStep(1)
      return
    }

    setLoading(true)
    try {
      await authApi.setPin({ pin: pinStr, confirm_pin: confirmStr })
      toast.success('Transaction PIN set successfully!')
      if (onSuccess) onSuccess()
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to set PIN')
    } finally {
      setLoading(false)
    }
  }

  const currentPin = step === 2 ? confirmPin : pin
  const currentRefs = step === 2 ? confirmRefs : inputRefs

  return (
    <Card className="max-w-sm mx-auto !p-8 text-center">
      <div className="w-16 h-16 rounded-2xl gradient-bg flex items-center justify-center mx-auto mb-5">
        <HiLockClosed className="w-8 h-8 text-white" />
      </div>

      <h3 className="text-xl font-bold mb-1">
        {step === 1 ? 'Set Transaction PIN' : 'Confirm Your PIN'}
      </h3>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-8">
        {step === 1
          ? 'Create a 4-digit PIN to secure your transactions'
          : 'Re-enter your PIN to confirm'}
      </p>

      <div className="flex justify-center gap-3 mb-6">
        {currentPin.map((digit, i) => (
          <motion.div key={i} animate={digit ? { scale: [1, 1.1, 1] } : {}} transition={{ duration: 0.15 }}>
            <input
              ref={currentRefs[i]}
              type="password"
              inputMode="numeric"
              maxLength={1}
              value={digit}
              onChange={(e) => handleChange(i, e.target.value, step === 2)}
              onKeyDown={(e) => handleKeyDown(i, e, step === 2)}
              className="pin-input-box"
            />
          </motion.div>
        ))}
      </div>

      {/* PIN strength indicator */}
      <div className="flex justify-center gap-2 mb-6">
        {[1, 2].map(s => (
          <div key={s} className={`h-1.5 w-16 rounded-full transition-all ${
            s <= step ? 'bg-primary-500' : 'bg-gray-200 dark:bg-dark-700'
          }`} />
        ))}
      </div>

      {step === 1 ? (
        <Button onClick={handleContinue} disabled={pin.some(d => !d)} className="w-full">
          Continue
        </Button>
      ) : (
        <div className="flex gap-3">
          <Button variant="secondary" onClick={() => { setStep(1); setConfirmPin(['','','','']) }} className="flex-1">
            Back
          </Button>
          <Button onClick={handleSubmit} loading={loading} disabled={confirmPin.some(d => !d)} className="flex-1">
            Set PIN
          </Button>
        </div>
      )}
    </Card>
  )
}
