import { useState } from 'react'
import { motion } from 'framer-motion'
import { predict } from '../services/api'
import FeatureImportanceChart from '../charts/FeatureImportanceChart'
import EmotionRadar from '../charts/EmotionRadar'
import toast from 'react-hot-toast'
import { BrainCircuit, Eye, Lightbulb } from 'lucide-react'

export default function Explainability() {
  const [headline, setHeadline] = useState('')
  const [article, setArticle]   = useState('')
  const [result, setResult]     = useState(null)
  const [loading, setLoading]   = useState(false)

  const analyse = async () => {
    if (!headline || article.split(' ').length < 10) {
      toast.error('Please enter headline and article (min 10 words)')
      return
    }
    setLoading(true)
    try {
      const { data } = await predict({ headline, article })
      setResult(data)
    } catch (e) {
      toast.error('Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center gap-2">
        <BrainCircuit className="w-6 h-6 text-primary" />
        <div>
          <h1 className="text-2xl font-display font-bold">Explainable AI</h1>
          <p className="text-slate-400 text-sm">Understand WHY the model made its decision</p>
        </div>
      </div>

      {/* Explainability Theory Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[
          {
            icon: '🔍',
            title: 'SHAP Values',
            desc: 'SHapley Additive exPlanations show each word\'s contribution to the final prediction using game theory.',
          },
          {
            icon: '🧪',
            title: 'LIME',
            desc: 'Local Interpretable Model-Agnostic Explanations perturb input text and observe prediction changes.',
          },
          {
            icon: '🎯',
            title: 'Attention Maps',
            desc: 'Transformer attention weights reveal which tokens the BERT model focused on during classification.',
          },
        ].map(({ icon, title, desc }) => (
          <div key={title} className="glass-card p-4">
            <div className="text-2xl mb-2">{icon}</div>
            <div className="font-semibold text-white mb-1">{title}</div>
            <div className="text-xs text-slate-400 leading-relaxed">{desc}</div>
          </div>
        ))}
      </div>

      {/* Input */}
      <div className="glass-card p-5 space-y-4">
        <input
          value={headline}
          onChange={e => setHeadline(e.target.value)}
          placeholder="Headline…"
          className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3
                     text-white placeholder-slate-500 focus:outline-none focus:border-primary/50 text-sm"
        />
        <textarea
          value={article}
          onChange={e => setArticle(e.target.value)}
          placeholder="Article body…"
          rows={5}
          className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3
                     text-white placeholder-slate-500 focus:outline-none focus:border-primary/50
                     text-sm resize-none font-mono"
        />
        <button onClick={analyse} disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
          {loading
            ? <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Explaining…</>
            : <><Eye className="w-4 h-4" /> Generate Explanation</>
          }
        </button>
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Prediction Banner */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`glass-card p-4 border ${result.prediction === 'FAKE' ? 'border-danger/40' : 'border-success/40'} flex items-center gap-4`}
          >
            <div className={`text-4xl font-display font-black ${result.prediction === 'FAKE' ? 'text-danger' : 'text-success'}`}>
              {result.prediction}
            </div>
            <div>
              <div className="text-white font-semibold">
                {(result.confidence * 100).toFixed(1)}% confidence
              </div>
              <div className="text-slate-400 text-sm">
                {result.prediction === 'FAKE'
                  ? 'The model detected multiple misinformation indicators.'
                  : 'The article appears credible based on linguistic and semantic analysis.'}
              </div>
            </div>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <FeatureImportanceChart data={result.feature_importance} />
            <EmotionRadar data={result.emotion_breakdown} />
          </div>

          {/* Highlighted Text */}
          <div className="glass-card p-5">
            <div className="section-title mb-1 flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-warning" />
              Token-Level Explanation
            </div>
            <div className="section-sub mb-4">
              Words highlighted in red were the strongest fake-news indicators
            </div>
            <div className="leading-9 font-mono text-sm">
              {result.highlighted_text?.slice(0, 120).map((item, i) => (
                <span
                  key={i}
                  className={`mr-1 cursor-help ${
                    item.type === 'fake_indicator' ? 'word-fake' :
                    item.type === 'real_indicator' ? 'word-real' : 'word-neutral'
                  }`}
                  title={`Score: ${(item.score * 100).toFixed(1)}%`}
                >
                  {item.word}
                </span>
              ))}
            </div>
            <div className="mt-3 flex gap-4 text-xs text-slate-500">
              <span><span className="word-fake px-1">word</span> = strong fake indicator</span>
              <span><span className="word-real px-1">word</span> = credibility indicator</span>
              <span>Hover words to see contribution scores</span>
            </div>
          </div>

          {/* Suspicious Phrases */}
          {result.suspicious_phrases?.length > 0 && (
            <div className="glass-card p-5">
              <div className="section-title mb-3">Detected Suspicious Phrases</div>
              <div className="flex flex-wrap gap-2">
                {result.suspicious_phrases.map((phrase, i) => (
                  <span key={i} className="text-sm bg-danger/10 text-danger px-3 py-1
                                           rounded-full border border-danger/20 font-mono">
                    "{phrase}"
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
