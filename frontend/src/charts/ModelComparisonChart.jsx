import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts'

export default function ModelComparisonChart({ data = {} }) {
  const chartData = Object.entries(data).map(([model, metrics]) => ({
    name: model.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase()),
    Accuracy: Math.round((metrics.accuracy || 0) * 100),
    F1: Math.round((metrics.f1 || 0) * 100),
    AUC: Math.round((metrics.auc || 0) * 100),
  }))

  return (
    <div className="glass-card p-5">
      <div className="section-title mb-0.5">Model Performance Comparison</div>
      <div className="section-sub mb-4">Accuracy · F1-Score · ROC-AUC (%)</div>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} />
          <YAxis domain={[70, 100]} tick={{ fill: '#64748b', fontSize: 10 }} unit="%" />
          <Tooltip
            contentStyle={{
              background: '#1a1a2e',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: 8,
              color: '#e2e8f0',
            }}
            formatter={(v) => [`${v}%`]}
          />
          <Legend wrapperStyle={{ color: '#94a3b8', fontSize: 12 }} />
          <Bar dataKey="Accuracy" fill="#6366f1" radius={[4,4,0,0]} />
          <Bar dataKey="F1"       fill="#22d3ee" radius={[4,4,0,0]} />
          <Bar dataKey="AUC"      fill="#f59e0b" radius={[4,4,0,0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
