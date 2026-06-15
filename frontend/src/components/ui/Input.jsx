import { forwardRef } from 'react'

const Input = forwardRef(({ label, error, className = '', ...props }, ref) => (
  <div className="space-y-1">
    {label && <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">{label}</label>}
    <input ref={ref} className={`input-field ${error ? 'ring-2 ring-red-500/50 border-red-500' : ''} ${className}`} {...props} />
    {error && <p className="text-sm text-red-500">{error}</p>}
  </div>
))

Input.displayName = 'Input'
export default Input
