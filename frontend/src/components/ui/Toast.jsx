import { Toaster } from 'react-hot-toast'

export default function Toast() {
  return (
    <Toaster
      position="top-right"
      toastOptions={{
        duration: 4000,
        style: {
          background: 'rgba(255,255,255,0.9)',
          backdropFilter: 'blur(16px)',
          border: '1px solid rgba(255,255,255,0.3)',
          color: '#1f2937',
          borderRadius: '12px',
          padding: '12px 16px',
        },
        className: 'dark:!bg-slate-800/90 dark:!text-white dark:!border-slate-700',
      }}
    />
  )
}
