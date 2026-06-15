import { motion } from 'framer-motion';
import { HiUsers, HiHeart, HiGlobe, HiShieldCheck } from 'react-icons/hi';
import Navbar from '../../components/layout/Navbar';
import Footer from '../../components/layout/Footer';

const team = [
  { name: 'Alex Johnson', role: 'CEO & Founder', avatar: 'AJ' },
  { name: 'Sarah Chen', role: 'CTO', avatar: 'SC' },
  { name: 'Michael Brown', role: 'Head of Security', avatar: 'MB' },
  { name: 'Emily Davis', role: 'Head of Design', avatar: 'ED' },
];

const values = [
  {
    icon: HiShieldCheck,
    title: 'Security First',
    description: 'We never compromise on security. Every transaction is encrypted and monitored.',
  },
  {
    icon: HiUsers,
    title: 'User Focused',
    description: 'Our users are at the heart of everything we do. We build for you.',
  },
  {
    icon: HiHeart,
    title: 'Transparency',
    description: 'No hidden fees, no fine print. We believe in complete transparency.',
  },
  {
    icon: HiGlobe,
    title: 'Global Reach',
    description: 'Breaking down financial borders. Access your money anywhere, anytime.',
  },
];

const About = () => {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50 dark:bg-slate-950">
      <Navbar />

      <section className="py-16 md:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Hero */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-20"
          >
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
              About <span className="gradient-text">Digital Wallet</span>
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              We're on a mission to make financial services accessible, secure, and effortless for
              everyone.
            </p>
          </motion.div>

          {/* Story */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="glass-card p-8 md:p-12 mb-16 max-w-4xl mx-auto"
          >
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Our Story</h2>
            <div className="space-y-4 text-gray-600 dark:text-gray-400">
              <p>
                Digital Wallet was born from a simple idea: managing money should be easy, secure,
                and accessible to everyone. Founded in 2023, we started with a small team of
                passionate engineers and designers who believed that financial technology could be
                both powerful and user-friendly.
              </p>
              <p>
                Today, we serve over 50,000 users across 30+ countries, processing billions of
                dollars in transactions. Our platform combines cutting-edge security with an
                intuitive interface that makes digital payments as simple as sending a message.
              </p>
              <p>
                We're not just building a wallet — we're building the future of digital finance.
                Every feature we design, every security measure we implement, and every line of
                code we write is in service of our users.
              </p>
            </div>
          </motion.div>

          {/* Values */}
          <div className="mb-16">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white text-center mb-12">
              Our Values
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {values.map((value, index) => (
                <motion.div
                  key={value.title}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="glass-card p-6 text-center"
                >
                  <div className="w-12 h-12 rounded-xl bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center mx-auto mb-4">
                    <value.icon className="w-6 h-6 text-primary-500" />
                  </div>
                  <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                    {value.title}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{value.description}</p>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Team */}
          <div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white text-center mb-12">
              Our Team
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {team.map((member, index) => (
                <motion.div
                  key={member.name}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="glass-card p-6 text-center"
                >
                  <div className="w-16 h-16 rounded-full animated-gradient-bg flex items-center justify-center mx-auto mb-4">
                    <span className="text-white font-bold text-lg">{member.avatar}</span>
                  </div>
                  <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                    {member.name}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{member.role}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default About;
