import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { refundApi } from '../../api/refundApi'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import Modal from '../../components/ui/Modal'
import Input from '../../components/ui/Input'
import Spinner from '../../components/ui/Spinner'
import { formatCurrency } from '../../utils/formatCurrency'
import { formatDateTime } from '../../utils/formatDate'
import { REFUND_STATUS } from '../../utils/constants'
import toast from 'react-hot-toast'

export default function RefundRequests() {
  const [refunds, setRefunds] = useState([])
  const [loading, setLoading] = useState(true)
  const [requestOpen, setRequestOpen] = useState(false)
  const [form, setForm] = useState({ transaction_id: '', reason: '' })
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    refundApi.getMyRefunds().then(res => {
      setRefunds(res.data?.data?.results || res.data?.results || res.data?.data || [])
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const handleRequest = async () => {
    if (!form.transaction_id || !form.reason.trim()) {
      toast.error('Fill all fields')
      return
    }
    setSubmitting(true)
    try {
      await refundApi.requestRefund(form)
      toast.success('Refund request submitted!')
      setRequestOpen(false)
      setForm({ transaction_id: '', reason: '' })
      // Refresh
      const res = await refundApi.getMyRefunds()
      setRefunds(res.data?.data?.results || res.data?.results || res.data?.data || [])
    } catch (err) {
      toast.error(err.response?.data?.message || 'Request failed')
    } finally { setSubmitting(false) }
  }

  if (loading) return <Spinner />

  return (
    <div className="section-padding">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Refund Requests</h1>
            <p className="text-gray-500 dark:text-gray-400">Track and manage your refund requests</p>
          </div>
          <Button onClick={() => setRequestOpen(true)}>New Request</Button>
        </div>
      </motion.div>

      {refunds.length > 0 ? (
        <div className="space-y-3">
          {refunds.map((refund, i) => {
            const statusInfo = REFUND_STATUS[refund.status] || REFUND_STATUS.pending
            return (
              <motion.div key={refund.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
                <Card>
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-medium">Refund #{refund.id}</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{refund.reason}</p>
                      <p className="text-xs text-gray-400 mt-1">{formatDateTime(refund.created_at)}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-primary-600 dark:text-primary-400">{formatCurrency(refund.amount)}</p>
                      <Badge variant={refund.status === 'completed' || refund.status === 'approved' ? 'success' : refund.status === 'rejected' ? 'danger' : 'warning'}>
                        {statusInfo.label}
                      </Badge>
                    </div>
                  </div>
                  {refund.admin_note && (
                    <p className="mt-2 text-sm text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-slate-800 p-2 rounded-lg">
                      Admin: {refund.admin_note}
                    </p>
                  )}
                </Card>
              </motion.div>
            )
          })}
        </div>
      ) : (
        <Card className="text-center py-12">
          <p className="text-gray-400 mb-2">No refund requests yet</p>
          <button onClick={() => setRequestOpen(true)} className="text-primary-500 hover:underline text-sm">Request a refund</button>
        </Card>
      )}

      <Modal isOpen={requestOpen} onClose={() => setRequestOpen(false)} title="Request Refund">
        <div className="space-y-4">
          <Input label="Transaction ID" type="number" value={form.transaction_id}
            onChange={e => setForm({ ...form, transaction_id: e.target.value })}
            placeholder="Enter the transaction ID" />
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Reason</label>
            <textarea value={form.reason} onChange={e => setForm({ ...form, reason: e.target.value })}
              placeholder="Explain why you need a refund" rows={3}
              className="input-field !h-auto" />
          </div>
          <Button onClick={handleRequest} loading={submitting} className="w-full">Submit Refund Request</Button>
        </div>
      </Modal>
    </div>
  )
}
