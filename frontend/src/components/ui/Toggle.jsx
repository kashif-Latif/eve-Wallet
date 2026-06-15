import { useTheme } from '../../context/ThemeContext'
import { HiSun, HiMoon } from 'react-icons/hi'
import { motion } from 'framer-motion'

export default function ThemeToggle() {
  const { darkMode, toggleTheme } = useTheme()
  return (
    <motion.button
      whileTap={{ scale: 0.9 }}
      onClick={toggleTheme}
      className="p-2 rounded-xl bg-gray-100 dark:bg-slate-800 hover:bg-gray-200 dark:hover:bg-slate-700 transition"
      aria-label="Toggle theme"
    >
      {darkMode ? <HiSun className="w-5 h-5 text-yellow-400" /> : <HiMoon className="w-5 h-5 text-slate-600" />}
    </motion.button>
  )
}
