import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { walletApi } from '../../api/walletApi'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import Spinner from '../../components/ui/Spinner'
import { formatCurrency } from '../../utils/formatCurrency'
import { formatDateTime } from '../../utils/formatDate'
import toast from 'react-hot-toast'

export default function WalletManagement() {
  const [wallets, setWallets] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    walletApi.adminGetAll().then(res => {
      setWallets(res.data?.data?.results || res.data?.results || res.data?.data || [])
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const toggleFreeze = async (id) => {
    try {
      await walletApi.freezeWallet(id)
      setWallets(prev => prev.map(w => w.id === id ? { ...w, is_frozen: !w.is_frozen } : w))
      toast.success('Wallet updated')
    } catch (err) {
      toast.error(err.response?.data?.message || 'Action failed')
    }
  }

  if (loading) return <Spinner />

  return (
    <div className="section-padding">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold mb-6">Wallet Management</h1>
      </motion.div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 dark:border-slate-700">
                <th className="text-left py-3 px-4 font-medium text-gray-500">Wallet #</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">User</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Balance</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Status</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Created</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody>
              {wallets.map(wallet => (
                <tr key={wallet.id} className="border-b border-gray-100 dark:border-slate-800 hover:bg-gray-50 dark:hover:bg-slate-800/50">
                  <td className="py-3 px-4 font-mono text-xs">{wallet.wallet_number}</td>
                  <td className="py-3 px-4">{wallet.user?.username || wallet.user}</td>
                  <td className="py-3 px-4 font-medium">{formatCurrency(wallet.balance)}</td>
                  <td className="py-3 px-4">
                    <Badge variant={wallet.is_frozen ? 'danger' : wallet.is_active ? 'success' : 'warning'}>
                      {wallet.is_frozen ? 'Frozen' : wallet.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </td>
                  <td className="py-3 px-4 text-gray-500 text-xs">{formatDateTime(wallet.created_at)}</td>
                  <td className="py-3 px-4">
                    <Button size="sm" variant={wallet.is_frozen ? 'primary' : 'danger'}
                      onClick={() => toggleFreeze(wallet.id)} className="!py-1 !px-3 !text-xs">
                      {wallet.is_frozen ? 'Unfreeze' : 'Freeze'}
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {wallets.length === 0 && <p className="text-center py-8 text-gray-400">No wallets found</p>}
        </div>
      </Card>
    </div>
  )
}
