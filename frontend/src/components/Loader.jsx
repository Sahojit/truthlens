import { motion } from 'framer-motion'

export function FullPageLoader({ message = 'Analysing with AI…' }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-6">
      <div className="relative w-20 h-20">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
          className="w-20 h-20 rounded-full border-2 border-transparent
                     border-t-primary border-r-accent"
        />
        <motion.div
          animate={{ rotate: -360 }}
          transition={{ duration: 2.5, repeat: Infinity, ease: 'linear' }}
          className="absolute inset-2 rounded-full border-2 border-transparent
                     border-b-primary/60"
        />
        <div className="absolute inset-0 flex items-center justify-center text-2xl">
          🔍
        </div>
      </div>
      <div className="text-center">
        <motion.p
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="text-slate-300 font-medium"
        >
          {message}
        </motion.p>
        <p className="text-xs text-slate-500 mt-1">Running semantic + linguistic analysis</p>
      </div>
      {/* Scanning steps */}
      <div className="flex flex-col gap-1.5 text-xs text-slate-500">
        {[
          'Semantic analysis',
          'Emotion detection',
          'Source credibility check',
          'Ensemble prediction',
        ].map((step, i) => (
          <motion.div
            key={step}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.4 }}
            className="flex items-center gap-2"
          >
            <motion.div
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.3 }}
              className="w-1.5 h-1.5 rounded-full bg-primary"
            />
            {step}
          </motion.div>
        ))}
      </div>
    </div>
  )
}

export function SkeletonCard() {
  return (
    <div className="glass-card p-6 animate-pulse">
      <div className="flex gap-3 mb-4">
        <div className="w-14 h-14 bg-white/10 rounded-2xl" />
        <div className="flex-1 space-y-2">
          <div className="h-7 bg-white/10 rounded w-24" />
          <div className="h-4 bg-white/5 rounded w-36" />
        </div>
      </div>
      <div className="h-6 bg-white/10 rounded-full mb-4" />
      <div className="grid grid-cols-4 gap-3">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-20 bg-white/5 rounded-xl" />
        ))}
      </div>
    </div>
  )
}
