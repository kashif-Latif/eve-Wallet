import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { refundApi } from '../../api/refundApi'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import Modal from '../../components/ui/Modal'
import Spinner from '../../components/ui/Spinner'
import { formatCurrency } from '../../utils/formatCurrency'
import { formatDateTime } from '../../utils/formatDate'
import { REFUND_STATUS } from '../../utils/constants'
import toast from 'react-hot-toast'

export default function RefundManagement() {
  const [refunds, setRefunds] = useState([])
  const [loading, setLoading] = useState(true)
  const [processing, setProcessing] = useState(null)
  const [adminNote, setAdminNote] = useState('')
  const [modalAction, setModalAction] = useState(null)

  useEffect(() => {
    refundApi.getAll().then(res => {
      setRefunds(res.data?.data?.results || res.data?.results || res.data?.data || [])
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const handleProcess = async (id, action) => {
    setProcessing(id)
    try {
      await refundApi.process(id, { action, admin_note: adminNote })
      toast.success(`Refund ${action}!`)
      setAdminNote('')
      setModalAction(null)
      // Refresh
      const res = await refundApi.getAll()
      setRefunds(res.data?.data?.results || res.data?.results || res.data?.data || [])
    } catch (err) {
      toast.error(err.response?.data?.message || 'Action failed')
    } finally { setProcessing(null) }
  }

  const handleComplete = async (id) => {
    setProcessing(id)
    try {
      await refundApi.complete(id)
      toast.success('Refund completed! Money returned.')
      const res = await refundApi.getAll()
      setRefunds(res.data?.data?.results || res.data?.results || res.data?.data || [])
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed')
    } finally { setProcessing(null) }
  }

  if (loading) return <Spinner />

  return (
    <div className="section-padding">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold mb-6">Refund Management</h1>
      </motion.div>

      <div className="space-y-3">
        {refunds.map((refund, i) => {
          const statusInfo = REFUND_STATUS[refund.status] || REFUND_STATUS.pending
          return (
            <motion.div key={refund.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
              <Card>
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="font-medium">Refund #{refund.id} - Transaction #{refund.transaction}</p>
                    <p className="text-sm text-gray-500 mt-1">{refund.reason}</p>
                    <p className="text-xs text-gray-400 mt-1">{formatDateTime(refund.created_at)}</p>
                    {refund.admin_note && <p className="text-xs text-gray-500 mt-1 bg-gray-50 dark:bg-slate-800 p-2 rounded">Admin: {refund.admin_note}</p>}
                  </div>
                  <div className="text-right flex-shrink-0">
                    <p className="font-bold">{formatCurrency(refund.amount)}</p>
                    <Badge variant={refund.status === 'completed' || refund.status === 'approved' ? 'success' : refund.status === 'rejected' ? 'danger' : 'warning'}>
                      {statusInfo.label}
                    </Badge>
                  </div>
                </div>
                {refund.status === 'pending' && (
                  <div className="flex gap-2 mt-3 pt-3 border-t border-gray-100 dark:border-slate-800">
                    <Button onClick={() => setModalAction({ id: refund.id, action: 'approve' })}
                      className="!py-1.5 !px-3 !text-xs">Approve</Button>
                    <Button variant="danger" onClick={() => setModalAction({ id: refund.id, action: 'reject' })}
                      className="!py-1.5 !px-3 !text-xs">Reject</Button>
                  </div>
                )}
                {refund.status === 'approved' && (
                  <div className="mt-3 pt-3 border-t border-gray-100 dark:border-slate-800">
                    <Button onClick={() => handleComplete(refund.id)} loading={processing === refund.id}
                      className="!py-1.5 !px-3 !text-xs">Complete Refund (Return Money)</Button>
                  </div>
                )}
              </Card>
            </motion.div>
          )
        })}
        {refunds.length === 0 && <Card className="text-center py-12"><p className="text-gray-400">No refund requests</p></Card>}
      </div>

      <Modal isOpen={!!modalAction} onClose={() => setModalAction(null)} title={`${modalAction?.action === 'approve' ? 'Approve' : 'Reject'} Refund`}>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Admin Note</label>
            <textarea value={adminNote} onChange={e => setAdminNote(e.target.value)}
              placeholder="Add a note..." rows={3} className="input-field !h-auto" />
          </div>
          <div className="flex gap-3">
            <Button variant="secondary" onClick={() => setModalAction(null)} className="flex-1">Cancel</Button>
            <Button variant={modalAction?.action === 'approve' ? 'primary' : 'danger'}
              onClick={() => handleProcess(modalAction.id, modalAction.action)} loading={processing === modalAction?.id}
              className="flex-1">{modalAction?.action === 'approve' ? 'Approve' : 'Reject'}</Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
