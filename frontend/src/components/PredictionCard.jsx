import { motion } from 'framer-motion'
import { Shield, ShieldAlert, AlertTriangle, CheckCircle, Clock, Zap } from 'lucide-react'
import ConfidenceMeter from './ConfidenceMeter'

export default function PredictionCard({ result }) {
  if (!result) return null
  const isFake = result.prediction === 'FAKE'

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`glass-card p-6 border-2 ${
        isFake ? 'border-danger/40 shadow-neon-red' : 'border-success/40 shadow-neon-green'
      }`}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className={`w-14 h-14 rounded-2xl flex items-center justify-center ${
            isFake ? 'bg-danger/15' : 'bg-success/15'
          }`}>
            {isFake
              ? <ShieldAlert className="w-8 h-8 text-danger" />
              : <Shield className="w-8 h-8 text-success" />
            }
          </div>
          <div>
            <div className={`text-3xl font-display font-black ${
              isFake ? 'text-danger' : 'text-success'
            }`}>
              {result.prediction}
            </div>
            <div className="text-slate-400 text-sm mt-0.5">
              Confidence: <span className="font-semibold text-white">
                {(result.confidence * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>

        <div className="flex flex-col items-end gap-2">
          <div className="flex items-center gap-1 text-xs text-slate-500">
            <Clock className="w-3 h-3" />
            {result.processing_time_ms?.toFixed(0)}ms
          </div>
          <div className={`score-badge ${isFake ? 'score-fake' : 'score-real'}`}>
            {isFake ? <AlertTriangle className="w-3 h-3" /> : <CheckCircle className="w-3 h-3" />}
            {isFake ? 'Misinformation Detected' : 'Appears Credible'}
          </div>
        </div>
      </div>

      {/* Confidence Meter */}
      <ConfidenceMeter
        fakeProb={result.fake_probability}
        realProb={result.real_probability}
      />

      {/* Score Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6">
        <ScoreItem
          label="Emotion Score"
          value={result.emotion_score}
          color={result.emotion_score > 0.6 ? 'danger' : 'warning'}
          icon="😤"
        />
        <ScoreItem
          label="Credibility"
          value={result.credibility_score}
          color={result.credibility_score > 0.6 ? 'success' : 'danger'}
          icon="🛡️"
        />
        <ScoreItem
          label="Contradiction"
          value={result.contradiction_score}
          color={result.contradiction_score > 0.5 ? 'danger' : 'success'}
          icon="⚡"
        />
        <ScoreItem
          label="AI-Generated"
          value={result.ai_generated_probability}
          color={result.ai_generated_probability > 0.5 ? 'warning' : 'success'}
          icon="🤖"
        />
      </div>

      {/* Suspicious Phrases */}
      {result.suspicious_phrases?.length > 0 && (
        <div className="mt-4 p-3 bg-danger/5 border border-danger/20 rounded-xl">
          <div className="text-xs text-danger font-semibold mb-2 flex items-center gap-1">
            <AlertTriangle className="w-3 h-3" />
            Suspicious Phrases Detected
          </div>
          <div className="flex flex-wrap gap-1.5">
            {result.suspicious_phrases.slice(0, 8).map((phrase, i) => (
              <span key={i} className="text-xs bg-danger/10 text-danger/80
                                       px-2 py-0.5 rounded-full border border-danger/20">
                {phrase}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* AI Verdict */}
      {result.ai_verdict && (
        <div className="mt-3 text-xs text-slate-400 flex items-center gap-1.5">
          <Zap className="w-3 h-3 text-accent" />
          AI Text Analysis: <span className="text-accent font-medium">{result.ai_verdict}</span>
        </div>
      )}
    </motion.div>
  )
}

function ScoreItem({ label, value, color, icon }) {
  const colorMap = {
    danger:  'text-danger  bg-danger/10  border-danger/20',
    success: 'text-success bg-success/10 border-success/20',
    warning: 'text-warning bg-warning/10 border-warning/20',
  }
  return (
    <div className={`p-3 rounded-xl border ${colorMap[color]} text-center`}>
      <div className="text-2xl mb-0.5">{icon}</div>
      <div className={`text-lg font-bold font-display`}>
        {(value * 100).toFixed(0)}%
      </div>
      <div className="text-[10px] font-medium opacity-70 uppercase tracking-wider">{label}</div>
    </div>
  )
}
