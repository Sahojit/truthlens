import { BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ResponsiveContainer, ReferenceLine } from 'recharts'

export default function FeatureImportanceChart({ data = {} }) {
  const chartData = Object.entries(data)
    .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
    .slice(0, 15)
    .map(([feature, value]) => ({ feature, value: parseFloat(value.toFixed(4)) }))

  if (chartData.length === 0) {
    return (
      <div className="glass-card p-5 flex items-center justify-center h-48 text-slate-500 text-sm">
        Feature importance data will appear after analysis
      </div>
    )
  }

  return (
    <div className="glass-card p-5">
      <div className="section-title mb-0.5">Feature Importance</div>
      <div className="section-sub mb-4">
        Red = fake indicators · Blue = real indicators
      </div>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 20, right: 20 }}>
          <XAxis type="number" tick={{ fill: '#64748b', fontSize: 10 }} />
          <YAxis
            type="category"
            dataKey="feature"
            tick={{ fill: '#94a3b8', fontSize: 10 }}
            width={100}
          />
          <ReferenceLine x={0} stroke="rgba(255,255,255,0.2)" />
          <Tooltip
            contentStyle={{
              background: '#1a1a2e',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: 8,
              color: '#e2e8f0',
            }}
            formatter={(v) => [v.toFixed(4), 'Contribution']}
          />
          <Bar dataKey="value" radius={[0, 4, 4, 0]}>
            {chartData.map((entry, i) => (
              <Cell
                key={i}
                fill={entry.value > 0 ? 'rgba(239,68,68,0.7)' : 'rgba(34,197,94,0.7)'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
