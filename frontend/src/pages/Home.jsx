import { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import {
  Search, Upload, Link2, Sparkles, AlertTriangle, CheckCircle
} from 'lucide-react'
import { predict } from '../services/api'
import PredictionCard from '../components/PredictionCard'
import EmotionRadar from '../charts/EmotionRadar'
import FeatureImportanceChart from '../charts/FeatureImportanceChart'
import { FullPageLoader, SkeletonCard } from '../components/Loader'
import VoiceInput from '../components/VoiceInput'

const EXAMPLE_FAKE = {
  headline: 'BREAKING: Government secretly poisoning water supply to control population!!!',
  article: `Anonymous whistleblowers have CONFIRMED that the deep state has been adding
mind-control chemicals to municipal water supplies for decades. This BOMBSHELL revelation
will destroy everything you thought you knew! Mainstream media is HIDING this explosive
truth from you. Share before it gets deleted! They don't want you to know what they're
doing to us all! Act NOW before it's too late! This SHOCKING conspiracy has been covered
up by the globalist elites who control our government and pharmaceutical companies.
WAKE UP SHEEPLE! The truth is out there if you dare to look!!!`,
  source: 'http://infowars.com',
}

const EXAMPLE_REAL = {
  headline: 'Federal Reserve raises interest rates by 0.25% amid inflation concerns',
  article: `The Federal Reserve announced on Wednesday that it would raise its benchmark
interest rate by a quarter percentage point, bringing it to a range of 5.25% to 5.5%,
the highest level in 22 years. The decision, which was widely expected, reflects the
central bank's ongoing effort to bring inflation back to its 2% target. Fed Chair Jerome
Powell said at a press conference that the committee would continue to monitor economic
data carefully and adjust policy as conditions warrant. Consumer prices rose 3.2% in the
past year, down from a peak of 9.1% in June 2022, according to Labor Department data.`,
  source: 'https://reuters.com',
}

export default function Home() {
  const [headline, setHeadline] = useState('')
  const [article, setArticle]   = useState('')
  const [sourceUrl, setSourceUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')

  const onDrop = useCallback((files) => {
    const file = files[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (e) => setArticle(e.target.result)
    reader.readAsText(file)
    toast.success(`Loaded: ${file.name}`)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/plain': ['.txt'] },
    multiple: false,
  })

  const handlePredict = async () => {
    if (!headline.trim()) { toast.error('Please enter a headline'); return }
    if (article.trim().split(' ').length < 10) { toast.error('Article too short (min 10 words)'); return }

    setLoading(true)
    setResult(null)
    try {
      const { data } = await predict({ headline, article, source_url: sourceUrl || undefined })
      setResult(data)
      toast.success('Analysis complete!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Analysis failed. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  const loadExample = (example) => {
    setHeadline(example.headline)
    setArticle(example.article)
    setSourceUrl(example.source)
    setResult(null)
    toast('Example loaded — click Analyse!', { icon: '💡' })
  }

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'emotions', label: 'Emotions' },
    { id: 'features', label: 'Features' },
    { id: 'linguistic', label: 'Linguistic' },
  ]

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-display font-bold text-white flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-primary" />
            Fake News Detector
          </h1>
          <p className="text-slate-400 text-sm mt-0.5">
            AI-powered semantic + linguistic analysis with explainable results
          </p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => loadExample(EXAMPLE_FAKE)}
            className="text-xs btn-ghost py-1.5 px-3 flex items-center gap-1.5">
            <AlertTriangle className="w-3 h-3 text-danger" /> Fake Example
          </button>
          <button onClick={() => loadExample(EXAMPLE_REAL)}
            className="text-xs btn-ghost py-1.5 px-3 flex items-center gap-1.5">
            <CheckCircle className="w-3 h-3 text-success" /> Real Example
          </button>
        </div>
      </div>

      {/* Input Panel */}
      <div className="glass-card p-6 space-y-4">
        {/* Headline */}
        <div>
          <label className="block text-xs text-slate-400 uppercase tracking-wider mb-2">
            Article Headline *
          </label>
          <input
            value={headline}
            onChange={e => setHeadline(e.target.value)}
            placeholder="Enter the news headline…"
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white
                       placeholder-slate-500 focus:outline-none focus:border-primary/50 focus:bg-white/8
                       transition-all text-sm"
          />
        </div>

        {/* Article Body */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-xs text-slate-400 uppercase tracking-wider">
              Article Body * (min 10 words)
            </label>
            <VoiceInput onTranscript={(t) => setArticle(prev => prev + ' ' + t)} />
          </div>
          <textarea
            value={article}
            onChange={e => setArticle(e.target.value)}
            placeholder="Paste the full article text here…"
            rows={7}
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white
                       placeholder-slate-500 focus:outline-none focus:border-primary/50 focus:bg-white/8
                       transition-all text-sm resize-none font-mono leading-relaxed"
          />
          <div className="text-right text-xs text-slate-600 mt-1">
            {article.trim().split(/\s+/).filter(Boolean).length} words
          </div>
        </div>

        {/* Source URL + file drop */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Source URL */}
          <div>
            <label className="block text-xs text-slate-400 uppercase tracking-wider mb-2">
              Source URL (optional)
            </label>
            <div className="flex items-center gap-2 bg-white/5 border border-white/10
                            rounded-xl px-4 py-3 focus-within:border-primary/50 transition-all">
              <Link2 className="w-4 h-4 text-slate-500 shrink-0" />
              <input
                value={sourceUrl}
                onChange={e => setSourceUrl(e.target.value)}
                placeholder="https://example.com/article"
                className="flex-1 bg-transparent text-white text-sm placeholder-slate-500
                           focus:outline-none"
              />
            </div>
          </div>

          {/* File drop */}
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-xl px-4 py-3 text-center cursor-pointer
                        transition-all text-sm flex items-center justify-center gap-2
                        ${isDragActive
                          ? 'border-primary/60 bg-primary/10 text-primary'
                          : 'border-white/10 text-slate-500 hover:border-white/20 hover:text-slate-400'
                        }`}
          >
            <input {...getInputProps()} />
            <Upload className="w-4 h-4 shrink-0" />
            {isDragActive ? 'Drop it here' : 'Drop .txt file or click'}
          </div>
        </div>

        {/* Analyse Button */}
        <button
          onClick={handlePredict}
          disabled={loading}
          className="w-full btn-primary flex items-center justify-center gap-2
                     disabled:opacity-50 disabled:cursor-not-allowed py-4 text-base"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Analysing…
            </>
          ) : (
            <>
              <Search className="w-5 h-5" />
              Analyse for Fake News
            </>
          )}
        </button>
      </div>

      {/* Loading State */}
      {loading && <FullPageLoader />}

      {/* Results */}
      {result && !loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-6"
        >
          <PredictionCard result={result} />

          {/* Tabs */}
          <div className="flex gap-1 p-1 bg-white/5 rounded-xl border border-white/10 w-fit">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeTab === tab.id
                    ? 'bg-primary text-white shadow-neon-blue'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Model Scores */}
              <div className="glass-card p-5">
                <div className="section-title mb-3">Model Scores</div>
                <div className="space-y-3">
                  {Object.entries(result.model_scores || {}).map(([model, score]) => (
                    score >= 0 && (
                      <div key={model}>
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-slate-400 capitalize">
                            {model.replace('_', ' ')}
                          </span>
                          <span className={score > 0.5 ? 'text-danger' : 'text-success'}>
                            {(score * 100).toFixed(1)}% Fake
                          </span>
                        </div>
                        <div className="progress-bar">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${score * 100}%` }}
                            transition={{ duration: 0.6 }}
                            className={`progress-fill ${
                              score > 0.5 ? 'bg-danger' : 'bg-success'
                            }`}
                          />
                        </div>
                      </div>
                    )
                  ))}
                </div>
              </div>

              {/* Linguistic Summary */}
              <div className="glass-card p-5">
                <div className="section-title mb-3">Linguistic Analysis</div>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  {[
                    ['Clickbait Score',    result.linguistic_features?.clickbait_score,    '%'],
                    ['Propaganda Score',   result.linguistic_features?.propaganda_score,   '%'],
                    ['Sensationalism',     result.linguistic_features?.sensationalism_score,'%'],
                    ['Urgency Score',      result.linguistic_features?.urgency_score,       '%'],
                    ['Caps Ratio',         result.linguistic_features?.caps_ratio,          '%'],
                    ['Lexical Diversity',  result.linguistic_features?.lexical_diversity,   ''],
                    ['Readability',        result.linguistic_features?.readability_score?.toFixed(0), '/100'],
                    ['Word Count',         result.linguistic_features?.word_count,          ''],
                  ].map(([label, val, unit]) => (
                    val !== undefined && (
                      <div key={label} className="flex justify-between">
                        <span className="text-slate-500">{label}</span>
                        <span className="text-white font-medium">
                          {unit === '%'
                            ? `${((val || 0) * 100).toFixed(0)}%`
                            : `${val}${unit}`
                          }
                        </span>
                      </div>
                    )
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'emotions' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <EmotionRadar data={result.emotion_breakdown} />
              <div className="glass-card p-5 space-y-3">
                <div className="section-title">Manipulation Signals</div>
                {[
                  { label: 'Manipulation Intensity', value: result.manipulation_intensity },
                  { label: 'Overall Emotion Score',  value: result.emotion_score },
                  { label: 'Sentiment Polarity',     value: Math.abs(result.sentiment_polarity) },
                  { label: 'Subjectivity',           value: result.subjectivity_score },
                ].map(({ label, value }) => (
                  <div key={label}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-slate-400">{label}</span>
                      <span className={value > 0.5 ? 'text-danger' : 'text-success'}>
                        {(value * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="progress-bar">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${value * 100}%` }}
                        transition={{ duration: 0.6 }}
                        className={`progress-fill ${value > 0.5 ? 'bg-danger' : 'bg-success'}`}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'features' && (
            <FeatureImportanceChart data={result.feature_importance} />
          )}

          {activeTab === 'linguistic' && (
            <div className="glass-card p-5">
              <div className="section-title mb-3">Highlighted Text Analysis</div>
              <div className="text-sm leading-8 font-mono text-slate-300">
                {result.highlighted_text?.slice(0, 100).map((item, i) => (
                  <span
                    key={i}
                    className={`${item.type === 'fake_indicator' ? 'word-fake' : item.type === 'real_indicator' ? 'word-real' : 'word-neutral'} mr-1`}
                    title={`Score: ${item.score?.toFixed(3)}`}
                  >
                    {item.word}
                  </span>
                ))}
              </div>
              <div className="flex gap-4 mt-3 text-xs text-slate-500">
                <span><span className="word-fake">red</span> = fake indicator</span>
                <span><span className="word-real">green</span> = credible indicator</span>
              </div>
            </div>
          )}
        </motion.div>
      )}
    </div>
  )
}
