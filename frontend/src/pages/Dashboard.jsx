import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { getAnalyticsSummary, getAnalyticsTrends, getEmotionDistribution, getModelAccuracy } from '../services/api'
import TrendChart from '../charts/TrendChart'
import EmotionRadar from '../charts/EmotionRadar'
import ModelComparisonChart from '../charts/ModelComparisonChart'
import { LayoutDashboard, TrendingUp, Shield, AlertTriangle, Brain, Zap } from 'lucide-react'

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [trends, setTrends]   = useState([])
  const [emotions, setEmotions] = useState({})
  const [modelAcc, setModelAcc] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      getAnalyticsSummary(),
      getAnalyticsTrends(30),
      getEmotionDistribution(),
      getModelAccuracy(),
    ]).then(([s, t, e, m]) => {
      setSummary(s.data)
      setTrends(t.data)
      setEmotions(e.data)
      setModelAcc(m.data)
    }).finally(() => setLoading(false))
  }, [])

  const metrics = summary ? [
    { label: 'Total Analysed',    value: summary.total_predictions, icon: Brain,         color: 'text-primary'  },
    { label: 'Fake Detected',     value: summary.fake_count,        icon: AlertTriangle,  color: 'text-danger'   },
    { label: 'Real Articles',     value: summary.real_count,        icon: Shield,         color: 'text-success'  },
    { label: 'Fake Rate',         value: `${summary.fake_percentage}%`, icon: TrendingUp, color: 'text-warning'  },
    { label: 'Avg Confidence',    value: `${(summary.avg_confidence * 100).toFixed(1)}%`, icon: Zap, color: 'text-accent' },
    { label: 'Avg Emotion Score', value: `${(summary.avg_emotion_score * 100).toFixed(1)}%`, icon: Brain, color: 'text-purple-400' },
  ] : []

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center gap-2">
        <LayoutDashboard className="w-6 h-6 text-primary" />
        <h1 className="text-2xl font-display font-bold">Analytics Dashboard</h1>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {loading
          ? [...Array(6)].map((_, i) => (
              <div key={i} className="metric-card animate-pulse">
                <div className="h-7 bg-white/10 rounded w-16 mb-1" />
                <div className="h-3 bg-white/5 rounded w-20" />
              </div>
            ))
          : metrics.map(({ label, value, icon: Icon, color }, i) => (
              <motion.div
                key={label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="metric-card"
              >
                <Icon className={`w-5 h-5 ${color} mb-1`} />
                <div className={`metric-value ${color}`}>{value}</div>
                <div className="metric-label">{label}</div>
              </motion.div>
            ))
        }
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TrendChart data={trends} />
        <EmotionRadar data={emotions} />
      </div>

      {/* Model Comparison */}
      <ModelComparisonChart data={modelAcc} />
    </div>
  )
}
