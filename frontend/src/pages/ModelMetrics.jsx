import { useEffect, useState } from 'react'
import { getModelEvaluation } from '../services/api'
import ModelComparisonChart from '../charts/ModelComparisonChart'
import { Activity } from 'lucide-react'

export default function ModelMetrics() {
  const [data, setData] = useState(null)

  useEffect(() => {
    getModelEvaluation().then(r => setData(r.data)).catch(() => {})
  }, [])

  const models = data?.models || {}
  const dataset = data?.dataset_info || {}

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center gap-2">
        <Activity className="w-6 h-6 text-primary" />
        <h1 className="text-2xl font-display font-bold">Model Evaluation Metrics</h1>
      </div>

      {/* Dataset Info */}
      {dataset.name && (
        <div className="glass-card p-5">
          <div className="section-title mb-3">Dataset Information</div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
            <div><div className="text-slate-400 text-xs mb-0.5">Dataset</div><div className="text-white font-medium">{dataset.name}</div></div>
            <div><div className="text-slate-400 text-xs mb-0.5">Total Samples</div><div className="text-primary font-bold text-lg">{dataset.total_samples?.toLocaleString()}</div></div>
            <div><div className="text-slate-400 text-xs mb-0.5">Fake</div><div className="text-danger font-bold text-lg">{dataset.fake_samples?.toLocaleString()}</div></div>
            <div><div className="text-slate-400 text-xs mb-0.5">Real</div><div className="text-success font-bold text-lg">{dataset.real_samples?.toLocaleString()}</div></div>
          </div>
        </div>
      )}

      {/* Model Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(models).map(([name, m]) => (
          <div key={name} className="glass-card p-5">
            <div className="font-display font-semibold text-white mb-3 capitalize">
              {name.replace(/_/g, ' ')}
            </div>
            <div className="space-y-2">
              {[
                { label: 'Accuracy',  value: m.accuracy,  color: 'text-primary' },
                { label: 'Precision', value: m.precision, color: 'text-accent'  },
                { label: 'Recall',    value: m.recall,    color: 'text-warning' },
                { label: 'F1-Score',  value: m.f1_score,  color: 'text-success' },
                { label: 'ROC-AUC',   value: m.roc_auc,   color: 'text-purple-400' },
              ].map(({ label, value, color }) => (
                <div key={label} className="flex items-center gap-2">
                  <span className="text-xs text-slate-500 w-20">{label}</span>
                  <div className="flex-1 progress-bar">
                    <div
                      className="progress-fill bg-primary/60"
                      style={{ width: `${value * 100}%` }}
                    />
                  </div>
                  <span className={`text-xs font-bold ${color} w-12 text-right`}>
                    {(value * 100).toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
            {/* Confusion Matrix Mini */}
            {m.confusion_matrix && (
              <div className="mt-3 pt-3 border-t border-white/5">
                <div className="text-xs text-slate-500 mb-2">Confusion Matrix</div>
                <div className="grid grid-cols-2 gap-1 text-center text-xs font-mono">
                  {m.confusion_matrix.flat().map((v, i) => (
                    <div key={i} className={`py-1.5 rounded ${
                      i === 0 || i === 3 ? 'bg-success/15 text-success' : 'bg-danger/15 text-danger'
                    }`}>{v}</div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Comparison Chart */}
      <ModelComparisonChart data={models} />
    </div>
  )
}
