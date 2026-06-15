import { motion } from 'framer-motion'
import Card from '../../components/ui/Card'

export default function AuditLogs() {
  return (
    <div className="section-padding">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold mb-2">Audit Logs</h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">Track all system activities and changes</p>
      </motion.div>

      <Card>
        <div className="text-center py-12">
          <p className="text-gray-400">Audit logs are recorded automatically by the system middleware.</p>
          <p className="text-gray-400 text-sm mt-2">Check the Django admin panel at /admin/ for detailed logs.</p>
        </div>
      </Card>
    </div>
  )
}
