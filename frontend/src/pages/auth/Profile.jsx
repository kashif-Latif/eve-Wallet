import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useAuth } from '../../context/AuthContext'
import { authApi } from '../../api/authApi'
import Card from '../../components/ui/Card'
import Input from '../../components/ui/Input'
import Button from '../../components/ui/Button'
import Spinner from '../../components/ui/Spinner'
import toast from 'react-hot-toast'

export default function Profile() {
  const { user, setUser } = useAuth()
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', phone: '' })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (user) {
      setForm({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        phone: user.phone || '',
      })
      setLoading(false)
    }
  }, [user])

  const handleSave = async () => {
    setSaving(true)
    try {
      const { data } = await authApi.updateProfile(form)
      const updated = data.data || data
      setUser(updated)
      toast.success('Profile updated!')
    } catch (err) {
      toast.error(err.response?.data?.message || 'Update failed')
    } finally { setSaving(false) }
  }

  if (loading) return <Spinner />

  return (
    <div className="section-padding max-w-2xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold mb-6">Profile</h1>
      </motion.div>

      <Card className="mb-6 !p-8 text-center">
        <div className="w-20 h-20 rounded-full gradient-bg flex items-center justify-center mx-auto mb-4">
          <span className="text-white text-2xl font-bold">
            {(user?.first_name?.[0] || user?.username?.[0] || '?').toUpperCase()}
          </span>
        </div>
        <h2 className="text-xl font-bold">{user?.first_name || user?.username}</h2>
        <p className="text-gray-500 text-sm">{user?.email}</p>
        <Badge className="mt-2">{user?.role || 'user'}</Badge>
      </Card>

      <Card>
        <h3 className="font-bold mb-4">Edit Profile</h3>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Input label="First Name" value={form.first_name} onChange={e => setForm({ ...form, first_name: e.target.value })} />
            <Input label="Last Name" value={form.last_name} onChange={e => setForm({ ...form, last_name: e.target.value })} />
          </div>
          <Input label="Email" type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
          <Input label="Phone" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} />
          <Button onClick={handleSave} loading={saving}>Save Changes</Button>
        </div>
      </Card>
    </div>
  )
}
