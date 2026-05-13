import { motion } from 'framer-motion'

export default function ConfidenceMeter({ fakeProb, realProb }) {
  const fakePercent = (fakeProb * 100).toFixed(1)
  const realPercent = (realProb * 100).toFixed(1)

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-xs text-slate-400 mb-1">
        <span>REAL</span>
        <span>Prediction Confidence</span>
        <span>FAKE</span>
      </div>

      {/* Dual bar */}
      <div className="relative h-6 bg-white/5 rounded-full overflow-hidden border border-white/10">
        {/* Real side (from left) */}
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${realProb * 100}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className="absolute left-0 top-0 h-full bg-success-gradient opacity-80"
        />
        {/* Fake side (from right) */}
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${fakeProb * 100}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className="absolute right-0 top-0 h-full bg-danger-gradient opacity-80"
        />
        {/* Center line */}
        <div className="absolute left-1/2 top-0 h-full w-0.5 bg-white/20" />
        {/* Labels */}
        <div className="absolute inset-0 flex items-center justify-between px-3 text-xs font-bold">
          <span className="text-success drop-shadow">{realPercent}%</span>
          <span className="text-danger drop-shadow">{fakePercent}%</span>
        </div>
      </div>
    </div>
  )
}
