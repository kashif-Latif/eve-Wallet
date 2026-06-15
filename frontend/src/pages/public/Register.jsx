import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { motion } from 'framer-motion'
import Input from '../../components/ui/Input'
import Button from '../../components/ui/Button'
import toast from 'react-hot-toast'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', email: '', phone: '', password: '', confirm_password: '' })
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({})

  const validate = () => {
    const errs = {}
    if (!form.username.trim()) errs.username = 'Username is required'
    if (!form.email.trim()) errs.email = 'Email is required'
    else if (!/\S+@\S+\.\S+/.test(form.email)) errs.email = 'Invalid email'
    if (!form.phone.trim()) errs.phone = 'Phone is required'
    if (!form.password) errs.password = 'Password is required'
    else if (form.password.length < 8) errs.password = 'Min 8 characters'
    if (form.password !== form.confirm_password) errs.confirm_password = 'Passwords do not match'
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  const passwordStrength = () => {
    const p = form.password
    if (!p) return 0
    let score = 0
    if (p.length >= 8) score++
    if (/[A-Z]/.test(p)) score++
    if (/[0-9]/.test(p)) score++
    if (/[^A-Za-z0-9]/.test(p)) score++
    return score
  }

  const strengthColors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-green-500']
  const strengthLabels = ['Weak', 'Fair', 'Good', 'Strong']

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!validate()) return
    setLoading(true)
    try {
      await register(form)
      toast.success('Wallet created! You received $1,000! 🎉')
      navigate('/dashboard')
    } catch (err) {
      const msg = err.response?.data?.message || err.response?.data?.detail || 'Registration failed'
      if (err.response?.data?.errors) {
        setErrors(err.response.data.errors)
      }
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  const str = passwordStrength()

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-slate-950 px-4 py-8">
      <div className="absolute inset-0 gradient-bg opacity-5" />
      <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md relative">
        <div className="glass-card">
          <div className="text-center mb-8">
            <div className="w-12 h-12 rounded-xl gradient-bg flex items-center justify-center mx-auto mb-4">
              <span className="text-white font-bold text-lg">W</span>
            </div>
            <h1 className="text-2xl font-bold">Create Your Wallet</h1>
            <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Get $1,000 instantly on signup</p>
          </div>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input label="Username" value={form.username} onChange={e => setForm({ ...form, username: e.target.value })}
              error={errors.username} placeholder="Choose a username" />
            <Input label="Email" type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })}
              error={errors.email} placeholder="you@example.com" />
            <Input label="Phone" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })}
              error={errors.phone} placeholder="+1 234 567 8900" />
            <div>
              <Input label="Password" type="password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })}
                error={errors.password} placeholder="Min 8 characters" />
              {form.password && (
                <div className="mt-2">
                  <div className="flex gap-1">
                    {[0,1,2,3].map(i => (
                      <div key={i} className={`h-1.5 flex-1 rounded-full ${i < str ? strengthColors[str-1] : 'bg-gray-200 dark:bg-slate-700'}`} />
                    ))}
                  </div>
                  <p className="text-xs mt-1 text-gray-500">{strengthLabels[str-1] || 'Too weak'}</p>
                </div>
              )}
            </div>
            <Input label="Confirm Password" type="password" value={form.confirm_password}
              onChange={e => setForm({ ...form, confirm_password: e.target.value })}
              error={errors.confirm_password} placeholder="Confirm your password" />
            <Button type="submit" loading={loading} className="w-full">Create Wallet</Button>
          </form>
          <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-6">
            Already have an account? <Link to="/login" className="text-primary-500 font-medium hover:underline">Sign In</Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}
