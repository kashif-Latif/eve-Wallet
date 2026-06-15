import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { motion } from 'framer-motion'
import Input from '../../components/ui/Input'
import Button from '../../components/ui/Button'
import toast from 'react-hot-toast'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({})

  const validate = () => {
    const errs = {}
    if (!form.username.trim()) errs.username = 'Username is required'
    if (!form.password) errs.password = 'Password is required'
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!validate()) return
    setLoading(true)
    try {
      await login(form)
      toast.success('Welcome back!')
      navigate('/dashboard')
    } catch (err) {
      const msg = err.response?.data?.message || err.response?.data?.detail || 'Login failed'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-slate-950 px-4">
      <div className="absolute inset-0 gradient-bg opacity-5" />
      <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md relative">
        <div className="glass-card">
          <div className="text-center mb-8">
            <div className="w-12 h-12 rounded-xl gradient-bg flex items-center justify-center mx-auto mb-4">
              <span className="text-white font-bold text-lg">W</span>
            </div>
            <h1 className="text-2xl font-bold">Welcome Back</h1>
            <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Sign in to your wallet</p>
          </div>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input label="Username" value={form.username} onChange={e => setForm({ ...form, username: e.target.value })}
              error={errors.username} placeholder="Enter your username" />
            <Input label="Password" type="password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })}
              error={errors.password} placeholder="Enter your password" />
            <Button type="submit" loading={loading} className="w-full">Sign In</Button>
          </form>
          <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-6">
            Don't have an account? <Link to="/register" className="text-primary-500 font-medium hover:underline">Sign Up</Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}
