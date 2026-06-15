import { motion } from 'framer-motion';
import {
  HiPaperAirplane,
  HiDownload,
  HiChartBar,
  HiShieldCheck,
  HiLightningBolt,
  HiDeviceMobile,
  HiLockClosed,
  HiCurrencyDollar,
  HiGlobe,
  HiSupport,
} from 'react-icons/hi';
import Navbar from '../../components/layout/Navbar';
import Footer from '../../components/layout/Footer';

const features = [
  {
    icon: HiPaperAirplane,
    title: 'Instant Transfers',
    description: 'Send money to anyone instantly using their wallet number. No bank details needed. Transfers are processed in real-time with confirmation notifications.',
    color: 'from-primary-500 to-primary-600',
  },
  {
    icon: HiDownload,
    title: 'Easy Deposits',
    description: 'Add money to your wallet using multiple payment methods. Bank transfers, cards, and more. Your funds are available immediately after deposit.',
    color: 'from-emerald-500 to-emerald-600',
  },
  {
    icon: HiChartBar,
    title: 'Smart Analytics',
    description: 'Track your spending with detailed charts and insights. Monthly reports, category breakdowns, and spending trends at your fingertips.',
    color: 'from-secondary-500 to-secondary-600',
  },
  {
    icon: HiShieldCheck,
    title: 'Bank-Level Security',
    description: 'Your data and funds are protected with AES-256 encryption, two-factor authentication, and continuous fraud monitoring.',
    color: 'from-cyan-500 to-cyan-600',
  },
  {
    icon: HiLightningBolt,
    title: 'Lightning Fast',
    description: 'Experience blazing-fast transaction processing. Our infrastructure ensures sub-second response times for all operations.',
    color: 'from-amber-500 to-amber-600',
  },
  {
    icon: HiDeviceMobile,
    title: 'Mobile First',
    description: 'Designed for mobile from the ground up. Enjoy a seamless experience on any device with our responsive design.',
    color: 'from-rose-500 to-rose-600',
  },
  {
    icon: HiLockClosed,
    title: 'Secure Wallet',
    description: 'Multi-layer security with biometric authentication, PIN protection, and instant freeze capabilities if your device is lost.',
    color: 'from-indigo-500 to-indigo-600',
  },
  {
    icon: HiCurrencyDollar,
    title: 'Low Fees',
    description: 'Only 1.5% transfer fee with a $0.50 minimum and $25 maximum. No hidden charges, no surprise fees. What you see is what you pay.',
    color: 'from-teal-500 to-teal-600',
  },
  {
    icon: HiGlobe,
    title: 'Global Access',
    description: 'Access your wallet from anywhere in the world. Send and receive money across borders with ease.',
    color: 'from-violet-500 to-violet-600',
  },
  {
    icon: HiSupport,
    title: '24/7 Support',
    description: 'Our dedicated support team is available around the clock to help you with any issues or questions.',
    color: 'from-sky-500 to-sky-600',
  },
];

const Features = () => {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50 dark:bg-slate-950">
      <Navbar />

      <section className="py-16 md:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-16"
          >
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
              Powerful <span className="gradient-text">Features</span>
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Everything you need to manage your money, all in one place.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.05 }}
                whileHover={{ y: -6 }}
                className="glass-card p-6 group"
              >
                <div
                  className={`w-12 h-12 rounded-xl bg-gradient-to-r ${feature.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}
                >
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default Features;
