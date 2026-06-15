import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { walletApi } from '../../api/walletApi'
import Card from '../../components/ui/Card'
import Spinner from '../../components/ui/Spinner'
import { HiDuplicate, HiCheck, HiShare } from 'react-icons/hi'
import toast from 'react-hot-toast'

export default function ReceiveMoney() {
  const [wallet, setWallet] = useState(null)
  const [loading, setLoading] = useState(true)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    walletApi.getMyWallet().then(res => {
      setWallet(res.data?.data || res.data)
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const copyWalletNumber = () => {
    navigator.clipboard.writeText(wallet?.wallet_number || '')
    setCopied(true)
    toast.success('Wallet number copied!')
    setTimeout(() => setCopied(false), 2000)
  }

  const shareWallet = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'My DigiWallet',
          text: `Send me money on DigiWallet! My wallet number is: ${wallet?.wallet_number}`,
        })
      } catch {}
    } else {
      copyWalletNumber()
    }
  }

  if (loading) return <Spinner />

  return (
    <div className="section-padding max-w-2xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold mb-2">Receive Money</h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">Share your wallet number to receive payments</p>
      </motion.div>

      <div className="space-y-6">
        <Card className="text-center !p-10">
          <div className="w-20 h-20 rounded-full gradient-bg flex items-center justify-center mx-auto mb-6">
            <span className="text-white text-3xl font-bold">$</span>
          </div>
          <p className="text-gray-500 dark:text-gray-400 mb-2">Your Wallet Number</p>
          <div className="flex items-center justify-center gap-3 mb-6">
            <p className="text-2xl sm:text-3xl font-mono font-bold tracking-widest">
              {wallet?.wallet_number || 'N/A'}
            </p>
          </div>
          <div className="flex items-center justify-center gap-3">
            <button onClick={copyWalletNumber}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-primary-500 text-white font-medium hover:bg-primary-600 transition">
              {copied ? <HiCheck className="w-5 h-5" /> : <HiDuplicate className="w-5 h-5" />}
              {copied ? 'Copied!' : 'Copy'}
            </button>
            <button onClick={shareWallet}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gray-100 dark:bg-slate-800 font-medium hover:bg-gray-200 dark:hover:bg-slate-700 transition">
              <HiShare className="w-5 h-5" />
              Share
            </button>
          </div>
        </Card>

        <Card>
          <h3 className="font-bold mb-3">How to Receive Money</h3>
          <ol className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
            <li className="flex gap-3">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 flex items-center justify-center text-xs font-bold">1</span>
              <span>Share your wallet number with the sender</span>
            </li>
            <li className="flex gap-3">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 flex items-center justify-center text-xs font-bold">2</span>
              <span>The sender enters your wallet number in the Send Money page</span>
            </li>
            <li className="flex gap-3">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 flex items-center justify-center text-xs font-bold">3</span>
              <span>Funds will be credited to your wallet instantly after confirmation</span>
            </li>
          </ol>
        </Card>
      </div>
    </div>
  )
}
