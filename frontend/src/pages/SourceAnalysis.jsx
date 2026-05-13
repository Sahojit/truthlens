import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { getCredibilityLeaderboard, checkSource } from '../services/api'
import { Globe, Search, Shield, AlertTriangle } from 'lucide-react'
import toast from 'react-hot-toast'

export default function SourceAnalysis() {
  const [leaderboard, setLeaderboard] = useState({ most_trusted: [], least_trusted: [] })
  const [url, setUrl] = useState('')
  const [checkResult, setCheckResult] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    getCredibilityLeaderboard()
      .then(r => setLeaderboard(r.data))
      .catch(() => {})
  }, [])

  const handleCheck = async () => {
    if (!url.trim()) { toast.error('Enter a URL'); return }
    setLoading(true)
    try {
      const { data } = await checkSource(url)
      setCheckResult(data)
    } catch {
      toast.error('Check failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center gap-2">
        <Globe className="w-6 h-6 text-primary" />
        <h1 className="text-2xl font-display font-bold">Source Credibility</h1>
      </div>

      {/* URL Checker */}
      <div className="glass-card p-5">
        <div className="section-title mb-3">Check a Source URL</div>
        <div className="flex gap-3">
          <input
            value={url}
            onChange={e => setUrl(e.target.value)}
            placeholder="https://example.com/article"
            onKeyDown={e => e.key === 'Enter' && handleCheck()}
            className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3
                       text-white placeholder-slate-500 focus:outline-none focus:border-primary/50 text-sm"
          />
          <button onClick={handleCheck} disabled={loading} className="btn-primary px-5">
            {loading
              ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              : <Search className="w-4 h-4" />
            }
          </button>
        </div>

        {checkResult && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-4 bg-white/5 rounded-xl border border-white/10"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="font-mono text-white">{checkResult.domain}</div>
              <span className={`score-badge ${checkResult.trust_score >= 0.6 ? 'score-real' : 'score-fake'}`}>
                {checkResult.credibility_label}
              </span>
            </div>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <div className="text-slate-500 text-xs mb-1">Trust Score</div>
                <div className="font-bold text-lg text-white">
                  {(checkResult.trust_score * 100).toFixed(0)}%
                </div>
              </div>
              <div>
                <div className="text-slate-500 text-xs mb-1">Political Bias</div>
                <div className="font-semibold text-accent capitalize">{checkResult.political_bias}</div>
              </div>
              <div>
                <div className="text-slate-500 text-xs mb-1">Category</div>
                <div className="font-semibold text-white capitalize">{checkResult.category}</div>
              </div>
            </div>
            <div className="progress-bar mt-3">
              <div
                className="progress-fill bg-gradient-to-r from-danger via-warning to-success"
                style={{ width: `${checkResult.trust_score * 100}%` }}
              />
            </div>
          </motion.div>
        )}
      </div>

      {/* Leaderboard */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <SourceTable title="Most Trusted Sources" icon={<Shield className="w-4 h-4 text-success" />}
          sources={leaderboard.most_trusted} color="success" />
        <SourceTable title="Least Trusted Sources" icon={<AlertTriangle className="w-4 h-4 text-danger" />}
          sources={leaderboard.least_trusted} color="danger" />
      </div>
    </div>
  )
}

function SourceTable({ title, icon, sources, color }) {
  return (
    <div className="glass-card p-5">
      <div className="flex items-center gap-2 section-title mb-4">
        {icon}{title}
      </div>
      <div className="space-y-2">
        {sources.map((s, i) => (
          <div key={s.domain} className="flex items-center gap-3">
            <span className="text-xs text-slate-600 w-5 text-right">{i + 1}</span>
            <span className="flex-1 font-mono text-sm text-white truncate">{s.domain}</span>
            <div className="w-24 progress-bar">
              <div
                className={`progress-fill bg-${color}`}
                style={{ width: `${s.trust * 100}%` }}
              />
            </div>
            <span className={`text-xs font-bold text-${color} w-10 text-right`}>
              {(s.trust * 100).toFixed(0)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
