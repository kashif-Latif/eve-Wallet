import { useState } from 'react'
import { motion } from 'framer-motion'
import { useAuth } from '../../context/AuthContext'
import { authApi } from '../../api/authApi'
import Card from '../../components/ui/Card'
import Input from '../../components/ui/Input'
import Button from '../../components/ui/Button'
import ThemeToggle from '../../components/ui/Toggle'
import SetPin from './SetPin'
import toast from 'react-hot-toast'
import { HiLockClosed, HiCheck } from 'react-icons/hi'

export default function Settings() {
  const { user, setUser, checkAuth } = useAuth()
  const [pwForm, setPwForm] = useState({ old_password: '', new_password: '', confirm_password: '' })
  const [changing, setChanging] = useState(false)
  const [showSetPin, setShowSetPin] = useState(false)

  const handleChangePassword = async () => {
    if (pwForm.new_password !== pwForm.confirm_password) {
      toast.error('Passwords do not match')
      return
    }
    if (pwForm.new_password.length < 8) {
      toast.error('Password must be at least 8 characters')
      return
    }
    setChanging(true)
    try {
      await authApi.changePassword({
        old_password: pwForm.old_password,
        new_password: pwForm.new_password,
      })
      toast.success('Password changed!')
      setPwForm({ old_password: '', new_password: '', confirm_password: '' })
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to change password')
    } finally { setChanging(false) }
  }

  const handlePinSet = async () => {
    setShowSetPin(false)
    await checkAuth() // Refresh user data to get updated pin_set
    toast.success('PIN set successfully!')
  }

  return (
    <div className="section-padding max-w-2xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold mb-6">Settings</h1>
      </motion.div>

      {/* Transaction PIN */}
      <Card className="mb-6">
        <h3 className="font-bold mb-2 flex items-center gap-2">
          <HiLockClosed className="w-5 h-5 text-primary-500" />
          Transaction PIN
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
          {user?.pin_set
            ? 'Your transaction PIN is set. You will be asked to enter it before sending money.'
            : 'Set a 4-digit PIN to secure your transactions. Required before sending money.'}
        </p>
        {user?.pin_set ? (
          <div className="flex items-center gap-2 text-sm text-emerald-600 dark:text-emerald-400">
            <HiCheck className="w-5 h-5" />
            <span>PIN is active and protecting your transactions</span>
          </div>
        ) : showSetPin ? (
          <SetPin onSuccess={handlePinSet} />
        ) : (
          <Button onClick={() => setShowSetPin(true)}>Set Transaction PIN</Button>
        )}
      </Card>

      {/* Appearance */}
      <Card className="mb-6">
        <h3 className="font-bold mb-4">Appearance</h3>
        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium">Dark Mode</p>
            <p className="text-sm text-gray-500">Toggle between light and dark themes</p>
          </div>
          <ThemeToggle />
        </div>
      </Card>

      {/* Change Password */}
      <Card className="mb-6">
        <h3 className="font-bold mb-4">Change Password</h3>
        <div className="space-y-4">
          <Input label="Current Password" type="password" value={pwForm.old_password}
            onChange={e => setPwForm({ ...pwForm, old_password: e.target.value })} />
          <Input label="New Password" type="password" value={pwForm.new_password}
            onChange={e => setPwForm({ ...pwForm, new_password: e.target.value })} />
          <Input label="Confirm New Password" type="password" value={pwForm.confirm_password}
            onChange={e => setPwForm({ ...pwForm, confirm_password: e.target.value })} />
          <Button onClick={handleChangePassword} loading={changing}>Update Password</Button>
        </div>
      </Card>

      {/* Danger Zone */}
      <Card className="!border-red-200 dark:!border-red-900/30">
        <h3 className="font-bold text-red-600 mb-2">Danger Zone</h3>
        <p className="text-sm text-gray-500 mb-4">Once you delete your account, there is no going back.</p>
        <Button variant="danger" onClick={() => toast('Contact admin to delete account')}>Delete Account</Button>
      </Card>
    </div>
  )
}
