import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { HiPaperAirplane, HiShieldCheck, HiLightningBolt, HiChartBar } from 'react-icons/hi'

const features = [
  { icon: HiPaperAirplane, title: 'Instant Transfers', desc: 'Send and receive money instantly with zero hassle. Transfer to any wallet number in seconds.' },
  { icon: HiShieldCheck, title: 'Bank-Grade Security', desc: 'Your funds are protected with JWT authentication, encryption, and atomic transaction safety.' },
  { icon: HiLightningBolt, title: 'Lightning Fast', desc: 'Experience blazing-fast transactions with real-time balance updates and notifications.' },
  { icon: HiChartBar, title: 'Smart Analytics', desc: 'Track your spending with beautiful charts and detailed transaction history at your fingertips.' },
]

const stats = [
  { value: '50K+', label: 'Active Users' },
  { value: '$2M+', label: 'Transferred' },
  { value: '99.9%', label: 'Uptime' },
  { value: '150+', label: 'Countries' },
]

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 gradient-bg opacity-10" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 py-20 sm:py-32 text-center">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
            <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold mb-6">
              Your Digital <span className="gradient-text">Wallet</span>
              <br />Reimagined
            </h1>
            <p className="text-lg sm:text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-10">
              Send, receive, and manage your money with enterprise-grade security and beautiful simplicity.
              Get started with $1,000 instantly.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/register" className="btn-primary text-lg !py-4 !px-8 w-full sm:w-auto">
                Get Started Free
              </Link>
              <Link to="/login" className="btn-secondary text-lg !py-4 !px-8 w-full sm:w-auto">
                Sign In
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 border-y border-gray-200 dark:border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, i) => (
              <motion.div key={i} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }} viewport={{ once: true }} className="text-center">
                <p className="text-3xl sm:text-4xl font-bold gradient-text">{stat.value}</p>
                <p className="text-gray-500 dark:text-gray-400 mt-1">{stat.label}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <h2 className="text-3xl sm:text-4xl font-bold text-center mb-4">
            Why Choose <span className="gradient-text">DigiWallet</span>?
          </h2>
          <p className="text-gray-500 dark:text-gray-400 text-center mb-16 max-w-2xl mx-auto">
            Built with cutting-edge technology to provide you the best digital wallet experience.
          </p>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, i) => (
              <motion.div key={i} initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }} viewport={{ once: true }}
                className="glass-card text-center group">
                <div className="w-14 h-14 rounded-2xl gradient-bg flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                  <feature.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-lg font-bold mb-2">{feature.title}</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 text-center">
          <motion.div initial={{ opacity: 0, scale: 0.95 }} whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }} className="glass-card gradient-bg text-white !border-0">
            <h2 className="text-3xl font-bold mb-4">Ready to Get Started?</h2>
            <p className="text-white/80 mb-8">Create your free wallet and receive $1,000 instantly to start exploring.</p>
            <Link to="/register" className="inline-block bg-white text-primary-600 font-bold py-3 px-8 rounded-xl hover:bg-gray-100 transition">
              Create Free Wallet
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  )
}
