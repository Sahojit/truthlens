import { useEffect, useState } from 'react'
import { getAnalyticsTrends, getAnalyticsSummary } from '../services/api'
import TrendChart from '../charts/TrendChart'
import { BarChart3, Calendar } from 'lucide-react'

export default function Analytics() {
  const [trends, setTrends] = useState([])
  const [summary, setSummary] = useState(null)
  const [days, setDays] = useState(30)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    Promise.all([getAnalyticsTrends(days), getAnalyticsSummary()])
      .then(([t, s]) => { setTrends(t.data); setSummary(s.data) })
      .finally(() => setLoading(false))
  }, [days])

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-6 h-6 text-primary" />
          <h1 className="text-2xl font-display font-bold">Analytics</h1>
        </div>
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-slate-400" />
          {[7, 14, 30, 60, 90].map(d => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                days === d
                  ? 'bg-primary text-white'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
            >
              {d}d
            </button>
          ))}
        </div>
      </div>

      {loading
        ? <div className="glass-card p-6 animate-pulse h-64" />
        : <TrendChart data={trends} />
      }

      {summary && (
        <>
          <p className="text-xs text-slate-400 -mt-2">ISOT Fake News Dataset — training statistics</p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { label: 'Training Articles', value: summary.total_predictions.toLocaleString(), color: 'text-primary' },
              { label: 'Fake Articles',     value: summary.fake_count.toLocaleString(),        color: 'text-danger'  },
              { label: 'Fake Rate',         value: `${summary.fake_percentage}%`,              color: 'text-warning' },
              { label: 'Model Accuracy',    value: `${(summary.avg_confidence*100).toFixed(1)}%`, color: 'text-success' },
            ].map(({ label, value, color }) => (
              <div key={label} className="metric-card">
                <div className={`metric-value ${color}`}>{value}</div>
                <div className="metric-label">{label}</div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
