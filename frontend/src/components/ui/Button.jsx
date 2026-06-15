import { motion } from 'framer-motion'

export default function Button({ children, variant = 'primary', className = '', loading = false, disabled = false, ...props }) {
  const variants = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    danger: 'btn-danger',
  }

  return (
    <motion.button
      whileTap={{ scale: 0.97 }}
      className={`${variants[variant]} ${className} inline-flex items-center justify-center gap-2`}
      disabled={loading || disabled}
      {...props}
    >
      {loading && (
        <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      )}
      {children}
    </motion.button>
  )
}
