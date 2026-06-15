export default function Skeleton({ className = '', count = 1 }) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className={`animate-pulse bg-gray-200 dark:bg-slate-700 rounded-lg ${className}`} />
      ))}
    </>
  )
}
